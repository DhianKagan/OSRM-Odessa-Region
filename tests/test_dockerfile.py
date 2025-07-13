"""Тест Dockerfile на создание файла .stxxl."""
from pathlib import Path

def test_stxxl_created():
    dockerfile = Path('Dockerfile').read_text()
    assert "disk=/tmp/stxxl,10G,syscall" in dockerfile
    assert "COPY .stxxl" not in dockerfile
