"""Тест запуска скрипта start.sh."""

import pathlib


def test_start_script_uses_python3():
    script = pathlib.Path('start.sh').read_text()
    assert 'python3' in script
    assert '--algorithm' in script
