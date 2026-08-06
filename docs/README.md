# atum docs 索引

三方協作（Claude Code / Codex / Antigravity）的資料交換區，本專案實質內容的唯一權威來源。
新增或移動檔案後，必須同步更新本索引（每檔一行）。

## 給新 Agent／Session 的交接

**閱讀順序：**

1. `/home/chiahao/projects/wiki/ops/collaboration.md` — 跨專案治理的權威來源
2. 本檔（索引）
3. [`spec/atum-v0.1.md`](spec/atum-v0.1.md) — 規格本體
4. [`decisions.md`](decisions.md) — 已定案，禁止重議
5. [`discussions/2026-08-06-open-questions.md`](discussions/2026-08-06-open-questions.md) — 還沒答案的

**現況：概念與規格討論階段。** 尚未建立遠端 repo、未安裝任何工具、未實作任何代理人。
未收到 PO 明確的「執行／開始做／GO」前，不得修改檔案或外部狀態。

> **兩個容易搞混的邊界：**
> 1. `spec/` 描述的是「Atum 未來會如何運作」，**不是**「本 repo 現在如何作業」。本 repo 自身開發依 wiki 現行規則。
> 2. `spec/` 中標註「**待治理正本同步**」的條款尚未在 wiki 生效，**不得據以作業**。

## 結構

- `spec/` — 規格：角色合約、狀態機、Constitution、Gate 與證據、額度模型
- `tech/` — 技術說明與外部參照附錄
- `discussions/` — 討論項目：一題一檔，命名 `YYYY-MM-DD-主題.md`；收斂後結論移入 decisions.md。固定四段結構（見下）
- `decisions.md` — 已定案決策，禁止重新爭論；含專案層「已排除」節
- `decision-<slug>.md` — 決策升格檔（僅在命中升格條件時建立，條件與四段結構見 `wiki/AGENTS.md`「決策升格」節）

### discussions/ 固定四段

每份討論檔一律四段，缺段留標題寫「無」——刻意不完整是常態，寫不出來的段落本身就是訊號：

- `## 目的地` — 這次討論要收斂成什麼。先定這個，它決定了什麼算範圍內
- `## 已定案` — 一行一條，收斂後同步進 `decisions.md` 並在此保留連結
- `## 待釐清` — **講得出問題、但還答不出來**的事項。判準是能否精確陳述問題，不是能否回答
- `## 已排除` — 這次確定不做的事，附一行理由。範圍問題不是進度問題，排除後不再回到待釐清

## 檔案清單

### spec/
- [atum-v0.1.md](spec/atum-v0.1.md) — Atum 規格本體：角色 id/display_name 雙層命名、角色合約表與 `vendor_constraint`、Role Contract frontmatter schema、Gate 與證據雙層機制、狀態機與三終態、與 wiki 治理的映射、額度與成本模型、風險審查框架、Constitution v0.1 十六條

### tech/
- [kratos-reference.md](tech/kratos-reference.md) — Kratos 參照附錄（查閱日 2026-08-06）：pipeline 九階段、Atum 六項主動調整、四項關鍵查證（hook gate／下游重跑／Cassandra 涵蓋範圍／frontmatter schema）、agent-browser 與 OpenCLI／CLI-Anything 定位

### discussions/
- [2026-08-06-open-questions.md](discussions/2026-08-06-open-questions.md) — v0.1 待釐清 8 題：runtime adapter、技術棧、artifact schema、browser 隔離策略、各角色模型層級、一致性驗證位置、示範功能、治理同步順序
