import json
from pathlib import Path


def get_session_root(session_id, base_dir=None):
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent

    session_root = Path(base_dir) / "sessions" / str(session_id)
    session_root.mkdir(parents=True, exist_ok=True)
    return session_root


def get_session_paths(session_id, base_dir=None):
    session_root = get_session_root(session_id, base_dir=base_dir)
    resume_index_path = session_root / "resume_faiss_index"
    jd_index_path = session_root / "jd_faiss_index"
    metadata_path = session_root / "metadata.json"
    return resume_index_path, jd_index_path, metadata_path


def index_exists(index_path):
    index_path = Path(index_path)
    return (
        (index_path / "index.faiss").is_file()
        and (index_path / "index.pkl").is_file()
    )


def write_metadata(session_id, payload, base_dir=None):
    session_root = get_session_root(session_id, base_dir=base_dir)
    metadata_path = session_root / "metadata.json"

    existing = {}
    if metadata_path.exists():
        try:
            existing = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}

    existing.update(payload)
    metadata_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    return metadata_path


def read_metadata(session_id, base_dir=None):
    _, _, metadata_path = get_session_paths(session_id, base_dir=base_dir)
    if not metadata_path.exists():
        return {}

    try:
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
