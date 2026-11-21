# Changelog

All notable changes to the Easy Cartoonify project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-11-20

### Added
- Modular package architecture under `easy_cartoonify/`.
- 6 tuned artistic filters: Smooth, Vibrant, Classic Comic Book, Pencil B&W, Color Pencil, and Edge-Preserving.
- Safe image finder with early termination and search depth limit.
- Command-line interface with batch directory processing and interactive mode.
- FastAPI REST microservice with interactive documentation at `/docs`.
- Multi-stage Dockerfile and Docker Compose service.
- Automated test suite (27 unit/integration tests) with pytest and coverage.
- GitHub Actions CI matrix testing Python 3.9 through 3.13.
- Open-source governance files: Contributing guide, Code of Conduct, Security policy, issue/PR templates.

## [1.0.0] - 2022-05-24

### Added
- Initial prototype script with OpenCV stylization and terminal input.
