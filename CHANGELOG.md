# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] - 2026-02-10

### Added

### Changed
- Minor tweak to online loader height (80vh)

## [0.3.0] - 2026-02-10

### Added
- Minified JS/CSS distribution (`effibemviewer.min.js`, `effibemviewer.min.css`) via terser and csso-cli
- Added an Online Loader page to the gh-pages website

### Changed
- Jinja2 environment now uses `trim_blocks`, `lstrip_blocks`, and `keep_trailing_newline` for cleaner HTML output
- Removed unused `gltf_viewer` module

## [0.2.3] - 2026-02-10

### Changed
- Move standalone viewer css for header/footer into the HTML template, not the effibemviewer.css

## [0.2.2] - 2026-02-05

### Changed
- Forgot to rerun `make dist`

## [0.2.1] - 2026-02-05

### Added
- `cdn` parameter to `display_model()` for better browser caching on notebook re-runs
- JavaScript library documentation page (`docs/javascript.md`)

### Changed
- Expanded CLI documentation with all options (`--embedded`, `--cdn`, `--loader`)

### Fixed
- Viewer height not being respected when using CDN mode (now uses inline style)

## [0.2.0] - 2026-02-05

### Added
- Reusable `EffiBEMViewer` JavaScript class with public API
- `runFromJSON()`, `runFromFile()`, `runFromFileObject()` convenience functions
- `--loader` CLI mode to generate file-input HTML for loading local GLTF files
- `--embedded` CLI flag to inline JS/CSS vs external files
- Header with EffiBEM logo
- CDN-ready distribution in `public/` folder (embedded and cdn variants)
- Pre-commit hook to auto-rebuild dist when templates change

### Changed
- Upgraded Three.js from 0.160 to 0.182
- Switched CDN from unpkg to jsDelivr
- Refactored templates into separate JS and CSS files

## [0.1.2] - 2026-02-05

- docs update

## [0.1.1] - 2026-02-05

- Readme update

## [0.1.0] - 2026-02-05

### Added
- Initial release
- 3D GLTF viewer for OpenStudio models using Three.js
- Jupyter notebook integration with `display_model()`
- Surface filters (floors, walls, roofs, windows, doors, shading, partitions)
- Render by: Surface Type, Boundary, Construction, Thermal Zone, Space Type, Building Story
- Show Story filter
- Geometry diagnostics support (convex, correctly oriented, space convex, space enclosed)
- Click-to-select with info panel
- Edge/wireframe rendering
- Back face coloring for orientation detection
- X, Y, Z axes display

[Unreleased]: https://github.com/jmarrec/effibemviewer/compare/v0.3.1...HEAD
[0.3.0]: https://github.com/jmarrec/effibemviewer/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/jmarrec/effibemviewer/compare/v0.2.3...v0.3.0
[0.2.3]: https://github.com/jmarrec/effibemviewer/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/jmarrec/effibemviewer/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/jmarrec/effibemviewer/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/jmarrec/effibemviewer/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/jmarrec/effibemviewer/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/jmarrec/effibemviewer/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/jmarrec/effibemviewer/releases/tag/v0.1.0
