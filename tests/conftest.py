"""
Pytest configuration and test fixtures.
"""

from pathlib import Path
import cv2
import numpy as np
import pytest


@pytest.fixture
def sample_image() -> np.ndarray:
    """Creates a 200x200 3-channel synthetic test image with colorful geometry."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    # Background gradient
    for i in range(200):
        img[i, :, 0] = int((i / 200) * 255)
        img[:, i, 1] = int((i / 200) * 200)
    # Geometric shapes with distinct edges
    cv2.circle(img, (100, 100), 50, (0, 0, 255), -1)
    cv2.rectangle(img, (20, 20), (70, 70), (0, 255, 0), -1)
    cv2.line(img, (0, 0), (200, 200), (255, 255, 255), 3)
    return img


@pytest.fixture
def sample_image_file(sample_image: np.ndarray, tmp_path: Path) -> Path:
    """Saves the sample image to a temporary file."""
    file_path = tmp_path / "test_sample.png"
    cv2.imwrite(str(file_path), sample_image)
    return file_path
