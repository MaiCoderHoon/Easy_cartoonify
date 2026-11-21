"""
Command Line Interface (CLI) for Easy Cartoonify.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

import cv2

from easy_cartoonify import __version__
from easy_cartoonify.core import Cartoonifier, cartoonify, load_image, save_image
from easy_cartoonify.exceptions import EasyCartoonifyError, ImageNotFoundError
from easy_cartoonify.finder import find_image, sanitize_path_input
from easy_cartoonify.models import CartoonConfig, CartoonStyle

logger = logging.getLogger("easy_cartoonify")


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def show_image_preview(image_data, window_name: str = "Cartoon Preview") -> None:
    """Safely display an OpenCV GUI window, handling headless failures gracefully."""
    try:
        cv2.imshow(window_name, image_data)
        print("Press any key in the image window to continue...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as exc:
        print(f"Notice: GUI preview unavailable ({exc}). Proceeding headlessly.")


def run_interactive() -> int:
    """Interactive wizard maintaining backward-compatible terminal flow with robust error handling."""
    print("=" * 60)
    print(f" Easy Cartoonify v{__version__} - Interactive Studio")
    print("=" * 60)

    try:
        raw_input = input("Please enter the image file name or path: ")
        image_name = sanitize_path_input(raw_input)
        if not image_name:
            print("Error: No image name provided.")
            return 1

        candidate = Path(image_name)
        if candidate.is_file():
            image_path = candidate.resolve()
            print(f"Found image: {image_path}")
        else:
            raw_dir = input("Please enter search directory (press Enter for current folder '.'): ")
            search_dir = sanitize_path_input(raw_dir) or "."

            print(f"\nLocating '{image_name}'...")
            try:
                image_path = find_image(image_name, search_dir=search_dir)
                print(f"Found image: {image_path}")
            except ImageNotFoundError as err:
                print(f"Error: {err}")
                return 1

        print("\nAvailable Cartoon Styles:")
        print("  1. Smooth Painterly Cartoon (Style 1 - Classic legacy)")
        print("  2. Crisp Vibrant Cartoon   (Style 2 - High edge contrast)")
        print("  3. Classic Comic Book      (Style 3 - Bilateral + Ink Outlines)")
        print("  4. Pencil Sketch B&W       (Style 4 - Graphite pencil)")
        print("  5. Color Pencil Sketch     (Style 5 - Colored pencil art)")
        print("  6. Edge Preserving Smooth  (Style 6 - Photography art)")

        style_choice = input("\nSelect style (1-6, default: 1): ").strip() or "1"
        try:
            selected_style = CartoonStyle.from_input(style_choice)
        except Exception:
            print(f"Invalid selection '{style_choice}', defaulting to Style 1.")
            selected_style = CartoonStyle.STYLE_1

        default_out = image_path.parent / f"{image_path.stem}_cartoon_{selected_style.value}{image_path.suffix}"
        out_prompt = input(f"Output path (press Enter for '{default_out.name}'): ").strip()
        out_path = Path(out_prompt) if out_prompt else default_out

        preview_prompt = input("Preview result in GUI window? [y/N]: ").strip().lower()
        should_preview = preview_prompt in ("y", "yes")

        print("\nProcessing image...")
        cfg = CartoonConfig.default_for_style(selected_style)
        engine = Cartoonifier(cfg)
        result = engine.process(image_path)

        saved = save_image(result, out_path)
        print(f"Success! Output saved to: {saved.resolve()}")

        if should_preview:
            show_image_preview(result, f"Easy Cartoonify - {selected_style.value}")

        return 0

    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled by user.")
        return 130
    except Exception as exc:
        print(f"\nError: {exc}")
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="easy-cartoonify",
        description="Easy Cartoonify: Convert images into cartoon, comic book, and sketch aesthetics.",
    )
    parser.add_argument(
        "-i", "--input",
        help="Path to input image file",
        default=None,
    )
    parser.add_argument(
        "-o", "--output",
        help="Destination path for cartoonified image (default: <input>_cartoon.<ext>)",
        default=None,
    )
    parser.add_argument(
        "-n", "--name",
        help="Image file name to locate automatically using search directory",
        default=None,
    )
    parser.add_argument(
        "-d", "--dir",
        help="Search directory when using --name (default: '.')",
        default=".",
    )
    parser.add_argument(
        "-s", "--style",
        help="Cartoon style: 1/smooth, 2/vibrant, 3/classic, 4/pencil_gray, 5/pencil_color, 6/edge_preserve",
        default="style_1",
    )
    parser.add_argument(
        "--batch",
        help="Directory of images to batch process",
        default=None,
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Display GUI window with preview",
    )
    parser.add_argument(
        "--sigma-s",
        type=float,
        default=None,
        help="Spatial smoothness factor (0-500)",
    )
    parser.add_argument(
        "--sigma-r",
        type=float,
        default=None,
        help="Color range smoothness factor (0.0-1.0)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Force interactive wizard mode",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose debug logging",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"easy-cartoonify {__version__}",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entrypoint."""
    if argv is None:
        argv = sys.argv[1:]

    # Run interactive wizard if no arguments provided or --interactive is set
    if len(argv) == 0 or "--interactive" in argv:
        return run_interactive()

    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(args.verbose)

    try:
        style = CartoonStyle.from_input(args.style)
        config = CartoonConfig.default_for_style(style)
        if args.sigma_s is not None:
            config.sigma_s = args.sigma_s
        if args.sigma_r is not None:
            config.sigma_r = args.sigma_r

        engine = Cartoonifier(config)

        # Batch mode
        if args.batch:
            batch_dir = Path(args.batch).resolve()
            if not batch_dir.is_dir():
                logger.error("Batch path is not a directory: %s", batch_dir)
                return 1

            out_dir = Path(args.output).resolve() if args.output else batch_dir / "cartoon_output"
            extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
            images = [p for p in batch_dir.iterdir() if p.suffix.lower() in extensions]

            if not images:
                logger.warning("No image files found in %s", batch_dir)
                return 0

            logger.info("Batch processing %d images into %s...", len(images), out_dir)
            processed = engine.process_batch(images, out_dir, config=config)
            print(f"Processed {len(processed)} images successfully.")
            return 0

        # Locate image path
        if args.input:
            target_path = Path(args.input).resolve()
        elif args.name:
            target_path = find_image(args.name, search_dir=args.dir)
        else:
            logger.error("Please specify --input <path> or --name <filename> (or run with no arguments for interactive mode).")
            return 1

        out_path = engine.process_file(target_path, output_path=args.output, config=config)
        print(f"Success: Saved cartoonified image to {out_path}")

        if args.preview:
            res_img = load_image(out_path)
            show_image_preview(res_img)

        return 0

    except EasyCartoonifyError as err:
        logger.error("%s", err)
        return 1
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
