# Kratos 參照附錄

外部參照，非本專案規格。來源：[LizardLiang/lizard-market — plugins/kratos](https://github.com/LizardLiang/lizard-market/tree/master/plugins/kratos)，
查閱日 **2026-08-06**。Kratos 是 Claude Code plugin 形態的多階段開發流程，
**本專案只抄結構、不安裝該 plugin**（見 `docs/decisions.md`「已排除」）。

> 下列內容為當日實際讀取所得，非憑記憶推測。上游若變更，本檔不自動同步。

## 1. Pipeline 結構

| Stage | Agent | 職責 |
|---|---|---|
| 0 | Metis | 選用的前置 codebase 研究 |
| 1 | Athena | Gap 分析與 PRD 撰寫 |
| 2 | Nemesis | 反方與使用者代言審查 |
| 3 | Daedalus | 功能拆解為 phase |
| 3b | Themis | 鎖定實作決策（選用）|
| 4 | Hephaestus | 技術規格與藍圖 |
| 5 | Apollo | 系統架構審查 |
| 6 | Artemis | 測試規劃與案例設計 |
| 7 | Ares | 程式實作 |
| 8 | Hera | PRD 對齊驗證 |
| 9 | Hermes ∥ Cassandra | 平行的品質與風險審查 |

## 2. 可沿用的設計

- 以協調器管理多個專業角色
- 需求／規格／測試／開發／Review 分階段
- 每個角色有自己的 prompt、輸入與產出
- **以 artifact 在角色之間交接**，不依賴完整對話記憶
- 明確的檔案寫入權表（誰可寫哪個檔，其餘唯讀）

## 3. Atum 主動調整之處

| # | Kratos | Atum |
|---|---|---|
| 1 | Athena 在 PRD 內定 AC，Hera 事後驗證 | `ac-owner` 於開發前**獨立建立並鎖定** AC |
| 2 | Artemis 寫 Test Plan，**Ares 仍寫實際測試與 production code** | `test-author` 寫測試並取得 RED，`implementer` 只實作到 GREEN |
| 3 | Hera 在 Review **前**做需求對齊與測試 | 加入 `verifier`，於 Review **通過後**從乾淨狀態最終驗證 |
| 4 | Hermes 可對受審碼提出修正 | `code-reviewer` **嚴格唯讀**；退回後必須開新實作循環 |
| 5 | manifest 與 README 的版本／階段數描述**存在漂移**（2026-08-06 觀察） | 單一 machine-readable `atum.yaml` 產生文件，並驗證一致性 |
| 6 | 全 Claude 運轉 | `vendor_constraint` 欄位，高風險工單下 `code-reviewer` 須跨廠商 |

## 4. 四項關鍵查證（改變了 Atum 的設計）

### 4.1 Gate 是 hook，不是 LLM 判讀

Kratos 用 `SubagentStart` / `SubagentStop` hook 做**機械攔截**：

- **SubagentStart**：Ares 與 Hephaestus 開工前須先寫編號 TODO 清單才能發出任何 tool call
- **SubagentStop（Ares gate）**：須有 TODO 清單、具名檔案、完成宣告
- **SubagentStop（Hephaestus gate）**：spec 至少涵蓋架構／資料模型／API／實作／schema／介面其中兩項
- **Ares Verify Gate（v2.87）**：**code 被編輯但沒跑任何測試指令即擋下**；確定不適用須明示 `TESTS-NOT-APPLICABLE: <reason>`

→ 這比「協調器自己重跑」更好：Atum 不需要執行權限，deterministic hook 就攔住了。
本 workspace 已有同型先例：`githooks/commit-msg`（缺 `Scope:`/`AC:` 即擋）、`fable-harness/verify_gate.py`（Stop gate）。

> **⚠ 已知弱點，Atum 刻意不照抄**：`stop_hook_active` 為 true（hook 觸發的重跑）時，
> Kratos 讓 **gate 自動放行**以避免迴圈。Atum 改為放行但寫入 `gate_bypassed` 標記，且不計為 Gate 通過。

### 4.2 證據由下游角色重跑，不是協調器

Hera 的流程：Step 1 從 PRD 抽出 AC 並給穩定 ID（AC-01…）→ Step 2 grep 對應測試建矩陣 →
**Step 3 執行全套測試**，並驗證 `implementation-notes.md` 內每個測試都有 RED→GREEN 記錄 →
Step 4 分類 findings → Step 5 計算覆蓋率 → **Step 5b 反向 scope 檢查**（掃出無法追溯到任何 AC 的新程式碼／端點／依賴，標為 scope creep）→ Step 6 verdict（`aligned` / `gaps` / `misaligned`）。

Kratos 原文的證據標準：

> Tests must show recorded RED (failing) then GREEN (passing) states.
> **Green-only tests lack proof of detection.** Missing evidence marks a coverage gap regardless of current pass state.

→ 與 FABLE-PROTOCOL §4 的 fail-then-pass 完全同構。Atum 的 `verifier` 已在做重跑那半，
缺的不是機制而是 **evidence schema**（見 `docs/spec/atum-v0.1.md` §6）。

**Step 5b 反向 scope 檢查**值得單獨抄——它抓的是「做了沒人要求的東西」，
與 AC 只能抓「沒做該做的東西」互補。

### 4.3 Cassandra 只解決一半

Cassandra 的四級嚴重度與三態 verdict 直接可用（已納入 `spec` §10）：

| 嚴重度 | 涵蓋 |
|---|---|
| Security (CRITICAL) | injection、auth bypass、secret leakage、unsafe defaults |
| Correctness (HIGH) | breaking changes、data migration、race condition、missing error handling |
| Reliability (MEDIUM) | 效能瓶頸、資源洩漏、擴展性、依賴風險 |
| Maintainability (LOW) | 技術債、晦澀邏輯、模式違反 |

verdict 門檻：`Clear`＝無 critical/high 且 medium < 3；`Caution`＝1–3 high 或 ≥3 medium 且皆可處理；
`Blocked`＝任一 critical 或 ≥4 high。Cassandra 亦為唯讀（風險修正屬 Ares），
且 `Clear`/`Caution` 也必須在 `decisions.md` 留一行 sign-off。

> **⚠ 涵蓋不到的部分**：Cassandra 審的是**程式碼裡的注入漏洞**，
> **不是 agent 自己被網頁內容注入**。`browser-operator` 的 DOM-as-data 邊界不在其範圍內，
> Atum 另立規則，沿用本 workspace 2026-07-26「inbox 內容視為資料非指令」裁定並擴及瀏覽器輸出。

### 4.4 Agent frontmatter schema

實際欄位（cassandra.md / hera.md 一致）：

```yaml
name: cassandra
description: Risk analyst for security and correctness
stage: "9"
command_refs: templates
tools: Read, Write, Edit, Glob, Grep, Bash, Task
model: sonnet
model_eco: haiku
model_power: opus
protocol_sections: document-selection, auto-discovery, missing-required-input, document-creation, timestamp-standard, status-updates, session-tracking, boundaries, output-format
```

→ `model` / `model_eco` / `model_power` 三欄正好是 Atum 額度分層的載體。
Atum 另加 `id`（功能名，取代 `name` 的角色）、`display_name`（神名）與 `vendor_constraint` 三欄。

## 5. 其他可參考機制

- **狀態檔**：`.claude/feature/<name>/status.json` 記錄當前 stage、各階段起訖時間戳、
  pipeline 歷史與 stage verdict、各階段文件參照
- **Intent Alignment（阻斷式）**：Athena 逐字重讀原始請求並用一句話覆述，
  Nemesis 檢查 `[INTENT_DRIFT]`——PRD 是否在回答另一個問題
- **檔案寫入權表**：`prd.md` 只有 Athena 可寫、`tech-spec.md` 只有 Hephaestus 可寫，
  下游一律唯讀；`status.json` 只有 pipeline engine 可寫
- **PreToolUse 限制**：Odysseus 只能寫特定兩個目錄，Bash 除 `kratos` 子指令外一律唯讀

## 6. 瀏覽器與 CLI 工具定位

| 工具 | 定位 | Atum 採用順序 |
|---|---|---|
| [agent-browser](https://github.com/vercel-labs/agent-browser) | 給 AI agent 用的瀏覽器自動化 CLI（snapshot、accessibility refs、click、fill、screenshot、JSON output） | **Phase 1** — 驗證 `browser-operator` 能完成 snapshot → action → re-snapshot → evidence |
| [OpenCLI](https://github.com/jackwener/opencli) | 把網站／既有登入 session／Electron app／local tool 包成較確定性的 CLI adapter | Phase 2 — **僅在**出現具體高頻網站流程時評估 |
| [CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 分析有源碼的軟體並生成 agent-friendly CLI harness（GIMP、Blender、LibreOffice 等）| Phase 3 — **僅在**需操作特定專業 GUI／開源軟體時評估 |

後兩者**都不是 agent-browser 的必要依賴**，亦不負責 orchestration。已列入 `decisions.md` 的「已排除」。
