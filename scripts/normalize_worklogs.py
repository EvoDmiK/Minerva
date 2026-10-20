#!/usr/bin/env python3
"""
normalize_worklogs.py
Minerva 볼트 내 모든 프로젝트의 작업 문서(worklog)와 백로그(backlog)를 표준 템플릿 규격으로 통일/정규화하는 도구.
"""

import argparse
import difflib
import os
import re
import sys
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent

def extract_date(filename: str) -> str:
    m = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    return m.group(1) if m else "2026-10-20"

def extract_task_id(filename: str) -> str:
    m = re.search(r"\b([A-Z]{2,3})[-_]?(\d{3})\b", filename)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return None

def parse_frontmatter(text: str):
    fm_dict = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_raw = parts[1]
            body = parts[2].lstrip("\n")
            current_key = None
            for line in fm_raw.splitlines():
                if not line.strip():
                    continue
                if line.startswith("  - ") and current_key:
                    val = line.replace("  - ", "").strip().strip("\"'")
                    fm_dict.setdefault(current_key, []).append(val)
                elif ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip("\"'")
                    current_key = k
                    if v.startswith("[") and v.endswith("]"):
                        items = [x.strip().strip("\"'") for x in v[1:-1].split(",") if x.strip()]
                        fm_dict[k] = items
                    elif v:
                        fm_dict[k] = v
                    else:
                        fm_dict[k] = []
    return fm_dict, body

def normalize_worklog(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    rel_path = path.resolve().relative_to(VAULT_ROOT.resolve())
    proj = rel_path.parts[1]
    file_date = extract_date(path.name)
    inferred_task_id = extract_task_id(path.name)
    
    fm_dict, body = parse_frontmatter(text)
    
    created = fm_dict.get("created") or fm_dict.get("date") or file_date
    date_val = fm_dict.get("date") or created
    status = fm_dict.get("status") or "completed"
    task_id = fm_dict.get("task_id") or inferred_task_id
    
    # Tags
    tags = fm_dict.get("tags")
    if isinstance(tags, list):
        tag_list = list(tags)
    elif isinstance(tags, str):
        tag_list = [tags]
    else:
        tag_list = []
        
    if "worklog" not in tag_list:
        tag_list.insert(0, "worklog")
    proj_tag = proj.lower()
    if proj_tag not in tag_list:
        tag_list.append(proj_tag)
        
    category = None
    for part in path.parts:
        if re.match(r"^\d{1,2}xx\s", part):
            category = part
            break
            
    # Assemble standard frontmatter lines
    lines = ["---", f"created: {created}", f"date: {date_val}", f"project: {proj}"]
    if category:
        lines.append(f"category: \"{category}\"")
    if task_id:
        lines.append(f"task_id: {task_id}")
    lines.append("type: worklog")
    lines.append(f"status: {status}")
    
    # Retain non-standard extra keys
    for k, v in fm_dict.items():
        if k in ("created", "date", "project", "category", "task_id", "type", "status", "tags", "updated"):
            continue
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{k}: {v}")
            
    lines.append("tags:")
    for t in tag_list:
        lines.append(f"  - {t}")
    lines.append("---\n")
    
    new_fm = "\n".join(lines)
    
    # Check bottom related links
    new_body = body
    if "## 관련" not in body and "## 관련 문서" not in body and "## 관련문서" not in body:
        new_body = body.rstrip() + f"\n\n---\n\n## 관련 문서\n\n- [[Home|🏠 홈으로]]\n- [[Work/{proj}/index|{proj} 프로젝트 인덱스]]\n- [[Work/{proj}/{proj} 작업 백로그|{proj} 작업 백로그]]\n"
        
    return new_fm + new_body

def main():
    parser = argparse.ArgumentParser(description="Minerva Work Document & Backlog Normalizer")
    parser.add_argument("--dry-run", action="store_true", help="Print stats and sample diffs without saving")
    parser.add_argument("--apply", action="store_true", help="Apply changes to all worklogs")
    parser.add_argument("files", nargs="*", help="Optional specific file paths to normalize")
    args = parser.parse_args()
    
    if args.files:
        worklogs = [Path(f).resolve() for f in args.files if Path(f).is_file() and Path(f).suffix == ".md"]
    else:
        work_dir = VAULT_ROOT / "Work"
        worklogs = sorted([p for p in work_dir.rglob("*.md") if "작업기록" in p.parts and "백로그" not in p.name and p.name != "index.md"])
    
    modified_count = 0
    sample_diffs = []
    
    for p in worklogs:
        orig = p.read_text(encoding="utf-8", errors="ignore")
        norm = normalize_worklog(p)
        if orig != norm:
            modified_count += 1
            if len(sample_diffs) < 3:
                diff = "".join(difflib.unified_diff(
                    orig.splitlines(True), norm.splitlines(True),
                    fromfile=str(p.relative_to(VAULT_ROOT)), tofile="normalized"
                ))
                sample_diffs.append(diff)
            if args.apply:
                p.write_text(norm, encoding="utf-8")
                
    print(f"Total worklogs: {len(worklogs)}")
    print(f"Modified worklogs: {modified_count}")
    
    if args.dry_run:
        print("\n=== Sample Diffs ===")
        for d in sample_diffs:
            print(d[:1000])
            print("=" * 60)
            
    if args.apply:
        print(f"\n[성공] {modified_count}개의 작업 문서 템플릿 정규화가 완료되었습니다.")

if __name__ == "__main__":
    main()
