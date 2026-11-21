# Contributing to Easy Cartoonify

Thank you for your interest in contributing to Easy Cartoonify! This document provides instructions for contributing improvements, fixes, and new cartoon styles.

---

## Code of Conduct

All contributors and participants are expected to uphold respectful, inclusive, and professional collaboration.

---

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/<your-username>/Easy_cartoonify.git
   cd Easy_cartoonify
   ```

2. **Set up Virtual Environment**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install Dependencies in Editable Mode**
   ```bash
   pip install -e ".[all]"
   ```

---

## Running Quality Checks

Before opening a pull request, ensure tests and styling pass:

```bash
# Run tests
pytest tests/

# Run coverage analysis
pytest --cov=easy_cartoonify tests/
```

---

## Adding a New Cartoon Style

To add a new aesthetic filter:

1. Add the style identifier to `CartoonStyle` in `easy_cartoonify/models.py`.
2. Configure default parameters in `CartoonConfig.default_for_style`.
3. Implement the processing logic in `Cartoonifier` in `easy_cartoonify/core.py`.
4. Add corresponding test cases in `tests/test_core.py`.
5. Update `easy_cartoonify/api.py` and `README.md` with descriptions.

---

## Pull Request Guidelines

1. Create a descriptive feature branch (`git checkout -b feature/cool-new-style`).
2. Keep changes focused and atomic.
3. Include tests for any new behavior or bug fixes.
4. Open a Pull Request referencing related issues.
