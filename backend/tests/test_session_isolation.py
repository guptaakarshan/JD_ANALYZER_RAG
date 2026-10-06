from pathlib import Path

from rag.session_store import get_session_paths, write_metadata


def test_session_paths_are_isolated(tmp_path):
    session_id = "session-123"

    resume_path, jd_path, metadata_path = get_session_paths(session_id, base_dir=tmp_path)

    assert resume_path.parent.name == session_id
    assert jd_path.parent.name == session_id
    assert resume_path != jd_path
    assert metadata_path.parent.name == session_id
    assert metadata_path.exists() is False

    write_metadata(session_id, {"resume_filename": "resume.pdf"}, base_dir=tmp_path)

    metadata_path = get_session_paths(session_id, base_dir=tmp_path)[2]
    assert metadata_path.exists()

    metadata = metadata_path.read_text(encoding="utf-8")
    assert "resume.pdf" in metadata
