# atum — Codex 入口

本專案規範以 `CLAUDE.md` 為準；本檔僅作為 Codex 入口，放讀取指引與 Codex 專屬事項。

## docs/ 讀取指引

- 進專案先讀 `docs/README.md` 索引，實質內容以 `docs/` 為唯一權威來源。
- 角色合約、狀態機、Constitution、Gate 與證據、額度模型讀 `docs/spec/`。
- 外部參照（Kratos 對照等）讀 `docs/tech/`。
- 討論項目讀 `docs/discussions/`，已定案內容讀 `docs/decisions.md`。

## Codex 專屬事項

- 嚴格依工單 Scope 作業；遇到 Scope 未涵蓋的必要變更，停手回報，不得代為擴大。
- 停損條件觸發時立即停手回報。
- 一般變更以結構化 commit 收尾（`Scope:` / `AC:` / `Notes:`）；高風險（外部狀態、secrets、不可逆資料、治理/schema、新依賴或基礎設施、跨專案）維持完整工單，依 wiki/ops/collaboration.md 風險分級。
- 新增 `docs/` 檔案時，須同步更新 `docs/README.md` 索引。
- 禁止讀取或輸出任何 secrets；本專案未來將含瀏覽器 session／token，一律不得輸出。

## 額度耗盡時的承接

依 2026-08-04 裁定，Claude 側 Effective usage ≥95% 時會寫 `<工單路徑>.handoff.md` 交由 Codex 承接。
承接時**先讀該 handoff 檔**，其內容須自足；若發現需倚賴 Claude session 上下文才能理解，回報而非猜測。
不得重議 handoff 中列為「已裁定」的事項。
