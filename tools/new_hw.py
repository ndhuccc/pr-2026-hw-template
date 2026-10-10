#!/usr/bin/env python3
"""建立新的作業資料夾骨架。

用法::

    python tools/new_hw.py 02      # 建立 hw02/(report.md、code/README.md、code/requirements.txt)

只會建立不存在的檔案,不會覆蓋已有的內容。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPORT = """# HW{nn} 報告

- 作業編號:hw{nn}
- 學號:(請填寫)

## 1. 摘要

(用 2–3 句話說明這次作業做了什麼、主要結果是什麼。)

## 2. 方法

(說明你的做法與關鍵程式的設計理由。引用公式時用 `$...$`。)

## 3. 結果

(放程式執行結果、圖表與數字。圖檔放在本資料夾內,用相對路徑引用,例如 `![收斂曲線](figures/curve.png)`。)

## 4. 討論

(解釋結果:為什麼是這樣?遇到什麼問題?怎麼解決?)

## AI 使用聲明與引用

- 是否使用生成式 AI:(是 / 否。沒有使用也請寫「本作業未使用生成式 AI」。)
- 若有使用,請寫:工具名稱、使用目的、你如何驗證輸出是正確的。
- 引用的他人程式碼、資料或文獻:(沒有請寫「無」。)
"""

CODE_README = """# HW{nn} 程式說明

## 環境
- Python 版本:(例如 3.11)
- 安裝套件:`pip install -r requirements.txt`

## 如何重現結果
(逐步寫出要執行的指令,以及會產生哪些輸出。使用隨機性請固定隨機種子並在此註明。)
"""

REQUIREMENTS = "# 在這裡列出本作業需要的套件,每行一個,例如:\n# numpy\n# matplotlib\n"


def write_new(path: Path, content: str) -> None:
    if path.exists():
        print(f"略過(已存在):{path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"建立:{path.relative_to(ROOT)}")


def main() -> int:
    if len(sys.argv) != 2 or not re.fullmatch(r"\d{1,2}", sys.argv[1]):
        print("用法:python tools/new_hw.py <作業編號>,例如 python tools/new_hw.py 02")
        return 2
    nn = f"{int(sys.argv[1]):02d}"
    hw = ROOT / f"hw{nn}"
    write_new(hw / "report.md", REPORT.format(nn=nn))
    write_new(hw / "code" / "README.md", CODE_README.format(nn=nn))
    write_new(hw / "code" / "requirements.txt", REQUIREMENTS)
    print(f"\n完成。接著請在 hw{nn}/code/ 放入你的程式,並完成 hw{nn}/report.md。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
