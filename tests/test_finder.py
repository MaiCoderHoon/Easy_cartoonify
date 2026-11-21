"""
Unit tests for the image finder module.
"""

from pathlib import Path
import pytest
from easy_cartoonify.exceptions import ImageNotFoundError
from easy_cartoonify.finder import find_image, find_images


def test_find_image_direct_path(sample_image_file: Path):
    found = find_image(sample_image_file)
    assert found == sample_image_file.resolve()


def test_find_image_in_directory(tmp_path: Path, sample_image_file: Path):
    sub = tmp_path / "nested" / "folder"
    sub.mkdir(parents=True)
    target = sub / "nested_photo.jpg"
    target.write_bytes(sample_image_file.read_bytes())

    found = find_image("nested_photo.jpg", search_dir=tmp_path)
    assert found == target.resolve()


def test_find_image_case_insensitive(tmp_path: Path, sample_image_file: Path):
    target = tmp_path / "MyPicture.PNG"
    target.write_bytes(sample_image_file.read_bytes())

    found = find_image("mypicture.png", search_dir=tmp_path)
    assert found == target.resolve()


def test_find_image_without_extension(tmp_path: Path, sample_image_file: Path):
    target = tmp_path / "avatar.jpg"
    target.write_bytes(sample_image_file.read_bytes())

    found = find_image("avatar", search_dir=tmp_path)
    assert found == target.resolve()


def test_find_image_not_found(tmp_path: Path):
    with pytest.raises(ImageNotFoundError):
        find_image("non_existent_file.png", search_dir=tmp_path)


def test_find_images_pattern(tmp_path: Path, sample_image_file: Path):
    (tmp_path / "pic_1.jpg").write_bytes(sample_image_file.read_bytes())
    (tmp_path / "pic_2.png").write_bytes(sample_image_file.read_bytes())
    (tmp_path / "other.txt").write_text("hello")

    found = find_images("pic", search_dir=tmp_path)
    assert len(found) == 2
