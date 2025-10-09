import re
from pathlib import Path

import pytest

from checklist_lite_review import (
    check_signal,
    section_status,
    update_checklist_progress,
    review_progress,
)


def test_check_signal_markdown(tmp_path):
    # create a minimal markdown file with a paragraph so the docs check passes
    f = tmp_path / "sample.md"
    f.write_text(
        """
This is a paragraph.

```python
print('hello')
```
""",
        encoding="utf-8",
    )

    signal = {"type": "file", "path": str(f)}
    assert check_signal(signal) is True


def test_section_status_ai_core_main_missing(tmp_path):
    # Simulate AI Core signals where main.py is missing but another signal exists
    dir_path = tmp_path / "some_dir"
    dir_path.mkdir()
    # create a small non-empty file to satisfy a dir signal
    (dir_path / "x.txt").write_text("content", encoding="utf-8")

    signals = [
        {"type": "dir", "path": str(dir_path)},
        {"type": "file", "path": str(tmp_path / "nonexistent_main.py")},
    ]

    status = section_status(signals)
    # since one signal (dir) is True and main.py check fails, AI Core should be at least started (🟨)
    assert status in ("🟨", "🟩")


def test_update_checklist_progress_updates_percent_and_formula(tmp_path):
    # create a fake checklist file with two markers (1 green, 1 red)
    content = (
        '<progress id="shieldcraft-progress" value="0" max="100"></progress>\n'
        '<div id="progress-label">0% Complete</div>\n'
        "\n"
        "Section A - status: 🟩\n"
        "Section B - status: 🟥\n"
        '<strong style="color:#a5b4fc;">Progress Formula:</strong> 1 complete / (1 complete + 1 remaining) = 50%.<br>\n'
    )
    p = tmp_path / "checklist.md"
    p.write_text(content, encoding="utf-8")

    # Call updater (progress arg is ignored by the function)
    update_checklist_progress(p, None)

    new = p.read_text(encoding="utf-8")
    # percent should be 50
    assert re.search(r">50% Complete<", new) or ">50% Complete</div>" in new
    # progress bar value attribute should be updated to 50
    assert re.search(r'value="50"', new)
    # formula should be rewritten to reflect counts (1 complete + 1 remaining)
    assert "1 complete / (1 complete + 1 remaining) = 50%" in new


def test_check_signal_dir_empty_and_nonempty(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()
    # create empty file (size 0)
    empty = d / "empty.txt"
    empty.write_bytes(b"")

    sig = {"type": "dir", "path": str(d)}
    assert check_signal(sig) is False

    # write non-empty file
    empty.write_text("hi", encoding="utf-8")
    assert check_signal(sig) is True


def test_check_signal_test_file_detection(tmp_path):
    f = tmp_path / "test_sample.py"
    f.write_text(
        "def test_example():\n    assert 1 == 1\n",
        encoding="utf-8",
    )
    sig = {"type": "test", "path": str(f)}
    assert check_signal(sig) is True

    # file without test function
    g = tmp_path / "notest.py"
    g.write_text("print('hello')\n", encoding="utf-8")
    sig2 = {"type": "test", "path": str(g)}
    assert check_signal(sig2) is False


def test_update_checklist_progress_no_markers(tmp_path):
    content = (
        '<progress id="shieldcraft-progress" value="0" max="100"></progress>\n'
        '<div id="progress-label">0% Complete</div>\n'
        "\n"
        "No statuses here.\n"
        '<strong style="color:#a5b4fc;">Progress Formula:</strong> none yet<br>\n'
    )
    p = tmp_path / "checklist2.md"
    p.write_text(content, encoding="utf-8")
    # Should not raise
    update_checklist_progress(p, None)
    new = p.read_text(encoding="utf-8")
    assert ">0% Complete<" in new or ">0% Complete</div>" in new


def test_review_progress_monkeypatched(monkeypatch):
    # Monkeypatch check_signal to return True for files named 'ok' and False otherwise
    def fake_check_signal(s):
        p = s.get("path", "")
        return "ok" in p

    monkeypatch.setattr("checklist_lite_review.check_signal", fake_check_signal)

    fake_sections = {
        "S1": [{"type": "file", "path": "some/ok_file.py"}],
        "S2": [{"type": "file", "path": "some/bad_file.py"}],
    }
    summary = review_progress(fake_sections)
    assert summary["S1"] == "🟩"
    assert summary["S2"] == "🟥"
