"""
Tests for the FastAPI microservice endpoints.
"""

import io
from pathlib import Path
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from easy_cartoonify.api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "easy-cartoonify"


def test_list_styles_endpoint():
    response = client.get("/api/v1/styles")
    assert response.status_code == 200
    styles = response.json()
    assert len(styles) >= 6
    style_ids = [s["id"] for s in styles]
    assert "style_1" in style_ids
    assert "classic" in style_ids


def test_cartoonify_endpoint(sample_image: np.ndarray):
    # Encode test image to PNG bytes
    success, buffer = cv2.imencode(".png", sample_image)
    assert success

    response = client.post(
        "/api/v1/cartoonify",
        files={"file": ("test.png", buffer.tobytes(), "image/png")},
        data={"style": "classic", "format": "jpeg"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert len(response.content) > 0


def test_cartoonify_invalid_style(sample_image: np.ndarray):
    success, buffer = cv2.imencode(".png", sample_image)
    response = client.post(
        "/api/v1/cartoonify",
        files={"file": ("test.png", buffer.tobytes(), "image/png")},
        data={"style": "invalid_style_name"},
    )
    assert response.status_code == 400
