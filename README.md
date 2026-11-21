# Easy Cartoonify

[![CI](https://github.com/your-username/Easy_cartoonify/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/Easy_cartoonify/actions)
[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-5.0%2B-5C3EE8)](https://opencv.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A production-grade Python computer vision library, CLI application, and REST API microservice that transforms photos and digital images into high-quality cartoon art, comic book illustrations, and sketches using OpenCV.

---

## What's New in v2.0 (Production Release)

Compared to the initial prototype:

| Feature | Legacy v1.0 | Production v2.0 |
|---|---|---|
| **Architecture** | Single imperative script with side effects | Modular Python package (`easy_cartoonify`) with typed models |
| **Available Styles** | 2 basic styles | **6 aesthetic filters** (Smooth, Vibrant, Classic Comic, Pencil B&W, Color Pencil, Edge-Preserving) |
| **File Discovery** | Slow disk scan, crashed if file not found, altered `os.chdir()` | Safe, early-exit search with depth protection and no working-directory side effects |
| **Interfaces** | Terminal `input()` prompts only | **Python Library**, **Production CLI**, **Interactive Studio**, and **FastAPI REST API** |
| **Batch Processing** | Not supported | Full batch directory processing with configurable output paths |
| **Containerization** | None | Multi-stage Dockerfile and `docker-compose.yml` |
| **Quality & Tests** | None | 27 automated unit & integration tests covering core, CLI, finder, and API |
| **CI/CD** | None | Automated GitHub Actions matrix workflow across Python 3.9–3.13 |

---

## Available Cartoon Styles

| Style Key | Number / Aliases | Algorithm / OpenCV Pipeline | Best Used For |
|---|---|---|---|
| **`style_1`** | `1`, `smooth` | Domain transform recursive filter (`sigma_s=150`, `sigma_r=0.25`) | Soft painterly effect with flat colors |
| **`style_2`** | `2`, `vibrant` | Stylization filter with edge preservation (`sigma_s=60`, `sigma_r=0.5`) | High-contrast cartoons & portraits |
| **`classic`** | `3`, `comic` | Bilateral color quantization + adaptive thresholding ink lines | True graphic novel / comic book look |
| **`pencil_gray`** | `4`, `sketch` | Non-photorealistic pencil sketch with contour shading | Charcoal & graphite sketches |
| **`pencil_color`** | `5`, `color_sketch` | Color pencil sketch with paper texture synthesis | Artistic hand-drawn color illustrations |
| **`edge_preserve`** | `6`, `subtle` | Fast recursive edge-preserving filter | Subtle skin smoothing & portrait cleanup |

---

## Installation

### From Source
```bash
git clone https://github.com/your-username/Easy_cartoonify.git
cd Easy_cartoonify

# Install core package
pip install .

# Or install with API server and development tools
pip install ".[all]"
```

---

## Quickstart

### 1. Python Library API

```python
from easy_cartoonify import cartoonify, CartoonStyle

# One-liner cartoonification
result = cartoonify("input.jpg", style=CartoonStyle.CLASSIC, output_path="output.jpg")

# Advanced usage with custom parameters
from easy_cartoonify import Cartoonifier, CartoonConfig

config = CartoonConfig(
    style=CartoonStyle.CLASSIC,
    bilateral_passes=6,
    edge_block_size=9,
    edge_c=2.0
)
engine = Cartoonifier(config)
engine.process_file("portrait.png", output_path="portrait_cartoon.png")
```

### 2. Command Line Interface (CLI)

#### Process a single image
```bash
# By explicit path
easy-cartoonify -i photo.jpg -o photo_cartoon.jpg -s classic

# By searching for a filename in a directory
easy-cartoonify -n photo.jpg -d ~/Pictures -s vibrant

# Or using the root runner
python main.py -i photo.jpg -s pencil_gray
```

#### Batch process a directory
```bash
easy-cartoonify --batch ./raw_photos/ -o ./cartoons/ -s classic
```

#### Interactive Studio Mode
Running without arguments launches the terminal studio (with automatic drag-and-drop file path detection):
```bash
python main.py
```
> **Tip:** You can drag & drop any image file directly from File Explorer into your terminal. PowerShell call operators (`&`) and quotation marks are sanitized automatically.

#### Advanced Tuning
Fine-tune smoothing and contrast for any style:
```bash
python main.py -i portrait.jpg -s vibrant --sigma-s 90 --sigma-r 0.4
```
- `--sigma-s` (0–500): Spatial neighborhood smoothness (higher = flatter, softer colors)
- `--sigma-r` (0.0–1.0): Color range edge sharpness (lower = finer detail, higher = bolder posterization)

### 3. REST API Microservice

Start the production FastAPI server:
```bash
uvicorn easy_cartoonify.api:app --host 0.0.0.0 --port 8000
```

Interactive documentation is automatically available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

#### Example cURL Request:
```bash
curl -X POST "http://localhost:8000/api/v1/cartoonify" \
  -F "file=@landscape.jpg" \
  -F "style=classic" \
  -F "format=jpeg" \
  --output cartoon_result.jpg
```

---

## Docker Deployment

Build and run using Docker:
```bash
# Build container image
docker build -t easy-cartoonify .

# Run the containerized API on port 8000
docker run -p 8000:8000 easy-cartoonify
```

Or with Docker Compose:
```bash
docker compose up -d
```

---

## Project Structure

```
Easy_cartoonify/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI workflow (Python 3.9 - 3.13)
├── easy_cartoonify/             # Core Python package
│   ├── __init__.py              # Public exports and version definition
│   ├── __main__.py              # python -m easy_cartoonify entrypoint
│   ├── api.py                   # FastAPI REST microservice endpoints
│   ├── cli.py                   # CLI parser and interactive studio
│   ├── core.py                  # Computer vision algorithms and pipelines
│   ├── exceptions.py            # Typed domain exceptions
│   ├── finder.py                # Safe, early-exit image discovery engine
│   └── models.py                # Data classes and style enums
├── tests/                       # Automated test suite (Pytest)
│   ├── __init__.py
│   ├── conftest.py              # Test fixtures and synthetic image generator
│   ├── test_api.py              # REST API endpoint tests
│   ├── test_cli.py              # CLI integration tests
│   ├── test_core.py             # Vision filter and pipeline unit tests
│   └── test_finder.py           # Image finder tests
├── .dockerignore
├── .editorconfig
├── .gitignore
├── Dockerfile                   # Multi-stage production container build
├── docker-compose.yml           # Compose service configuration
├── main.py                      # Root convenience entry point
├── pyproject.toml               # PEP 517/621 package build specification
├── requirements.txt             # Runtime dependencies
├── requirements-dev.txt         # Development and testing dependencies
└── README.md                    # Project documentation
```

---

## Running Tests

Run the complete test suite with coverage:
```bash
pytest --cov=easy_cartoonify tests/
```

---

## Contributing & Community

Contributions are warmly welcomed! Please see our guides before submitting a pull request:
- [Contributing Guidelines](CONTRIBUTING.md): Setup instructions, testing workflow, and how to add new cartoon styles.
- [Code of Conduct](CODE_OF_CONDUCT.md): Standards for an open, respectful, and inclusive community.
- [Security Policy](SECURITY.md): Vulnerability reporting procedures.
- [Changelog](CHANGELOG.md): Historical record of features and improvements.

---

## License

This project is licensed under the permissive open-source MIT License. See [pyproject.toml](pyproject.toml) for package metadata.

