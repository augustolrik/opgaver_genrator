from __future__ import annotations

import os
import re
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import unikke_opgaver_set_up as opgaver


APP_NAME = "Random Opgaver"
LEVELS = ["let", "mellem", "svaer", "random"]
DEFAULT_BOXES = [
    ("laes_og_forstaa", "let"),
    ("laes_og_forstaa", "mellem"),
    ("raekkefoelger", "let"),
    ("plus", "let"),
    ("visuel_gange", "let"),
    ("ligninger", "let"),
    ("talpyramide", "let"),
    ("rutespil", "let"),
]


TEXT = {
    "da": {
        "window_title": "Random Opgaver - PDF generator",
        "app_title": "Random Opgaver",
        "app_subtitle": "Byg matematikark som PDF med få klik.",
        "language": "Sprog",
        "settings": "Indstillinger",
        "file_name": "Filnavn",
        "output_folder": "Gem i mappe",
        "browse": "Vælg",
        "pages": "Antal sider",
        "tasks_per_box": "Opgaver pr. firkant",
        "double_sided": "8 firkanter til dobbeltsidet print",
        "boxes": "Firkantvalg",
        "box": "Firkant",
        "assignment": "Opgavetype",
        "level": "Niveau",
        "empty": "Tom firkant",
        "generate": "Byg PDF",
        "open_pdf": "Åbn PDF",
        "open_folder": "Åbn mappe",
        "clear": "Ryd valg",
        "reset": "Standardvalg",
        "ready": "Klar.",
        "building": "Bygger PDF...",
        "done": "PDF færdig:",
        "error": "Fejl",
        "choose_output": "Vælg mappe til PDF'er",
        "max_tasks": "maks",
        "none_hint": "Denne firkant springes over.",
        "created": "PDF'en er lavet.",
    },
    "en": {
        "window_title": "Random Assignments - PDF generator",
        "app_title": "Random Assignments",
        "app_subtitle": "Create math worksheet PDFs in a few clicks.",
        "language": "Language",
        "settings": "Settings",
        "file_name": "File name",
        "output_folder": "Output folder",
        "browse": "Browse",
        "pages": "Pages",
        "tasks_per_box": "Tasks per box",
        "double_sided": "8 boxes for double-sided print",
        "boxes": "Box setup",
        "box": "Box",
        "assignment": "Assignment type",
        "level": "Level",
        "empty": "Empty box",
        "generate": "Generate PDF",
        "open_pdf": "Open PDF",
        "open_folder": "Open folder",
        "clear": "Clear",
        "reset": "Defaults",
        "ready": "Ready.",
        "building": "Building PDF...",
        "done": "PDF ready:",
        "error": "Error",
        "choose_output": "Choose output folder",
        "max_tasks": "max",
        "none_hint": "This box is skipped.",
        "created": "The PDF has been created.",
    },
}


CATEGORY_DA = {
    "plus": "Regning",
    "minus": "Regning",
    "gange": "Regning",
    "division": "Regning",
    "procent": "Regning",
    "broeker": "Regning",
    "visuel_plus": "Visuelle opgaver",
    "visuel_minus": "Visuelle opgaver",
    "visuel_gange": "Visuelle opgaver",
    "visuel_division": "Visuelle opgaver",
    "visuel_division_2": "Visuelle opgaver",
    "visuel_procent": "Visuelle opgaver",
    "visuel_broek": "Visuelle opgaver",
    "visuel_areal": "Visuelle opgaver",
    "areal_firkant": "Geometri",
    "omkreds_firkant": "Geometri",
    "areal_trekant": "Geometri",
    "areal_cirkel": "Geometri",
    "omkreds_cirkel": "Geometri",
    "pytagoras": "Geometri",
    "vinkel_trekant": "Geometri",
    "vinkel_firkant": "Geometri",
    "ligninger": "Algebra og tal",
    "lav_tallet": "Algebra og tal",
    "find_primtal": "Algebra og tal",
    "talpyramide": "Mønstre og logik",
    "gangepyramide": "Mønstre og logik",
    "raekkefoelger": "Mønstre og logik",
    "rangering_regnestykker": "Mønstre og logik",
    "rutespil": "Mønstre og logik",
    "labyrint_spil": "Mønstre og logik",
    "klokke": "Tid",
    "cykeltid": "Tid",
    "laes_og_forstaa": "Matematiklæsning",
}


CATEGORY_EN = {
    "Regning": "Arithmetic",
    "Visuelle opgaver": "Visual tasks",
    "Geometri": "Geometry",
    "Algebra og tal": "Algebra and numbers",
    "Mønstre og logik": "Patterns and logic",
    "Tid": "Time",
    "Matematiklæsning": "Math reading",
}


LEVEL_LABELS = {
    "da": {"let": "Let", "mellem": "Mellem", "svaer": "Svær", "random": "Blandet"},
    "en": {"let": "Easy", "mellem": "Medium", "svaer": "Hard", "random": "Mixed"},
}


TASK_TEXT_EN = {
    "plus": ("Addition", "Calculate each addition problem and write the answer."),
    "visuel_plus": ("Visual addition", "Count the objects and write the answer."),
    "minus": ("Subtraction", "Calculate each subtraction problem and write the answer."),
    "visuel_minus": ("Visual subtraction", "Cross out objects and write how many are left."),
    "gange": ("Multiplication", "Calculate each multiplication problem and write the answer."),
    "visuel_gange": ("Visual multiplication", "Count rows and columns, then write the multiplication."),
    "division": ("Division", "Calculate each division problem and write the answer."),
    "visuel_division": ("Visual division", "Share the objects equally and write the answer."),
    "visuel_division_2": ("Cake sharing", "Share the cakes equally between the people eating."),
    "procent": ("Percent", "Calculate each percent problem and write the answer."),
    "broeker": ("Fractions", "Calculate the fraction problems and write the answer."),
    "visuel_procent": ("Visual percent", "Find what percent of the squares are colored."),
    "visuel_broek": ("Visual fraction", "Write the fraction for the colored part."),
    "visuel_areal": ("Visual area", "Find how many cakes can be made from the dough."),
    "areal_firkant": ("Area of rectangles", "Find the area in each problem."),
    "omkreds_firkant": ("Perimeter of rectangles", "Find the perimeter in each problem."),
    "areal_trekant": ("Area of triangles", "Find the area in each problem."),
    "areal_cirkel": ("Area of circles", "Find the area in each problem."),
    "omkreds_cirkel": ("Circumference of circles", "Find the circumference in each problem."),
    "pytagoras": ("Pythagoras", "Use a^2 + b^2 = c^2 to find the missing side."),
    "cykeltid": ("Cycling time", "Calculate how long the trip takes."),
    "ligninger": ("Equations", "Find x, or find x and y, in each problem."),
    "klokke": ("Clock", "Find the time between the two clock times."),
    "talpyramide": ("Number pyramids", "Add the two lower boxes together."),
    "gangepyramide": ("Multiplication pyramids", "Multiply the two lower boxes together."),
    "lav_tallet": ("Make the number", "Build the number by multiplying prime numbers."),
    "find_primtal": ("Find primes", "Find the prime numbers among the numbers."),
    "rangering_regnestykker": ("Order calculations", "Use estimation. Put the calculations from smallest to largest."),
    "rutespil": ("Route game", "Find three paths down to the correct numbers."),
    "vinkel_trekant": ("Triangle angles", "Find the hidden angle."),
    "vinkel_firkant": ("Quadrilateral angles", "Find the hidden angle."),
    "labyrint_spil": ("Maze game", "Go from START to FINISH through the maze."),
    "raekkefoelger": ("Sequences", "Find the pattern and write the missing term."),
    "laes_og_forstaa": ("Read and understand math", "Read the text. Find the information you need and solve the problem."),
}


def app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def clean_filename(filename: str) -> str:
    filename = filename.strip() or "opgaver.pdf"
    filename = re.sub(r"[^\w .()-]", "_", filename, flags=re.UNICODE)
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"
    return filename


def clamp_int(value: str, minimum: int, maximum: int, default: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


class StoreApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.option_add("*TCombobox*Listbox.background", "#ffffff")
        self.option_add("*TCombobox*Listbox.foreground", "#2f2b3d")
        self.option_add("*TCombobox*Listbox.selectBackground", "#e7dfef")
        self.option_add("*TCombobox*Listbox.selectForeground", "#2f2b3d")
        self.lang = tk.StringVar(value="da")
        self.last_pdf: Path | None = None
        self.box_rows: list[dict[str, object]] = []
        self.task_names = list(opgaver.BOKS_SKABELONER.keys())
        self.task_options: list[str] = []
        self.task_display_to_name: dict[str, str | None] = {}
        self.level_options: list[str] = []
        self.level_display_to_value: dict[str, str] = {}

        self.title(self.t("window_title"))
        self.geometry("1060x760")
        self.minsize(860, 620)
        self.configure(bg="#f5f3f8")
        self._configure_style()
        self._build_ui()
        self.refresh_language()
        self.load_defaults()

    def t(self, key: str) -> str:
        return TEXT[self.lang.get()][key]

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Root.TFrame", background="#f5f3f8")
        style.configure("Hero.TFrame", background="#5b5277")
        style.configure("Panel.TFrame", background="#fbfaff", relief="flat")
        style.configure("Box.TFrame", background="#f8f4fb", relief="solid", borderwidth=1)
        style.configure("TLabel", background="#fbfaff", foreground="#2f2b3d", font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background="#f8f4fb", foreground="#6c6680", font=("Segoe UI", 9))
        style.configure("HeroTitle.TLabel", background="#5b5277", foreground="#fbfaff", font=("Segoe UI Semibold", 22))
        style.configure("HeroSub.TLabel", background="#5b5277", foreground="#e8e1ef", font=("Segoe UI", 10))
        style.configure("Section.TLabel", background="#fbfaff", foreground="#3d3657", font=("Segoe UI Semibold", 13))
        style.configure("TButton", background="#e7dfef", foreground="#332d45", font=("Segoe UI", 10), padding=(10, 7))
        style.map("TButton", background=[("active", "#d9cee8")], foreground=[("active", "#332d45")])
        style.configure("Primary.TButton", background="#75689a", foreground="#fbfaff", font=("Segoe UI Semibold", 10), padding=(16, 9))
        style.map("Primary.TButton", background=[("active", "#665986")], foreground=[("active", "#fbfaff")])
        style.configure("TEntry", fieldbackground="#ffffff", foreground="#2f2b3d", padding=6)
        style.configure("TCombobox", background="#ffffff", fieldbackground="#ffffff", foreground="#2f2b3d", arrowcolor="#5b5277", padding=5)
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", "#ffffff"), ("active", "#ffffff"), ("focus", "#ffffff")],
            background=[("readonly", "#ffffff"), ("active", "#ffffff"), ("focus", "#ffffff")],
            foreground=[("readonly", "#2f2b3d"), ("active", "#2f2b3d"), ("focus", "#2f2b3d")],
        )
        style.configure("TCheckbutton", background="#fbfaff", foreground="#2f2b3d", font=("Segoe UI", 10))
        style.configure("TSpinbox", fieldbackground="#ffffff", foreground="#2f2b3d")

    def _build_ui(self) -> None:
        root = ttk.Frame(self, style="Root.TFrame", padding=18)
        root.pack(fill="both", expand=True)

        hero = ttk.Frame(root, style="Hero.TFrame", padding=18)
        hero.pack(fill="x")
        hero.columnconfigure(0, weight=1)
        self.title_label = ttk.Label(hero, style="HeroTitle.TLabel")
        self.title_label.grid(row=0, column=0, sticky="w")
        self.subtitle_label = ttk.Label(hero, style="HeroSub.TLabel")
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.lang_label = ttk.Label(hero, style="HeroSub.TLabel")
        self.lang_label.grid(row=0, column=1, sticky="e", padx=(12, 6))
        self.lang_combo = ttk.Combobox(hero, textvariable=self.lang, values=["da", "en"], width=6, state="readonly")
        self.lang_combo.grid(row=0, column=2, sticky="e")
        self.lang_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_language())

        settings = ttk.Frame(root, style="Panel.TFrame", padding=16)
        settings.pack(fill="x", pady=(14, 12))
        for column in range(6):
            settings.columnconfigure(column, weight=1)

        self.settings_label = ttk.Label(settings, style="Section.TLabel")
        self.settings_label.grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))

        self.file_label = ttk.Label(settings)
        self.file_label.grid(row=1, column=0, sticky="w")
        self.filename_var = tk.StringVar(value="opgaver.pdf")
        self.filename_entry = ttk.Entry(settings, textvariable=self.filename_var)
        self.filename_entry.grid(row=2, column=0, columnspan=2, sticky="ew", padx=(0, 10))

        self.folder_label = ttk.Label(settings)
        self.folder_label.grid(row=1, column=2, sticky="w")
        self.output_dir_var = tk.StringVar(value=str(app_base_dir() / "random_opgaver_pdf"))
        self.folder_entry = ttk.Entry(settings, textvariable=self.output_dir_var)
        self.folder_entry.grid(row=2, column=2, columnspan=2, sticky="ew", padx=(0, 10))
        self.browse_button = ttk.Button(settings, command=self.choose_output_dir)
        self.browse_button.grid(row=2, column=4, sticky="ew", padx=(0, 10))

        self.pages_label = ttk.Label(settings)
        self.pages_label.grid(row=3, column=0, sticky="w", pady=(12, 0))
        self.pages_var = tk.StringVar(value="10")
        ttk.Spinbox(settings, from_=1, to=300, textvariable=self.pages_var, width=8).grid(row=4, column=0, sticky="ew", padx=(0, 10))

        self.tasks_label = ttk.Label(settings)
        self.tasks_label.grid(row=3, column=1, sticky="w", pady=(12, 0))
        self.tasks_var = tk.StringVar(value=str(opgaver.ANTAL_OPGAVER_I_BOKS))
        ttk.Spinbox(settings, from_=1, to=12, textvariable=self.tasks_var, width=8).grid(row=4, column=1, sticky="ew", padx=(0, 10))

        self.double_sided_var = tk.BooleanVar(value=False)
        self.double_sided_check = ttk.Checkbutton(settings, variable=self.double_sided_var, command=self.render_boxes)
        self.double_sided_check.grid(row=4, column=2, columnspan=3, sticky="w")

        actions_top = ttk.Frame(settings, style="Panel.TFrame")
        actions_top.grid(row=4, column=5, sticky="e")
        self.reset_button = ttk.Button(actions_top, command=self.load_defaults)
        self.reset_button.pack(side="left", padx=(0, 6))
        self.clear_button = ttk.Button(actions_top, command=self.clear_boxes)
        self.clear_button.pack(side="left")

        box_panel = ttk.Frame(root, style="Panel.TFrame", padding=16)
        box_panel.pack(fill="both", expand=True)
        box_panel.columnconfigure(0, weight=1)
        self.boxes_label = ttk.Label(box_panel, style="Section.TLabel")
        self.boxes_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.box_grid = ttk.Frame(box_panel, style="Panel.TFrame")
        self.box_grid.grid(row=1, column=0, sticky="nsew")
        box_panel.rowconfigure(1, weight=1)

        footer = ttk.Frame(root, style="Root.TFrame")
        footer.pack(fill="x", pady=(12, 0))
        footer.columnconfigure(0, weight=1)
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(footer, textvariable=self.status_var, background="#f5f3f8", foreground="#3d3657")
        self.status_label.grid(row=0, column=0, sticky="w")
        self.open_folder_button = ttk.Button(footer, command=self.open_output_folder)
        self.open_folder_button.grid(row=0, column=1, padx=(8, 0))
        self.open_pdf_button = ttk.Button(footer, command=self.open_last_pdf)
        self.open_pdf_button.grid(row=0, column=2, padx=(8, 0))
        self.generate_button = ttk.Button(footer, style="Primary.TButton", command=self.generate_pdf)
        self.generate_button.grid(row=0, column=3, padx=(12, 0))

    def task_category(self, name: str) -> str:
        category_da = CATEGORY_DA.get(name, "Andre")
        if self.lang.get() == "en":
            return CATEGORY_EN.get(category_da, "Other")
        return category_da

    def task_display(self, name: str | None) -> str:
        if not name:
            return self.t("empty")
        title = self.task_title(name)
        template = opgaver.BOKS_SKABELONER[name]
        max_count = template.get("maks_antal")
        max_text = f" ({self.t('max_tasks')} {max_count})" if max_count else ""
        return f"{self.task_category(name)} - {title} [{name}]{max_text}"

    def task_title(self, name: str) -> str:
        if self.lang.get() == "en" and name in TASK_TEXT_EN:
            return TASK_TEXT_EN[name][0]
        return opgaver.BOKS_SKABELONER[name].get("titel", name)

    def task_hint(self, name: str) -> str:
        if self.lang.get() == "en" and name in TASK_TEXT_EN:
            return TASK_TEXT_EN[name][1]
        return opgaver.BOKS_SKABELONER[name].get("forklaring", "")

    def refresh_language(self) -> None:
        self.title(self.t("window_title"))
        self.title_label.configure(text=self.t("app_title"))
        self.subtitle_label.configure(text=self.t("app_subtitle"))
        self.lang_label.configure(text=self.t("language"))
        self.settings_label.configure(text=self.t("settings"))
        self.file_label.configure(text=self.t("file_name"))
        self.folder_label.configure(text=self.t("output_folder"))
        self.browse_button.configure(text=self.t("browse"))
        self.pages_label.configure(text=self.t("pages"))
        self.tasks_label.configure(text=self.t("tasks_per_box"))
        self.double_sided_check.configure(text=self.t("double_sided"))
        self.boxes_label.configure(text=self.t("boxes"))
        self.generate_button.configure(text=self.t("generate"))
        self.open_pdf_button.configure(text=self.t("open_pdf"))
        self.open_folder_button.configure(text=self.t("open_folder"))
        self.clear_button.configure(text=self.t("clear"))
        self.reset_button.configure(text=self.t("reset"))

        selected = self.current_box_values()
        self.task_options = [self.task_display(None)] + [self.task_display(name) for name in self.task_names]
        self.task_display_to_name = {self.task_display(None): None}
        self.task_display_to_name.update({self.task_display(name): name for name in self.task_names})
        self.level_options = [LEVEL_LABELS[self.lang.get()][level] for level in LEVELS]
        self.level_display_to_value = {
            LEVEL_LABELS[self.lang.get()][level]: level for level in LEVELS
        }
        self.render_boxes(selected)
        self.status_var.set(self.t("ready"))

    def current_box_values(self) -> list[tuple[str | None, str]]:
        values: list[tuple[str | None, str]] = []
        for row in self.box_rows:
            task_var = row["task_var"]
            level_var = row["level_var"]
            if isinstance(task_var, tk.StringVar) and isinstance(level_var, tk.StringVar):
                name = self.task_display_to_name.get(task_var.get())
                level = self.level_display_to_value.get(level_var.get(), "random")
                values.append((name, level))
        return values

    def render_boxes(self, values: list[tuple[str | None, str]] | None = None) -> None:
        if values is None:
            values = self.current_box_values()

        for child in self.box_grid.winfo_children():
            child.destroy()
        self.box_rows = []

        count = 8 if self.double_sided_var.get() else 4
        for index in range(count):
            name, level = values[index] if index < len(values) else (None, "random")
            frame = ttk.Frame(self.box_grid, style="Box.TFrame", padding=10)
            frame.grid(row=index // 2, column=index % 2, sticky="nsew", padx=6, pady=6)
            self.box_grid.columnconfigure(index % 2, weight=1)

            title = ttk.Label(frame, text=f"{self.t('box')} {index + 1}", style="Section.TLabel")
            title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
            ttk.Label(frame, text=self.t("assignment")).grid(row=1, column=0, sticky="w")
            ttk.Label(frame, text=self.t("level")).grid(row=1, column=1, sticky="w")

            task_var = tk.StringVar(value=self.task_display(name))
            level_var = tk.StringVar(value=LEVEL_LABELS[self.lang.get()].get(level, LEVEL_LABELS[self.lang.get()]["random"]))
            task_combo = ttk.Combobox(frame, textvariable=task_var, values=self.task_options, state="readonly", width=48)
            level_combo = ttk.Combobox(frame, textvariable=level_var, values=self.level_options, state="readonly", width=13)
            task_combo.grid(row=2, column=0, sticky="ew", padx=(0, 8))
            level_combo.grid(row=2, column=1, sticky="ew")
            frame.columnconfigure(0, weight=1)

            hint_var = tk.StringVar()
            hint = ttk.Label(frame, textvariable=hint_var, style="Muted.TLabel", wraplength=430)
            hint.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))
            row = {"task_var": task_var, "level_var": level_var, "hint_var": hint_var}
            self.box_rows.append(row)

            task_combo.bind("<<ComboboxSelected>>", lambda _event, item=row: self.update_hint(item))
            self.update_hint(row)

    def update_hint(self, row: dict[str, object]) -> None:
        task_var = row["task_var"]
        hint_var = row["hint_var"]
        if not isinstance(task_var, tk.StringVar) or not isinstance(hint_var, tk.StringVar):
            return
        name = self.task_display_to_name.get(task_var.get())
        if not name:
            hint_var.set(self.t("none_hint"))
            return
        template = opgaver.BOKS_SKABELONER[name]
        hint = self.task_hint(name)
        if template.get("maks_antal"):
            hint += f" ({self.t('max_tasks')} {template['maks_antal']})"
        hint_var.set(hint)

    def load_defaults(self) -> None:
        self.double_sided_var.set(False)
        values = [(name, level) for name, level in DEFAULT_BOXES[:4]]
        self.render_boxes(values)

    def clear_boxes(self) -> None:
        self.render_boxes([(None, "random") for _ in range(8 if self.double_sided_var.get() else 4)])

    def choose_output_dir(self) -> None:
        selected = filedialog.askdirectory(title=self.t("choose_output"), initialdir=self.output_dir_var.get())
        if selected:
            self.output_dir_var.set(selected)

    def build_box_choices(self) -> list[tuple[str, str] | None]:
        choices: list[tuple[str, str] | None] = []
        for row in self.box_rows:
            task_var = row["task_var"]
            level_var = row["level_var"]
            if not isinstance(task_var, tk.StringVar) or not isinstance(level_var, tk.StringVar):
                choices.append(None)
                continue
            name = self.task_display_to_name.get(task_var.get())
            if not name:
                choices.append(None)
                continue
            level = self.level_display_to_value.get(level_var.get(), "random")
            choices.append((name, level))
        return choices

    def generate_pdf(self) -> None:
        try:
            self.status_var.set(self.t("building"))
            self.update_idletasks()
            output_dir = Path(self.output_dir_var.get()).expanduser()
            output_dir.mkdir(parents=True, exist_ok=True)
            filename = clean_filename(self.filename_var.get())
            pages = clamp_int(self.pages_var.get(), 1, 300, opgaver.ANTAL_SIDER)
            tasks = clamp_int(self.tasks_var.get(), 1, 12, opgaver.ANTAL_OPGAVER_I_BOKS)
            choices = self.build_box_choices()
            setup = opgaver.byg_boks_opsaetning(choices, opgaver.BOKS_SKABELONER)
            output_path = output_dir / filename
            opgaver.byg_pdf(str(output_path), pages, setup, tasks)
            self.last_pdf = output_path
            self.status_var.set(f"{self.t('done')} {output_path}")
            messagebox.showinfo(APP_NAME, f"{self.t('created')}\n\n{output_path}")
        except Exception as error:
            self.status_var.set(str(error))
            messagebox.showerror(self.t("error"), str(error))

    def open_output_folder(self) -> None:
        path = Path(self.output_dir_var.get()).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        os.startfile(path)

    def open_last_pdf(self) -> None:
        if self.last_pdf and self.last_pdf.exists():
            os.startfile(self.last_pdf)
            return
        self.open_output_folder()


def main() -> None:
    app = StoreApp()
    app.mainloop()


if __name__ == "__main__":
    main()
