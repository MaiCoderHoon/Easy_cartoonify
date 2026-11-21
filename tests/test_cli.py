"""
Tests for the Command Line Interface.
"""

from pathlib import Path
import pytest
from easy_cartoonify.cli import main


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "easy-cartoonify" in captured.out


def test_cli_process_file(sample_image_file: Path, tmp_path: Path):
    out = tmp_path / "cli_out.jpg"
    code = main([
        "-i", str(sample_image_file),
        "-o", str(out),
        "-s", "classic",
    ])
    assert code == 0
    assert out.exists()


def test_cli_batch(sample_image_file: Path, tmp_path: Path):
    batch_in = tmp_path / "batch_in"
    batch_in.mkdir()
    (batch_in / "pic.png").write_bytes(sample_image_file.read_bytes())

    batch_out = tmp_path / "batch_out"
    code = main([
        "--batch", str(batch_in),
        "-o", str(batch_out),
        "-s", "2",
    ])
    assert code == 0
    assert (batch_out / "pic_cartoon.png").exists()


def test_cli_missing_input():
    code = main(["-s", "1"])
    assert code == 1
