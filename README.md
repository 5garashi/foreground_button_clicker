<!--
File: README.md
Summary: Japanese and English usage guide for Foreground Button Clicker.
Author: 5garashi.com設計事務所 / 5garashi.com Design Office
Created: 2026-07-24
License: Not specified
SPDX-License-Identifier: NOASSERTION
-->

# 最前面ボタン自動クリック / Foreground Button Clicker v1.3.0

## 日本語

Windows 10／11で、最前面ウィンドウまたは固定した追跡対象ウィンドウから
登録した文字に一致するUI要素を検出し、優先順位に従ってクリックするプログラムです。
初期設定では、クリック前に「検出だけ」で動作を確認できます。

### 起動方法

1. ZIPファイルを右クリックして［すべて展開］します。ZIP内から直接起動しないでください。
2. `START_BUTTON_CLICKER.cmd` をダブルクリックします。
3. 初回だけ、必要なPythonライブラリがインストールされます。
4. 画面で表示言語を選び、［監視を開始］を押します。

Python 3が必要です。PythonがPATHに登録されていない場合は、Pythonをインストールしてから
再度起動してください。

### 起動時の言語指定

コマンドプロンプトから起動スクリプトに言語を渡すと、その起動だけ表示言語を指定できます。

```text
START_BUTTON_CLICKER.cmd --language ja
START_BUTTON_CLICKER.cmd --language en
```

Pythonを直接実行する場合も同じオプションを使えます。

```text
py -3 foreground_button_clicker.py --language ja
py -3 foreground_button_clicker.py --language en
```

`ja` は日本語、`en` は英語です。指定を省略すると、設定ファイルに保存された言語で起動します。
起動オプションは保存済み言語より優先され、終了時に選択言語として保存されます。
画面上の切替ボタンも設定言語を更新します。
バージョンは `py -3 foreground_button_clicker.py --version` で確認できます。

### 画面の言語切替

画面右上のボタンには、現在の表示言語とは反対の言語名が表示されます。
日本語表示中は［English］、英語表示中は［日本語］を押して切り替えます。

### 最初の動作確認

1. 初期設定の［検出だけ（クリックしない）］を有効にしたまま監視を開始します。
2. 対象の確認画面を最前面にします。
3. 動作履歴に検出結果が表示されることを確認します。
4. 監視を停止し、必要な場合だけ検出専用設定を解除して再開します。

### ウィンドウ追跡モード

1. ［ウィンドウ追跡モード］を有効にして監視を開始します。
2. 対象アプリを最前面にします。同じウィンドウが連続して確認されると追跡対象に固定されます。
3. 固定後は、対象アプリが背面にあっても、そのウィンドウだけを監視します。

対象を変更するには監視を停止し、再度開始して別のウィンドウを選択します。
追跡対象を閉じると監視は停止します。

### 設定

- 対象ウィンドウのタイトルを含む文字：空欄ならすべての候補が対象です。入力するとタイトルで絞り込みます。
- 確認間隔：監視する間隔です。初期値は0.5秒です。
- クリック後の待機：同じ画面への連続クリックを抑えます。初期値は2秒です。
- 登録ボタン：追加、編集、削除ができます。優先順位の数字が小さいルールから照合します。
- 照合方法：
  - 完全一致：ボタン名全体が登録文字と一致する場合に照合します。
  - 前方一致：ボタン名が登録文字から始まる場合に照合します。
  - 部分一致：ボタン名に登録文字が含まれる場合に照合します。

設定は `button_clicker_config.json` に自動保存されます。
画面上で言語を切り替えると、`language` に `ja` または `en` が保存されます。
起動時の `--language` オプションはその起動時の表示言語を指定します。

### 安全上の注意

「常に許可」などのボタンを自動クリックすると、後続の操作も確認なしに許可される場合があります。
まず検出専用で動作を確認し、対象ウィンドウを必要に応じて限定してください。
使わないときは監視を停止し、信頼できる操作に限って使用してください。

追跡対象が背面にある場合はWindows UI AutomationのInvoke操作だけを使います。
対象ボタンがInvokeに対応しない場合は座標クリックへ切り替えず、操作を中止します。
この動作により、手前にある別のウィンドウを誤クリックしないようにします。

### 検出できない場合・起動しない場合

このプログラムはWindows UI Automationが公開するUI要素の名前を読み取ります。
独自描画などにより名前が公開されない要素は検出できません。
対象画面が最前面か、監視中か、ウィンドウタイトル条件が厳しすぎないか、
対象アプリと同じ実行権限で起動しているかを確認してください。

起動に失敗した場合は、ZIPを展開したこと、`foreground_button_clicker.py` と
`requirements.txt` があることを確認してください。起動ログは `startup_log.txt`、
監視の履歴は `runtime_log.txt` に記録されます。

### 対応範囲

- Windows 10／11
- Windows UI Automationに対応するWindowsアプリとブラウザー画面

## English

Foreground Button Clicker detects UI elements whose names match your rules in the
foreground window or a pinned tracking window, then clicks the highest-priority match.
It runs on Windows 10 and Windows 11. Use “Detect only” first to verify matches without clicking.

### Starting the program

1. Right-click the ZIP file and select **Extract All**. Do not run the program from inside the ZIP.
2. Double-click `START_BUTTON_CLICKER.cmd`.
3. Required Python libraries are installed on the first launch.
4. Choose the display language and select **Start monitoring**.

Python 3 is required. If Python is not available on PATH, install Python and start the program again.

### Choose the startup language

Pass a language option to the startup script from Command Prompt to choose the interface language
for that launch:

```text
START_BUTTON_CLICKER.cmd --language ja
START_BUTTON_CLICKER.cmd --language en
```

The same option is available when running Python directly:

```text
py -3 foreground_button_clicker.py --language ja
py -3 foreground_button_clicker.py --language en
```

Use `ja` for Japanese or `en` for English. If you omit the option, the program uses the language
saved in its configuration file. The command-line choice takes precedence over the saved language
and is saved as the preference when the program exits. The on-screen language button also updates
the saved preference.
Check the version with `py -3 foreground_button_clicker.py --version`.

### Switch the interface language

The button in the upper-right corner displays the language opposite to the current interface.
When the interface is in Japanese, select **English**. When it is in English, select **日本語**.

### First-run check

1. Start monitoring with **Detect only (do not click)** enabled.
2. Bring the target confirmation window to the foreground.
3. Confirm that a detection result appears in the activity log.
4. Stop monitoring. Disable detection-only mode and restart only if clicking is required.

### Track a window

1. Enable **Track a window** and start monitoring.
2. Bring the target app to the foreground. The program pins it after observing the same window consecutively.
3. Once pinned, the program monitors only that window, even when it is behind another window.

To change the target, stop monitoring and start again before selecting another window.
Monitoring stops if the tracked window closes.

### Settings

- **Text contained in the window title:** Leave blank to consider all candidate windows, or enter text to filter by title.
- **Scan interval:** Time between scans; the default is 0.5 seconds.
- **Cooldown after click:** Prevents repeated clicks on the same screen; the default is 2 seconds.
- **Button rules:** Add, edit, or delete rules. Rules with smaller priority numbers are checked first.
- **Match method:**
  - **Exact:** The entire UI element name must match the rule text.
  - **Starts with:** The UI element name must begin with the rule text.
  - **Contains:** The UI element name must contain the rule text.

Settings are saved automatically to `button_clicker_config.json`.
Changing the interface language stores `ja` or `en` in the `language` setting.
The startup `--language` option chooses the interface language for that launch.

### Safety

Automatically clicking buttons such as “Always allow” may authorize later actions without confirmation.
Verify matches in detection-only mode first and, when appropriate, restrict the target window.
Stop monitoring when it is not needed, and use automatic clicking only for trusted actions.

When the tracked window is in the background, the program uses only the Windows UI Automation
Invoke operation. If a target button does not support Invoke, the program stops that action instead
of switching to coordinate clicking. This avoids accidentally clicking a different foreground window.

### Troubleshooting

The program reads UI element names exposed through Windows UI Automation. Elements with names hidden
by custom drawing cannot be detected. Check that the target window is in the foreground, monitoring
is running, the title filter is not too restrictive, and the program has the same execution privileges
as the target app.

If startup fails, confirm that the ZIP was extracted and that `foreground_button_clicker.py` and
`requirements.txt` are present. Startup details are written to `startup_log.txt`; monitoring events
are written to `runtime_log.txt`.

### Supported environment

- Windows 10 and Windows 11
- Windows applications and browser windows that expose controls through Windows UI Automation

---

**作成者 / Author**: 5garashi.com設計事務所 / 5garashi.com Design Office

**最終更新 / Last updated**: 2026-10-10 JST
