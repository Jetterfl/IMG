import platform
import tkinter as tk
from dataclasses import dataclass

try:
    import winreg  # type: ignore
except ImportError:
    winreg = None


@dataclass(frozen=True)
class RegistryValueTarget:
    path: str
    name: str
    enabled_value: int
    disabled_value: int


@dataclass(frozen=True)
class FeatureItem:
    title: str
    description: str
    key: str
    registry_targets: tuple[RegistryValueTarget, ...] = ()


SYSTEM_FEATURES = [
    FeatureItem(
        title="Отключить все уведомления Windows",
        description="Toast-уведомления отключаются через HKCU. Состояние читается при запуске.",
        key="windows_notifications",
        registry_targets=(
            RegistryValueTarget(
                path=r"Software\Microsoft\Windows\CurrentVersion\PushNotifications",
                name="ToastEnabled",
                enabled_value=0,
                disabled_value=1,
            ),
            RegistryValueTarget(
                path=r"Software\Microsoft\Windows\CurrentVersion\Notifications\Settings",
                name="NOC_GLOBAL_SETTING_TOASTS_ENABLED",
                enabled_value=0,
                disabled_value=1,
            ),
        ),
    ),
    FeatureItem(
        title="Отключить уведомления на lock screen",
        description="Блокирует показ toast-уведомлений на экране блокировки.",
        key="lockscreen_notifications",
        registry_targets=(
            RegistryValueTarget(
                path=r"Software\Microsoft\Windows\CurrentVersion\Notifications\Settings",
                name="NOC_GLOBAL_SETTING_ALLOW_TOASTS_ABOVE_LOCK",
                enabled_value=0,
                disabled_value=1,
            ),
        ),
    ),
    FeatureItem(
        title="Отключить рекламный ID",
        description="Отключает персональный advertising ID для приложений.",
        key="advertising_id",
        registry_targets=(
            RegistryValueTarget(
                path=r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                name="Enabled",
                enabled_value=0,
                disabled_value=1,
            ),
        ),
    ),
    FeatureItem(
        title="Отключить советы Windows",
        description="Выключает рекомендации и советы в интерфейсе Windows.",
        key="windows_tips",
        registry_targets=(
            RegistryValueTarget(
                path=r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                name="SubscribedContent-338389Enabled",
                enabled_value=0,
                disabled_value=1,
            ),
            RegistryValueTarget(
                path=r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                name="SubscribedContent-338388Enabled",
                enabled_value=0,
                disabled_value=1,
            ),
        ),
    ),
    FeatureItem(
        title="Отключить рекомендации в меню Пуск",
        description="Блокирует suggestion-контент и app recommendations.",
        key="start_suggestions",
        registry_targets=(
            RegistryValueTarget(
                path=r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                name="SystemPaneSuggestionsEnabled",
                enabled_value=0,
                disabled_value=1,
            ),
        ),
    ),
    FeatureItem(
        title="Отключить activity history",
        description="Отключает публикацию и загрузку активности пользователя.",
        key="activity_history",
        registry_targets=(
            RegistryValueTarget(
                path=r"Software\Microsoft\Windows\CurrentVersion\Privacy",
                name="PublishUserActivities",
                enabled_value=0,
                disabled_value=1,
            ),
            RegistryValueTarget(
                path=r"Software\Microsoft\Windows\CurrentVersion\Privacy",
                name="UploadUserActivities",
                enabled_value=0,
                disabled_value=1,
            ),
        ),
    ),
]

SECTIONS = [
    {
        "title": "System Tweaks",
        "description": "Neverlose-style переключатели реальных системных параметров через реестр.",
        "items": SYSTEM_FEATURES,
    },
    {
        "title": "Workspace",
        "description": "Локальные переключатели прототипа для рабочих сценариев.",
        "items": [
            FeatureItem("Рабочий режим", "Минимум отвлечений в интерфейсе приложения.", "work_mode"),
            FeatureItem("Учебный режим", "Упор на фокус и простую навигацию.", "study_mode"),
            FeatureItem("Игровой режим", "Ускоренный визуальный пресет приложения.", "game_mode"),
        ],
    },
]


class RegistryManager:
    @staticmethod
    def is_supported() -> bool:
        return platform.system() == "Windows" and winreg is not None

    @staticmethod
    def _read_dword(path: str, name: str) -> int | None:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, name)
            return int(value)
        except OSError:
            return None

    @staticmethod
    def _write_dword(path: str, name: str, value: int) -> bool:
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, path) as key:
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, int(value))
            return True
        except OSError:
            return False

    @classmethod
    def is_feature_enabled(cls, feature: FeatureItem) -> bool:
        if not feature.registry_targets:
            return False
        if not cls.is_supported():
            return False

        for target in feature.registry_targets:
            current = cls._read_dword(target.path, target.name)
            if current is None or current != target.enabled_value:
                return False
        return True

    @classmethod
    def set_feature_enabled(cls, feature: FeatureItem, enabled: bool) -> bool:
        if not cls.is_supported():
            return False

        for target in feature.registry_targets:
            desired = target.enabled_value if enabled else target.disabled_value
            if not cls._write_dword(target.path, target.name, desired):
                return False

        return cls.is_feature_enabled(feature) == enabled


class AnimatedToggle(tk.Canvas):
    def __init__(self, master, initial: bool, command, **kwargs):
        super().__init__(master, width=58, height=30, highlightthickness=0, bd=0, **kwargs)
        self.state = initial
        self.command = command
        self.knob_x = 30 if initial else 2
        self.target_x = self.knob_x
        self.animating = False
        self.bind("<Button-1>", self._on_click)
        self.configure(cursor="hand2")
        self._draw()

    def _draw(self):
        self.delete("all")
        track = "#9a6bff" if self.state else "#35395b"
        border = "#bb97ff" if self.state else "#4b4f75"
        self.create_oval(2, 2, 28, 28, fill=track, outline=border, width=1)
        self.create_oval(30, 2, 56, 28, fill=track, outline=border, width=1)
        self.create_rectangle(15, 2, 43, 28, fill=track, outline=track)
        self.create_oval(self.knob_x, 3, self.knob_x + 24, 27, fill="#ffffff", outline="#d9daf5")

    def _on_click(self, _event):
        if self.animating:
            return

        desired = not self.state
        result = self.command(desired)
        if result is False:
            return

        self.state = desired
        self.target_x = 30 if self.state else 2
        self.animating = True
        self._animate()

    def _animate(self):
        if abs(self.knob_x - self.target_x) <= 1:
            self.knob_x = self.target_x
            self.animating = False
            self._draw()
            return

        self.knob_x += 3 if self.knob_x < self.target_x else -3
        self._draw()
        self.after(10, self._animate)

    def sync_state(self, value: bool):
        self.state = value
        self.knob_x = 30 if value else 2
        self.target_x = self.knob_x
        self.animating = False
        self._draw()


class ControlCenterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Neverlose Control Center")
        self.root.geometry("1080x640")
        self.root.minsize(940, 560)
        self.root.configure(bg="#0a0b12")

        self.local_states: dict[str, bool] = {
            "work_mode": True,
            "study_mode": False,
            "game_mode": False,
        }

        self.menu_buttons: list[tk.Button] = []
        self.card_container: tk.Frame | None = None
        self.status_label: tk.Label | None = None

        self._build_ui()
        self.render_section(0)

    def _build_ui(self):
        shell = tk.Frame(self.root, bg="#0a0b12")
        shell.pack(fill="both", expand=True)

        sidebar = tk.Frame(shell, bg="#111322", width=260, highlightthickness=1, highlightbackground="#282d49")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo = tk.Frame(sidebar, bg="#111322")
        logo.pack(fill="x", padx=16, pady=(16, 14))
        tk.Label(logo, text="NEVERLOSE", bg="#111322", fg="#c59bff", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(logo, text="control center", bg="#111322", fg="#8f95b8", font=("Segoe UI", 10)).pack(anchor="w")

        for idx, section in enumerate(SECTIONS):
            btn = tk.Button(
                sidebar,
                text=section["title"],
                bg="#1a1f36",
                fg="#e8e9ff",
                activebackground="#7d4cff",
                activeforeground="#ffffff",
                bd=0,
                relief="flat",
                anchor="w",
                padx=14,
                pady=10,
                font=("Segoe UI", 11, "bold"),
                cursor="hand2",
                command=lambda i=idx: self.render_section(i),
            )
            btn.pack(fill="x", padx=14, pady=5)
            self.menu_buttons.append(btn)

        content = tk.Frame(shell, bg="#0a0b12")
        content.pack(side="left", fill="both", expand=True, padx=18, pady=16)

        self.section_title = tk.Label(content, bg="#0a0b12", fg="#f0edff", font=("Segoe UI", 22, "bold"))
        self.section_title.pack(anchor="w")
        self.section_desc = tk.Label(content, bg="#0a0b12", fg="#9298bf", font=("Segoe UI", 10))
        self.section_desc.pack(anchor="w", pady=(3, 8))

        self.status_label = tk.Label(content, bg="#0a0b12", fg="#b694ff", font=("Segoe UI", 10, "bold"), text="")
        self.status_label.pack(anchor="w", pady=(0, 8))

        self.card_container = tk.Frame(content, bg="#0a0b12")
        self.card_container.pack(fill="both", expand=True)

    def _set_status(self, message: str):
        if self.status_label is None:
            return
        self.status_label.config(text=message)
        self.root.after(2200, lambda: self.status_label and self.status_label.config(text=""))

    def _clear_cards(self):
        if self.card_container:
            for child in self.card_container.winfo_children():
                child.destroy()

    def _initial_state(self, feature: FeatureItem) -> bool:
        if feature.registry_targets:
            enabled = RegistryManager.is_feature_enabled(feature)
            return enabled
        return self.local_states.get(feature.key, False)

    def _toggle_feature(self, feature: FeatureItem, desired: bool) -> bool:
        if feature.registry_targets:
            if not RegistryManager.is_supported():
                self._set_status("Реестровые функции доступны только на Windows.")
                return False

            ok = RegistryManager.set_feature_enabled(feature, desired)
            if not ok:
                self._set_status(f"Не удалось применить: {feature.title}")
                return False

            state_text = "ON" if desired else "OFF"
            self._set_status(f"{feature.title}: {state_text}")
            return True

        self.local_states[feature.key] = desired
        self._set_status(f"{feature.title}: {'ON' if desired else 'OFF'}")
        return True

    def render_section(self, section_index: int):
        section = SECTIONS[section_index]
        self.section_title.config(text=section["title"])
        self.section_desc.config(text=section["description"])

        for idx, button in enumerate(self.menu_buttons):
            if idx == section_index:
                button.config(bg="#7d4cff", fg="#ffffff")
            else:
                button.config(bg="#1a1f36", fg="#e8e9ff")

        self._clear_cards()
        if self.card_container is None:
            return

        for i, feature in enumerate(section["items"]):
            card = tk.Frame(
                self.card_container,
                bg="#151a2d",
                highlightthickness=1,
                highlightbackground="#2c3253",
                width=330,
                height=106,
            )
            card.grid(row=i // 2, column=i % 2, padx=6, pady=6, sticky="n")
            card.grid_propagate(False)

            self.card_container.grid_columnconfigure(0, weight=1)
            self.card_container.grid_columnconfigure(1, weight=1)

            head = tk.Frame(card, bg="#151a2d")
            head.pack(fill="x", padx=10, pady=(8, 0))

            tk.Label(head, text=feature.title, bg="#151a2d", fg="#f4f2ff", font=("Segoe UI", 10, "bold")).pack(side="left", anchor="w")

            toggle = AnimatedToggle(
                head,
                initial=self._initial_state(feature),
                bg="#151a2d",
                command=lambda desired, f=feature: self._toggle_feature(f, desired),
            )
            toggle.pack(side="right")

            tk.Label(
                card,
                text=feature.description,
                bg="#151a2d",
                fg="#9da3c7",
                font=("Segoe UI", 9),
                justify="left",
                wraplength=300,
            ).pack(anchor="w", padx=10, pady=(4, 0))


def main():
    root = tk.Tk()
    ControlCenterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
