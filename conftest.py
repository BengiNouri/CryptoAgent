# conftest.py
import pytest

@pytest.fixture(autouse=True)
def _chdir_tmp_path(tmp_path, monkeypatch):
    # every test will run with cwd == tmp_path
    monkeypatch.chdir(tmp_path)
