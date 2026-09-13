import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
SPIDER = ROOT / "Spider" / "Spider.py"


def _html_response(html):
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


def test_collect_links_stops_on_cycle(spider_module):
    # a -> b -> a: must not loop forever, must not revisit a.
    pages = {
        "http://a.test/": '<a href="http://b.test/">b</a>',
        "http://b.test/": '<a href="http://a.test/">a</a>',
    }

    def fake_get(url, headers=None, timeout=None):
        return _html_response(pages.get(url, ""))

    with patch("requests.get", side_effect=fake_get), \
         patch("validators.url", return_value=True):
        links = spider_module.collect_links("http://a.test/", level=5)

    assert links.count("http://b.test/") == 1
    assert "http://a.test/" not in links


def test_collect_links_respects_depth(spider_module):
    pages = {
        "http://a.test/": '<a href="http://b.test/">b</a>',
        "http://b.test/": '<a href="http://c.test/">c</a>',
        "http://c.test/": '<a href="http://d.test/">d</a>',
    }

    def fake_get(url, headers=None, timeout=None):
        return _html_response(pages.get(url, ""))

    with patch("requests.get", side_effect=fake_get), \
         patch("validators.url", return_value=True):
        links = spider_module.collect_links("http://a.test/", level=2)

    assert "http://d.test/" not in links


def test_download_images_dedups_by_url_and_basename(spider_module, tmp_path):
    page_html = (
        '<img src="http://img.test/photo.jpg">'
        '<img src="http://img.test/photo.jpg">'
        '<img src="http://other.test/photo.jpg">'
    )

    def fake_get(url, headers=None, timeout=None, stream=False):
        if url == "http://page.test/":
            return _html_response(page_html)
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.iter_content = lambda chunk_size: [b"fakejpegbytes"]
        return resp

    with patch("requests.get", side_effect=fake_get), \
         patch("validators.url", return_value=True):
        count = spider_module.download_images(["http://page.test/"], str(tmp_path))

    assert count == 1
    assert (tmp_path / "photo.jpg").exists()


def test_download_images_rejects_path_traversal_basename(spider_module, tmp_path):
    page_html = '<img src="http://img.test/..">'

    def fake_get(url, headers=None, timeout=None, stream=False):
        return _html_response(page_html)

    with patch("requests.get", side_effect=fake_get), \
         patch("validators.url", return_value=True):
        count = spider_module.download_images(["http://page.test/"], str(tmp_path))

    assert count == 0


def test_cli_rejects_invalid_url():
    result = subprocess.run(
        [sys.executable, str(SPIDER), "not-a-url"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "Invalid URL" in result.stdout


def test_cli_rejects_all_and_extensions_together():
    result = subprocess.run(
        [sys.executable, str(SPIDER), "--all", "-e", ".jpg", "http://example.com"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "mutually exclusive" in result.stdout
