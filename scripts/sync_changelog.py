#!/usr/bin/env python3
"""sync_changelog.py

ดึงข้อความจาก changelog.md แล้วเขียนทับค่า addon_changelog ใน buildVars.py
ให้เป็น string literal ตรงๆ (เพื่อให้ xgettext จับ string นี้เข้า .pot ได้)

โหมดการทำงาน:
- ถ้ามี env var CHANGELOG_VERSION (หรือรันตอน push tag v*.*.*) จะดึงเฉพาะ
  หัวข้อ "## <version>" ที่ตรงกับ VERSION นั้น (logic เดียวกับ step
  "Extract Changelog" เดิมใน build_addon.yaml)
- ถ้าไม่มี VERSION ระบุ (เช่นตอนรันแบบ workflow_dispatch/push ปกติ
  ก่อนตัดสินใจ tag เวอร์ชัน) จะดึง "หัวข้อบนสุด" ของไฟล์แทน
  (เหมาะกับช่วง sync เพื่อแจ้งนักแปลก่อนออก release จริง)

ใช้งาน:
    python scripts/sync_changelog.py                # เอาหัวข้อบนสุด
    CHANGELOG_VERSION=2026.9.3 python scripts/sync_changelog.py  # ระบุเวอร์ชัน
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "changelog.md"
BUILD_VARS = ROOT / "buildVars.py"

START_MARK = "# CHANGELOG-START"
END_MARK = "# CHANGELOG-END"


def get_version_from_ref() -> str | None:
    """เลียนแบบ VERSION=${GITHUB_REF#refs/tags/v} จาก workflow เดิม"""
    ref = os.environ.get("GITHUB_REF", "")
    if ref.startswith("refs/tags/v"):
        return ref[len("refs/tags/v"):]
    return None


def get_section_by_version(text: str, version: str) -> str:
    """เหมือน: sed -n "/^## $VERSION/,/^## /p" changelog.md | sed '1d;$d'"""
    pattern = re.compile(
        rf"^## {re.escape(version)}\s*$(.*?)(?=^## |\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise SystemExit(f"ไม่พบหัวข้อ '## {version}' ใน changelog.md")
    return match.group(1).strip()


def get_topmost_section(text: str) -> str:
    parts = re.split(r"^## .*$", text, flags=re.MULTILINE)
    if len(parts) < 2:
        raise SystemExit("ไม่พบหัวข้อ '## ' ใน changelog.md")
    return parts[1].strip()


def inject(build_vars_text: str, changelog_body: str) -> str:
    safe_body = changelog_body.replace('"""', '\\"\\"\\"')
    pattern = re.compile(
        re.escape(START_MARK) + r".*?" + re.escape(END_MARK),
        flags=re.DOTALL,
    )
    replacement = f'{START_MARK}\n        """{safe_body}"""\n        {END_MARK}'
    new_text, count = pattern.subn(replacement, build_vars_text)
    if count == 0:
        raise SystemExit(f"ไม่พบ marker {START_MARK} ... {END_MARK} ใน buildVars.py")
    return new_text


def main() -> None:
    changelog_text = CHANGELOG.read_text(encoding="utf-8")

    version = os.environ.get("CHANGELOG_VERSION") or get_version_from_ref()
    if version:
        body = get_section_by_version(changelog_text, version)
        print(f"ดึง changelog ของเวอร์ชัน {version}")
    else:
        body = get_topmost_section(changelog_text)
        print("ไม่พบ VERSION ที่ระบุ — ใช้หัวข้อบนสุดของ changelog.md แทน")

    build_vars_text = BUILD_VARS.read_text(encoding="utf-8")
    BUILD_VARS.write_text(inject(build_vars_text, body), encoding="utf-8")
    print("อัปเดต addon_changelog ใน buildVars.py เรียบร้อยแล้ว")


if __name__ == "__main__":
    sys.exit(main())

