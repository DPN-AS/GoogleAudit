import db
import audit_engine


def test_run_audit_creates_db(tmp_path):
    original = db.DB_PATH
    db.DB_PATH = tmp_path / 'test.db'
    db.init_db()
    results = audit_engine.run_audit()
    assert db.DB_PATH.exists()
    assert results
    db.DB_PATH = original
