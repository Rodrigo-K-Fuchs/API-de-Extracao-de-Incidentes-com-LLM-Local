import sys
from pathlib import Path
import pytest
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from core.text_preprocessor import TextPreprocessor


@pytest.fixture
def fixed_reference_date():
    return datetime(2026, 2, 23)


@pytest.fixture
def preprocessor(fixed_reference_date):
    return TextPreprocessor(reference_date=fixed_reference_date)