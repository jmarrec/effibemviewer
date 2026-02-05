#!/usr/bin/env python
"""Tests for `effibemviewer` CLI."""

import subprocess


def test_cli_cdn_flag_produces_cdn_urls(tmp_path):
    """Test that --cdn flag produces HTML with CDN URLs."""
    output_file = tmp_path / "test.html"
    result = subprocess.run(
        ["python", "-m", "effibemviewer", "--cdn", "--loader", "-o", str(output_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert output_file.exists()

    html = output_file.read_text()
    assert "cdn.jsdelivr.net/gh/jmarrec/effibemviewer@v" in html
    assert "/public/cdn/effibemviewer.js" in html
    assert "/public/cdn/effibemviewer.css" in html


def test_cli_cdn_and_embedded_mutually_exclusive(tmp_path):
    """Test that --cdn and --embedded flags are mutually exclusive."""
    output_file = tmp_path / "test.html"
    result = subprocess.run(
        ["python", "-m", "effibemviewer", "--cdn", "--embedded", "--loader", "-o", str(output_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "not allowed with argument" in result.stderr


def test_cli_cdn_does_not_generate_local_files(tmp_path):
    """Test that --cdn flag does not generate local JS/CSS files."""
    output_file = tmp_path / "test.html"
    result = subprocess.run(
        ["python", "-m", "effibemviewer", "--cdn", "--loader", "-o", str(output_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Should not generate local JS/CSS files when using CDN
    assert not (tmp_path / "effibemviewer.js").exists()
    assert not (tmp_path / "effibemviewer.css").exists()
