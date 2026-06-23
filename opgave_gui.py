from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote
import html
import json
import re

import unikke_opgaver_set_up as opgaver


HOST = "127.0.0.1"
PORT = 8000
PDF_MAPPE = Path(opgaver.PDF_MAPPE)
NIVEAUER = ["let", "mellem", "svaer", "random"]


def rens_filnavn(filnavn):
    filnavn = filnavn.strip() or "opgaver.pdf"
    filnavn = re.sub(r"[^\w .()-]", "_", filnavn, flags=re.UNICODE)
    if not filnavn.lower().endswith(".pdf"):
        filnavn += ".pdf"
    return filnavn


def clamp_int(value, mindste, stoerste, standard):
    try:
        tal = int(value)
    except (TypeError, ValueError):
        return standard
    return max(mindste, min(stoerste, tal))


def hent_opgave_metadata():
    metadata = []
    for navn, skabelon in opgaver.BOKS_SKABELONER.items():
        metadata.append(
            {
                "navn": navn,
                "titel": skabelon.get("titel", navn),
                "forklaring": skabelon.get("forklaring", ""),
                "maks_antal": skabelon.get("maks_antal"),
            }
        )
    return metadata


def byg_pdf_fra_payload(payload):
    antal_bokse = 8 if payload.get("dobbeltsidet") else 4
    antal_sider = clamp_int(payload.get("antal_sider"), 1, 300, opgaver.ANTAL_SIDER)
    antal_opgaver = clamp_int(payload.get("antal_opgaver"), 1, 12, opgaver.ANTAL_OPGAVER_I_BOKS)
    filnavn = rens_filnavn(payload.get("filnavn", "opgaver.pdf"))
    bokse = payload.get("bokse", [])

    boks_valg = []
    for indeks in range(antal_bokse):
        valg = bokse[indeks] if indeks < len(bokse) else {}
        navn = valg.get("navn")
        niveau = valg.get("niveau", "random")

        if not navn:
            boks_valg.append(None)
            continue
        if navn not in opgaver.BOKS_SKABELONER:
            raise ValueError(f"Ukendt opgave: {navn}")
        if niveau not in NIVEAUER:
            niveau = "random"
        boks_valg.append((navn, niveau))

    PDF_MAPPE.mkdir(parents=True, exist_ok=True)
    filsti = PDF_MAPPE / filnavn
    boks_opsaetning = opgaver.byg_boks_opsaetning(boks_valg, opgaver.BOKS_SKABELONER)
    opgaver.byg_pdf(str(filsti), antal_sider, boks_opsaetning, antal_opgaver)

    return {
        "filnavn": filnavn,
        "sti": str(filsti),
        "url": f"/pdf/{quote(filnavn)}",
    }


HTML_TEMPLATE = r"""<!doctype html>
<html lang="da">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Opgavegenerator</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f7f4;
      --panel: #ffffff;
      --ink: #202124;
      --muted: #62645f;
      --line: #d8d8d2;
      --accent: #207567;
      --accent-dark: #15594e;
      --soft: #eef5f2;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--ink);
    }

    header {
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }

    .wrap {
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
    }

    .topbar {
      min-height: 72px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }

    h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: 0;
    }

    main {
      padding: 24px 0 36px;
    }

    .controls {
      display: grid;
      grid-template-columns: repeat(4, minmax(150px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
      align-items: end;
    }

    label {
      display: grid;
      gap: 6px;
      font-size: 13px;
      color: var(--muted);
      font-weight: 700;
    }

    input, select, button {
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 10px;
      font: inherit;
      background: var(--panel);
      color: var(--ink);
    }

    input[type="checkbox"] {
      min-height: auto;
      width: 18px;
      height: 18px;
      padding: 0;
    }

    .checkline {
      display: flex;
      align-items: center;
      gap: 8px;
      min-height: 38px;
      padding: 0 2px;
      color: var(--ink);
      font-weight: 600;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(260px, 1fr));
      gap: 12px;
    }

    .box {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      display: grid;
      gap: 10px;
    }

    .box-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      font-weight: 700;
    }

    .box-fields {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 120px;
      gap: 10px;
    }

    .hint {
      color: var(--muted);
      font-size: 12px;
      min-height: 16px;
      line-height: 1.35;
    }

    .actions {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-top: 18px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
    }

    button {
      border-color: var(--accent);
      background: var(--accent);
      color: white;
      cursor: pointer;
      font-weight: 700;
      padding-inline: 16px;
    }

    button:hover { background: var(--accent-dark); }
    button:disabled { opacity: 0.6; cursor: wait; }

    .result {
      min-height: 38px;
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--muted);
    }

    .result a {
      color: var(--accent-dark);
      font-weight: 700;
    }

    .note {
      margin: 0 0 18px;
      padding: 10px 12px;
      border: 1px solid #cfe1da;
      background: var(--soft);
      border-radius: 8px;
      color: #26453f;
      font-size: 14px;
      line-height: 1.35;
    }

    @media (max-width: 760px) {
      .controls, .grid { grid-template-columns: 1fr; }
      .box-fields { grid-template-columns: 1fr; }
      .actions { align-items: stretch; flex-direction: column; }
      button { width: 100%; }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap topbar">
      <h1>Opgavegenerator</h1>
      <span class="hint">PDF'er gemmes i C:\Python\random_opgaver_pdf</span>
    </div>
  </header>

  <main class="wrap">
    <p class="note">Opgaverne i listen kommer direkte fra <code>BOKS_SKABELONER</code>. Når du tilføjer en ny opgavetype i Python-filen og registrerer den der, kommer den automatisk med her.</p>

    <section class="controls">
      <label>
        Filnavn
        <input id="filnavn" value="opgaver.pdf">
      </label>
      <label>
        Antal sider
        <input id="antalSider" type="number" min="1" max="300" value="10">
      </label>
      <label>
        Opgaver pr. boks
        <input id="antalOpgaver" type="number" min="1" max="12" value="5">
      </label>
      <label>
        Print
        <span class="checkline"><input id="dobbeltsidet" type="checkbox"> 8 bokse til dobbeltsidet</span>
      </label>
    </section>

    <section id="bokse" class="grid"></section>

    <section class="actions">
      <div id="resultat" class="result">Klar til at bygge en PDF.</div>
      <button id="bygKnap" type="button">Byg PDF</button>
    </section>
  </main>

  <script>
    const OPGAVER = __TASKS__;
    const NIVEAUER = ["let", "mellem", "svaer", "random"];
    const standard = [
      ["raekkefoelger", "let"],
      ["raekkefoelger", "mellem"],
      ["raekkefoelger", "svaer"],
      ["plus", "let"],
      ["minus", "let"],
      ["gange", "let"],
      ["klokke", "random"],
      ["rutespil", "let"]
    ];

    const bokseEl = document.querySelector("#bokse");
    const dobbeltsidetEl = document.querySelector("#dobbeltsidet");
    const resultatEl = document.querySelector("#resultat");
    const bygKnap = document.querySelector("#bygKnap");

    function option(label, value) {
      const el = document.createElement("option");
      el.value = value;
      el.textContent = label;
      return el;
    }

    function opgaveLabel(opgave) {
      const maks = opgave.maks_antal ? ` (maks ${opgave.maks_antal})` : "";
      return `${opgave.titel}${maks}`;
    }

    function renderBokse() {
      const antal = dobbeltsidetEl.checked ? 8 : 4;
      bokseEl.innerHTML = "";

      for (let i = 0; i < antal; i++) {
        const box = document.createElement("article");
        box.className = "box";

        const title = document.createElement("div");
        title.className = "box-title";
        title.textContent = `Boks ${i + 1}`;

        const fields = document.createElement("div");
        fields.className = "box-fields";

        const opgaveSelect = document.createElement("select");
        opgaveSelect.dataset.role = "navn";
        opgaveSelect.append(option("Tom boks", ""));
        for (const opgave of OPGAVER) {
          opgaveSelect.append(option(opgaveLabel(opgave), opgave.navn));
        }

        const niveauSelect = document.createElement("select");
        niveauSelect.dataset.role = "niveau";
        for (const niveau of NIVEAUER) {
          niveauSelect.append(option(niveau, niveau));
        }

        const valg = standard[i] || ["", "random"];
        opgaveSelect.value = OPGAVER.some(o => o.navn === valg[0]) ? valg[0] : "";
        niveauSelect.value = valg[1];

        const hint = document.createElement("div");
        hint.className = "hint";

        function updateHint() {
          const valgt = OPGAVER.find(o => o.navn === opgaveSelect.value);
          hint.textContent = valgt ? valgt.forklaring : "Boksen springes over.";
        }

        opgaveSelect.addEventListener("change", updateHint);
        updateHint();

        fields.append(opgaveSelect, niveauSelect);
        box.append(title, fields, hint);
        bokseEl.append(box);
      }
    }

    function hentPayload() {
      const bokse = [...bokseEl.querySelectorAll(".box")].map(box => ({
        navn: box.querySelector('[data-role="navn"]').value,
        niveau: box.querySelector('[data-role="niveau"]').value
      }));

      return {
        filnavn: document.querySelector("#filnavn").value,
        antal_sider: document.querySelector("#antalSider").value,
        antal_opgaver: document.querySelector("#antalOpgaver").value,
        dobbeltsidet: dobbeltsidetEl.checked,
        bokse
      };
    }

    async function bygPdf() {
      bygKnap.disabled = true;
      resultatEl.textContent = "Bygger PDF...";

      try {
        const response = await fetch("/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(hentPayload())
        });
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "PDF'en kunne ikke bygges.");
        }

        resultatEl.innerHTML = "";
        const tekst = document.createElement("span");
        tekst.textContent = `Færdig: ${data.filnavn}`;
        const link = document.createElement("a");
        link.href = data.url;
        link.target = "_blank";
        link.textContent = "Åbn PDF";
        resultatEl.append(tekst, link);
      } catch (error) {
        resultatEl.textContent = error.message;
      } finally {
        bygKnap.disabled = false;
      }
    }

    dobbeltsidetEl.addEventListener("change", renderBokse);
    bygKnap.addEventListener("click", bygPdf);
    renderBokse();
  </script>
</body>
</html>
"""


class OpgaveGuiHandler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            tasks_json = json.dumps(hent_opgave_metadata(), ensure_ascii=False)
            body = HTML_TEMPLATE.replace("__TASKS__", tasks_json).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path.startswith("/pdf/"):
            filnavn = unquote(self.path.removeprefix("/pdf/"))
            filsti = (PDF_MAPPE / filnavn).resolve()
            if PDF_MAPPE.resolve() not in filsti.parents or not filsti.exists():
                self.send_error(404, "PDF blev ikke fundet")
                return
            body = filsti.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f'inline; filename="{html.escape(filsti.name)}"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404, "Siden blev ikke fundet")

    def do_POST(self):
        if self.path != "/generate":
            self.send_error(404, "Siden blev ikke fundet")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            resultat = byg_pdf_fra_payload(payload)
        except Exception as fejl:
            self.send_json(400, {"error": str(fejl)})
            return

        self.send_json(200, resultat)

    def log_message(self, format, *args):
        return


def main():
    server = ThreadingHTTPServer((HOST, PORT), OpgaveGuiHandler)
    print(f"Opgave-GUI kører på http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
