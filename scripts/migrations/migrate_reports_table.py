"""Safe forward and rollback migration for reports table in ClaimSense AI.

Conforms to Phase 10 Stage 2 ADR (runs/phase10/stage2_database_architecture_decision.md).
"""
import sys
from pathlib import Path

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import inspect, text
from backend.database.db import get_engine, init_database
from backend.config import Config


def upgrade(engine=None):
    """Apply forward schema migrations for reports table."""
    if engine is None:
        engine = init_database(Config.SQLALCHEMY_DATABASE_URI)

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "reports" not in table_names:
        print("[MIGRATE] 'reports' table does not exist. Creating schema...")
        from backend.database.models import Base
        Base.metadata.create_all(bind=engine)
        print("[MIGRATE] Schema created successfully.")
        return

    columns = {col["name"] for col in inspector.get_columns("reports")}
    migrations = {
        "report_type": "VARCHAR(32) NOT NULL DEFAULT 'VERIFICATION_AUDIT'",
        "file_hash": "VARCHAR(64)",
        "file_size_bytes": "INTEGER",
        "generated_by": "INTEGER REFERENCES users(id)",
        "status": "VARCHAR(32) NOT NULL DEFAULT 'ACTIVE'",
    }

    added = 0
    with engine.begin() as conn:
        for col_name, ddl in migrations.items():
            if col_name not in columns:
                conn.execute(text(f"ALTER TABLE reports ADD COLUMN {col_name} {ddl}"))
                print(f"[MIGRATE] Added column: reports.{col_name}")
                added += 1

    print(f"[MIGRATE] Forward migration complete. {added} column(s) added.")


def downgrade(engine=None):
    """Roll back reports table to legacy schema."""
    if engine is None:
        engine = init_database(Config.SQLALCHEMY_DATABASE_URI)

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS reports_backup (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id VARCHAR(32) NOT NULL REFERENCES claims(claim_id),
                report_path VARCHAR(512) NOT NULL,
                created_at DATETIME NOT NULL
            );
        """))
        conn.execute(text("""
            INSERT INTO reports_backup (id, claim_id, report_path, created_at)
            SELECT id, claim_id, report_path, created_at FROM reports;
        """))
        conn.execute(text("DROP TABLE reports;"))
        conn.execute(text("ALTER TABLE reports_backup RENAME TO reports;"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_reports_claim_id ON reports(claim_id);"))

    print("[MIGRATE] Rollback migration complete. Reverted reports table to legacy schema.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Migrate reports table")
    parser.add_argument("--downgrade", action="store_true", help="Rollback migration")
    args = parser.parse_args()

    if args.downgrade:
        downgrade()
    else:
        upgrade()
