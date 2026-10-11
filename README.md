# 我的作業 Repo(pr-2026)

- 學號:(請填寫)
- 課程:圖型識別 2026 秋季
- 這個 Repo 存放**整學期所有作業**,每次作業一個資料夾:`hw01/`、`hw02/`…

> 請務必:
> 1. 這個 Repo 設為 **Private(私人)**。
> 2. 在 **Settings → Collaborators** 把教師帳號 **`ndhuccc`** 加為協作者(只需做一次)。
> 3. 每次作業完成後,在截止前打標籤並推送,這就是你的「繳交」。
>
> 完整規範請看課程網站的「作業說明」。
> **怎麼在 LabTube 登記與繳交,請先看 [`LABTUBE.md`](LABTUBE.md)(一頁版)。**

## 目錄

| 作業 | 資料夾 | 狀態 |
|---|---|---|
| HW01 | `hw01/` | (進行中 / 已打標籤 hw01-submit) |

## 環境(整學期共用的部分)

- Python 版本:(例如 3.11)
- **每個作業資料夾必須自給自足**:各自附 `requirements.txt` 與 `code/README.md`(執行說明),不要依賴其他作業資料夾的程式。

## 常用指令

```bash
# 建立新作業資料夾骨架(例如 hw02)
python tools/new_hw.py 02

# 繳交前檢查結構(有錯誤要先修正)
python tools/check_structure.py

# 完成後打繳交標籤並推送(以 hw01 為例)
git tag hw01-submit
git push origin hw01-submit

# 截止前要更新繳交版本時,可以移動標籤(僅限截止前)
git tag -f hw01-submit
git push -f origin hw01-submit
```

## 規則提醒

- 資料夾命名固定為小寫兩位數:`hw01`、`hw02`…。
- 不要放大型資料、模型權重(`.pt`、`.pth`、`.zip` 等)、帳號密碼、API Key。需要大型資料時,附下載腳本與說明。
- 截止後不要再移動或重打標籤,也不要修改已繳交作業的資料夾。
- 報告末尾一定要有「AI 使用聲明與引用」(沒有使用也要寫)。
