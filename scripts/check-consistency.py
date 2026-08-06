#!/usr/bin/env python3
"""Atum 一致性驗證——防止 manifest、role contract 與 docs 之間漂移。

為何存在：docs/tech/kratos-reference.md §3 第 5 項記錄了 Kratos 在 manifest 與 README
之間出現版本／階段數漂移。Atum 以單一 machine-readable 權威加本腳本避免重蹈。

注意：本腳本是**工具**，不是 Atum 的產品技術棧。Q2（語言與技術棧）尚未裁定，
選用 python3 只因系統環境已具備 PyYAML 與 jsonschema，零新增依賴。
不得以本檔的存在推論 Atum 將以 Python 實作。

用法：python3 scripts/check-consistency.py   （exit 0 = 全通過，1 = 有不一致）
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def report(name: str, problems: list[str]) -> None:
    if problems:
        print(f"FAIL: {name}")
        for p in problems:
            print(f"      - {p}")
        FAILURES.extend(problems)
    else:
        print(f"ok   {name}")


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_json(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


manifest = load_yaml(ROOT / "atum.yaml")


# 1. manifest 的 roles 索引 ↔ roles/*.yaml 實檔
def check_role_index() -> None:
    problems = []
    indexed = {}
    for entry in manifest["roles"]:
        path = ROOT / entry["file"]
        if not path.is_file():
            problems.append(f"索引指向不存在的檔案：{entry['file']}")
            continue
        data = load_yaml(path)
        indexed[entry["id"]] = data
        if data.get("id") != entry["id"]:
            problems.append(
                f"{entry['file']} 的 id 為 {data.get('id')!r}，索引寫 {entry['id']!r}"
            )

    on_disk = {p.name for p in (ROOT / "roles").glob("*.yaml")}
    referenced = {Path(e["file"]).name for e in manifest["roles"]}
    for orphan in sorted(on_disk - referenced):
        problems.append(f"roles/{orphan} 存在但未登錄於 atum.yaml")

    report("1. manifest roles 索引 ↔ roles/*.yaml", problems)
    return indexed


roles = check_role_index()


# 2. 每份 role contract 通過 role.schema.json
def check_role_schema() -> None:
    schema = load_json(ROOT / manifest["schemas"]["role"])
    validator = Draft202012Validator(schema)
    problems = []
    for role_id, data in roles.items():
        for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
            loc = "/".join(str(x) for x in err.path) or "(root)"
            problems.append(f"{role_id}: {loc} — {err.message}")
    report("2. roles/*.yaml 通過 role.schema.json", problems)


check_role_schema()


# 3. workflow 通過 schema，且轉換與回退不指向未定義的 state／role
def check_workflow() -> None:
    schema = load_json(ROOT / manifest["schemas"]["workflow"])
    wf = manifest["workflow"]
    problems = [
        f"{'/'.join(str(x) for x in e.path) or '(root)'} — {e.message}"
        for e in Draft202012Validator(schema).iter_errors(wf)
    ]

    states = set(wf["states"])
    terminals = {t["name"] for t in wf["terminal_states"]}
    known_states = states | terminals
    actors = set(roles) | {"human_product_owner"}

    for t in wf["transitions"]:
        if t["from"] not in known_states:
            problems.append(f"transition 來源 {t['from']} 非合法 state")
        if t["to"] not in known_states:
            problems.append(f"transition 目標 {t['to']} 非合法 state")
        if t["actor"] not in actors:
            problems.append(f"transition actor {t['actor']} 非已知角色")

    # human_terminations 可自任何非終態宣告，不需逐一列 transition
    reachable = (
        {wf["states"][0]}
        | {t["to"] for t in wf["transitions"]}
        | set(wf.get("human_terminations", []))
    )
    for orphan in sorted(known_states - reachable):
        problems.append(f"state {orphan} 無任何轉換可抵達（孤兒節點）")

    for term in wf.get("human_terminations", []):
        if term not in terminals:
            problems.append(f"human_terminations 列出 {term}，但它不是 terminal_state")

    for fb in wf["fallbacks"]:
        if fb["to_role"] not in actors:
            problems.append(f"fallback 目的地 {fb['to_role']} 非已知角色")
        if "resets_state_to" in fb and fb["resets_state_to"] not in known_states:
            problems.append(f"fallback resets_state_to {fb['resets_state_to']} 非合法 state")

    if wf.get("risk_classification_after") not in states:
        problems.append("risk_classification_after 非合法 state")

    report("3. workflow schema 與狀態／角色參照", problems)


check_workflow()


# 4. Constitution 條目數 ↔ manifest 宣告
def check_constitution() -> None:
    path = ROOT / manifest["constitution"]["source"]
    problems = []
    if not path.is_file():
        problems.append(f"constitution.source 指向不存在的檔案：{path}")
    else:
        text = path.read_text(encoding="utf-8")
        actual = len(re.findall(r"^\d+\. ", text, flags=re.MULTILINE))
        declared = manifest["constitution"]["count"]
        if actual != declared:
            problems.append(
                f"{path.name} 實際 {actual} 條，atum.yaml 宣告 {declared} 條"
            )
    report("4. Constitution 條目數一致", problems)


check_constitution()


# 5. spec §2 命名表列出的 id ↔ roles/ 檔名集合
def check_spec_role_table() -> None:
    spec = (ROOT / "docs/spec/atum-v0.1.md").read_text(encoding="utf-8")
    # 只取 §2 命名表所在區段——全檔比對會誤抓 §10 的 verdict 表（clear/caution/blocked）
    section = re.search(r"^## 2\. .*?(?=^## 3\. )", spec, flags=re.MULTILINE | re.DOTALL)
    problems = []
    if not section:
        report("5. spec §2 角色表 ↔ roles/", ["找不到 spec §2 區段，比對無法進行"])
        return
    in_spec = set(re.findall(r"^\| `([a-z][a-z0-9-]*)` \|", section.group(0), flags=re.MULTILINE))
    if not in_spec:
        problems.append("spec §2 區段內找不到角色命名表，比對無法進行")
    else:
        for missing in sorted(in_spec - set(roles)):
            problems.append(f"spec 列出 {missing} 但 roles/ 無對應檔")
        for extra in sorted(set(roles) - in_spec):
            problems.append(f"roles/{extra}.yaml 存在但 spec §2 未列出")
    report("5. spec §2 角色表 ↔ roles/", problems)


check_spec_role_table()


# 6. docs/ 下每個 .md（除 README）皆登錄於 docs/README.md
def check_docs_index() -> None:
    index = (ROOT / "docs/README.md").read_text(encoding="utf-8")
    problems = [
        f"{md.relative_to(ROOT)} 未登錄於 docs/README.md"
        for md in sorted((ROOT / "docs").rglob("*.md"))
        if md.name != "README.md" and md.name not in index
    ]
    report("6. docs/ 索引無漏登", problems)


check_docs_index()


print()
if FAILURES:
    print(f"不一致 {len(FAILURES)} 項")
    sys.exit(1)
print("全部通過")
sys.exit(0)
