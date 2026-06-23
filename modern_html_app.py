from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote
import json
import os
import re
import socket
import threading
import webbrowser

import unikke_opgaver_set_up as opgaver
from store_app import CATEGORY_DA, CATEGORY_EN, LEVEL_LABELS, TASK_TEXT_EN


HOST = "127.0.0.1"
START_PORT = 8765
APP_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = APP_DIR / "random_opgaver_pdf"
LEVELS = ["let", "mellem", "svaer", "random"]
GENERATED_FILES: dict[str, Path] = {}


TEXT = {
    "da": {
        "appTitle": "Random Opgaver",
        "subtitle": "PDF-generator til matematikark.",
        "language": "Sprog",
        "setup": "Opsætning",
        "filename": "Filnavn",
        "output": "Outputmappe",
        "pages": "Sider",
        "tasks": "Opgaver pr. firkant",
        "doubleSided": "8 firkanter til dobbeltsidet print",
        "boxes": "Firkantvalg",
        "assignment": "Opgavetype",
        "level": "Niveau",
        "empty": "Tom firkant",
        "generate": "Byg PDF",
        "filter": "Sortering",
        "allCategories": "Alle kategorier",
        "testPdf": "Test-PDF",
        "testPdfText": "Lav en PDF med alle opgavetyper, så du hurtigt kan se layout og niveau.",
        "testLevel": "Testniveau",
        "generateTest": "Lav test-PDF",
        "testFilename": "test_alle_opgaver.pdf",
        "clear": "Ryd",
        "ready": "Klar til at bygge.",
        "building": "Bygger PDF...",
        "done": "PDF færdig",
        "openPdf": "Åbn PDF",
        "openFolder": "Åbn mappe",
        "max": "maks",
        "skipped": "Denne firkant springes over.",
        "tip": "Nye opgavetyper vises automatisk, når de er registreret i Python-generatoren.",
    },
    "en": {
        "appTitle": "Random Assignments",
        "subtitle": "PDF generator for math worksheets.",
        "language": "Language",
        "setup": "Setup",
        "filename": "File name",
        "output": "Output folder",
        "pages": "Pages",
        "tasks": "Tasks per box",
        "doubleSided": "8 boxes for double-sided print",
        "boxes": "Box setup",
        "assignment": "Assignment type",
        "level": "Level",
        "empty": "Empty box",
        "generate": "Generate PDF",
        "filter": "Filter",
        "allCategories": "All categories",
        "testPdf": "Test PDF",
        "testPdfText": "Create a PDF with every assignment type so you can review layout and difficulty.",
        "testLevel": "Test difficulty",
        "generateTest": "Generate test PDF",
        "testFilename": "test_all_assignments.pdf",
        "clear": "Clear",
        "ready": "Ready to build.",
        "building": "Building PDF...",
        "done": "PDF ready",
        "openPdf": "Open PDF",
        "openFolder": "Open folder",
        "max": "max",
        "skipped": "This box is skipped.",
        "tip": "New assignment types appear automatically when registered in the Python generator.",
    },
}


def app_base_dir() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", APP_DIR)) / "RandomOpgaver"


def clean_filename(filename: str) -> str:
    filename = (filename or "opgaver.pdf").strip()
    filename = re.sub(r"[^\w .()-]", "_", filename, flags=re.UNICODE)
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"
    return filename


def clamp_int(value, minimum: int, maximum: int, default: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


def task_category(name: str, lang: str) -> str:
    category_da = CATEGORY_DA.get(name, "Andre")
    if lang == "en":
        return CATEGORY_EN.get(category_da, "Other")
    return category_da


def task_title(name: str, lang: str) -> str:
    if lang == "en" and name in TASK_TEXT_EN:
        return TASK_TEXT_EN[name][0]
    return opgaver.BOKS_SKABELONER[name].get("titel", name)


def task_hint(name: str, lang: str) -> str:
    if lang == "en" and name in TASK_TEXT_EN:
        return TASK_TEXT_EN[name][1]
    return opgaver.BOKS_SKABELONER[name].get("forklaring", "")


def task_metadata() -> list[dict[str, object]]:
    items = []
    for name, template in opgaver.BOKS_SKABELONER.items():
        items.append(
            {
                "name": name,
                "max": template.get("maks_antal"),
                "da": {
                    "title": task_title(name, "da"),
                    "hint": task_hint(name, "da"),
                    "category": task_category(name, "da"),
                },
                "en": {
                    "title": task_title(name, "en"),
                    "hint": task_hint(name, "en"),
                    "category": task_category(name, "en"),
                },
            }
        )
    return items


def build_pdf(payload: dict) -> dict[str, str]:
    lang = payload.get("lang", "da")
    box_count = 8 if payload.get("doubleSided") else 4
    pages = clamp_int(payload.get("pages"), 1, 300, 10)
    tasks = clamp_int(payload.get("tasks"), 1, 12, opgaver.ANTAL_OPGAVER_I_BOKS)
    filename = clean_filename(payload.get("filename", "opgaver.pdf"))
    out_dir = Path(payload.get("outputDir") or DEFAULT_OUTPUT_DIR).expanduser()
    boxes = payload.get("boxes", [])

    choices = []
    for index in range(box_count):
        box = boxes[index] if index < len(boxes) else {}
        name = box.get("name")
        level = box.get("level", "random")
        if not name:
            choices.append(None)
            continue
        if name not in opgaver.BOKS_SKABELONER:
            raise ValueError(f"Unknown assignment type: {name}" if lang == "en" else f"Ukendt opgavetype: {name}")
        if level not in LEVELS:
            level = "random"
        choices.append((name, level))

    out_dir.mkdir(parents=True, exist_ok=True)
    setup = opgaver.byg_boks_opsaetning(choices, opgaver.BOKS_SKABELONER)
    output_path = out_dir / filename
    opgaver.byg_pdf(str(output_path), pages, setup, tasks)

    file_id = quote(str(output_path.resolve()), safe="")
    GENERATED_FILES[file_id] = output_path.resolve()
    return {"filename": filename, "path": str(output_path), "fileId": file_id}


def build_pdf_from_page_boxes(output_path: Path, page_boxes: list[list[dict]], tasks: int) -> None:
    doc = opgaver.SimpleDocTemplate(
        str(output_path),
        pagesize=opgaver.A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=opgaver.HEADER_HOEJDE + 20,
        bottomMargin=36,
    )
    elements = []
    sideikon = opgaver.vaelg_sideikon()
    draw_header = opgaver.lav_tegnefunktion(sideikon)

    for index, boxes in enumerate(page_boxes):
        elements.append(opgaver.lav_side(boxes, tasks, doc.width, doc.height))
        if index < len(page_boxes) - 1:
            elements.append(opgaver.PageBreak())

    doc.build(elements, onFirstPage=draw_header, onLaterPages=draw_header)


def build_all_assignments_pdf(payload: dict) -> dict[str, str]:
    lang = payload.get("lang", "da")
    level = payload.get("level", "random")
    if level not in LEVELS:
        level = "random"

    filename = clean_filename(payload.get("filename") or TEXT[lang].get("testFilename", "test_all_assignments.pdf"))
    out_dir = Path(payload.get("outputDir") or DEFAULT_OUTPUT_DIR).expanduser()
    tasks = clamp_int(payload.get("tasks"), 1, 12, opgaver.ANTAL_OPGAVER_I_BOKS)

    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / filename

    names = list(opgaver.BOKS_SKABELONER.keys())
    page_boxes: list[list[dict]] = []
    for start in range(0, len(names), 4):
        choices = [(name, level) for name in names[start:start + 4]]
        while len(choices) < 4:
            choices.append(None)
        page_boxes.append(opgaver.byg_boks_opsaetning(choices, opgaver.BOKS_SKABELONER))

    build_pdf_from_page_boxes(output_path, page_boxes, tasks)

    file_id = quote(str(output_path.resolve()), safe="")
    GENERATED_FILES[file_id] = output_path.resolve()
    return {"filename": filename, "path": str(output_path), "fileId": file_id}


HTML = r"""<!doctype html>
<html lang="da">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Random Opgaver</title>
  <style>
    :root {
      --bg: #f5f3f8;
      --panel: rgba(255, 255, 255, 0.78);
      --panel-solid: #fbfaff;
      --ink: #2f2b3d;
      --muted: #6c6680;
      --line: #ddd5e8;
      --accent: #74639d;
      --accent-2: #8d7db4;
      --soft: #f1eaf6;
      --rose: #f7edf4;
      --white: #ffffff;
      --shadow: 0 18px 50px rgba(73, 61, 105, 0.14);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Aptos", "Segoe UI", Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 14% 8%, #efe6f6 0, transparent 28rem),
        radial-gradient(circle at 92% 18%, #e5e9f6 0, transparent 24rem),
        linear-gradient(135deg, #f7f5fa 0%, #eeebf5 52%, #f8f2f7 100%);
    }

    button, input, select { font: inherit; }

    .shell {
      width: min(1220px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 34px;
    }

    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      align-items: center;
      padding: 28px;
      border: 1px solid rgba(255,255,255,0.72);
      border-radius: 28px;
      background: linear-gradient(135deg, rgba(91,82,119,0.96), rgba(122,111,158,0.92));
      box-shadow: var(--shadow);
      color: white;
      overflow: hidden;
      position: relative;
    }

    .hero::after {
      content: "";
      position: absolute;
      width: 280px;
      height: 280px;
      right: -92px;
      top: -118px;
      border-radius: 999px;
      background: rgba(255,255,255,0.12);
    }

    h1 {
      margin: 0;
      font-size: clamp(32px, 5vw, 52px);
      line-height: 0.95;
      letter-spacing: -0.03em;
    }

    .subtitle {
      margin-top: 12px;
      max-width: 620px;
      color: #ebe5f2;
      font-size: 16px;
    }

    .language {
      position: relative;
      z-index: 1;
      display: grid;
      gap: 8px;
      min-width: 160px;
    }

    .language label {
      color: #f5effb;
      font-size: 13px;
      font-weight: 700;
    }

    .panel {
      margin-top: 16px;
      padding: 20px;
      border: 1px solid rgba(221,213,232,0.9);
      border-radius: 24px;
      background: var(--panel);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
    }

    .section-title {
      margin: 0 0 14px;
      font-size: 18px;
      letter-spacing: -0.01em;
    }

    .settings {
      display: grid;
      grid-template-columns: 1.2fr 1.6fr 0.55fr 0.65fr;
      gap: 14px;
      align-items: end;
    }

    .field {
      display: grid;
      gap: 7px;
    }

    label {
      color: var(--muted);
      font-size: 13px;
      font-weight: 750;
    }

    input, select {
      width: 100%;
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: var(--white);
      color: var(--ink);
      padding: 9px 12px;
      outline: none;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.8);
    }

    select { cursor: pointer; }

    input:focus, select:focus {
      border-color: var(--accent-2);
      box-shadow: 0 0 0 4px rgba(141,125,180,0.14);
    }

    .toggle {
      display: flex;
      gap: 10px;
      align-items: center;
      min-height: 42px;
      padding: 0 2px;
      color: var(--ink);
      font-weight: 700;
    }

    .toggle input {
      width: 20px;
      min-height: 20px;
      accent-color: var(--accent);
    }

    .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
    }

    .toolbar-stack {
      display: grid;
      gap: 12px;
      margin-bottom: 14px;
    }

    .filter-row,
    .test-row {
      display: grid;
      grid-template-columns: minmax(220px, 320px) minmax(0, 1fr);
      gap: 12px;
      align-items: end;
    }

    .test-row {
      grid-template-columns: minmax(220px, 320px) auto minmax(0, 1fr);
      padding-top: 12px;
      border-top: 1px solid var(--line);
    }

    .tip {
      max-width: 620px;
      color: var(--muted);
      font-size: 13px;
    }

    .buttons {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    button {
      min-height: 42px;
      border: 0;
      border-radius: 14px;
      padding: 10px 16px;
      color: var(--ink);
      background: #e7dfef;
      cursor: pointer;
      font-weight: 800;
      transition: transform 140ms ease, background 140ms ease, box-shadow 140ms ease;
    }

    button:hover {
      transform: translateY(-1px);
      background: #d9cee8;
    }

    button.primary {
      color: #ffffff;
      background: linear-gradient(135deg, #74639d, #5b5277);
      box-shadow: 0 12px 24px rgba(91,82,119,0.24);
    }

    button:disabled {
      opacity: 0.68;
      cursor: wait;
      transform: none;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(280px, 1fr));
      gap: 14px;
    }

    .box-card {
      display: grid;
      gap: 12px;
      padding: 15px;
      border: 1px solid var(--line);
      border-radius: 22px;
      background: linear-gradient(180deg, var(--panel-solid), var(--rose));
    }

    .box-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    .box-title {
      font-weight: 900;
      letter-spacing: -0.01em;
    }

    .pill {
      padding: 4px 9px;
      border-radius: 999px;
      color: #51486d;
      background: #eee7f6;
      font-size: 12px;
      font-weight: 850;
    }

    .box-fields {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 140px;
      gap: 10px;
    }

    .hint {
      min-height: 34px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.35;
    }

    .status {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-top: 16px;
      padding: 14px 16px;
      border-radius: 18px;
      background: rgba(255,255,255,0.62);
      color: var(--muted);
    }

    .status strong { color: var(--ink); }

    .links {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .links a {
      color: var(--accent);
      font-weight: 900;
      text-decoration: none;
    }

    @media (max-width: 900px) {
      .hero, .settings, .grid, .filter-row, .test-row { grid-template-columns: 1fr; }
      .box-fields { grid-template-columns: 1fr; }
      .status { align-items: flex-start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div>
        <h1 id="appTitle"></h1>
        <div class="subtitle" id="subtitle"></div>
      </div>
      <div class="language">
        <label id="languageLabel" for="language"></label>
        <select id="language">
          <option value="da">Dansk</option>
          <option value="en">English</option>
        </select>
      </div>
    </section>

    <section class="panel">
      <h2 class="section-title" id="setupTitle"></h2>
      <div class="settings">
        <div class="field">
          <label id="filenameLabel" for="filename"></label>
          <input id="filename" value="opgaver.pdf">
        </div>
        <div class="field">
          <label id="outputLabel" for="outputDir"></label>
          <input id="outputDir">
        </div>
        <div class="field">
          <label id="pagesLabel" for="pages"></label>
          <input id="pages" type="number" min="1" max="300" value="10">
        </div>
        <div class="field">
          <label id="tasksLabel" for="tasks"></label>
          <input id="tasks" type="number" min="1" max="12" value="5">
        </div>
      </div>
      <label class="toggle">
        <input id="doubleSided" type="checkbox">
        <span id="doubleSidedLabel"></span>
      </label>
    </section>

    <section class="panel">
      <div class="toolbar-stack">
        <div class="toolbar">
          <div>
            <h2 class="section-title" id="boxesTitle"></h2>
            <div class="tip" id="tip"></div>
          </div>
          <div class="buttons">
            <button id="clearBtn" type="button"></button>
            <button id="generateBtn" class="primary" type="button"></button>
          </div>
        </div>
        <div class="filter-row">
          <div class="field">
            <label id="filterLabel" for="categoryFilter"></label>
            <select id="categoryFilter"></select>
          </div>
        </div>
        <div class="test-row">
          <div class="field">
            <label id="testLevelLabel" for="testLevel"></label>
            <select id="testLevel"></select>
          </div>
          <button id="testPdfBtn" type="button"></button>
          <div class="tip" id="testPdfText"></div>
        </div>
      </div>
      <div id="boxes" class="grid"></div>
      <div class="status">
        <div id="statusText"></div>
        <div id="resultLinks" class="links"></div>
      </div>
    </section>
  </main>

  <script>
    const TASKS = __TASKS__;
    const TEXT = __TEXT__;
    const DEFAULT_OUTPUT = __DEFAULT_OUTPUT__;
    const LEVELS = ["let", "mellem", "svaer", "random"];
    const LEVEL_LABELS = {
      da: { let: "Let", mellem: "Mellem", svaer: "Svær", random: "Blandet" },
      en: { let: "Easy", mellem: "Medium", svaer: "Hard", random: "Mixed" }
    };

    const state = { lang: "da", boxes: [], category: "" };
    const el = id => document.getElementById(id);

    function t(key) { return TEXT[state.lang][key]; }
    function taskByName(name) { return TASKS.find(task => task.name === name); }
    function categories() {
      return [...new Set(TASKS.map(task => task[state.lang].category))].sort((a, b) => a.localeCompare(b));
    }
    function visibleTasks() {
      if (!state.category) return TASKS;
      return TASKS.filter(task => task[state.lang].category === state.category);
    }
    function taskLabel(task) {
      const info = task[state.lang];
      const max = task.max ? ` (${t("max")} ${task.max})` : "";
      return `${info.category} · ${info.title} [${task.name}]${max}`;
    }

    function setText() {
      document.documentElement.lang = state.lang;
      el("appTitle").textContent = t("appTitle");
      el("subtitle").textContent = t("subtitle");
      el("languageLabel").textContent = t("language");
      el("setupTitle").textContent = t("setup");
      el("filenameLabel").textContent = t("filename");
      el("outputLabel").textContent = t("output");
      el("pagesLabel").textContent = t("pages");
      el("tasksLabel").textContent = t("tasks");
      el("doubleSidedLabel").textContent = t("doubleSided");
      el("boxesTitle").textContent = t("boxes");
      el("tip").textContent = t("tip");
      el("filterLabel").textContent = t("filter");
      el("testLevelLabel").textContent = t("testLevel");
      el("testPdfBtn").textContent = t("generateTest");
      el("testPdfText").textContent = t("testPdfText");
      el("clearBtn").textContent = t("clear");
      el("generateBtn").textContent = t("generate");
      renderCategoryFilter();
      renderTestLevel();
      if (!el("statusText").dataset.locked) el("statusText").textContent = t("ready");
    }

    function renderCategoryFilter() {
      const select = el("categoryFilter");
      const allCategories = categories();
      const current = state.category;
      state.category = allCategories.includes(current) ? current : "";
      select.innerHTML = `<option value="">${t("allCategories")}</option>` + allCategories.map(category => `<option value="${category}">${category}</option>`).join("");
      select.value = state.category;
    }

    function renderTestLevel() {
      const select = el("testLevel");
      const current = select.value || "random";
      select.innerHTML = LEVELS.map(level => `<option value="${level}">${LEVEL_LABELS[state.lang][level]}</option>`).join("");
      select.value = LEVELS.includes(current) ? current : "random";
    }

    function ensureBoxCount() {
      const count = el("doubleSided").checked ? 8 : 4;
      while (state.boxes.length < count) state.boxes.push({ name: "", level: "random" });
      state.boxes = state.boxes.slice(0, count);
    }

    function renderBoxes() {
      ensureBoxCount();
      const root = el("boxes");
      root.innerHTML = "";

      state.boxes.forEach((box, index) => {
        const card = document.createElement("article");
        card.className = "box-card";

        const head = document.createElement("div");
        head.className = "box-head";
        head.innerHTML = `<div class="box-title">${t("boxes").replace(" setup", "")} ${index + 1}</div><div class="pill">${index + 1}</div>`;

        const fields = document.createElement("div");
        fields.className = "box-fields";

        const taskField = document.createElement("div");
        taskField.className = "field";
        const taskLabelEl = document.createElement("label");
        taskLabelEl.textContent = t("assignment");
        const taskSelect = document.createElement("select");
        const selectedTask = box.name ? taskByName(box.name) : null;
        const selectedMissing = selectedTask && state.category && selectedTask[state.lang].category !== state.category;
        taskSelect.innerHTML =
          `<option value="">${t("empty")}</option>` +
          (selectedMissing ? `<option value="${selectedTask.name}">${taskLabel(selectedTask)}</option>` : "") +
          visibleTasks().map(task => `<option value="${task.name}">${taskLabel(task)}</option>`).join("");
        taskSelect.value = box.name;
        taskSelect.addEventListener("change", () => {
          box.name = taskSelect.value;
          updateHint(card, box);
        });
        taskField.append(taskLabelEl, taskSelect);

        const levelField = document.createElement("div");
        levelField.className = "field";
        const levelLabelEl = document.createElement("label");
        levelLabelEl.textContent = t("level");
        const levelSelect = document.createElement("select");
        levelSelect.innerHTML = LEVELS.map(level => `<option value="${level}">${LEVEL_LABELS[state.lang][level]}</option>`).join("");
        levelSelect.value = box.level || "random";
        levelSelect.addEventListener("change", () => { box.level = levelSelect.value; });
        levelField.append(levelLabelEl, levelSelect);

        const hint = document.createElement("div");
        hint.className = "hint";
        fields.append(taskField, levelField);
        card.append(head, fields, hint);
        root.append(card);
        updateHint(card, box);
      });
    }

    function updateHint(card, box) {
      const hint = card.querySelector(".hint");
      const task = taskByName(box.name);
      if (!task) {
        hint.textContent = t("skipped");
        return;
      }
      hint.textContent = task[state.lang].hint + (task.max ? ` (${t("max")} ${task.max})` : "");
    }

    function clearBoxes() {
      state.boxes = Array.from({ length: el("doubleSided").checked ? 8 : 4 }, () => ({ name: "", level: "random" }));
      renderBoxes();
    }

    function payload() {
      ensureBoxCount();
      return {
        lang: state.lang,
        filename: el("filename").value,
        outputDir: el("outputDir").value,
        pages: el("pages").value,
        tasks: el("tasks").value,
        doubleSided: el("doubleSided").checked,
        boxes: state.boxes
      };
    }

    async function generatePdf() {
      const button = el("generateBtn");
      const status = el("statusText");
      const links = el("resultLinks");
      button.disabled = true;
      status.dataset.locked = "1";
      status.textContent = t("building");
      links.innerHTML = "";

      try {
        const response = await fetch("/api/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload())
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Error");
        status.innerHTML = `<strong>${t("done")}:</strong> ${data.path}`;
        links.innerHTML = `<a href="/pdf/${data.fileId}" target="_blank">${t("openPdf")}</a><a href="/api/open-folder/${data.fileId}">${t("openFolder")}</a>`;
      } catch (error) {
        status.textContent = error.message;
      } finally {
        button.disabled = false;
      }
    }

    async function generateTestPdf() {
      const button = el("testPdfBtn");
      const status = el("statusText");
      const links = el("resultLinks");
      button.disabled = true;
      status.dataset.locked = "1";
      status.textContent = t("building");
      links.innerHTML = "";

      try {
        const response = await fetch("/api/generate-test", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            lang: state.lang,
            filename: t("testFilename"),
            outputDir: el("outputDir").value,
            tasks: el("tasks").value,
            level: el("testLevel").value
          })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Error");
        status.innerHTML = `<strong>${t("done")}:</strong> ${data.path}`;
        links.innerHTML = `<a href="/pdf/${data.fileId}" target="_blank">${t("openPdf")}</a><a href="/api/open-folder/${data.fileId}">${t("openFolder")}</a>`;
      } catch (error) {
        status.textContent = error.message;
      } finally {
        button.disabled = false;
      }
    }

    el("language").addEventListener("change", event => {
      state.lang = event.target.value;
      state.category = "";
      setText();
      renderBoxes();
    });
    el("categoryFilter").addEventListener("change", event => {
      state.category = event.target.value;
      renderBoxes();
    });
    el("doubleSided").addEventListener("change", () => renderBoxes());
    el("clearBtn").addEventListener("click", clearBoxes);
    el("generateBtn").addEventListener("click", generatePdf);
    el("testPdfBtn").addEventListener("click", generateTestPdf);

    el("outputDir").value = DEFAULT_OUTPUT;
    setText();
    clearBoxes();
  </script>
</body>
</html>
"""


class ModernHandler(BaseHTTPRequestHandler):
    def send_json(self, status: int, data: dict) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            body = (
                HTML.replace("__TASKS__", json.dumps(task_metadata(), ensure_ascii=False))
                .replace("__TEXT__", json.dumps(TEXT, ensure_ascii=False))
                .replace("__DEFAULT_OUTPUT__", json.dumps(str(DEFAULT_OUTPUT_DIR), ensure_ascii=False))
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path.startswith("/pdf/"):
            file_id = self.path.removeprefix("/pdf/")
            path = GENERATED_FILES.get(file_id)
            if not path or not path.exists():
                self.send_error(404, "PDF not found")
                return
            body = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f'inline; filename="{path.name}"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path.startswith("/api/open-folder/"):
            file_id = self.path.removeprefix("/api/open-folder/")
            path = GENERATED_FILES.get(file_id)
            if path:
                os.startfile(path.parent)
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if self.path == "/api/generate":
                result = build_pdf(payload)
            elif self.path == "/api/generate-test":
                result = build_all_assignments_pdf(payload)
            else:
                self.send_error(404, "Not found")
                return
            self.send_json(200, result)
        except Exception as error:
            self.send_json(400, {"error": str(error)})

    def log_message(self, _format: str, *_args) -> None:
        return


def find_free_port(start_port: int = START_PORT) -> int:
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((HOST, port))
            except OSError:
                continue
            return port
    raise RuntimeError("No free local port found")


def main() -> None:
    port = find_free_port()
    server = ThreadingHTTPServer((HOST, port), ModernHandler)
    url = f"http://{HOST}:{port}"
    print(f"Modern HTML GUI running at {url}")
    threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
