"""
Core image processing engine for Easy Cartoonify.
"""

import logging
from pathlib import Path
from typing import List, Optional, Sequence, Union
import cv2
import numpy as np

from easy_cartoonify.exceptions import (
    ImageLoadError,
    ImageSaveError,
    ProcessingError,
)
from easy_cartoonify.models import CartoonConfig, CartoonStyle

logger = logging.getLogger(__name__)


def load_image(source: Union[str, Path, bytes, np.ndarray]) -> np.ndarray:
    """
    Load an image from a file path, bytes, or numpy array.

    Returns:
        np.ndarray: BGR image array with uint8 dtype.

    Raises:
        ImageLoadError: If loading fails or image is empty/corrupt.
    """
    if isinstance(source, np.ndarray):
        if source.size == 0:
            raise ImageLoadError("Input numpy image array is empty.")
        if source.dtype != np.uint8:
            source = source.astype(np.uint8)
        if len(source.shape) == 2:
            return cv2.cvtColor(source, cv2.COLOR_GRAY2BGR)
        elif len(source.shape) == 3:
            if source.shape[2] == 4:
                return cv2.cvtColor(source, cv2.COLOR_BGRA2BGR)
            return source
        raise ImageLoadError(f"Unsupported image array shape: {source.shape}")

    if isinstance(source, (bytes, bytearray)):
        if len(source) == 0:
            raise ImageLoadError("Image byte buffer is empty.")
        arr = np.frombuffer(source, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ImageLoadError("Failed to decode image from byte buffer.")
        return img

    path = Path(source)
    if not path.exists():
        raise ImageLoadError(f"Image file does not exist: {path}")
    if not path.is_file():
        raise ImageLoadError(f"Specified path is not a file: {path}")

    # Read file bytes safely to handle Unicode paths and detect virtual/cloud placeholder files
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        err_msg = str(exc)
        if "crossdevice" in str(path).lower() or exc.errno == 22:
            raise ImageLoadError(
                f"Cannot access image '{path.name}' on your connected phone ({path}).\n"
                f"Windows Phone Link / CrossDevice is not synced or your phone is locked/disconnected.\n"
                f"Solution: Please unlock your phone and open Phone Link, or copy the image directly to your PC (e.g. Pictures or Desktop) first."
            ) from exc
        raise ImageLoadError(f"Failed to read image '{path}': {err_msg}") from exc

    if len(raw_bytes) == 0:
        raise ImageLoadError(f"Image file is empty (0 bytes): {path}")

    arr = np.frombuffer(raw_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is None:
        raise ImageLoadError(f"OpenCV could not decode image format for: {path}")

    return img


def save_image(
    image: np.ndarray,
    output_path: Union[str, Path],
    quality: int = 95,
) -> Path:
    """
    Save an image array to the specified destination path.

    Creates missing directories automatically and handles Unicode paths safely.
    """
    if image is None or image.size == 0:
        raise ImageSaveError("Cannot save an empty or None image array.")

    target_path = Path(output_path).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    ext = target_path.suffix.lower()
    params = []
    if ext in (".jpg", ".jpeg"):
        params = [int(cv2.IMWRITE_JPEG_QUALITY), max(1, min(100, quality))]
    elif ext == ".png":
        params = [int(cv2.IMWRITE_PNG_COMPRESSION), 3]
    elif ext == ".webp":
        params = [int(cv2.IMWRITE_WEBP_QUALITY), max(1, min(100, quality))]

    try:
        success, encoded_img = cv2.imencode(ext if ext else ".jpg", image, params)
        if not success:
            raise ImageSaveError(f"Failed to encode image to format: {ext}")
        encoded_img.tofile(str(target_path))
    except Exception as exc:
        raise ImageSaveError(f"Could not write image to '{target_path}': {exc}") from exc

    logger.info("Saved cartoonified image to: %s", target_path)
    return target_path


class Cartoonifier:
    """
    Production-grade image cartoonization engine supporting multiple aesthetics.
    """

    def __init__(self, config: Optional[CartoonConfig] = None) -> None:
        self.config = config or CartoonConfig()

    def process(
        self,
        image_input: Union[str, Path, bytes, np.ndarray],
        config: Optional[CartoonConfig] = None,
    ) -> np.ndarray:
        """
        Process an image into a cartoonified representation.
        """
        cfg = config or self.config
        img = load_image(image_input)

        try:
            if cfg.style in (CartoonStyle.STYLE_1, CartoonStyle.STYLE_2):
                return self._style_stylization(img, cfg)
            elif cfg.style == CartoonStyle.CLASSIC:
                return self._style_classic(img, cfg)
            elif cfg.style == CartoonStyle.PENCIL_GRAY:
                return self._style_pencil(img, cfg, color=False)
            elif cfg.style == CartoonStyle.PENCIL_COLOR:
                return self._style_pencil(img, cfg, color=True)
            elif cfg.style == CartoonStyle.EDGE_PRESERVE:
                return self._style_edge_preserving(img, cfg)
            else:
                raise ProcessingError(f"Unhandled cartoon style: {cfg.style}")
        except Exception as exc:
            if isinstance(exc, (ProcessingError, ImageLoadError)):
                raise
            raise ProcessingError(f"Error during cartoonization: {exc}") from exc

    def process_file(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        config: Optional[CartoonConfig] = None,
        quality: int = 95,
    ) -> Path:
        """
        Transform a file and write the result to output_path.
        If output_path is omitted, appends '_cartoon' to the original filename.
        """
        input_p = Path(input_path).resolve()
        result_img = self.process(input_p, config=config)

        if output_path is None:
            output_p = input_p.parent / f"{input_p.stem}_cartoon{input_p.suffix}"
        else:
            output_p = Path(output_path).resolve()

        return save_image(result_img, output_p, quality=quality)

    def process_batch(
        self,
        input_paths: Sequence[Union[str, Path]],
        output_dir: Union[str, Path],
        config: Optional[CartoonConfig] = None,
        quality: int = 95,
    ) -> List[Path]:
        """
        Process a collection of images and save them into output_dir.
        """
        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        results: List[Path] = []

        for p in input_paths:
            path_obj = Path(p)
            target = out_dir / f"{path_obj.stem}_cartoon{path_obj.suffix}"
            saved = self.process_file(path_obj, output_path=target, config=config, quality=quality)
            results.append(saved)

        return results

    # Pipeline implementations
    @staticmethod
    def _style_stylization(img: np.ndarray, cfg: CartoonConfig) -> np.ndarray:
        return cv2.stylization(img, sigma_s=float(cfg.sigma_s), sigma_r=float(cfg.sigma_r))

    @staticmethod
    def _style_classic(img: np.ndarray, cfg: CartoonConfig) -> np.ndarray:
        # 1. Bilateral filter smoothing passes for color posterization
        color = img.copy()
        for _ in range(cfg.bilateral_passes):
            color = cv2.bilateralFilter(
                color,
                d=cfg.bilateral_d,
                sigmaColor=cfg.bilateral_sigma_color,
                sigmaSpace=cfg.bilateral_sigma_space,
            )

        # 2. Extract edges with grayscale median blur + adaptive thresholding
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(
            gray_blur,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            blockSize=cfg.edge_block_size,
            C=cfg.edge_c,
        )
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # 3. Combine color smooth image with crisp comic edge lines
        return cv2.bitwise_and(color, edges_bgr)

    @staticmethod
    def _style_pencil(img: np.ndarray, cfg: CartoonConfig, color: bool = False) -> np.ndarray:
        gray_sketch, color_sketch = cv2.pencilSketch(
            img,
            sigma_s=float(cfg.sketch_sigma_s),
            sigma_r=float(cfg.sketch_sigma_r),
            shade_factor=float(cfg.sketch_shade_factor),
        )
        if color:
            return color_sketch
        return cv2.cvtColor(gray_sketch, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def _style_edge_preserving(img: np.ndarray, cfg: CartoonConfig) -> np.ndarray:
        return cv2.edgePreservingFilter(
            img,
            flags=cv2.RECURS_FILTER,
            sigma_s=float(cfg.sigma_s),
            sigma_r=float(cfg.sigma_r),
        )


def cartoonify(
    image: Union[str, Path, bytes, np.ndarray],
    style: Union[str, int, CartoonStyle] = CartoonStyle.STYLE_1,
    output_path: Optional[Union[str, Path]] = None,
    **config_kwargs,
) -> np.ndarray:
    """
    Convenience function to cartoonify an image in a single call.

    Args:
        image: File path, bytes, or numpy BGR image array.
        style: CartoonStyle or string name ("style_1", "style_2", "classic", etc.)
        output_path: Optional file path to write the output image to.
        **config_kwargs: Override configuration parameters (sigma_s, sigma_r, etc.)

    Returns:
        np.ndarray: Cartoonified BGR image.
    """
    base_config = CartoonConfig.default_for_style(style)
    for k, v in config_kwargs.items():
        if hasattr(base_config, k):
            setattr(base_config, k, v)

    engine = Cartoonifier(base_config)
    result = engine.process(image)

    if output_path is not None:
        save_image(result, output_path)

    return result
