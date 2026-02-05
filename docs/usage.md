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
    include_geometry_diagnostics=False
)
```

**Note**: `use_iframe=True` is not needed unless you are using `jupyter nbclassic` (and not `notebook` (V7) or `lab`)

**Note**: OpenStudio, as of 3.11.0, does NOT export geometry diagnostics in GLTF. I am adding this myself locally, but will upstream my changes.

## Generate standalone HTML

To generate a standalone HTML file:

```python
from effibemviewer import model_to_gltf_html
from pathlib import Path

html = model_to_gltf_html(model)
Path("viewer.html").write_text(html)
```

## Command Line

Generate an HTML viewer from the command line:

```console
$ python -m effibemviewer --model mymodel.osm --output output.html
```

With geometry diagnostics enabled, and when `--model` is omitted it uses the `create_example_model`

```console
$ python -m effibemviewer --geometry-diagnostics --output output.html
```
