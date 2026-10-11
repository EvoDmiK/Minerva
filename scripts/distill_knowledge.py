#!/usr/bin/env python3
"""
distill_knowledge.py
Minerva 볼트의 Work/ 작업기록에서 Dev/ 상록수 지식을 추출(증류)하는 CLI & 자동화 도구.

사용법:
    python3 scripts/distill_knowledge.py --file Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-06-전체종-근연관계우선-계통근거-NAS배포.md
    python3 scripts/distill_knowledge.py --recent-days 3
    python3 scripts/distill_knowledge.py --list-candidates
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent

def find_work_logs(recent_days: int = None):
    """Work/ 하위의 작업기록 마크다운 파일 목록을 반환"""
    work_dir = VAULT_ROOT / "Work"
    logs = []
    
    cutoff_time = None
    if recent_days is not None:
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=recent_days)

    for path in work_dir.rglob("*.md"):
        if "작업기록" in path.parts:
            if cutoff_time:
                mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
                if mtime >= cutoff_time:
                    logs.append(path)
            else:
                logs.append(path)
    return sorted(logs, key=lambda p: p.name, reverse=True)

def parse_frontmatter_and_content(file_path: Path):
    """마크다운 파일에서 YAML 프론트매터와 본문 분리"""
    text = file_path.read_text(encoding="utf-8")
    frontmatter = {}
    content = text
    
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            content = parts[2].strip()
            for line in fm_text.strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    frontmatter[k.strip()] = v.strip().strip("'\"")
                    
    return frontmatter, content

def extract_distill_candidates(file_path: Path):
    """작업기록 본문에서 재사용 가능한 기술 지식 섹션/키워드 분석"""
    fm, content = parse_frontmatter_and_content(file_path)
    
    # 주요 기술 키워드 매칭
    keywords = {
        "n8n / 워크플로우": ["n8n", "webhook", "웹훅", "workflow", "실패율", "파이프라인"],
        "LLM / 관측성": ["token", "토큰", "cache", "캐시", "grafana", "prometheus", "mlflow", "telemetry"],
        "인프라 / 네트워크": ["tailscale", "dns", "cloudflare", "인증서", "origin", "let's encrypt", "npm"],
        "데이터 / 그래프": ["neo4j", "cypher", "지식그래프", "계통", "taxo", "timescaledb", "postgresql"],
        "에이전트 / MCP": ["hermes", "mcp", "semantic-vault", "dovie", "kestrel", "openviking"]
    }
    
    matched_domains = []
    content_lower = content.lower()
    for domain, kws in keywords.items():
        if any(kw.lower() in content_lower for kw in kws):
            matched_domains.append(domain)
            
    # 코드 블록 추출
    code_blocks = re.findall(r"```([a-zA-Z0-9_-]+)?\n(.*?)```", content, re.DOTALL)
    
    # 머리말/요약 추출
    first_heading = ""
    for line in content.splitlines():
        if line.startswith("# "):
            first_heading = line.replace("# ", "").strip()
            break
            
    return {
        "file": file_path.relative_to(VAULT_ROOT),
        "title": first_heading or file_path.stem,
        "project": fm.get("project", file_path.parts[file_path.parts.index("Work") + 1] if "Work" in file_path.parts else "Unknown"),
        "domains": matched_domains,
        "code_block_count": len(code_blocks),
        "code_languages": list(set(lang for lang, _ in code_blocks if lang)),
    }

def get_category_folder(domains: list):
    """도메인 매칭 결과에 따라 적절한 Dev 하위 폴더 반환"""
    if not domains:
        return "인프라"
    d = domains[0]
    if "인프라" in d or "네트워크" in d:
        return "인프라"
    elif "워크플로우" in d or "n8n" in d:
        return "자동화"
    elif "관측성" in d or "LLM" in d:
        return "관측성"
    elif "데이터" in d or "그래프" in d:
        return "데이터"
    return "인프라"

def generate_dev_draft(candidate: dict, output_dir: Path = None):
    """Dev/ 상록수 노트 초안 생성"""
    cat_folder = get_category_folder(candidate.get("domains", []))
    if output_dir is None:
        output_dir = VAULT_ROOT / "Dev" / cat_folder
    output_dir.mkdir(parents=True, exist_ok=True)
        
    safe_slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", candidate["file"].stem)
    draft_name = f"초안-{safe_slug}.md"
    draft_path = output_dir / draft_name
    
    domains_str = ", ".join(candidate["domains"]) if candidate["domains"] else "general"
    
    template = f"""---
created: {datetime.date.today().isoformat()}
updated: {datetime.date.today().isoformat()}
type: reference
category: {cat_folder}
status: draft
source_project: {candidate["project"]}
source_work_log: "[[{candidate["file"]}]]"
tags:
  - dev
  - draft
  - {candidate["project"].lower()}
---

# [지식 증류 초안] {candidate["title"]}

## 1. 개요 및 목적
* 본 문서는 [[{candidate["file"]}|{candidate["project"]} 작업 기록]]에서 추출된 공통 기술 패턴 초안입니다.
* 관련 기술 영역: **{domains_str}**

## 2. 핵심 아키텍처 및 원칙
* (이 패턴이 해결하고자 하는 일반적인 문제와 설계 원칙을 작성하세요)

## 3. 재사용 가능한 코드 스니펫 / 설정
* (작업 기록에서 검증된 스니펫을 범용 템플릿 형태로 정리하세요)

## 4. 검증 근거 및 트러블슈팅
* 원천 프로젝트: [[Work/{candidate["project"]}/index|{candidate["project"]} 인덱스]]
* 세부 실행 로그: [[{candidate["file"]}]]

## 5. 관련 Dev 가이드
* [[Dev/index|Dev 인덱스]]
"""
    return draft_path, template

def main():
    parser = argparse.ArgumentParser(description="Minerva Knowledge Distillation CLI")
    parser.add_argument("--file", type=str, help="특정 작업기록 파일 증류")
    parser.add_argument("--recent-days", type=int, help="최근 N일 내 수정된 작업기록 검사")
    parser.add_argument("--list-candidates", action="store_true", help="증류 후보 작업기록 목록 출력")
    parser.add_argument("--create-draft", action="store_true", help="Dev/ 폴더에 초안 마크다운 생성")
    
    args = parser.parse_args()
    
    if args.file:
        target_path = VAULT_ROOT / args.file
        if not target_path.exists():
            print(f"오류: 파일을 찾을 수 없습니다: {target_path}", file=sys.stderr)
            sys.exit(1)
        info = extract_distill_candidates(target_path)
        print("\n=== 지식 증류 분석 결과 ===")
        print(f"• 대상 파일: {info['file']}")
        print(f"• 제목: {info['title']}")
        print(f"• 소속 프로젝트: {info['project']}")
        print(f"• 매칭된 기술 영역: {', '.join(info['domains']) or '없음'}")
        print(f"• 포함된 코드 블록 수: {info['code_block_count']}개 ({', '.join(info['code_languages']) or 'plain'})")
        
        if args.create_draft:
            draft_path, draft_content = generate_dev_draft(info)
            draft_path.write_text(draft_content, encoding="utf-8")
            print(f"\n[성공] 초안 노트가 생성되었습니다: {draft_path.relative_to(VAULT_ROOT)}")
        return

    # 목록 조회 모드
    logs = find_work_logs(args.recent_days)
    print(f"\n총 {len(logs)}개의 작업기록이 검색되었습니다.\n")
    print(f"{'프로젝트':<14} | {'기술 영역':<22} | {'코드블록':<8} | {'파일명'}")
    print("-" * 80)
    
    for log in logs[:15]:
        info = extract_distill_candidates(log)
        domains = ", ".join(info['domains'][:2]) or "기타"
        print(f"{info['project']:<14} | {domains:<22} | {info['code_block_count']}개{'':<5} | {log.name}")

if __name__ == "__main__":
    main()
