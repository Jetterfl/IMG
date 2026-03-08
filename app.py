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
        title="Disable Windows notifications",
        description="Global toast notifications",
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
        title="Disable lock screen toasts",
        description="No toasts above lock screen",
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
        title="Disable advertising ID",
        description="Privacy hardening",
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
        title="Disable Windows tips",
        description="Disable suggestion content",
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
        title="Disable Start suggestions",
        description="Disable Start recommendation entries",
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
        title="Disable activity history",
        description="Disable publishing/uploading user activities",
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

LOCAL_FEATURES = [
    FeatureItem("Auto Save", "Local prototype behavior", "auto_save"),
    FeatureItem("Compact Mode", "Reduce spacing and labels", "compact_mode"),
    FeatureItem("Fast Animations", "Speed up UI transitions", "fast_animations"),
    FeatureItem("Focus Accent", "Use strong selection highlight", "focus_accent"),
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
        if not feature.registry_targets or not cls.is_supported():
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


class DotToggle(tk.Canvas):
    def __init__(self, master, initial: bool, command, **kwargs):
        super().__init__(master, width=48, height=22, highlightthickness=0, bd=0, **kwargs)
        self.command = command
        self.state = initial
        self.dot_x = 27 if initial else 3
        self.target_x = self.dot_x
        self.animating = False
        self.configure(cursor="hand2")
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _draw(self):
        self.delete("all")
        track = "#224c73" if self.state else "#22273f"
        border = "#2f9af0" if self.state else "#3b4060"
        self.create_oval(1, 1, 21, 21, fill=track, outline=border)
        self.create_oval(27, 1, 47, 21, fill=track, outline=border)
        self.create_rectangle(11, 1, 37, 21, fill=track, outline=track)
        self.create_oval(self.dot_x, 2, self.dot_x + 18, 20, fill="#05b7ff" if self.state else "#8a91b5", outline="")

    def _on_click(self, _event):
        if self.animating:
            return
        desired = not self.state
        if self.command(desired) is False:
            return
        self.state = desired
        self.target_x = 27 if desired else 3
        self.animating = True
        self._animate()

    def _animate(self):
        if abs(self.dot_x - self.target_x) <= 1:
            self.dot_x = self.target_x
            self.animating = False
            self._draw()
            return
        self.dot_x += 3 if self.dot_x < self.target_x else -3
        self._draw()
        self.after(11, self._animate)


class NeverloseApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Neverlose Control Panel")
        self.root.geometry("1220x700")
        self.root.minsize(1100, 620)
        self.root.configure(bg="#7f9aaa")

        self.local_states = {
            "auto_save": True,
            "compact_mode": False,
            "fast_animations": True,
            "focus_accent": True,
        }

        self.status_label: tk.Label | None = None
        self.main_left: tk.Frame | None = None
        self.main_right: tk.Frame | None = None

        self._build_shell()
        self._build_panels()

    def _build_shell(self):
        shell = tk.Frame(self.root, bg="#0a0d12", highlightthickness=1, highlightbackground="#2b2f44")
        shell.pack(fill="both", expand=True, padx=18, pady=18)

        sidebar = tk.Frame(shell, bg="#111821", width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="NEVERLOSE", bg="#111821", fg="#f1f4ff", font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=16, pady=(18, 2))

        self._menu_group(sidebar, "Aimbot", ["Ragebot", "Anti Aim", "Legitbot"], active="Anti Aim")
        self._menu_group(sidebar, "Visuals", ["Players", "Weapon", "Grenades", "World", "View"])
        self._menu_group(sidebar, "Miscellaneous", ["Main", "Inventory", "Scripts", "Configs"])

        center = tk.Frame(shell, bg="#070b10")
        center.pack(side="left", fill="both", expand=True)

        topbar = tk.Frame(center, bg="#0d1118", height=54, highlightthickness=1, highlightbackground="#1f2735")
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        tk.Button(
            topbar,
            text="💾  Save",
            bg="#0f1621",
            fg="#d5e4ff",
            activebackground="#102338",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=6,
            cursor="hand2",
        ).pack(side="left", padx=14, pady=10)

        tk.Label(topbar, text="⚙  🔍", bg="#0d1118", fg="#8994b9", font=("Segoe UI", 12)).pack(side="right", padx=14)

        content = tk.Frame(center, bg="#070b10")
        content.pack(fill="both", expand=True, padx=12, pady=12)

        self.main_left = tk.Frame(content, bg="#0f141d", highlightthickness=1, highlightbackground="#252c3d")
        self.main_left.pack(side="left", fill="both", expand=True)

        self.main_right = tk.Frame(content, bg="#0f141d", width=300, highlightthickness=1, highlightbackground="#252c3d")
        self.main_right.pack(side="left", fill="y", padx=(10, 0))
        self.main_right.pack_propagate(False)

    def _menu_group(self, parent, title: str, items: list[str], active: str | None = None):
        tk.Label(parent, text=title, bg="#111821", fg="#7f89ad", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16, pady=(16, 6))
        for item in items:
            is_active = item == active
            tk.Button(
                parent,
                text=f"   {item}",
                anchor="w",
                bg="#2b3242" if is_active else "#111821",
                fg="#f2f6ff" if is_active else "#9ca7cb",
                activebackground="#2d4f74",
                activeforeground="#ffffff",
                relief="flat",
                bd=0,
                padx=8,
                pady=8,
                font=("Segoe UI", 10, "bold" if is_active else "normal"),
                cursor="hand2",
            ).pack(fill="x", padx=12, pady=2)

    def _build_panels(self):
        if self.main_left is None or self.main_right is None:
            return

        head = tk.Frame(self.main_left, bg="#0f141d")
        head.pack(fill="x", padx=14, pady=(12, 8))
        tk.Label(head, text="System Tweaks", bg="#0f141d", fg="#e9f1ff", font=("Segoe UI", 14, "bold")).pack(anchor="w")

        grids = tk.Frame(self.main_left, bg="#0f141d")
        grids.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left_panel = tk.Frame(grids, bg="#0b1017", highlightthickness=1, highlightbackground="#20283a")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 6))
        right_panel = tk.Frame(grids, bg="#0b1017", highlightthickness=1, highlightbackground="#20283a")
        right_panel.pack(side="left", fill="both", expand=True, padx=(6, 0))

        self._feature_list(left_panel, "Movement", SYSTEM_FEATURES[:3])
        self._feature_list(right_panel, "Other", SYSTEM_FEATURES[3:])

        tk.Label(self.main_right, text="About Neverlose", bg="#0f141d", fg="#66b6ff", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(12, 2))
        tk.Label(self.main_right, text="NEVERLOSE.CC", bg="#0f141d", fg="#f7f8ff", font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=12)

        sep = tk.Frame(self.main_right, bg="#1d2334", height=1)
        sep.pack(fill="x", padx=12, pady=12)

        self._feature_list(self.main_right, "Workspace", LOCAL_FEATURES, compact=True)

        self.status_label = tk.Label(self.main_right, text="", bg="#0f141d", fg="#67c3ff", font=("Segoe UI", 9, "bold"))
        self.status_label.pack(anchor="w", padx=12, pady=(8, 0))

    def _feature_list(self, parent: tk.Frame, title: str, features: list[FeatureItem], compact: bool = False):
        tk.Label(parent, text=title, bg=parent["bg"], fg="#a8b2d4", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(10, 6))

        for feature in features:
            row = tk.Frame(parent, bg=parent["bg"])
            row.pack(fill="x", padx=10, pady=3)

            text = tk.Frame(row, bg=parent["bg"])
            text.pack(side="left", fill="x", expand=True)

            tk.Label(text, text=feature.title, bg=parent["bg"], fg="#dce5ff", font=("Segoe UI", 10)).pack(anchor="w")
            if not compact:
                tk.Label(text, text=feature.description, bg=parent["bg"], fg="#6f7da3", font=("Segoe UI", 8)).pack(anchor="w")

            toggle = DotToggle(
                row,
                initial=self._initial_state(feature),
                bg=parent["bg"],
                command=lambda desired, f=feature: self._toggle_feature(f, desired),
            )
            toggle.pack(side="right", pady=1)

    def _initial_state(self, feature: FeatureItem) -> bool:
        if feature.registry_targets:
            return RegistryManager.is_feature_enabled(feature)
        return self.local_states.get(feature.key, False)

    def _set_status(self, message: str):
        if self.status_label is None:
            return
        self.status_label.config(text=message)
        self.root.after(2200, lambda: self.status_label and self.status_label.config(text=""))

    def _toggle_feature(self, feature: FeatureItem, desired: bool) -> bool:
        if feature.registry_targets:
            if not RegistryManager.is_supported():
                self._set_status("Registry features are available only on Windows")
                return False

            if not RegistryManager.set_feature_enabled(feature, desired):
                self._set_status(f"Failed: {feature.title}")
                return False

            self._set_status(f"{feature.title}: {'ON' if desired else 'OFF'}")
            return True

        self.local_states[feature.key] = desired
        self._set_status(f"{feature.title}: {'ON' if desired else 'OFF'}")
        return True


def main():
    root = tk.Tk()
    NeverloseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
