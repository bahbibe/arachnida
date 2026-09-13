import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SCORPION = ROOT / "Scorpion" / "Scorpion.py"


def test_resolve_tag_id_by_name(scorpion_module):
    assert scorpion_module.resolve_tag_id("Artist") == 315


def test_resolve_tag_id_by_number(scorpion_module):
    assert scorpion_module.resolve_tag_id("315") == 315


def test_resolve_tag_id_unknown_raises(scorpion_module):
    with pytest.raises(ValueError):
        scorpion_module.resolve_tag_id("NotARealTag")


def test_set_exif_tag_string_value(scorpion_module):
    exif = Image.Exif()
    scorpion_module.set_exif_tag(exif, "Artist", "Jane Doe")
    assert exif[315] == "Jane Doe"


def test_set_exif_tag_numeric_value_is_coerced_to_int(scorpion_module):
    exif = Image.Exif()
    scorpion_module.set_exif_tag(exif, "Orientation", "1")
    assert exif[274] == 1


def test_delete_exif_tag_removes_existing(scorpion_module):
    exif = Image.Exif()
    exif[315] = "Jane Doe"
    scorpion_module.delete_exif_tag(exif, "Artist")
    assert 315 not in exif


def test_delete_exif_tag_missing_raises(scorpion_module):
    exif = Image.Exif()
    with pytest.raises(ValueError):
        scorpion_module.delete_exif_tag(exif, "Artist")


def test_edit_file_round_trip(scorpion_module, tmp_path):
    img_path = tmp_path / "sample.jpg"
    Image.new("RGB", (10, 10), color="red").save(img_path)

    scorpion_module.edit_file(str(img_path), ["Artist=Jane Doe"], None, False)
    with Image.open(img_path) as img:
        assert img.getexif()[315] == "Jane Doe"

    scorpion_module.edit_file(str(img_path), None, ["Artist"], False)
    with Image.open(img_path) as img:
        assert 315 not in img.getexif()


def test_cli_rejects_all_and_extensions_together(tmp_path):
    img_path = tmp_path / "sample.jpg"
    Image.new("RGB", (5, 5)).save(img_path)
    result = subprocess.run(
        [sys.executable, str(SCORPION), "--all", "-e", ".jpg", str(img_path)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "mutually exclusive" in result.stdout


def test_cli_extension_match_is_case_insensitive(tmp_path):
    img_path = tmp_path / "sample.JPG"
    Image.new("RGB", (5, 5)).save(img_path)
    result = subprocess.run(
        [sys.executable, str(SCORPION), "-e", ".jpg", str(img_path)],
        capture_output=True, text=True,
    )
    assert "not a valid image file" not in result.stdout
