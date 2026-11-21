"""
Easy Cartoonify: Production-ready image cartoonization library, CLI, and REST API.
"""

from easy_cartoonify.models import CartoonConfig, CartoonStyle
from easy_cartoonify.exceptions import (
    EasyCartoonifyError,
    ImageNotFoundError,
    ImageLoadError,
    ImageSaveError,
    InvalidConfigError,
    ProcessingError,
)
from easy_cartoonify.finder import find_image, find_images
from easy_cartoonify.core import (
    Cartoonifier,
    cartoonify,
    load_image,
    save_image,
)

__version__ = "2.0.0"
__author__ = "Easy Cartoonify Contributors"
__all__ = [
    "CartoonConfig",
    "CartoonStyle",
    "Cartoonifier",
    "cartoonify",
    "find_image",
    "find_images",
    "load_image",
    "save_image",
    "EasyCartoonifyError",
    "ImageNotFoundError",
    "ImageLoadError",
    "ImageSaveError",
    "InvalidConfigError",
    "ProcessingError",
]
