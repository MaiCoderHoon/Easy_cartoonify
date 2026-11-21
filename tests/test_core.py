"""
Unit tests for the core cartoonification algorithms and transformations.
"""

from pathlib import Path
import numpy as np
import pytest

from easy_cartoonify.core import (
    Cartoonifier,
    cartoonify,
    load_image,
    save_image,
)
from easy_cartoonify.exceptions import (
    ImageLoadError,
    ImageSaveError,
    InvalidConfigError,
)
from easy_cartoonify.models import CartoonConfig, CartoonStyle


def test_load_image_from_numpy(sample_image: np.ndarray):
    loaded = load_image(sample_image)
    assert isinstance(loaded, np.ndarray)
    assert loaded.shape == sample_image.shape


def test_load_image_from_bytes(sample_image_file: Path):
    raw_data = sample_image_file.read_bytes()
    loaded = load_image(raw_data)
    assert isinstance(loaded, np.ndarray)
    assert loaded.shape[2] == 3


def test_load_image_invalid_file(tmp_path: Path):
    with pytest.raises(ImageLoadError):
        load_image(tmp_path / "non_existent.jpg")


def test_save_image(sample_image: np.ndarray, tmp_path: Path):
    out = tmp_path / "sub" / "output.jpg"
    saved_path = save_image(sample_image, out)
    assert saved_path.exists()
    assert saved_path.stat().st_size > 0


@pytest.mark.parametrize(
    "style",
    [
        CartoonStyle.STYLE_1,
        CartoonStyle.STYLE_2,
        CartoonStyle.CLASSIC,
        CartoonStyle.PENCIL_GRAY,
        CartoonStyle.PENCIL_COLOR,
        CartoonStyle.EDGE_PRESERVE,
    ],
)
def test_all_cartoon_styles(sample_image: np.ndarray, style: CartoonStyle):
    cfg = CartoonConfig.default_for_style(style)
    engine = Cartoonifier(cfg)
    result = engine.process(sample_image)

    assert isinstance(result, np.ndarray)
    assert result.shape[:2] == sample_image.shape[:2]
    assert result.shape[2] == 3


def test_cartoonify_convenience_function(sample_image_file: Path, tmp_path: Path):
    out_file = tmp_path / "result.png"
    result = cartoonify(sample_image_file, style="classic", output_path=out_file)

    assert isinstance(result, np.ndarray)
    assert out_file.exists()


def test_batch_processing(sample_image_file: Path, tmp_path: Path):
    img1 = tmp_path / "img1.png"
    img2 = tmp_path / "img2.png"
    img1.write_bytes(sample_image_file.read_bytes())
    img2.write_bytes(sample_image_file.read_bytes())

    out_dir = tmp_path / "batch_out"
    engine = Cartoonifier()
    saved = engine.process_batch([img1, img2], out_dir)

    assert len(saved) == 2
    assert all(p.exists() for p in saved)


def test_invalid_config():
    with pytest.raises(InvalidConfigError):
        CartoonConfig(sigma_s=-10.0)

    with pytest.raises(InvalidConfigError):
        CartoonConfig(edge_block_size=4)  # Must be odd
