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

## JavaScript API

The generated HTML exposes a JavaScript API that allows you to load and display GLTF models programmatically. This is useful if you want to integrate the viewer into your own web application or load models dynamically.

### Global Functions

Two convenience functions are exposed globally, matching the API of OpenStudio's `geometry_preview.html`:

```javascript
// Load from a JSON object (GLTF data)
runFromJSON(gltfData, options);

// Load from a URL (requires HTTP server, won't work with file://)
runFromFile(url, options);

// Load from a File object (works with local files via <input type="file">)
runFromFileObject(file, options);
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `containerId` | string | `'viewer'` | ID of the container element |
| `includeGeometryDiagnostics` | boolean | `false` | Show geometry diagnostic controls |

**Example:**

```html
<div id="viewer" class="effibem-viewer">
  <!-- Controls and info panel structure here -->
</div>

<script type="module">
  // Assuming the viewer script is loaded...

  // Load from a URL
  runFromFile('./model.gltf', { includeGeometryDiagnostics: true });

  // Or load from a JSON object
  fetch('./model.gltf')
    .then(r => r.json())
    .then(data => runFromJSON(data));
</script>
```

### EffiBEMViewer Class

For more control, you can use the `EffiBEMViewer` class directly:

```javascript
// Create a viewer instance
const viewer = new EffiBEMViewer('my-container', {
  includeGeometryDiagnostics: true
});

// Load a model from JSON
viewer.loadFromJSON(gltfData);

// Or load from a URL (returns a Promise)
viewer.loadFromFile('./model.gltf')
  .then(() => console.log('Model loaded'));

// Or load from a File object (e.g., from file input)
const fileInput = document.querySelector('input[type="file"]');
fileInput.addEventListener('change', (e) => {
  viewer.loadFromFileObject(e.target.files[0])
    .then(() => console.log('Model loaded from file'));
});
```

The class provides access to the Three.js scene, camera, and renderer for advanced customization:

```javascript
const viewer = new EffiBEMViewer('viewer');
viewer.loadFromJSON(gltfData);

// Access Three.js objects
console.log(viewer.scene);       // THREE.Scene
console.log(viewer.camera);      // THREE.PerspectiveCamera
console.log(viewer.renderer);    // THREE.WebGLRenderer
console.log(viewer.orbitControls); // OrbitControls
```

### Required HTML Structure

The viewer expects a container with the `effibem-viewer` class and specific child elements for controls and info panel. The easiest way to get the correct structure is to use the Python API to generate the HTML, then customize as needed:

```python
from effibemviewer import model_to_gltf_html

# Generate HTML with empty/minimal model, then replace the data
html = model_to_gltf_html(model)
```

Alternatively, you can create your own container and only include the controls you need. The viewer uses class-based selectors (e.g., `.showFloors`, `.renderBy`) rather than IDs, allowing multiple viewers on the same page.
