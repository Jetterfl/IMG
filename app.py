import platform
import tkinter as tk
from dataclasses import dataclass
from typing import Callable

try:
    import winreg  # type: ignore
except ImportError:  # non-Windows environment
    winreg = None


@dataclass
class FeatureItem:
    title: str
    description: str
    key: str


SECTIONS = [
    {
        "title": "Профили",
        "description": "Быстрое включение и отключение рабочих функций.",
        "items": [
            FeatureItem("Рабочий режим", "Отключает отвлекающие всплывающие сценарии в приложении.", "work_mode"),
            FeatureItem("Учебный режим", "Фокус на задачах без отвлекающих элементов.", "study_mode"),
            FeatureItem("Игровой режим", "Приоритет интерфейса для игрового сценария.", "game_mode"),
        ],
    },
    {
        "title": "Система",
        "description": "Системные функции с переключателями ON/OFF.",
        "items": [
            FeatureItem(
                "Отключить все уведомления Windows",
                "Выключает уведомления через реестр. Если уже выключены, переключатель активен при запуске.",
                "windows_notifications",
            ),
            FeatureItem("Автозапуск профиля", "Автоматически применять выбранный профиль при старте.", "autostart_profile"),
            FeatureItem("Тихий режим UI", "Минимум лишних визуальных событий в интерфейсе.", "silent_ui"),
        ],
    },
    {
        "title": "Приватность",
        "description": "Конфиденциальность в формате простых переключателей.",
        "items": [
            FeatureItem("Доступ к камере", "Включить или отключить доступ приложений к камере.", "camera"),
            FeatureItem("Доступ к микрофону", "Включить или отключить доступ приложений к микрофону.", "microphone"),
            FeatureItem("Диагностика", "Разрешить или запретить диагностические события.", "telemetry"),
        ],
    },
]


class WindowsNotificationManager:
    TARGETS = [
        (r"Software\Microsoft\Windows\CurrentVersion\PushNotifications", "ToastEnabled", 0),
        (r"Software\Microsoft\Windows\CurrentVersion\Notifications\Settings", "NOC_GLOBAL_SETTING_TOASTS_ENABLED", 0),
    ]

    @classmethod
    def is_supported(cls) -> bool:
        return platform.system() == "Windows" and winreg is not None

    @classmethod
    def is_disabled(cls) -> bool:
        if not cls.is_supported():
            return False

        for path, name, expected in cls.TARGETS:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ) as key:
                    value, _ = winreg.QueryValueEx(key, name)
                    if int(value) != expected:
                        return False
            except FileNotFoundError:
                return False
            except OSError:
                return False

        return True

    @classmethod
    def set_disabled(cls, disabled: bool) -> bool:
        if not cls.is_supported():
            return False

        target_value = 0 if disabled else 1
        for path, name, _ in cls.TARGETS:
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, path) as key:
                    winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, target_value)
            except OSError:
                return False

        return True


class AnimatedToggle(tk.Canvas):
    def __init__(self, master, initial: bool, command: Callable[[bool], bool | None], **kwargs):
        super().__init__(master, width=62, height=32, highlightthickness=0, bd=0, **kwargs)
        self.command = command
        self.state = initial
        self.knob_x = 33 if self.state else 3
        self.target_x = self.knob_x
        self.animating = False

        self.bind("<Button-1>", self.on_click)
        self.configure(cursor="hand2")
        self.draw()

    def draw(self):
        self.delete("all")
        color = "#37d67a" if self.state else "#4a5375"
        self.create_oval(2, 2, 30, 30, fill=color, outline=color)
        self.create_oval(32, 2, 60, 30, fill=color, outline=color)
        self.create_rectangle(16, 2, 46, 30, fill=color, outline=color)
        self.create_oval(self.knob_x, 3, self.knob_x + 26, 29, fill="#ffffff", outline="#d9ddf3")

    def on_click(self, _event):
        if self.animating:
            return

        desired_state = not self.state
        callback_result = self.command(desired_state)
        if callback_result is False:
            return

        self.state = desired_state
        self.target_x = 33 if self.state else 3
        self.animating = True
        self.animate()

    def animate(self):
        if abs(self.knob_x - self.target_x) <= 1:
            self.knob_x = self.target_x
            self.animating = False
            self.draw()
            return

        direction = 1 if self.knob_x < self.target_x else -1
        self.knob_x += direction * 3
        self.draw()
        self.after(12, self.animate)

    def set_state(self, value: bool):
        self.state = value
        self.knob_x = 33 if self.state else 3
        self.target_x = self.knob_x
        self.animating = False
        self.draw()


class ControlCenterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Control Center Prototype")
        self.root.geometry("1120x700")
        self.root.minsize(980, 620)
        self.root.configure(bg="#0b1020")

        self.feature_states: dict[str, bool] = {
            "work_mode": True,
            "study_mode": False,
            "game_mode": False,
            "autostart_profile": True,
            "silent_ui": False,
            "camera": True,
            "microphone": True,
            "telemetry": False,
        }
        self.menu_buttons: list[tk.Button] = []
        self.card_container: tk.Frame | None = None
        self.status_label: tk.Label | None = None

        self._build_layout()
        self.render_section(0)

    def _build_layout(self):
        shell = tk.Frame(self.root, bg="#0b1020")
        shell.pack(fill="both", expand=True)

        sidebar = tk.Frame(shell, bg="#131a31", width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Control Center", bg="#131a31", fg="#e7eaff", font=("Segoe UI", 17, "bold")).pack(
            anchor="w", padx=18, pady=(18, 2)
        )
        tk.Label(sidebar, text="Desktop prototype (.exe)", bg="#131a31", fg="#a9b3d6", font=("Segoe UI", 10)).pack(
            anchor="w", padx=18, pady=(0, 16)
        )

        for idx, section in enumerate(SECTIONS):
            btn = tk.Button(
                sidebar,
                text=section["title"],
                font=("Segoe UI", 11, "bold"),
                fg="#e7eaff",
                bg="#1b2444",
                activebackground="#2a396d",
                activeforeground="#ffffff",
                bd=0,
                relief="flat",
                padx=14,
                pady=11,
                cursor="hand2",
                command=lambda i=idx: self.render_section(i),
            )
            btn.pack(fill="x", padx=14, pady=5)
            self.menu_buttons.append(btn)

        content = tk.Frame(shell, bg="#0b1020")
        content.pack(side="left", fill="both", expand=True, padx=24, pady=20)

        header = tk.Frame(content, bg="#0b1020")
        header.pack(fill="x", pady=(0, 14))

        self.section_title = tk.Label(header, bg="#0b1020", fg="#e7eaff", font=("Segoe UI", 23, "bold"))
        self.section_title.pack(anchor="w")

        self.section_description = tk.Label(header, bg="#0b1020", fg="#a9b3d6", font=("Segoe UI", 11))
        self.section_description.pack(anchor="w", pady=(4, 0))

        self.status_label = tk.Label(content, bg="#0b1020", fg="#86a2ff", font=("Segoe UI", 10, "bold"), text="")
        self.status_label.pack(anchor="w", pady=(0, 8))

        self.card_container = tk.Frame(content, bg="#0b1020")
        self.card_container.pack(fill="both", expand=True)

    def set_status(self, text: str):
        if self.status_label is None:
            return
        self.status_label.config(text=text)
        self.root.after(2200, lambda: self.status_label and self.status_label.config(text=""))

    def clear_cards(self):
        if self.card_container:
            for widget in self.card_container.winfo_children():
                widget.destroy()

    def render_section(self, section_index: int):
        section = SECTIONS[section_index]
        self.section_title.config(text=section["title"])
        self.section_description.config(text=section["description"])

        for idx, btn in enumerate(self.menu_buttons):
            if idx == section_index:
                btn.config(bg="#30447d")
            else:
                btn.config(bg="#1b2444")

        self.clear_cards()
        if not self.card_container:
            return

        for idx, feature in enumerate(section["items"]):
            card = tk.Frame(self.card_container, bg="#17213f", bd=0, highlightthickness=1, highlightbackground="#2a3358")
            card.grid(row=idx // 2, column=idx % 2, padx=8, pady=8, sticky="nsew")

            self.card_container.grid_columnconfigure(0, weight=1)
            self.card_container.grid_columnconfigure(1, weight=1)

            row = tk.Frame(card, bg="#17213f")
            row.pack(fill="x", padx=14, pady=(14, 8))

            text_col = tk.Frame(row, bg="#17213f")
            text_col.pack(side="left", fill="both", expand=True)

            tk.Label(text_col, text=feature.title, bg="#17213f", fg="#e7eaff", font=("Segoe UI", 12, "bold")).pack(anchor="w")
            tk.Label(
                text_col,
                text=feature.description,
                bg="#17213f",
                fg="#a9b3d6",
                font=("Segoe UI", 10),
                justify="left",
                wraplength=390,
            ).pack(anchor="w", pady=(4, 0))

            initial_state = self.initial_feature_state(feature.key)

            toggle = AnimatedToggle(
                row,
                initial=initial_state,
                bg="#17213f",
                command=lambda state, key=feature.key: self.toggle_feature(key, state),
            )
            toggle.pack(side="right", padx=(10, 0), pady=2)

    def initial_feature_state(self, key: str) -> bool:
        if key == "windows_notifications":
            disabled = WindowsNotificationManager.is_disabled()
            self.feature_states[key] = disabled
            return disabled

        return self.feature_states.get(key, False)

    def toggle_feature(self, key: str, state: bool) -> bool:
        if key == "windows_notifications":
            if not WindowsNotificationManager.is_supported():
                self.set_status("Функция проверки реестра доступна только на Windows.")
                return False

            success = WindowsNotificationManager.set_disabled(state)
            if not success:
                self.set_status("Не удалось изменить реестр для уведомлений.")
                return False

            final_state = WindowsNotificationManager.is_disabled()
            self.feature_states[key] = final_state
            self.set_status("Уведомления Windows отключены." if final_state else "Уведомления Windows включены.")
            return final_state == state

        self.feature_states[key] = state
        self.set_status(f"{key}: {'ON' if state else 'OFF'}")
        return True


def main():
    root = tk.Tk()
    ControlCenterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
