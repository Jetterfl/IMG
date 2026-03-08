import tkinter as tk
from tkinter import ttk

SECTIONS = [
    {
        "title": "Профили",
        "description": "Готовые режимы работы и отдыха.",
        "items": [
            ("Рабочий режим", "Отключает отвлекающие уведомления и мессенджеры."),
            ("Учебный режим", "Ограничивает фоновые приложения и сайты."),
            ("Игровой режим", "Переводит систему в производительный профиль."),
        ],
    },
    {
        "title": "Система",
        "description": "Быстрые системные параметры в одном окне.",
        "items": [
            ("Энергосбережение", "Снижает потребление батареи и фоновые задачи."),
            ("Автоочистка", "Удаляет временные файлы каждый день."),
            ("Автозагрузка", "Управление запуском приложений при старте Windows."),
        ],
    },
    {
        "title": "Приватность",
        "description": "Управление доступом и безопасностью.",
        "items": [
            ("Камера", "Разрешение приложениям использовать камеру."),
            ("Микрофон", "Глобальный доступ к микрофону."),
            ("Telemetry", "Сбор диагностических данных Windows."),
        ],
    },
    {
        "title": "Внешний вид",
        "description": "Настройка темы и читаемости интерфейса.",
        "items": [
            ("Тёмная тема", "Автоматическое переключение по времени суток."),
            ("Крупный шрифт", "Увеличивает размер текста в приложениях."),
            ("Анимации", "Управление эффектами интерфейса."),
        ],
    },
]


class ControlCenterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Control Center Prototype")
        self.root.geometry("1080x680")
        self.root.minsize(920, 560)

        self.current_section_index = 0
        self.menu_buttons: list[ttk.Button] = []
        self.card_container: ttk.Frame | None = None

        self._configure_styles()
        self._build_layout()
        self.render_section(0)

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")

        bg_main = "#0b1020"
        panel = "#141a31"
        panel_alt = "#1c2442"
        text = "#e7eaff"
        muted = "#a9b3d6"

        self.root.configure(bg=bg_main)

        style.configure("Root.TFrame", background=bg_main)
        style.configure("Panel.TFrame", background=panel)
        style.configure("Card.TFrame", background=panel_alt)
        style.configure("Title.TLabel", background=bg_main, foreground=text, font=("Segoe UI", 20, "bold"))
        style.configure("Subtitle.TLabel", background=bg_main, foreground=muted, font=("Segoe UI", 11))
        style.configure("SidebarTitle.TLabel", background=panel, foreground=text, font=("Segoe UI", 16, "bold"))
        style.configure("SidebarSub.TLabel", background=panel, foreground=muted, font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background=panel_alt, foreground=text, font=("Segoe UI", 11, "bold"))
        style.configure("CardDesc.TLabel", background=panel_alt, foreground=muted, font=("Segoe UI", 9), wraplength=250)

        style.configure(
            "Menu.TButton",
            background=panel,
            foreground=text,
            padding=(10, 8),
            borderwidth=1,
            relief="flat",
        )
        style.map(
            "Menu.TButton",
            background=[("active", panel_alt)],
            bordercolor=[("active", "#2f3964")],
        )
        style.configure(
            "MenuActive.TButton",
            background=panel_alt,
            foreground=text,
            padding=(10, 8),
            borderwidth=1,
            relief="flat",
        )

        style.configure(
            "Primary.TButton",
            background="#6c8cff",
            foreground="#ffffff",
            padding=(12, 8),
            borderwidth=0,
            relief="flat",
        )
        style.map("Primary.TButton", background=[("active", "#86a2ff")])

        style.configure("Custom.Horizontal.TScale", background=panel_alt, troughcolor="#3c4a7b")

    def _build_layout(self) -> None:
        root_frame = ttk.Frame(self.root, style="Root.TFrame")
        root_frame.pack(fill="both", expand=True)

        sidebar = ttk.Frame(root_frame, style="Panel.TFrame", padding=16)
        sidebar.pack(side="left", fill="y")

        ttk.Label(sidebar, text="Control Center", style="SidebarTitle.TLabel").pack(anchor="w")
        ttk.Label(sidebar, text="Прототип Windows-приложения", style="SidebarSub.TLabel").pack(anchor="w", pady=(2, 16))

        for idx, section in enumerate(SECTIONS):
            btn = ttk.Button(
                sidebar,
                text=section["title"],
                style="Menu.TButton",
                command=lambda i=idx: self.render_section(i),
                width=24,
            )
            btn.pack(anchor="w", fill="x", pady=4)
            self.menu_buttons.append(btn)

        content = ttk.Frame(root_frame, style="Root.TFrame", padding=20)
        content.pack(side="left", fill="both", expand=True)

        header = ttk.Frame(content, style="Root.TFrame")
        header.pack(fill="x")

        label_wrap = ttk.Frame(header, style="Root.TFrame")
        label_wrap.pack(side="left", fill="x", expand=True)

        self.section_title = ttk.Label(label_wrap, style="Title.TLabel")
        self.section_title.pack(anchor="w")

        self.section_description = ttk.Label(label_wrap, style="Subtitle.TLabel")
        self.section_description.pack(anchor="w", pady=(4, 0))

        self.save_button = ttk.Button(header, text="Сохранить пресет", style="Primary.TButton", command=self.on_save)
        self.save_button.pack(side="right", padx=(10, 0))

        self.card_container = ttk.Frame(content, style="Root.TFrame")
        self.card_container.pack(fill="both", expand=True, pady=(18, 0))

    def clear_cards(self) -> None:
        if not self.card_container:
            return
        for widget in self.card_container.winfo_children():
            widget.destroy()

    def render_section(self, index: int) -> None:
        self.current_section_index = index
        section = SECTIONS[index]
        self.section_title.configure(text=section["title"])
        self.section_description.configure(text=section["description"])

        for i, btn in enumerate(self.menu_buttons):
            btn.configure(style="MenuActive.TButton" if i == index else "Menu.TButton")

        self.clear_cards()

        if not self.card_container:
            return

        for row_index, (item_title, item_desc) in enumerate(section["items"]):
            card = ttk.Frame(self.card_container, style="Card.TFrame", padding=12)
            card.grid(row=row_index // 2, column=row_index % 2, padx=8, pady=8, sticky="nsew")

            self.card_container.grid_columnconfigure(0, weight=1)
            self.card_container.grid_columnconfigure(1, weight=1)

            title_row = ttk.Frame(card, style="Card.TFrame")
            title_row.pack(fill="x")

            ttk.Label(title_row, text=item_title, style="CardTitle.TLabel").pack(side="left", anchor="w")

            enabled = tk.BooleanVar(value=row_index % 2 == 0)
            ttk.Checkbutton(title_row, variable=enabled).pack(side="right")

            ttk.Label(card, text=item_desc, style="CardDesc.TLabel").pack(anchor="w", pady=(8, 10))

            ttk.Label(card, text="Уровень", style="CardDesc.TLabel").pack(anchor="w")
            level = tk.IntVar(value=30 + row_index * 20)
            ttk.Scale(card, from_=0, to=100, variable=level, style="Custom.Horizontal.TScale").pack(fill="x", pady=(5, 0))

    def on_save(self) -> None:
        self.save_button.configure(text="Сохранено")
        self.root.after(1300, lambda: self.save_button.configure(text="Сохранить пресет"))


def main() -> None:
    root = tk.Tk()
    app = ControlCenterApp(root)
    _ = app
    root.mainloop()


if __name__ == "__main__":
    main()
