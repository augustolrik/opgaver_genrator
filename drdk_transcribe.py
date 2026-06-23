"""
Download subtitles from a DRTV page, or transcribe a local media file.

Examples:
    python drdk_transcribe.py "https://www.dr.dk/drtv/se/vores-spektakulaere-solsystem_-vilde-vulkaner_574353"
    python drdk_transcribe.py "https://www.dr.dk/drtv/se/..." --output "C:\\Temp\\dr_tekst.txt"
    python drdk_transcribe.py "https://www.dr.dk/drtv/se/..." --format txt
    python drdk_transcribe.py --media "C:\\Users\\me\\video.mp4" --language da

If you run the script without arguments, it asks for:
    1. the DR link
    2. the file path where the text should be saved

This script does not bypass DRM or login/geo restrictions. It only uses subtitle
files exposed by the page/metadata, or a local media file you provide.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

link = "https://www.dr.dk/drtv/se/vores-spektakulaere-solsystem_-vilde-vulkaner_574353"

DEFAULT_OUT_DIR = Path(__file__).with_name("dr_transcripts")
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0 Safari/537.36"
)


@dataclass
class SubtitleCandidate:
    url: str
    source: str


def fetch_text(url: str, timeout: int = 25) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def fetch_bytes(url: str, timeout: int = 25) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def safe_name(text: str, fallback: str = "drtv_transcript") -> str:
    text = html.unescape(text or "").strip()
    text = re.sub(r"[^\w .()-]+", "_", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "_", text).strip("._ ")
    return text[:90] or fallback


def resolve_output_path(output: str | None, out_dir: Path, title: str, suffix: str = ".txt") -> Path:
    if output:
        path = Path(output).expanduser()
        if path.suffix:
            return path
        return path / f"{title}{suffix}"
    return out_dir / f"{title}{suffix}"


def prompt_if_missing(args: argparse.Namespace) -> argparse.Namespace:
    if args.url or args.media:
        return args

    print("DR transcribe")
    print("Skriv DR-linket, og skriv bagefter den fulde sti hvor teksten skal gemmes.")
    args.url = input("DR link: ").strip()
    args.output = input(r"Gem tekst som fx C:\Python\opgaver_genrator\dr_transcripts\solsystem.txt: ").strip()
    return args


def episode_id_from_url(url: str) -> str | None:
    match = re.search(r"_(\d+)(?:[/?#]|$)", url)
    return match.group(1) if match else None


def extract_title(page_html: str, url: str) -> str:
    title_patterns = [
        r"<title>(.*?)</title>",
        r'"title"\s*:\s*"([^"]+)"',
        r'"programTitle"\s*:\s*"([^"]+)"',
        r'"episodeTitle"\s*:\s*"([^"]+)"',
    ]
    for pattern in title_patterns:
        match = re.search(pattern, page_html, flags=re.DOTALL)
        if match:
            title = match.group(1)
            title = title.replace("\\u0026", "&")
            title = title.encode("utf-8", errors="ignore").decode("unicode_escape", errors="ignore")
            return safe_name(title)

    episode_id = episode_id_from_url(url)
    return f"drtv_{episode_id}" if episode_id else "drtv_transcript"


def normalize_possible_url(raw: str, base_url: str) -> str | None:
    raw = raw.strip().strip("'\"")
    raw = raw.replace("\\u002F", "/").replace("\\/", "/").replace("&amp;", "&")
    raw = unquote(raw)

    if not re.search(r"\.(vtt|srt|ttml|dfxp|xml)(?:[?#]|$)", raw, flags=re.I):
        return None

    if raw.startswith("//"):
        parsed_base = urlparse(base_url)
        return f"{parsed_base.scheme}:{raw}"

    return urljoin(base_url, raw)


def find_subtitle_urls_in_text(text: str, base_url: str, source: str) -> list[SubtitleCandidate]:
    candidates: list[SubtitleCandidate] = []
    seen: set[str] = set()

    patterns = [
        r'https?:\\?/\\?/[^"\'<>\s]+?\.(?:vtt|srt|ttml|dfxp|xml)(?:\?[^"\'<>\s]*)?',
        r'//[^"\'<>\s]+?\.(?:vtt|srt|ttml|dfxp|xml)(?:\?[^"\'<>\s]*)?',
        r'/[^"\'<>\s]+?\.(?:vtt|srt|ttml|dfxp|xml)(?:\?[^"\'<>\s]*)?',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.I):
            url = normalize_possible_url(match.group(0), base_url)
            if url and url not in seen:
                seen.add(url)
                candidates.append(SubtitleCandidate(url=url, source=source))

    return candidates


def walk_json_urls(value, base_url: str, source: str) -> Iterable[SubtitleCandidate]:
    if isinstance(value, dict):
        for item in value.values():
            yield from walk_json_urls(item, base_url, source)
    elif isinstance(value, list):
        for item in value:
            yield from walk_json_urls(item, base_url, source)
    elif isinstance(value, str):
        url = normalize_possible_url(value, base_url)
        if url:
            yield SubtitleCandidate(url=url, source=source)


def find_next_data_candidates(page_html: str, base_url: str) -> list[SubtitleCandidate]:
    candidates: list[SubtitleCandidate] = []
    seen: set[str] = set()

    match = re.search(
        r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        page_html,
        flags=re.DOTALL | re.I,
    )
    if not match:
        return candidates

    try:
        data = json.loads(html.unescape(match.group(1)))
    except json.JSONDecodeError:
        return candidates

    for candidate in walk_json_urls(data, base_url, "__NEXT_DATA__"):
        if candidate.url not in seen:
            seen.add(candidate.url)
            candidates.append(candidate)
    return candidates


def candidate_api_urls(drtv_url: str) -> list[str]:
    episode_id = episode_id_from_url(drtv_url)
    if not episode_id:
        return []

    # DR changes internal API paths occasionally. These are harmless probes:
    # if an endpoint is gone, the script just ignores it.
    return [
        f"https://www.dr.dk/drtv/api/programcard/{episode_id}",
        f"https://www.dr.dk/drtv/api/programs/{episode_id}",
        f"https://www.dr.dk/drtv/api/episode/{episode_id}",
    ]


def find_subtitle_candidates(drtv_url: str) -> tuple[str, list[SubtitleCandidate]]:
    page_html = fetch_text(drtv_url)
    title = extract_title(page_html, drtv_url)

    candidates: list[SubtitleCandidate] = []
    candidates.extend(find_subtitle_urls_in_text(page_html, drtv_url, "page_html"))
    candidates.extend(find_next_data_candidates(page_html, drtv_url))

    for api_url in candidate_api_urls(drtv_url):
        try:
            api_text = fetch_text(api_url, timeout=12)
        except Exception:
            continue
        candidates.extend(find_subtitle_urls_in_text(api_text, api_url, api_url))
        try:
            api_json = json.loads(api_text)
        except json.JSONDecodeError:
            continue
        candidates.extend(walk_json_urls(api_json, api_url, api_url))

    unique: list[SubtitleCandidate] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate.url not in seen:
            seen.add(candidate.url)
            unique.append(candidate)

    return title, unique


def strip_vtt_or_srt(subtitle_text: str) -> str:
    lines: list[str] = []
    previous = ""

    for raw_line in subtitle_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.upper().startswith("WEBVTT"):
            continue
        if line.isdigit():
            continue
        if "-->" in line:
            continue
        if re.match(r"^(NOTE|STYLE|REGION)\b", line, flags=re.I):
            continue

        line = re.sub(r"<[^>]+>", "", line)
        line = html.unescape(line).strip()
        if not line or line == previous:
            continue
        lines.append(line)
        previous = line

    return "\n".join(lines) + ("\n" if lines else "")


def save_subtitles(
    candidates: list[SubtitleCandidate],
    out_dir: Path,
    title: str,
    output_format: str,
    output_path: str | None = None,
) -> Path:
    if not candidates:
        raise RuntimeError("Jeg fandt ingen undertekstfiler på siden eller i metadata.")

    out_dir.mkdir(parents=True, exist_ok=True)
    first_error: Exception | None = None

    for index, candidate in enumerate(candidates, start=1):
        try:
            content = fetch_bytes(candidate.url)
        except Exception as error:
            first_error = error
            continue

        suffix_match = re.search(r"\.(vtt|srt|ttml|dfxp|xml)(?:[?#]|$)", candidate.url, flags=re.I)
        source_suffix = suffix_match.group(1).lower() if suffix_match else "vtt"
        subtitle_text = content.decode("utf-8-sig", errors="replace")

        if output_format == "raw":
            out_path = resolve_output_path(output_path, out_dir, title, f".{source_suffix}")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(subtitle_text, encoding="utf-8")
            return out_path

        transcript = strip_vtt_or_srt(subtitle_text)
        if transcript.strip():
            out_path = resolve_output_path(output_path, out_dir, title, ".txt")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(transcript, encoding="utf-8")
            return out_path

        raw_path = out_dir / f"{title}_raw_{index}.{source_suffix}"
        raw_path.write_text(subtitle_text, encoding="utf-8")

    if first_error:
        raise RuntimeError(f"Undertekstlinks blev fundet, men kunne ikke hentes: {first_error}")
    raise RuntimeError("Undertekstlinks blev fundet, men de indeholdt ikke læsbar tekst.")


def run_command(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")


def fetch_with_ytdlp(
    drtv_url: str,
    out_dir: Path,
    output_format: str,
    output_path: str | None = None,
) -> Path | None:
    ytdlp = shutil.which("yt-dlp")
    if not ytdlp:
        return None

    out_dir.mkdir(parents=True, exist_ok=True)
    before = {path.resolve() for path in out_dir.glob("*")}
    template = str(out_dir / "%(title).90s.%(ext)s")
    command = [
        ytdlp,
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        "da,da-DK,en",
        "--convert-subs",
        "srt",
        "-o",
        template,
        drtv_url,
    ]

    result = run_command(command)
    after = sorted(
        (path for path in out_dir.glob("*") if path.resolve() not in before),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    subtitle_files = [
        path for path in after
        if path.suffix.lower() in {".srt", ".vtt", ".ttml", ".dfxp", ".xml"}
    ]
    if not subtitle_files:
        if result.returncode != 0:
            raise RuntimeError("yt-dlp kunne ikke hente undertekster:\n" + result.stderr.strip())
        return None

    subtitle_file = subtitle_files[0]
    if output_format == "raw":
        if output_path:
            destination = resolve_output_path(output_path, out_dir, subtitle_file.stem, subtitle_file.suffix)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(subtitle_file), str(destination))
            return destination
        return subtitle_file

    transcript = strip_vtt_or_srt(subtitle_file.read_text(encoding="utf-8-sig", errors="replace"))
    out_path = resolve_output_path(output_path, out_dir, subtitle_file.stem, ".txt")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(transcript, encoding="utf-8")
    return out_path


def transcribe_local_media(
    media_path: Path,
    out_dir: Path,
    language: str,
    model_name: str,
    output_path: str | None = None,
) -> Path:
    if not media_path.exists():
        raise FileNotFoundError(f"Filen findes ikke: {media_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = resolve_output_path(output_path, out_dir, safe_name(media_path.stem), ".txt")

    try:
        import whisper  # type: ignore
    except ImportError:
        raise RuntimeError(
            "Whisper er ikke installeret. Installer fx med: pip install -U openai-whisper"
        )

    model = whisper.load_model(model_name)
    result = model.transcribe(str(media_path), language=language)
    out_path.write_text(result.get("text", "").strip() + "\n", encoding="utf-8")
    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hent DR-undertekster fra en DRTV-side eller transskriber en lokal mediefil."
    )
    parser.add_argument("url", nargs="?", help="DRTV URL, fx https://www.dr.dk/drtv/se/...")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Mappe til output")
    parser.add_argument(
        "-o",
        "--output",
        help=r"Fuld filsti til teksten, fx C:\Python\opgaver_genrator\dr_transcripts\solsystem.txt",
    )
    parser.add_argument(
        "--format",
        choices=["txt", "raw"],
        default="txt",
        help="txt fjerner tidskoder. raw gemmer den originale undertekstfil.",
    )
    parser.add_argument("--media", help="Lokal video/lydfil der skal transskriberes med Whisper")
    parser.add_argument("--language", default="da", help="Whisper-sprogkode, fx da eller en")
    parser.add_argument("--model", default="small", help="Whisper-model, fx tiny, base, small, medium")
    return parser.parse_args()


def main() -> int:
    args = prompt_if_missing(parse_args())
    out_dir = Path(args.out_dir)

    try:
        if args.media:
            out_path = transcribe_local_media(Path(args.media), out_dir, args.language, args.model, args.output)
            print(f"Transskription gemt: {out_path}")
            return 0

        if not args.url:
            print("Fejl: Angiv enten en DRTV URL eller --media.", file=sys.stderr)
            return 2

        title, candidates = find_subtitle_candidates(args.url)
        if candidates:
            print(f"Fandt {len(candidates)} mulige undertekstfil(er). Bruger den første der kan hentes.")
            out_path = save_subtitles(candidates, out_dir, title, args.format, args.output)
        else:
            out_path = fetch_with_ytdlp(args.url, out_dir, args.format, args.output)
            if out_path is None:
                raise RuntimeError(
                    "Jeg fandt ingen undertekstfiler på siden eller i metadata. "
                    "Installer evt. yt-dlp med 'pip install -U yt-dlp' og prøv igen, "
                    "eller brug --media med en lokal fil."
                )
        print(f"Transkript gemt: {out_path}")
        return 0
    except Exception as error:
        print(f"Fejl: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
