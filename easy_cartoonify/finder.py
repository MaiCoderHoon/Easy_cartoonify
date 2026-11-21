"""
High-performance, safe image discovery utilities.
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Union
from easy_cartoonify.exceptions import ImageNotFoundError

logger = logging.getLogger(__name__)

COMMON_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif"}


def sanitize_path_input(raw: Union[str, Path]) -> str:
    """Clean raw CLI or terminal input, stripping PowerShell '& ' prefixes, quotes, and whitespace."""
    s = str(raw).strip()
    if s.startswith("&"):
        s = s[1:].strip()
    return s.strip("\"'").strip()


def find_image(
    filename: Union[str, Path],
    search_dir: Union[str, Path] = ".",
    recursive: bool = True,
    max_depth: Optional[int] = 12,
    case_sensitive: bool = False,
) -> Path:
    """
    Search for an image by name starting from search_dir and return its resolved Path.

    Exits immediately upon finding the first match for maximum speed.
    Does NOT change the current working directory, preventing side effects.

    Args:
        filename: Name of the file (e.g. 'cat.jpg', or 'cat' if extension is unknown)
        search_dir: Root directory to begin the search from (default: current directory)
        recursive: Whether to search subdirectories recursively (default: True)
        max_depth: Maximum directory recursion depth (default: 12)
        case_sensitive: Whether matching should be case-sensitive (default: False)

    Returns:
        Path: Resolved absolute path to the found image.

    Raises:
        ImageNotFoundError: If the image is not found or search_dir does not exist.
    """
    # Clean potential PowerShell '& ' operators or surrounding quotes
    clean_filename = sanitize_path_input(filename)
    clean_search_dir = sanitize_path_input(search_dir)

    candidate_path = Path(clean_filename)

    # 1. Direct path check
    if candidate_path.is_file():
        logger.debug("Direct path found: %s", candidate_path)
        return candidate_path.resolve()

    # 2. Check search_dir
    root_dir = Path(clean_search_dir if clean_search_dir else ".").expanduser()
    if not root_dir.exists() or not root_dir.is_dir():
        raise ImageNotFoundError(
            f"Search directory '{search_dir}' does not exist or is not a directory."
        )

    target_name = candidate_path.name
    target_stem = candidate_path.stem
    has_ext = bool(candidate_path.suffix)

    if not case_sensitive:
        target_name_cmp = target_name.lower()
        target_stem_cmp = target_stem.lower()
    else:
        target_name_cmp = target_name
        target_stem_cmp = target_stem

    root_depth = len(root_dir.resolve().parts)

    for current_root, dirs, files in os.walk(root_dir, topdown=True, followlinks=False):
        current_path = Path(current_root)
        current_depth = len(current_path.resolve().parts) - root_depth

        if max_depth is not None and current_depth > max_depth:
            dirs.clear()  # Prune further traversal
            continue

        for fname in files:
            fname_cmp = fname if case_sensitive else fname.lower()
            matched = False

            if has_ext:
                if fname_cmp == target_name_cmp:
                    matched = True
            else:
                # Match exact or match stem with common image extensions
                file_stem = Path(fname).stem
                file_stem_cmp = file_stem if case_sensitive else file_stem.lower()
                file_ext = Path(fname).suffix.lower()

                if fname_cmp == target_name_cmp or (
                    file_stem_cmp == target_stem_cmp and file_ext in COMMON_IMAGE_EXTENSIONS
                ):
                    matched = True

            if matched:
                found_path = (current_path / fname).resolve()
                logger.info("Found image at: %s", found_path)
                return found_path

        if not recursive:
            break

    raise ImageNotFoundError(
        f"Image '{filename}' not found in '{search_dir}' (recursive={recursive}, max_depth={max_depth})."
    )


def find_images(
    pattern: str,
    search_dir: Union[str, Path] = ".",
    recursive: bool = True,
    max_depth: Optional[int] = 12,
) -> List[Path]:
    """
    Find all matching images in a directory tree.
    """
    root_dir = Path(search_dir).expanduser()
    if not root_dir.exists() or not root_dir.is_dir():
        raise ImageNotFoundError(f"Search directory '{search_dir}' does not exist.")

    matches: List[Path] = []
    pattern_lower = pattern.lower()
    root_depth = len(root_dir.resolve().parts)

    for current_root, dirs, files in os.walk(root_dir):
        current_path = Path(current_root)
        current_depth = len(current_path.resolve().parts) - root_depth

        if max_depth is not None and current_depth > max_depth:
            dirs.clear()
            continue

        for fname in files:
            if pattern_lower in fname.lower():
                ext = Path(fname).suffix.lower()
                if ext in COMMON_IMAGE_EXTENSIONS:
                    matches.append((current_path / fname).resolve())

        if not recursive:
            break

    return sorted(matches)
