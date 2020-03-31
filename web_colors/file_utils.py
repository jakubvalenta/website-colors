from pathlib import Path


def write_text_if_different(path: Path, text: str):
    if not path.is_file() or path.read_text().strip() != text.strip():
        path.write_text(text)
