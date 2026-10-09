# File: foreground_button_clicker.py
# Summary: Japanese/English foreground-window button monitor and clicker.
# Author: 5garashi.com設計事務所 / 5garashi.com Design Office
# Created: 2026-07-25
# License: Not specified
# SPDX-License-Identifier: NOASSERTION

from __future__ import annotations

import argparse
import ctypes
import json
import os
import queue
import sys
import threading
import time
import traceback
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import tkinter as tk
from tkinter import messagebox, ttk


APP_NAME = "最前面ボタン自動クリック"
APP_VERSION = "1.3.0"
CONFIG_PATH = Path(__file__).with_name("button_clicker_config.json")
RUNTIME_LOG_PATH = Path(__file__).with_name("runtime_log.txt")
BRAND_MARK_PATH = Path(__file__).parent / "assets" / "office_identity_mark.png"

PAPER = "#F9EFCB"
HEAD = "#FFE699"
INK = "#385723"
STEEL = "#7B4A21"
VOLT = "#B92613"
VOLT_DEEP = "#8C1B0D"
CARD = "#FFFDF2"
LINE = "#DFCF9A"
OK = "#3E6B2A"
CREAM = "#FFF3D6"

BUTTON_PALETTES = {
    "normal": (HEAD, INK, LINE, INK, INK),
    "primary": (INK, HEAD, OK, CREAM, INK),
    "danger": (VOLT_DEEP, CREAM, VOLT, CREAM, VOLT_DEEP),
    "destructive": (CREAM, VOLT_DEEP, HEAD, VOLT_DEEP, VOLT_DEEP),
}

MATCH_LABELS = {
    "prefix": "前方一致",
    "exact": "完全一致",
    "contains": "部分一致",
}

TRANSLATIONS = {
    "最前面ボタン自動クリック": "Foreground Button Clicker",
    "日本語": "日本語",
    "最前面ウィンドウのボタンを優先順位順に検出します": (
        "Detect buttons in the foreground window by priority."
    ),
    (
        "注意：［常に許可］は、今後の操作も確認なしで許可する場合があります。"
        "最初は「検出だけ」で確認してください。"
    ): (
        "Warning: “Always allow” may approve future actions without confirmation. "
        "Start with “Detect only” to verify."
    ),
    "監視設定": "Monitoring settings",
    "対象ウィンドウのタイトルを含む文字": "Text contained in the window title",
    "空欄ならすべて（追跡時は取得候補を絞り込み）": (
        "Blank = all windows; tracking mode filters candidates."
    ),
    "確認間隔［秒］": "Scan interval [seconds]",
    "クリック後の待機［秒］": "Cooldown after click [seconds]",
    "検出だけ（クリックしない）": "Detect only (do not click)",
    "ウィンドウ追跡モード（監視開始後、次に最前面にしたアプリを固定）": (
        "Track a window (after starting, bring the target app to the foreground)"
    ),
    "追跡対象": "Tracked window",
    "登録ボタン": "Button rules",
    "追加": "Add",
    "編集": "Edit",
    "削除": "Delete",
    "一覧を表示": "Show list",
    "初期設定に戻す": "Restore defaults",
    "優先順位": "Priority",
    "ボタン文字": "Button text",
    "照合方法": "Match",
    "状態": "Status",
    "有効": "Enabled",
    "無効": "Disabled",
    "（タイトルなし）": "(untitled window)",
    "ウィンドウ追跡モード": "window tracking mode",
    "追跡対象を選択中": "Waiting to track",
    "追跡中": "Tracking",
    "監視中": "Monitoring",
    "選択待ち：対象アプリを最前面にしてください": (
        "Waiting: bring the target app to the foreground"
    ),
    "監視を開始": "Start monitoring",
    "停止": "Stop",
    "動作履歴": "Activity log",
    "5garashi.com設計事務所　|　Office Identity v4.6": (
        "5garashi.com Design Office | Office Identity v4.6"
    ),
    "登録ボタン一覧": "Button rules",
    "閉じる": "Close",
    "選択してください": "Select a rule",
    "対象の行を選択してください。": "Select a row first.",
    "ボタンを追加": "Add button rule",
    "ボタンを編集": "Edit button rule",
    "削除の確認": "Confirm deletion",
    "初期設定に戻す": "Restore defaults",
    "入力エラー": "Input error",
    "設定エラー": "Settings error",
    "優先順位（1が最優先）": "Priority (1 is highest)",
    "ボタンに表示される文字": "Text shown on the button",
    "このルールを有効にする": "Enable this rule",
    "キャンセル": "Cancel",
    "保存": "Save",
    "優先順位は1～999の整数で入力してください。": (
        "Enter a whole-number priority from 1 to 999."
    ),
    "ボタン文字を入力してください。": "Enter button text.",
    "「常に許可」「一度だけ許可」": "“Always allow” and “Allow once”",
    "「{text}」を削除しますか？": "Delete “{text}”?",
    "登録ボタンを「常に許可」「一度だけ許可」に戻しますか？": (
        "Restore the default “Always allow” and “Allow once” rules?"
    ),
    "確認間隔とクリック後の待機は数値で入力してください。": (
        "Enter numbers for the scan interval and click cooldown."
    ),
    "確認間隔は0.2～60秒で入力してください。": (
        "Enter a scan interval from 0.2 to 60 seconds."
    ),
    "クリック後の待機は0.5～600秒で入力してください。": (
        "Enter a click cooldown from 0.5 to 600 seconds."
    ),
    "有効なボタンを1件以上登録してください。": (
        "Add at least one enabled button rule."
    ),
    "Windows専用": "Windows only",
    "このプログラムはWindows 10／11専用です。": (
        "This program requires Windows 10 or 11."
    ),
    "必要な機能がありません": "Required component missing",
    "uiautomationがインストールされていません。\n"
    "「install_and_run.bat」から起動してください。": (
        "The uiautomation package is not installed.\n"
        "Start the program with “install_and_run.bat”."
    ),
    "停止中": "Stopped",
    "検出だけ": "Detect only",
    "自動クリック": "Auto-click",
    "未選択（監視開始後、対象アプリを最前面にしてください）": (
        "Not selected (bring the target app to the foreground after starting)"
    ),
    "通常モード：最前面ウィンドウを監視": (
        "Normal mode: monitoring the foreground window"
    ),
    "選択待ち：対象アプリを最前面にしてください": (
        "Waiting for selection: bring the target app to the foreground"
    ),
    "完全一致": "Exact",
    "前方一致": "Starts with",
    "部分一致": "Contains",
}


def translate(language: str, text: str) -> str:
    if language != "en":
        return text
    return TRANSLATIONS.get(text, text)


def match_label(match: str, language: str) -> str:
    label = MATCH_LABELS[match]
    return translate(language, label)


@dataclass
class Rule:
    priority: int
    text: str
    match: str = "prefix"
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rule":
        match = str(data.get("match", "prefix"))
        if match not in MATCH_LABELS:
            match = "prefix"
        return cls(
            priority=max(1, int(data.get("priority", 1))),
            text=str(data.get("text", "")).strip(),
            match=match,
            enabled=bool(data.get("enabled", True)),
        )


DEFAULT_CONFIG: dict[str, Any] = {
    "title_contains": "",
    "interval_seconds": 0.5,
    "cooldown_seconds": 2.0,
    "dry_run": True,
    "tracking_mode": False,
    "rules": [
        asdict(Rule(priority=1, text="常に許可", match="prefix")),
        asdict(Rule(priority=2, text="一度だけ許可", match="prefix")),
    ],
}


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return " ".join(value.split()).casefold()


def text_matches(actual: str, rule: Rule) -> bool:
    actual_n = normalize_text(actual)
    wanted_n = normalize_text(rule.text)
    if not wanted_n:
        return False
    if rule.match == "exact":
        return actual_n == wanted_n
    if rule.match == "contains":
        return wanted_n in actual_n
    return actual_n.startswith(wanted_n)


def get_foreground_window() -> int:
    if os.name != "nt":
        return 0
    return int(ctypes.windll.user32.GetForegroundWindow())


def get_window_title(hwnd: int) -> str:
    if os.name != "nt" or not hwnd:
        return ""
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def is_window(hwnd: int) -> bool:
    if os.name != "nt" or not hwnd:
        return False
    return bool(ctypes.windll.user32.IsWindow(hwnd))


def get_window_process_id(hwnd: int) -> int:
    if os.name != "nt" or not hwnd:
        return 0
    process_id = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(
        hwnd,
        ctypes.byref(process_id),
    )
    return int(process_id.value)


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return json.loads(json.dumps(DEFAULT_CONFIG, ensure_ascii=False))
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("設定ファイルの形式が正しくありません。")
        merged = json.loads(json.dumps(DEFAULT_CONFIG, ensure_ascii=False))
        merged.update(data)
        return merged
    except Exception:
        backup = CONFIG_PATH.with_suffix(".broken.json")
        try:
            CONFIG_PATH.replace(backup)
        except OSError:
            pass
        return json.loads(json.dumps(DEFAULT_CONFIG, ensure_ascii=False))


def save_config(config: dict[str, Any]) -> None:
    temporary = CONFIG_PATH.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(CONFIG_PATH)


def set_office_button_state(button: tk.Button, state: str) -> None:
    """Apply enabled/disabled colours without relying on a ttk theme."""
    palette_name = str(getattr(button, "_office_palette_name", "normal"))
    background, foreground, active_background, active_foreground, border = (
        BUTTON_PALETTES[palette_name]
    )
    if state == "disabled":
        button.configure(
            state="disabled",
            bg=LINE,
            fg=STEEL,
            activebackground=LINE,
            activeforeground=STEEL,
            disabledforeground=STEEL,
            highlightbackground=LINE,
            cursor="arrow",
        )
    else:
        button.configure(
            state="normal",
            bg=background,
            fg=foreground,
            activebackground=active_background,
            activeforeground=active_foreground,
            disabledforeground=STEEL,
            highlightbackground=border,
            cursor="hand2",
        )


def office_button(
    parent: tk.Misc,
    *,
    text: str,
    command: Any,
    palette: str = "normal",
    width: int | None = None,
    state: str = "normal",
) -> tk.Button:
    """Create a consistently rendered Office Identity button.

    Classic Tk buttons are used intentionally. On some Windows display-scale
    combinations the ``clam`` ttk button label is painted only partially.
    """
    button = tk.Button(
        parent,
        text=text,
        command=command,
        font=("Yu Gothic UI", 10, "bold"),
        padx=14,
        pady=8,
        relief="raised",
        overrelief="raised",
        borderwidth=2,
        highlightthickness=1,
        highlightcolor=VOLT,
        takefocus=True,
    )
    button._office_palette_name = palette  # type: ignore[attr-defined]
    if width is not None:
        button.configure(width=width)
    set_office_button_state(button, state)
    return button


class RuleDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Misc,
        title: str,
        rule: Rule | None = None,
        language: str = "ja",
    ):
        super().__init__(parent)
        self.language = language
        self.title(translate(language, title))
        self.resizable(False, False)
        self.transient(parent)
        self.result: Rule | None = None

        self.priority_var = tk.StringVar(value=str(rule.priority if rule else 1))
        self.text_var = tk.StringVar(value=rule.text if rule else "")
        self.match_var = tk.StringVar(
            value=match_label(rule.match if rule else "prefix", language)
        )
        self.enabled_var = tk.BooleanVar(value=rule.enabled if rule else True)

        frame = ttk.Frame(self, padding=18)
        frame.grid(sticky="nsew")

        ttk.Label(
            frame, text=translate(language, "優先順位（1が最優先）")
        ).grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )
        priority = ttk.Spinbox(
            frame,
            from_=1,
            to=999,
            textvariable=self.priority_var,
            width=12,
        )
        priority.grid(row=1, column=0, sticky="ew", pady=(0, 14))

        ttk.Label(
            frame, text=translate(language, "ボタンに表示される文字")
        ).grid(
            row=2, column=0, sticky="w", pady=(0, 6)
        )
        text_entry = ttk.Entry(frame, textvariable=self.text_var, width=38)
        text_entry.grid(row=3, column=0, sticky="ew", pady=(0, 14))

        ttk.Label(frame, text=translate(language, "照合方法")).grid(
            row=4, column=0, sticky="w", pady=(0, 6)
        )
        match = ttk.Combobox(
            frame,
            textvariable=self.match_var,
            values=[match_label(key, language) for key in MATCH_LABELS],
            state="readonly",
            width=18,
        )
        match.grid(row=5, column=0, sticky="w", pady=(0, 12))

        ttk.Checkbutton(
            frame,
            text=translate(language, "このルールを有効にする"),
            variable=self.enabled_var,
        ).grid(row=6, column=0, sticky="w", pady=(0, 18))

        buttons = ttk.Frame(frame)
        buttons.grid(row=7, column=0, sticky="e")
        office_button(
            buttons,
            text=translate(language, "キャンセル"),
            command=self.destroy,
            width=10,
        ).pack(side="left", padx=(0, 8))
        office_button(
            buttons,
            text=translate(language, "保存"),
            command=self._accept,
            palette="primary",
            width=10,
        ).pack(side="left")

        self.bind("<Escape>", lambda _event: self.destroy())
        self.bind("<Return>", lambda _event: self._accept())
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.update_idletasks()
        self.geometry(
            f"+{parent.winfo_rootx() + 80}+{parent.winfo_rooty() + 80}"
        )
        self.grab_set()
        text_entry.focus_set()

    def _accept(self) -> None:
        try:
            priority = int(self.priority_var.get())
            if not 1 <= priority <= 999:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                translate(self.language, "入力エラー"),
                translate(
                    self.language,
                    "優先順位は1～999の整数で入力してください。",
                ),
                parent=self,
            )
            return

        text = self.text_var.get().strip()
        if not text:
            messagebox.showerror(
                translate(self.language, "入力エラー"),
                translate(self.language, "ボタン文字を入力してください。"),
                parent=self,
            )
            return

        self.result = Rule(
            priority=priority,
            text=text,
            match={
                match_label(key, self.language): key for key in MATCH_LABELS
            }.get(self.match_var.get(), "prefix"),
            enabled=self.enabled_var.get(),
        )
        self.destroy()


class ButtonClickerApp:
    def __init__(self, root: tk.Tk, language_override: str | None = None):
        self.root = root
        self.config = load_config()
        self.language = (
            language_override
            if language_override in {"ja", "en"}
            else ("en" if self.config.get("language") == "en" else "ja")
        )
        self.rules = [
            Rule.from_dict(item)
            for item in self.config.get("rules", [])
            if isinstance(item, dict)
        ]
        if not self.rules:
            self.rules = [Rule.from_dict(item) for item in DEFAULT_CONFIG["rules"]]

        self.events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.stop_event = threading.Event()
        self.worker: threading.Thread | None = None
        self.running = False
        self.self_hwnd = 0

        self.title_var = tk.StringVar(
            value=str(self.config.get("title_contains", ""))
        )
        self.interval_var = tk.StringVar(
            value=str(self.config.get("interval_seconds", 0.5))
        )
        self.cooldown_var = tk.StringVar(
            value=str(self.config.get("cooldown_seconds", 2.0))
        )
        self.dry_run_var = tk.BooleanVar(
            value=bool(self.config.get("dry_run", True))
        )
        self.tracking_mode_var = tk.BooleanVar(
            value=bool(self.config.get("tracking_mode", False))
        )
        self.tracked_title_var = tk.StringVar(
            value="通常モード：最前面ウィンドウを監視"
        )
        self.status_var = tk.StringVar(
            value=translate(self.language, "停止中")
        )
        self.rule_list_window: tk.Toplevel | None = None
        self.rule_list_tree: ttk.Treeview | None = None

        self._build_ui()
        self._refresh_rules()
        try:
            RUNTIME_LOG_PATH.write_text(
                f"{translate(self.language, APP_NAME)} v{APP_VERSION}\n"
                f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
                encoding="utf-8",
            )
        except OSError:
            pass
        self.root.after(100, self._capture_self_hwnd)
        self.root.after(100, self._process_events)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        self.root.title(
            f"{translate(self.language, APP_NAME)}  v{APP_VERSION}"
        )
        self.root.geometry("920x690")
        self.root.minsize(800, 620)
        self.root.configure(background=PAPER)

        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        base_font = ("Yu Gothic UI", 10)
        bold_font = ("Yu Gothic UI", 10, "bold")
        style.configure(
            ".",
            font=base_font,
            background=PAPER,
            foreground=INK,
        )
        style.configure("TFrame", background=PAPER)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=PAPER, foreground=INK)
        style.configure("Card.TLabel", background=CARD, foreground=INK)
        style.configure(
            "Muted.TLabel",
            background=PAPER,
            foreground=STEEL,
            font=("Yu Gothic UI", 9, "bold"),
        )
        style.configure(
            "Section.TLabelframe",
            background=CARD,
            bordercolor=LINE,
            lightcolor=LINE,
            darkcolor=LINE,
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "Section.TLabelframe.Label",
            background=PAPER,
            foreground=INK,
            font=("Yu Gothic UI", 11, "bold"),
        )
        style.configure(
            "TEntry",
            fieldbackground=CARD,
            foreground=INK,
            insertcolor=INK,
            bordercolor=LINE,
            lightcolor=LINE,
            darkcolor=LINE,
            padding=7,
        )
        style.map(
            "TEntry",
            bordercolor=[("focus", VOLT)],
            lightcolor=[("focus", VOLT)],
            darkcolor=[("focus", VOLT)],
        )
        style.configure(
            "TCombobox",
            fieldbackground=CARD,
            foreground=INK,
            arrowcolor=INK,
            bordercolor=LINE,
            padding=6,
        )
        style.configure(
            "TSpinbox",
            fieldbackground=CARD,
            foreground=INK,
            arrowcolor=INK,
            bordercolor=LINE,
            padding=6,
        )
        style.configure(
            "Card.TCheckbutton",
            background=CARD,
            foreground=INK,
            font=bold_font,
            indicatorcolor=CARD,
            bordercolor=INK,
            padding=(2, 5),
        )
        style.map(
            "Card.TCheckbutton",
            background=[("active", CARD)],
            indicatorcolor=[("selected", INK), ("!selected", CARD)],
            foreground=[("disabled", STEEL)],
        )
        style.configure(
            "Treeview",
            background=CARD,
            fieldbackground=CARD,
            foreground=INK,
            bordercolor=LINE,
            lightcolor=LINE,
            darkcolor=LINE,
            rowheight=32,
            font=base_font,
        )
        style.map(
            "Treeview",
            background=[("selected", INK)],
            foreground=[("selected", HEAD)],
        )
        style.configure(
            "Treeview.Heading",
            background=HEAD,
            foreground=INK,
            bordercolor=INK,
            relief="flat",
            padding=(8, 8),
            font=bold_font,
        )
        style.map("Treeview.Heading", background=[("active", LINE)])

        header = tk.Frame(self.root, bg=HEAD, padx=20, pady=8)
        header.pack(fill="x")

        self.brand_mark_image: tk.PhotoImage | None = None
        if BRAND_MARK_PATH.exists():
            try:
                self.brand_mark_image = tk.PhotoImage(file=str(BRAND_MARK_PATH))
                self.root.iconphoto(True, self.brand_mark_image)
                tk.Label(
                    header,
                    image=self.brand_mark_image,
                    bg=HEAD,
                    bd=0,
                ).pack(side="left", padx=(0, 14))
            except tk.TclError:
                self.brand_mark_image = None

        header_titles = tk.Frame(header, bg=HEAD)
        header_titles.pack(side="left", fill="x", expand=True)
        tk.Label(
            header_titles,
            text=translate(self.language, APP_NAME),
            bg=HEAD,
            fg=INK,
            font=("Yu Gothic UI", 16, "bold"),
            anchor="w",
        ).pack(anchor="w")
        tk.Label(
            header_titles,
            text="FOREGROUND BUTTON CLICKER",
            bg=HEAD,
            fg=STEEL,
            font=("Yu Gothic UI", 9, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(1, 0))
        tk.Label(
            header,
            text=f"v{APP_VERSION}",
            bg=VOLT,
            fg=CREAM,
            padx=12,
            pady=5,
            font=("Consolas", 9, "bold"),
        ).pack(side="right")
        self.language_button = office_button(
            header,
            text="English" if self.language == "ja" else "日本語",
            command=self._toggle_language,
            width=10,
        )
        self.language_button.pack(side="right", padx=(0, 12))
        tk.Frame(self.root, bg=INK, height=3).pack(fill="x")

        outer = ttk.Frame(self.root, padding=(20, 12, 20, 8))
        outer.pack(fill="both", expand=True)

        heading = ttk.Label(
            outer,
            text="最前面ウィンドウのボタンを優先順位順に検出します",
            font=("Yu Gothic UI", 13, "bold"),
        )
        heading.pack(anchor="w")

        warning = tk.Label(
            outer,
            text=(
                "注意：［常に許可］は、今後の操作も確認なしで許可する場合があります。"
                "最初は「検出だけ」で確認してください。"
            ),
            bg=VOLT_DEEP,
            fg=CREAM,
            padx=14,
            pady=9,
            anchor="w",
            justify="left",
            wraplength=860,
            relief="flat",
            font=bold_font,
        )
        warning.pack(fill="x", pady=(10, 14))

        settings = ttk.LabelFrame(
            outer,
            text="監視設定",
            padding=12,
            style="Section.TLabelframe",
        )
        settings.pack(fill="x")
        settings.columnconfigure(1, weight=1)

        ttk.Label(
            settings,
            text="対象ウィンドウのタイトルを含む文字",
            style="Card.TLabel",
        ).grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=5
        )
        ttk.Entry(settings, textvariable=self.title_var).grid(
            row=0, column=1, sticky="ew", pady=5
        )
        ttk.Label(
            settings,
            text="空欄ならすべて（追跡時は取得候補を絞り込み）",
            style="Card.TLabel",
        ).grid(
            row=0, column=2, sticky="w", padx=(10, 0), pady=5
        )

        ttk.Label(
            settings,
            text="確認間隔［秒］",
            style="Card.TLabel",
        ).grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=5
        )
        ttk.Entry(settings, textvariable=self.interval_var, width=10).grid(
            row=1, column=1, sticky="w", pady=5
        )
        ttk.Label(
            settings,
            text="クリック後の待機［秒］",
            style="Card.TLabel",
        ).grid(
            row=1, column=2, sticky="e", padx=(10, 10), pady=5
        )
        ttk.Entry(settings, textvariable=self.cooldown_var, width=10).grid(
            row=1, column=3, sticky="w", pady=5
        )

        dry_run = ttk.Checkbutton(
            settings,
            text="検出だけ（クリックしない）",
            variable=self.dry_run_var,
            style="Card.TCheckbutton",
        )
        dry_run.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 2))

        self.tracking_check = ttk.Checkbutton(
            settings,
            text=(
                "ウィンドウ追跡モード"
                "（監視開始後、次に最前面にしたアプリを固定）"
            ),
            variable=self.tracking_mode_var,
            command=self._on_tracking_mode_changed,
            style="Card.TCheckbutton",
        )
        self.tracking_check.grid(
            row=3,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(4, 2),
        )

        ttk.Label(
            settings,
            text="追跡対象",
            style="Card.TLabel",
        ).grid(row=4, column=0, sticky="w", padx=(0, 10), pady=(4, 2))
        ttk.Entry(
            settings,
            textvariable=self.tracked_title_var,
            state="readonly",
        ).grid(
            row=4,
            column=1,
            columnspan=3,
            sticky="ew",
            pady=(4, 2),
        )
        self._on_tracking_mode_changed()

        rule_frame = ttk.LabelFrame(
            outer,
            text="登録ボタン",
            padding=12,
            style="Section.TLabelframe",
        )
        rule_frame.pack(fill="both", expand=True, pady=(14, 0))

        rule_buttons = ttk.Frame(rule_frame, style="Card.TFrame")
        rule_buttons.pack(fill="x", pady=(0, 10))
        office_button(
            rule_buttons,
            text="追加",
            command=self._add_rule,
            width=10,
        ).pack(side="left")
        office_button(
            rule_buttons,
            text="編集",
            command=self._edit_rule,
            width=10,
        ).pack(side="left", padx=(8, 0))
        office_button(
            rule_buttons,
            text="削除",
            command=self._delete_rule,
            palette="destructive",
            width=10,
        ).pack(side="left", padx=(8, 0))
        office_button(
            rule_buttons,
            text="一覧を表示",
            command=self._open_rule_list,
            width=12,
        ).pack(side="left", padx=(8, 0))
        office_button(
            rule_buttons,
            text="初期設定に戻す",
            command=self._restore_defaults,
            width=18 if self.language == "en" else 14,
        ).pack(side="right")

        columns = ("priority", "text", "match", "enabled")
        self.tree = ttk.Treeview(
            rule_frame,
            columns=columns,
            show="headings",
            height=4,
            selectmode="browse",
        )
        self.tree.heading(
            "priority", text=translate(self.language, "優先順位")
        )
        self.tree.heading(
            "text", text=translate(self.language, "ボタン文字")
        )
        self.tree.heading(
            "match", text=translate(self.language, "照合方法")
        )
        self.tree.heading("enabled", text=translate(self.language, "状態"))
        self.tree.column("priority", width=90, anchor="center", stretch=False)
        self.tree.column("text", width=320, anchor="w")
        self.tree.column("match", width=120, anchor="center", stretch=False)
        self.tree.column("enabled", width=90, anchor="center", stretch=False)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda _event: self._edit_rule())

        # Keep the primary controls outside the vertically flexible content.
        # On short displays, packing this row inside ``outer`` allowed the
        # parent frame to clip the lower half of the button labels.
        controls = ttk.Frame(
            self.root,
            padding=(20, 8, 20, 8),
        )
        controls.pack(
            fill="x",
            side="bottom",
            before=outer,
        )
        self.start_button = office_button(
            controls,
            text="監視を開始",
            command=self._start,
            palette="primary",
            width=18 if self.language == "en" else 12,
        )
        self.start_button.pack(side="left")
        self.stop_button = office_button(
            controls,
            text="停止",
            command=self._stop,
            palette="danger",
            width=10,
            state="disabled",
        )
        self.stop_button.pack(
            side="left",
            padx=(10, 0),
        )
        self.status_badge = tk.Label(
            controls,
            textvariable=self.status_var,
            bg=STEEL,
            fg=CREAM,
            padx=14,
            pady=7,
            font=bold_font,
        )
        self.status_badge.pack(
            side="right", padx=(12, 0)
        )
        ttk.Label(
            controls,
            text=translate(
                self.language,
                "5garashi.com設計事務所　|　Office Identity v4.6",
            ),
            style="Muted.TLabel",
        ).pack(side="right")

        log_frame = ttk.LabelFrame(
            outer,
            text="動作履歴",
            padding=8,
            style="Section.TLabelframe",
        )
        log_frame.pack(fill="both", expand=True, pady=(14, 0))
        self.log = tk.Text(
            log_frame,
            height=5,
            state="disabled",
            wrap="word",
            bg=CARD,
            fg=INK,
            insertbackground=INK,
            selectbackground=INK,
            selectforeground=HEAD,
            relief="flat",
            borderwidth=0,
            padx=8,
            pady=6,
            font=("Consolas", 9),
        )
        scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        self.log.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self._apply_language_to_widgets()

    def _apply_language_to_widgets(self) -> None:
        english_to_japanese = {
            english: japanese for japanese, english in TRANSLATIONS.items()
        }

        def visit(widget: tk.Misc) -> None:
            try:
                current = str(widget.cget("text"))
                original = english_to_japanese.get(current, current)
                localized = translate(self.language, original)
                if localized != current:
                    widget.configure(text=localized)
            except (tk.TclError, TypeError):
                pass
            for child in widget.winfo_children():
                visit(child)

        for child in self.root.winfo_children():
            visit(child)

    def _toggle_language(self) -> None:
        selected_language = "en" if self.language == "ja" else "ja"
        log_text = self.log.get("1.0", "end-1c")
        selected_rule = self.tree.selection()
        previous_status = self.status_var.get()
        previous_tracked_title = self.tracked_title_var.get()
        self.language = selected_language
        self._close_rule_list()
        for child in self.root.winfo_children():
            child.destroy()

        self._build_ui()
        self._refresh_rules()
        if selected_rule and self.tree.exists(selected_rule[0]):
            self.tree.selection_set(selected_rule[0])
        self.log.configure(state="normal")
        self.log.insert("end", log_text)
        self.log.configure(state="disabled")
        self.log.see("end")

        if self.running:
            self.tracking_check.configure(state="disabled")
            set_office_button_state(self.start_button, "disabled")
            set_office_button_state(self.stop_button, "normal")
            mode = translate(
                self.language,
                "検出だけ" if self.dry_run_var.get() else "自動クリック",
            )
            if previous_status.startswith(
                ("追跡対象を選択中", "追跡中", "Waiting to track", "Tracking")
            ):
                status_prefix = (
                    "Waiting to track"
                    if "選択中" in previous_status
                    or "Waiting to track" in previous_status
                    else "Tracking"
                ) if self.language == "en" else (
                    "追跡対象を選択中"
                    if "選択中" in previous_status
                    or "Waiting to track" in previous_status
                    else "追跡中"
                )
                self.status_var.set(f"{status_prefix}: {mode}")
            else:
                self.status_var.set(
                    f"{'Monitoring' if self.language == 'en' else '監視中'}: {mode}"
                )
            self.tracked_title_var.set(
                translate(self.language, previous_tracked_title)
            )
            self.status_badge.configure(bg=OK, fg=CREAM)
        else:
            self.status_var.set(translate(self.language, previous_status))
            self.tracked_title_var.set(
                translate(self.language, previous_tracked_title)
            )
            self.status_badge.configure(bg=STEEL, fg=CREAM)
        self._save_current_config()

    def _capture_self_hwnd(self) -> None:
        try:
            self.self_hwnd = int(self.root.winfo_id())
        except tk.TclError:
            self.self_hwnd = 0

    def _is_own_window(self, hwnd: int) -> bool:
        return bool(
            hwnd
            and (
                hwnd == self.self_hwnd
                or get_window_process_id(hwnd) == os.getpid()
            )
        )

    def _on_tracking_mode_changed(self) -> None:
        if self.running:
            return
        if self.tracking_mode_var.get():
            self.tracked_title_var.set(
                translate(
                    self.language,
                    "未選択（監視開始後、対象アプリを最前面にしてください）",
                )
            )
        else:
            self.tracked_title_var.set(
                translate(
                    self.language, "通常モード：最前面ウィンドウを監視"
                )
            )

    def _sorted_rules(self) -> list[Rule]:
        return sorted(self.rules, key=lambda item: (item.priority, item.text))

    def _refresh_rule_list_tree(self) -> None:
        if (
            self.rule_list_window is None
            or self.rule_list_tree is None
            or not self.rule_list_window.winfo_exists()
        ):
            return
        selected = self.rule_list_tree.selection()
        self.rule_list_tree.delete(*self.rule_list_tree.get_children())
        for index, rule in enumerate(self._sorted_rules()):
            self.rule_list_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    rule.priority,
                    rule.text,
                    match_label(rule.match, self.language),
                    translate(
                        self.language, "有効" if rule.enabled else "無効"
                    ),
                ),
            )
        if selected and self.rule_list_tree.exists(selected[0]):
            self.rule_list_tree.selection_set(selected[0])

    def _close_rule_list(self) -> None:
        if self.rule_list_window is not None and self.rule_list_window.winfo_exists():
            self.rule_list_window.destroy()
        self.rule_list_window = None
        self.rule_list_tree = None

    def _open_rule_list(self) -> None:
        if self.rule_list_window is not None and self.rule_list_window.winfo_exists():
            self.rule_list_window.deiconify()
            self.rule_list_window.lift()
            self.rule_list_window.focus_force()
            self._refresh_rule_list_tree()
            return

        window = tk.Toplevel(self.root)
        window.title(translate(self.language, "登録ボタン一覧"))
        window.geometry("760x420")
        window.minsize(680, 300)
        window.configure(background=PAPER)
        window.transient(self.root)
        window.protocol("WM_DELETE_WINDOW", self._close_rule_list)
        self.rule_list_window = window

        frame = ttk.Frame(window, padding=12)
        frame.pack(fill="both", expand=True)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        columns = ("priority", "text", "match", "enabled")
        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=12,
            selectmode="browse",
        )
        tree.heading("priority", text=translate(self.language, "優先順位"))
        tree.heading("text", text=translate(self.language, "ボタン文字"))
        tree.heading("match", text=translate(self.language, "照合方法"))
        tree.heading("enabled", text=translate(self.language, "状態"))
        tree.column("priority", width=90, anchor="center", stretch=False)
        tree.column("text", width=420, anchor="w")
        tree.column("match", width=120, anchor="center", stretch=False)
        tree.column("enabled", width=90, anchor="center", stretch=False)
        tree.grid(row=0, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")

        footer = ttk.Frame(frame)
        footer.grid(row=1, column=0, columnspan=2, sticky="e", pady=(10, 0))
        office_button(
            footer,
            text=translate(self.language, "閉じる"),
            command=self._close_rule_list,
            width=10,
        ).pack(side="right")

        self.rule_list_tree = tree
        self._refresh_rule_list_tree()

    def _refresh_rules(self) -> None:
        self.tree.heading(
            "priority", text=translate(self.language, "優先順位")
        )
        self.tree.heading(
            "text", text=translate(self.language, "ボタン文字")
        )
        self.tree.heading(
            "match", text=translate(self.language, "照合方法")
        )
        self.tree.heading("enabled", text=translate(self.language, "状態"))
        selected = self.tree.selection()
        self.tree.delete(*self.tree.get_children())
        for index, rule in enumerate(self._sorted_rules()):
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    rule.priority,
                    rule.text,
                    match_label(rule.match, self.language),
                    translate(
                        self.language, "有効" if rule.enabled else "無効"
                    ),
                ),
            )
        if selected and self.tree.exists(selected[0]):
            self.tree.selection_set(selected[0])
        self._refresh_rule_list_tree()

    def _selected_rule(self) -> tuple[int, Rule] | None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(
                translate(self.language, "選択してください"),
                translate(self.language, "対象の行を選択してください。"),
            )
            return None
        sorted_rules = self._sorted_rules()
        index = int(selected[0])
        return index, sorted_rules[index]

    def _add_rule(self) -> None:
        dialog = RuleDialog(
            self.root, "ボタンを追加", language=self.language
        )
        self.root.wait_window(dialog)
        if dialog.result:
            self.rules.append(dialog.result)
            self._refresh_rules()
            self._save_current_config()

    def _edit_rule(self) -> None:
        selected = self._selected_rule()
        if not selected:
            return
        _index, old_rule = selected
        dialog = RuleDialog(
            self.root, "ボタンを編集", old_rule, language=self.language
        )
        self.root.wait_window(dialog)
        if dialog.result:
            original_index = self.rules.index(old_rule)
            self.rules[original_index] = dialog.result
            self._refresh_rules()
            self._save_current_config()

    def _delete_rule(self) -> None:
        selected = self._selected_rule()
        if not selected:
            return
        _index, rule = selected
        if not messagebox.askyesno(
            translate(self.language, "削除の確認"),
            translate(self.language, "「{text}」を削除しますか？").format(
                text=rule.text
            ),
        ):
            return
        self.rules.remove(rule)
        self._refresh_rules()
        self._save_current_config()

    def _restore_defaults(self) -> None:
        if not messagebox.askyesno(
            translate(self.language, "初期設定に戻す"),
            translate(
                self.language,
                "登録ボタンを「常に許可」「一度だけ許可」に戻しますか？",
            ),
        ):
            return
        self.rules = [
            Rule.from_dict(item) for item in DEFAULT_CONFIG["rules"]
        ]
        self._refresh_rules()
        self._save_current_config()

    def _validated_settings(self) -> tuple[float, float] | None:
        try:
            interval = float(self.interval_var.get())
            cooldown = float(self.cooldown_var.get())
        except ValueError:
            messagebox.showerror(
                translate(self.language, "入力エラー"),
                translate(
                    self.language,
                    "確認間隔とクリック後の待機は数値で入力してください。",
                ),
            )
            return None
        if not 0.2 <= interval <= 60:
            messagebox.showerror(
                translate(self.language, "入力エラー"),
                translate(
                    self.language,
                    "確認間隔は0.2～60秒で入力してください。",
                ),
            )
            return None
        if not 0.5 <= cooldown <= 600:
            messagebox.showerror(
                translate(self.language, "入力エラー"),
                translate(
                    self.language,
                    "クリック後の待機は0.5～600秒で入力してください。",
                ),
            )
            return None
        if not any(rule.enabled and rule.text for rule in self.rules):
            messagebox.showerror(
                translate(self.language, "設定エラー"),
                translate(
                    self.language, "有効なボタンを1件以上登録してください。"
                ),
            )
            return None
        return interval, cooldown

    def _current_config(self) -> dict[str, Any]:
        try:
            interval = float(self.interval_var.get())
        except ValueError:
            interval = 0.5
        try:
            cooldown = float(self.cooldown_var.get())
        except ValueError:
            cooldown = 2.0
        return {
            "title_contains": self.title_var.get().strip(),
            "interval_seconds": interval,
            "cooldown_seconds": cooldown,
            "dry_run": self.dry_run_var.get(),
            "tracking_mode": self.tracking_mode_var.get(),
            "language": self.language,
            "rules": [
                asdict(rule)
                for rule in sorted(
                    self.rules, key=lambda item: (item.priority, item.text)
                )
            ],
        }

    def _save_current_config(self) -> None:
        try:
            save_config(self._current_config())
        except OSError as error:
            self._append_log(
                f"Could not save settings: {error}"
                if self.language == "en"
                else f"設定を保存できませんでした: {error}"
            )

    def _start(self) -> None:
        if self.running:
            return
        validated = self._validated_settings()
        if validated is None:
            return
        if os.name != "nt":
            messagebox.showerror(
                translate(self.language, "Windows専用"),
                translate(
                    self.language,
                    "このプログラムはWindows 10／11専用です。",
                ),
            )
            return
        try:
            import uiautomation  # noqa: F401
        except ImportError:
            messagebox.showerror(
                translate(self.language, "必要な機能がありません"),
                translate(
                    self.language,
                    "uiautomationがインストールされていません。\n"
                    "「install_and_run.bat」から起動してください。",
                ),
            )
            return

        interval, cooldown = validated
        snapshot = {
            "title_contains": self.title_var.get().strip(),
            "interval": interval,
            "cooldown": cooldown,
            "dry_run": self.dry_run_var.get(),
            "tracking_mode": self.tracking_mode_var.get(),
            "rules": sorted(
                [
                    Rule(
                        priority=rule.priority,
                        text=rule.text,
                        match=rule.match,
                        enabled=rule.enabled,
                    )
                    for rule in self.rules
                    if rule.enabled and rule.text
                ],
                key=lambda item: (item.priority, item.text),
            ),
        }
        self._save_current_config()
        self.stop_event.clear()
        self.running = True
        self.tracking_check.configure(state="disabled")
        set_office_button_state(self.start_button, "disabled")
        set_office_button_state(self.stop_button, "normal")
        mode = translate(
            self.language,
            "検出だけ" if snapshot["dry_run"] else "自動クリック",
        )
        if snapshot["tracking_mode"]:
            self.status_var.set(
                f"{'Waiting to track' if self.language == 'en' else '追跡対象を選択中'}: {mode}"
            )
            self.tracked_title_var.set(
                translate(
                    self.language,
                    "選択待ち：対象アプリを最前面にしてください",
                )
            )
            guidance = (
                f"Monitoring started ({mode}, window tracking). "
                "Bring the target app to the foreground."
                if self.language == "en"
                else (
                    f"監視を開始しました（{mode}／ウィンドウ追跡モード）。"
                    "次に対象アプリを最前面にしてください。"
                )
            )
        else:
            self.status_var.set(
                f"{'Monitoring' if self.language == 'en' else '監視中'}: {mode}"
            )
            self.tracked_title_var.set(
                translate(self.language, "通常モード：最前面ウィンドウを監視")
            )
            guidance = (
                f"Monitoring started ({mode}). Bring the target window to the foreground."
                if self.language == "en"
                else f"監視を開始しました（{mode}）。対象画面を最前面にしてください。"
            )
        self.status_badge.configure(bg=OK, fg=CREAM)
        self._append_log(guidance)
        self.worker = threading.Thread(
            target=self._monitor,
            args=(snapshot,),
            daemon=True,
            name="foreground-button-monitor",
        )
        self.worker.start()

    def _stop(self) -> None:
        if not self.running:
            return
        self.stop_event.set()
        self.running = False
        self.tracking_check.configure(state="normal")
        set_office_button_state(self.start_button, "normal")
        set_office_button_state(self.stop_button, "disabled")
        self.status_var.set(translate(self.language, "停止中"))
        self.status_badge.configure(bg=STEEL, fg=CREAM)
        self._append_log(
            "Monitoring stopped."
            if self.language == "en"
            else "監視を停止しました。"
        )

    def _monitor(self, settings: dict[str, Any]) -> None:
        import uiautomation as auto

        last_action_at = 0.0
        last_report_signature = ""
        last_report_at = 0.0
        scan_number = 0
        highest_priority = min(rule.priority for rule in settings["rules"])
        title_filter = normalize_text(settings["title_contains"])
        tracked_hwnd = 0
        tracked_title = ""
        selection_candidate_hwnd = 0
        selection_candidate_count = 0

        try:
            with auto.UIAutomationInitializerInThread():
                while not self.stop_event.wait(settings["interval"]):
                    try:
                        foreground_hwnd = get_foreground_window()
                        if settings["tracking_mode"]:
                            if not tracked_hwnd:
                                if (
                                    not foreground_hwnd
                                    or self._is_own_window(foreground_hwnd)
                                ):
                                    selection_candidate_hwnd = 0
                                    selection_candidate_count = 0
                                    continue
                                candidate_title = get_window_title(
                                    foreground_hwnd
                                )
                                if (
                                    not candidate_title
                                    or (
                                        title_filter
                                        and title_filter
                                        not in normalize_text(candidate_title)
                                    )
                                ):
                                    selection_candidate_hwnd = 0
                                    selection_candidate_count = 0
                                    continue
                                if foreground_hwnd == selection_candidate_hwnd:
                                    selection_candidate_count += 1
                                else:
                                    selection_candidate_hwnd = foreground_hwnd
                                    selection_candidate_count = 1
                                # Require two consecutive observations so that
                                # a transient taskbar or switcher window is not
                                # accidentally fixed as the tracking target.
                                if selection_candidate_count < 2:
                                    continue
                                tracked_hwnd = foreground_hwnd
                                tracked_title = candidate_title
                                self.events.put(
                                    (
                                        "tracked_window",
                                        {
                                            "hwnd": tracked_hwnd,
                                            "title": tracked_title,
                                        },
                                    )
                                )
                                self.events.put(
                                    (
                                        "log",
                                        (
                                            f"Tracking target locked: “{tracked_title}” "
                                            f"(HWND: 0x{tracked_hwnd:X})"
                                            if self.language == "en"
                                            else (
                                                "追跡対象を固定しました："
                                                f"「{tracked_title}」"
                                                f"（HWND: 0x{tracked_hwnd:X}）"
                                            )
                                        ),
                                    )
                                )

                            hwnd = tracked_hwnd
                            if not is_window(hwnd):
                                self.events.put(
                                    (
                                        "tracked_window_lost",
                                        tracked_title,
                                    )
                                )
                                break
                            current_title = get_window_title(hwnd)
                            if current_title and current_title != tracked_title:
                                tracked_title = current_title
                                self.events.put(
                                    (
                                        "tracked_window",
                                        {
                                            "hwnd": tracked_hwnd,
                                            "title": tracked_title,
                                        },
                                    )
                                )
                            title = tracked_title
                        else:
                            hwnd = foreground_hwnd
                            if not hwnd or self._is_own_window(hwnd):
                                continue
                            title = get_window_title(hwnd)
                            if (
                                title_filter
                                and title_filter not in normalize_text(title)
                            ):
                                continue

                        scan_number += 1
                        scan_started = time.monotonic()
                        if scan_number == 1:
                            window_kind = (
                                (
                                    "tracked window"
                                    if settings["tracking_mode"]
                                    else "foreground window"
                                )
                                if self.language == "en"
                                else (
                                    "追跡画面"
                                    if settings["tracking_mode"]
                                    else "最前面画面"
                                )
                            )
                            self.events.put(
                                (
                                    "log",
                                    (
                                        f"Scanning {window_kind} “{title}” "
                                        "(including non-button text elements)."
                                        if self.language == "en"
                                        else (
                                            f"解析開始：{window_kind}「{title}」"
                                            "（ボタン以外の文字要素も対象）"
                                        )
                                    ),
                                )
                            )

                        window = auto.ControlFromHandle(hwnd)
                        candidate: tuple[Rule, Any, str, str] | None = None
                        scanned_count = 0
                        named_count = 0

                        try:
                            controls = auto.WalkControl(
                                window,
                                includeTop=True,
                                maxDepth=80,
                            )
                            for control, _depth in controls:
                                if self.stop_event.is_set():
                                    break
                                scanned_count += 1
                                try:
                                    name = control.Name or ""
                                except Exception:
                                    continue
                                if not name:
                                    continue
                                named_count += 1

                                for rule in settings["rules"]:
                                    if text_matches(name, rule):
                                        try:
                                            control_type = control.ControlTypeName
                                        except Exception:
                                            control_type = type(control).__name__
                                        if (
                                            candidate is None
                                            or rule.priority
                                            < candidate[0].priority
                                        ):
                                            candidate = (
                                                rule,
                                                control,
                                                name,
                                                str(control_type),
                                            )
                                        break

                                if (
                                    candidate is not None
                                    and candidate[0].priority == highest_priority
                                ):
                                    break
                        except Exception as scan_error:
                            self.events.put(
                                (
                                    "log",
                                    (
                                        f"UI scan error: {type(scan_error).__name__}: "
                                        f"{scan_error}"
                                        if self.language == "en"
                                        else (
                                            f"UI解析エラー：{type(scan_error).__name__}: "
                                            f"{scan_error}"
                                        )
                                    ),
                                )
                            )
                            self.stop_event.wait(1.0)
                            continue

                        scan_elapsed = time.monotonic() - scan_started
                        now = time.monotonic()

                        if candidate is None:
                            if now - last_report_at >= 5.0:
                                self.events.put(
                                    (
                                        "log",
                                        (
                                            f"Monitoring: scan {scan_number}, checked "
                                            f"{scanned_count} elements ({named_count} "
                                            f"with text) in {scan_elapsed:.1f}s; no match "
                                            f"on “{title}”."
                                            if self.language == "en"
                                            else (
                                                f"監視動作中：解析{scan_number}回目、"
                                                f"{scanned_count}要素"
                                                f"（文字あり{named_count}）を"
                                                f"{scan_elapsed:.1f}秒で確認／一致なし"
                                                f"／画面「{title}」"
                                            )
                                        ),
                                    )
                                )
                                last_report_at = now
                            continue

                        rule, control, actual_name, control_type = candidate
                        signature = (
                            f"{hwnd}|{rule.priority}|{normalize_text(actual_name)}"
                        )

                        if settings["dry_run"]:
                            if (
                                signature != last_report_signature
                                or now - last_report_at >= 3.0
                            ):
                                self.events.put(
                                    (
                                        "log",
                                        (
                                            f"Detected: priority {rule.priority}, "
                                            f"“{actual_name}” (type: {control_type}) "
                                            f"on “{title}”."
                                            if self.language == "en"
                                            else (
                                                f"検出：優先度{rule.priority} "
                                                f"「{actual_name}」"
                                                f"（種類：{control_type}）"
                                                f"／画面「{title}」"
                                            )
                                        ),
                                    )
                                )
                                last_report_signature = signature
                                last_report_at = now
                            continue

                        if now - last_action_at < settings["cooldown"]:
                            continue
                        target_is_foreground = (
                            get_foreground_window() == hwnd
                        )
                        if (
                            not settings["tracking_mode"]
                            and not target_is_foreground
                        ):
                            self.events.put(
                                (
                                    "log",
                                    (
                                        "Cancelled because the foreground window changed "
                                        "before clicking."
                                        if self.language == "en"
                                        else (
                                            "クリック直前に最前面画面が変わったため"
                                            "中止しました。"
                                        )
                                    ),
                                )
                            )
                            continue

                        try:
                            try:
                                control.GetInvokePattern().Invoke(waitTime=0.1)
                                click_method = "Invoke"
                            except Exception as invoke_error:
                                if (
                                    settings["tracking_mode"]
                                    and not target_is_foreground
                                ):
                                    if now - last_report_at >= 5.0:
                                        self.events.put(
                                            (
                                                "log",
                                                (
                                                    f"Background action cancelled: "
                                                    f"“{actual_name}” does not support "
                                                    "Invoke. Coordinate clicking was not "
                                                    "attempted to avoid clicking another "
                                                    f"window. ({type(invoke_error).__name__})"
                                                    if self.language == "en"
                                                    else (
                                                        "背面操作を中止："
                                                        f"「{actual_name}」はInvoke非対応です。"
                                                        "手前の別画面を誤クリックしないため、"
                                                        "座標クリックは行いません。"
                                                        f"（{type(invoke_error).__name__}）"
                                                    )
                                                ),
                                            )
                                        )
                                        last_report_at = now
                                    continue
                                if get_foreground_window() != hwnd:
                                    self.events.put(
                                        (
                                            "log",
                                            (
                                                "Cancelled because the target window lost "
                                                "the foreground before coordinate clicking."
                                                if self.language == "en"
                                                else (
                                                    "座標クリック直前に対象画面が"
                                                    "最前面でなくなったため中止しました。"
                                                )
                                            ),
                                        )
                                    )
                                    continue
                                control.Click(waitTime=0.1)
                                click_method = "Click"
                        except Exception as click_error:
                            self.events.put(
                                (
                                    "log",
                                    (
                                        f"Click failed: {type(click_error).__name__}: "
                                        f"{click_error}"
                                        if self.language == "en"
                                        else (
                                            f"クリック失敗：{type(click_error).__name__}: "
                                            f"{click_error}"
                                        )
                                    ),
                                )
                            )
                            continue

                        last_action_at = time.monotonic()
                        self.events.put(
                            (
                                "log",
                                (
                                    f"Clicked: priority {rule.priority}, "
                                    f"“{actual_name}” (type: {control_type}, "
                                    f"method: {click_method}) on “{title}”."
                                    if self.language == "en"
                                    else (
                                        f"クリック：優先度{rule.priority} "
                                        f"「{actual_name}」"
                                        f"（種類：{control_type}）"
                                        f"／方式：{click_method}"
                                        f"／画面「{title}」"
                                    )
                                ),
                            )
                        )
                    except Exception as error:
                        self.events.put(
                            (
                                "log",
                                (
                                    f"Temporary error while scanning the window: "
                                    f"{type(error).__name__}: {error}"
                                    if self.language == "en"
                                    else (
                                        f"画面の確認中に一時的なエラー: "
                                        f"{type(error).__name__}: {error}"
                                    )
                                ),
                            )
                        )
                        self.stop_event.wait(max(1.0, settings["interval"]))
        except Exception:
            self.events.put(("fatal", traceback.format_exc()))
        finally:
            self.events.put(("stopped", None))

    def _process_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "log":
                    self._append_log(str(payload))
                elif event == "tracked_window":
                    title = str(
                        payload.get("title", translate(self.language, "（タイトルなし）"))
                    )
                    self.tracked_title_var.set(title)
                    mode = translate(
                        self.language,
                        "検出だけ" if self.dry_run_var.get() else "自動クリック",
                    )
                    self.status_var.set(
                        f"{'Tracking' if self.language == 'en' else '追跡中'}: {mode}"
                    )
                elif event == "tracked_window_lost":
                    title = str(payload)
                    self.tracked_title_var.set(
                        (
                            f"Target window closed: {title}"
                            if self.language == "en"
                            else f"対象が閉じられました：{title}"
                        )
                    )
                    self._append_log(
                        (
                            f"Stopping because the tracked window was closed: "
                            f"“{title}”."
                            if self.language == "en"
                            else (
                                f"追跡対象のウィンドウが閉じられたため停止します："
                                f"「{title}」"
                            )
                        )
                    )
                elif event == "fatal":
                    fatal_message = (
                        "Monitoring could not continue."
                        if self.language == "en"
                        else "監視処理を継続できませんでした。"
                    )
                    self._append_log(fatal_message)
                    messagebox.showerror(
                        "Monitoring error" if self.language == "en" else "監視エラー",
                        (
                            fatal_message
                            + "\n\n"
                            + str(payload)[-2000:]
                        ),
                    )
                    self._set_stopped_state()
                elif event == "stopped" and self.running:
                    self._set_stopped_state()
        except queue.Empty:
            pass
        try:
            self.root.after(100, self._process_events)
        except tk.TclError:
            pass

    def _set_stopped_state(self) -> None:
        self.running = False
        self.tracking_check.configure(state="normal")
        set_office_button_state(self.start_button, "normal")
        set_office_button_state(self.stop_button, "disabled")
        self.status_var.set(translate(self.language, "停止中"))
        self.status_badge.configure(bg=STEEL, fg=CREAM)

    def _append_log(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self.log.configure(state="normal")
        self.log.insert("end", f"[{timestamp}] {message}\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        try:
            with RUNTIME_LOG_PATH.open("a", encoding="utf-8") as stream:
                stream.write(f"[{timestamp}] {message}\n")
        except OSError:
            pass

    def _on_close(self) -> None:
        self.stop_event.set()
        self._close_rule_list()
        self._save_current_config()
        self.root.destroy()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Foreground Button Clicker / 最前面ボタン自動クリック"
    )
    parser.add_argument(
        "--language",
        choices=("ja", "en"),
        default=None,
        help="Startup language: ja (Japanese) or en (English).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {APP_VERSION}",
    )
    args = parser.parse_args(argv)
    root = tk.Tk()
    ButtonClickerApp(root, language_override=args.language)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
