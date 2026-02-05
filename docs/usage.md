# Usage

## In a Jupyter Notebook

To display an OpenStudio model in a Jupyter notebook:

```python
import openstudio
from effibemviewer import create_example_model, display_model

# model = openstudio.model.exampleModel()
# This helper creates a model with an incorrectly oriented surface and two stories
model = create_example_model(include_geometry_diagnostics=True)
display_model(
    model=model,
    height="500px",
    use_iframe=False,
    include_geometry_diagnostics=False,
    cdn=False,  # Set to True for better caching on re-runs
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `openstudio.model.Model` | required | The OpenStudio model to display |
| `height` | `str` | `"500px"` | CSS height value for the viewer |
| `use_iframe` | `bool` | `False` | Use IFrame for nbclassic compatibility |
| `include_geometry_diagnostics` | `bool` | `False` | Show geometry diagnostic controls |
| `cdn` | `bool` | `False` | Load JS/CSS from CDN (better caching on re-runs) |

!!! note
    `use_iframe=True` is only needed if you are using `jupyter nbclassic` (not `notebook` V7 or `lab`)

!!! note
    OpenStudio, as of 3.11.0, does NOT export geometry diagnostics in GLTF. This feature requires a patched version.

## Generate Standalone HTML

To generate a standalone HTML file programmatically:

```python
from effibemviewer import model_to_gltf_html
from pathlib import Path

html = model_to_gltf_html(model)
Path("viewer.html").write_text(html)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `openstudio.model.Model` | required | The OpenStudio model to render |
| `height` | `str` | `"100vh"` | CSS height value |
| `pretty_json` | `bool` | `False` | Format JSON with indentation |
| `include_geometry_diagnostics` | `bool` | `False` | Include geometry diagnostic info |
| `embedded` | `bool` | `True` | Inline JS/CSS in HTML |
| `cdn` | `bool` | `False` | Reference JS/CSS from jsDelivr CDN |

## Command Line Interface

Generate an HTML viewer from the command line:

```console
$ python -m effibemviewer --help
usage: __main__.py [-h] [-m MODEL] [-g] [-o OUTPUT] [--embedded | --cdn]
                   [--pretty] [--loader]

Generate GLTF viewer HTML from OpenStudio model
```

### Basic Usage

Generate a viewer with an OpenStudio model:

```console
$ python -m effibemviewer --model mymodel.osm --output viewer.html
```

When `--model` is omitted, it uses a built-in example model:

```console
$ python -m effibemviewer --output viewer.html
```

### Options

| Option | Description |
|--------|-------------|
| `-m, --model PATH` | Path to OpenStudio model file (.osm) |
| `-o, --output PATH` | Output HTML file path (default: `viewer.html`) |
| `-g, --geometry-diagnostics` | Include geometry diagnostic controls |
| `--pretty` | Pretty-print JSON in the HTML output |

### Library Mode Options

By default, the CLI generates a separate `effibemviewer.js` and `effibemviewer.css` file alongside the HTML. You can change this behavior:

| Option | Description |
|--------|-------------|
| `--embedded` | Inline JS/CSS directly in the HTML file |
| `--cdn` | Reference JS/CSS from jsDelivr CDN (no local files needed) |

!!! note
    `--embedded` and `--cdn` are mutually exclusive.

**Examples:**

```console
# Generate with external local files (default)
$ python -m effibemviewer -m model.osm -o viewer.html
# Creates: viewer.html, effibemviewer.js, effibemviewer.css

# Generate with embedded JS/CSS (single file, larger but portable)
$ python -m effibemviewer -m model.osm -o viewer.html --embedded
# Creates: viewer.html (self-contained)

# Generate with CDN references (smallest file, requires internet)
$ python -m effibemviewer -m model.osm -o viewer.html --cdn
# Creates: viewer.html (loads JS/CSS from cdn.jsdelivr.net)
```

### Loader Mode

Generate an HTML page with a file input for loading local GLTF files, instead of embedding model data:

```console
$ python -m effibemviewer --loader --output loader.html
```

This is useful for creating a standalone viewer that users can use to load their own GLTF files. No OpenStudio installation is required for loader mode.

```console
# Loader with CDN (minimal deployment - just one HTML file)
$ python -m effibemviewer --loader --cdn --output loader.html
```
