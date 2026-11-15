"""ClaimSense AI - Claim Submission Cleanup Utility

Performs safe, transactional cleanup of claim submissions, uploaded evidence,
and generated claim reports while strictly preserving user accounts, authentication,
application source code, configuration, and research datasets (FUNSD, SROIE, CarDD).
"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def identify_claim_targets(repo_root: Path) -> Dict[str, Any]:
    db_path = repo_root / "data" / "claimsense.db"
    uploads_dir = repo_root / "uploads"
    reports_dir = repo_root / "reports"

    # 1. Database counts
    db_counts = {}
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        for tbl in [
            "claims",
            "documents",
            "claim_images",
            "extracted_information",
            "verification_results",
            "risk_assessments",
            "reports",
            "image_analysis",
            "users",
        ]:
            try:
                cnt = c.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
                db_counts[tbl] = cnt
            except Exception:
                db_counts[tbl] = 0
        conn.close()

    # 2. Upload directories
    claim_upload_dirs = []
    upload_files = []
    if uploads_dir.exists():
        for item in uploads_dir.iterdir():
            if item.is_dir() and item.name.startswith("CLM-"):
                claim_upload_dirs.append(item.name)
                for f in item.glob("**/*"):
                    if f.is_file():
                        upload_files.append(str(f.relative_to(repo_root)))

    # 3. Report files to clean (claim-specific only)
    claim_report_items = []
    if reports_dir.exists():
        for item in reports_dir.iterdir():
            if (
                item.name.startswith("CLM-")
                or item.name.startswith("document_report_")
                or item.name.startswith("receipt_")
                or "report_UOMH" in item.name
                or item.name in {"final_validation_report.pdf", "rendered"}
            ):
                claim_report_items.append(item.name)

    return {
        "db_counts": db_counts,
        "claim_upload_dirs": sorted(claim_upload_dirs),
        "upload_files_count": len(upload_files),
        "claim_report_items": sorted(claim_report_items),
    }


def create_safety_backup(repo_root: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = repo_root / "backups" / f"pre_cleanup_backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Backup SQLite DB
    db_src = repo_root / "data" / "claimsense.db"
    db_dst = backup_dir / "claimsense.db"
    if db_src.exists():
        src_conn = sqlite3.connect(db_src)
        dst_conn = sqlite3.connect(db_dst)
        src_conn.backup(dst_conn)
        dst_conn.close()
        src_conn.close()

    # Backup Uploads
    uploads_src = repo_root / "uploads"
    uploads_dst = backup_dir / "uploads"
    uploads_dst.mkdir(parents=True, exist_ok=True)
    if uploads_src.exists():
        for d in uploads_src.iterdir():
            if d.is_dir() and d.name.startswith("CLM-"):
                shutil.copytree(d, uploads_dst / d.name)

    # Backup Reports
    reports_src = repo_root / "reports"
    reports_dst = backup_dir / "reports"
    reports_dst.mkdir(parents=True, exist_ok=True)
    if reports_src.exists():
        for item in reports_src.iterdir():
            if (
                item.name.startswith("CLM-")
                or item.name.startswith("document_report_")
                or item.name.startswith("receipt_")
                or "report_UOMH" in item.name
                or item.name in {"final_validation_report.pdf", "rendered"}
            ):
                if item.is_dir():
                    shutil.copytree(item, reports_dst / item.name)
                else:
                    shutil.copy2(item, reports_dst / item.name)

    manifest = {
        "timestamp": timestamp,
        "backup_path": str(backup_dir),
        "db_size": db_dst.stat().st_size if db_dst.exists() else 0,
        "backed_up_upload_dirs": len(list(uploads_dst.iterdir())),
        "backed_up_report_items": len(list(reports_dst.iterdir())),
    }
    (backup_dir / "backup_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return backup_dir


def execute_claim_cleanup(repo_root: Path) -> Dict[str, Any]:
    db_path = repo_root / "data" / "claimsense.db"
    uploads_dir = repo_root / "uploads"
    reports_dir = repo_root / "reports"

    # 1. Clean database records
    deleted_db_counts = {}
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON;")
        for tbl in [
            "extracted_information",
            "documents",
            "claim_images",
            "image_analysis",
            "reports",
            "risk_assessments",
            "verification_results",
            "claims",
        ]:
            try:
                cnt = c.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
                c.execute(f"DELETE FROM {tbl};")
                deleted_db_counts[tbl] = cnt
            except Exception as e:
                deleted_db_counts[tbl] = 0
        conn.commit()
        conn.close()

    # 2. Clean upload directories
    deleted_upload_dirs = 0
    deleted_upload_files = 0
    if uploads_dir.exists():
        for item in list(uploads_dir.iterdir()):
            if item.is_dir() and item.name.startswith("CLM-"):
                files_count = len(list(item.glob("**/*")))
                shutil.rmtree(item)
                deleted_upload_dirs += 1
                deleted_upload_files += files_count

    # 3. Clean claim-specific report items
    deleted_report_items = 0
    if reports_dir.exists():
        for item in list(reports_dir.iterdir()):
            if (
                item.name.startswith("CLM-")
                or item.name.startswith("document_report_")
                or item.name.startswith("receipt_")
                or "report_UOMH" in item.name
                or item.name in {"final_validation_report.pdf", "rendered"}
            ):
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                deleted_report_items += 1

    return {
        "deleted_db_counts": deleted_db_counts,
        "deleted_upload_dirs": deleted_upload_dirs,
        "deleted_upload_files": deleted_upload_files,
        "deleted_report_items": deleted_report_items,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ClaimSense AI Claim Cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Display deletion targets without removing files")
    parser.add_argument("--execute", action="store_true", help="Execute deletion")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    targets = identify_claim_targets(root)

    if args.dry_run:
        print("=== DRY RUN SUMMARY ===")
        print(json.dumps(targets, indent=2))
    elif args.execute:
        backup = create_safety_backup(root)
        result = execute_claim_cleanup(root)
        print("=== CLEANUP COMPLETED ===")
        print("Backup created at:", backup)
        print(json.dumps(result, indent=2))
