#!/usr/bin/env python3
"""檢查作業 Repo 的結構是否符合課程規範。只讀取,不會修改任何檔案。

用法::

    python tools/check_structure.py            # 檢查所有 hwNN 資料夾
    python tools/check_structure.py hw01 hw02  # 只檢查指定的作業

只需要 Python 3.9 以上,不需要安裝任何套件。有任何 FAIL 時退出碼為 1。
規範全文見課程網站的「作業說明」。
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HW_RE = re.compile(r"^hw\d{2}$")
BAD_HW_RE = re.compile(r"^hw[_\-\s]?\d+$", re.IGNORECASE)  # 看起來像作業資料夾但命名不對
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".ipynb_checkpoints", ".idea", ".vscode"}

WARN_MB, FAIL_MB = 5, 25
BIG_EXTS = {".pt", ".pth", ".ckpt", ".h5", ".onnx", ".safetensors", ".zip", ".tar", ".gz", ".7z", ".rar",
            ".mp4", ".avi", ".mov", ".mkv"}
TEXT_EXTS = {".py", ".md", ".txt", ".json", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".ipynb", ".csv", ".sh", ".env"}
SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]
AI_HEADING = re.compile(r"^#{1,6}\s*.*AI\s*使用聲明", re.MULTILINE)
IMG_LINK = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")

results: list[tuple[str, str, str]] = []  # (level, 範圍, 訊息)


def add(level: str, scope: str, msg: str) -> None:
    results.append((level, scope, msg))


def tracked_files() -> list[Path]:
    """優先使用 git 追蹤的檔案(等同會被推送的內容);沒有 git 時改為走訪資料夾。"""
    try:
        out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                             cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace", timeout=20)
        if out.returncode == 0 and out.stdout:
            return [ROOT / p for p in out.stdout.split("\0") if p and (ROOT / p).is_file()]
    except (OSError, subprocess.TimeoutExpired):
        pass
    files = []
    for p in ROOT.rglob("*"):
        if p.is_file() and not (set(p.relative_to(ROOT).parts) & SKIP_DIRS):
            files.append(p)
    return files


def check_root(all_files: list[Path]) -> None:
    if not (ROOT / "README.md").is_file():
        add("FAIL", "根目錄", "缺少 README.md")
    for d in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name not in SKIP_DIRS):
        if BAD_HW_RE.match(d.name) and not HW_RE.match(d.name):
            add("FAIL", d.name, "資料夾命名不符,請改為小寫兩位數,例如 hw01")
    for f in all_files:
        rel = f.relative_to(ROOT)
        if f.name == ".env" or (f.name.startswith(".env.") and f.name != ".env.example"):
            add("FAIL", str(rel), "不要把 .env 之類的私密設定放進 Repo")
        mb = f.stat().st_size / (1024 * 1024)
        if mb >= FAIL_MB:
            add("FAIL", str(rel), f"檔案太大({mb:.1f} MB),請改用下載腳本或縮小")
        elif mb >= WARN_MB or f.suffix.lower() in BIG_EXTS:
            add("WARN", str(rel), f"檔案偏大或屬於大型檔案類型({mb:.1f} MB),請確認是否必要")
        if f.suffix.lower() in TEXT_EXTS and f.stat().st_size < 2 * 1024 * 1024:
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if any(p.search(text) for p in SECRET_PATTERNS):
                add("FAIL", str(rel), "疑似含有金鑰或 Token,請移除並立刻到對應服務撤銷該金鑰")


def check_hw(name: str) -> None:
    hw = ROOT / name
    if not hw.is_dir():
        add("FAIL", name, "找不到這個作業資料夾")
        return
    report = hw / "report.md"
    if not report.is_file():
        add("FAIL", name, "缺少 report.md")
    else:
        text = report.read_text(encoding="utf-8", errors="ignore")
        if not AI_HEADING.search(text):
            add("FAIL", f"{name}/report.md", "缺少「AI 使用聲明」標題(沒有使用也要寫)")
        # 忽略程式碼區塊與行內程式碼裡的範例語法(例如說明文字中的 `![說明](路徑)`)
        scan = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        scan = re.sub(r"`[^`\n]*`", "", scan)
        for link in IMG_LINK.findall(scan):
            if re.match(r"^(https?:|data:)", link):
                continue
            if re.match(r"^([A-Za-z]:[\\/]|/|file:)", link):
                add("FAIL", f"{name}/report.md", f"圖片使用絕對路徑,請改為相對路徑:{link}")
            elif not (report.parent / link.split("#")[0]).exists():
                add("FAIL", f"{name}/report.md", f"找不到圖片檔:{link}")
    code = hw / "code"
    if not code.is_dir() or not any(p.is_file() for p in code.rglob("*")):
        add("FAIL", name, "缺少 code/ 或其中沒有檔案")
    if not ((hw / "requirements.txt").is_file() or (code / "requirements.txt").is_file()):
        add("WARN", name, "沒有 requirements.txt(每個作業資料夾必須自給自足,請列出需要的套件)")
    if not ((code / "README.md").is_file() or (hw / "README.md").is_file()):
        add("WARN", name, "沒有執行說明(請在 code/README.md 寫明如何重現結果)")
    # 提交標籤(僅提示)
    try:
        tag = f"{name}-submit"
        out = subprocess.run(["git", "tag", "-l", tag], cwd=ROOT, capture_output=True,
                             encoding="utf-8", errors="replace", timeout=20)
        if out.returncode == 0:
            add("INFO", name, f"標籤 {tag} " + ("已建立" if out.stdout.strip() else "尚未建立(完成後記得打標籤並推送)"))
    except (OSError, subprocess.TimeoutExpired):
        pass


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    wanted = [a for a in sys.argv[1:] if not a.startswith("-")]
    all_files = tracked_files()
    check_root(all_files)
    hws = wanted or sorted(p.name for p in ROOT.iterdir() if p.is_dir() and HW_RE.match(p.name))
    if not hws:
        add("WARN", "根目錄", "還沒有任何 hwNN 作業資料夾(可用 python tools/new_hw.py 01 建立)")
    for name in hws:
        check_hw(name)

    order = {"FAIL": 0, "WARN": 1, "INFO": 2}
    for level, scope, msg in sorted(results, key=lambda r: (order[r[0]], r[1])):
        print(f"[{level}] {scope}: {msg}")
    fails = sum(1 for r in results if r[0] == "FAIL")
    warns = sum(1 for r in results if r[0] == "WARN")
    print(f"\n結果:{fails} 個錯誤、{warns} 個警告。" + ("請先修正錯誤再繳交。" if fails else "結構檢查通過。"))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
