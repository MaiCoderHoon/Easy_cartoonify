"""
Custom exceptions for Easy Cartoonify.
"""


class EasyCartoonifyError(Exception):
    """Base exception for all easy_cartoonify errors."""
    pass


class ImageNotFoundError(EasyCartoonifyError, FileNotFoundError):
    """Raised when the specified image file could not be found."""
    pass


class ImageLoadError(EasyCartoonifyError, ValueError):
    """Raised when an image fails to load or is invalid/corrupted."""
    pass


class ImageSaveError(EasyCartoonifyError, IOError):
    """Raised when an image fails to be written to disk."""
    pass


class InvalidConfigError(EasyCartoonifyError, ValueError):
    """Raised when invalid parameters or style options are provided."""
    pass


class ProcessingError(EasyCartoonifyError, RuntimeError):
    """Raised when an error occurs during OpenCV image processing."""
    pass
