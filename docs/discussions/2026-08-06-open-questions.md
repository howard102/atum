# 2026-08-06 Atum v0.1 待釐清事項

固定四段結構（見 `wiki/AGENTS.md`／專案 `docs/README.md`）。缺段留標題寫「無」。

## 目的地

把 Atum 從「討論稿」推進到 **Constitution v0.1 定版**——鎖定 Atum 與 PO 的權力邊界、
不可跳過的 Gate、角色最小權限、退回與停損、artifact 最低要求。

本檔只收「**講得出問題但還答不出來**」的事項。已收斂者移入 `docs/decisions.md`，
確定不做者移入其「已排除」節。

## 已定案

本輪十六條裁定已全數寫入 [`docs/decisions.md`](../decisions.md)，此處不重複。
規格本體見 [`docs/spec/atum-v0.1.md`](../spec/atum-v0.1.md)。

## 待釐清

### Q1 — 第一個 runtime adapter 支援誰？

Claude Code、Codex，或先做獨立 CLI。**判準未定**：若先做獨立 CLI，`vendor_constraint`
的跨廠商切換最乾淨；若先接 Claude Code，MVP 最快但容易把 adapter 細節寫進核心規格。

### Q2 — 語言與技術棧

repo 位置已定（`/home/chiahao/projects/atum/`）。語言與技術棧未定。
相關限制：`atum.yaml` 需 machine-readable、schema 驗證需要 JSON Schema 工具鏈。

### Q3 — Requirement / spec / AC / evidence 的實際 schema

`docs/spec/atum-v0.1.md` §6 已定 evidence 的最小欄位
（`command` / `exit_code` / `stdout_digest` / `timestamp` / `executor`），
但 requirement brief、AC registry、traceability matrix 三者的 schema 未定。

### Q4 — `browser-operator` 的 session／profile／CDP 隔離策略

已定安全邊界（不入版控、DOM 視為資料）。**未定**：用獨立 profile 還是既有登入 session？
CDP endpoint 綁 localhost 或另設？多個並行任務是否共用瀏覽器？

### Q5 — 各角色的模型層級與 context budget

三段模型欄位（`model`／`model_eco`／`model_power`）已定為機制，
但**每個角色實際填什麼值**未定。每工單總呼叫預算暫定 15，尚未經實測校準。

### Q6 — 一致性驗證的執行位置

`atum.yaml` 與 Markdown 文件的一致性須驗證（Kratos 正是在此出現漂移）。
**CI 屬高風險第 5 類「新增依賴或基礎設施」**，需完整工單；
本 workspace 目前無 CI，只有本機 `githooks/`。
MVP 階段是否先用本機 `scripts/` + pre-commit hook？

### Q7 — 第一個驗證完整 pipeline 的示範功能

須「很小」但能走完垂直流程（需求 → 規格 → AC → RED → GREEN → review → verify → accept）。
候選未提出。**判準**：要能產生真實的 RED，不能是純文件變更。

### Q8 — 治理正本同步的先後順序

`docs/spec/atum-v0.1.md` 中兩處標註「待治理正本同步」：
額度規則放寬（T1）與異質審查改風險分級制（T2），皆為 **wiki 高風險第 4 類**，各需完整工單。

**未定**：先落地治理變更再做 MVP，還是先讓 MVP 在現行規則下跑通再改治理？
後者較安全（現行規則已驗證），但 MVP 會受併發上限限制。

## 已排除

以下於本輪確定不做，理由見 [`docs/decisions.md`](../decisions.md)「已排除」節：

- 整包安裝 Kratos plugin
- Ra 置於最高協調層
- Set（adversarial requirements reviewer）納入 v0.1
- 把 OpenCLI／CLI-Anything 當成 agent-browser 的前置依賴
- Atum 自行執行驗證指令或寫檔
- 自動解析 `/usage` 畫面
