import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def spider_module():
    return _load_module("spider_module", ROOT / "Spider" / "Spider.py")


@pytest.fixture(scope="session")
def scorpion_module():
    return _load_module("scorpion_module", ROOT / "Scorpion" / "Scorpion.py")
