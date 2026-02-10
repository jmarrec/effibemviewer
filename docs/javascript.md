# JavaScript Library

The EffiBEM Viewer is available as a JavaScript library that you can use directly in web pages without Python. This is useful for integrating the viewer into existing web applications or for loading GLTF models dynamically.

## Quick Start with CDN

The easiest way to use the viewer is via the jsDelivr CDN:

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/jmarrec/effibemviewer@v0.2.3/public/cdn/effibemviewer.css">
</head>
<body>
  <div id="viewer" class="effibem-viewer">
    <!-- Controls and info panel will be populated by the viewer -->
  </div>

  <script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.182.0/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.182.0/examples/jsm/"
    }
  }
  </script>
  <script type="module" src="https://cdn.jsdelivr.net/gh/jmarrec/effibemviewer@v0.2.3/public/cdn/effibemviewer.js"></script>
  <script type="module">
    // Load a GLTF file
    runFromFile('./model.gltf');
  </script>
</body>
</html>
```

!!! tip
    Replace `@v0.2.3` with the version you want to use. Check the [releases page](https://github.com/jmarrec/effibemviewer/releases) for available versions.

## Global Functions

Three convenience functions are exposed globally:

### `runFromJSON(gltfData, options)`

Load a model from a GLTF JSON object:

```javascript
fetch('./model.gltf')
  .then(r => r.json())
  .then(data => runFromJSON(data, { includeGeometryDiagnostics: true }));
```

### `runFromFile(url, options)`

Load a model from a URL:

```javascript
runFromFile('./model.gltf', { includeGeometryDiagnostics: true });
```

!!! warning
    Loading from file:// URLs won't work due to CORS. Use a local HTTP server for development.

### `runFromFileObject(file, options)`

Load a model from a File object (e.g., from `<input type="file">`):

```javascript
document.getElementById('fileInput').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    runFromFileObject(file);
  }
});
```

### Options

All functions accept an options object:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `containerId` | `string` | `'viewer'` | ID of the container element |
| `includeGeometryDiagnostics` | `boolean` | `false` | Show geometry diagnostic controls |

## EffiBEMViewer Class

For more control, use the `EffiBEMViewer` class directly:

```javascript
// Create a viewer instance
const viewer = new EffiBEMViewer('my-container', {
  includeGeometryDiagnostics: true
});

// Load a model (choose one method)
viewer.loadFromJSON(gltfData);
// or
await viewer.loadFromFile('./model.gltf');
// or
await viewer.loadFromFileObject(file);
```

### Accessing Three.js Objects

The viewer exposes the underlying Three.js objects for advanced customization:

```javascript
const viewer = new EffiBEMViewer('viewer');
await viewer.loadFromFile('./model.gltf');

// Access Three.js objects
console.log(viewer.scene);         // THREE.Scene
console.log(viewer.camera);        // THREE.PerspectiveCamera
console.log(viewer.renderer);      // THREE.WebGLRenderer
console.log(viewer.orbitControls); // OrbitControls
```

## Required HTML Structure

The viewer expects a container with specific child elements for controls and the info panel. The easiest way to get the correct structure is to generate it using the Python CLI:

```console
$ python -m effibemviewer --loader --cdn --output viewer.html
```

Then customize the generated HTML as needed.

### Minimal Structure

At minimum, you need:

```html
<div id="viewer" class="effibem-viewer">
  <div class="controls">
    <!-- Control elements with specific classes -->
    <select class="renderBy">...</select>
    <select class="showStory">...</select>
    <input type="checkbox" class="showFloors" checked>
    <!-- etc. -->
  </div>
  <div class="info-panel">
    <!-- Info display elements -->
    <h4 class="info-name"></h4>
    <span class="info-type"></span>
    <!-- etc. -->
  </div>
</div>
```

The viewer uses class-based selectors (e.g., `.showFloors`, `.renderBy`) rather than IDs, allowing multiple viewers on the same page.

## File Input Example

A complete example with file input for loading local GLTF files:

```html
<!DOCTYPE html>
<html>
<head>
  <title>EffiBEM Viewer</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/jmarrec/effibemviewer@v0.2.3/public/cdn/effibemviewer.css">
  <style>
    .loader { padding: 20px; text-align: center; }
    .loader.hidden { display: none; }
  </style>
</head>
<body>
  <div id="loaderPrompt" class="loader">
    <h2>EffiBEM Viewer</h2>
    <p>Select an OpenStudio GLTF file to visualize</p>
    <input type="file" id="fileInput" accept=".gltf,.json">
  </div>

  <div id="viewer" class="effibem-viewer">
    <!-- Full control structure here - generate with CLI -->
  </div>

  <script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@0.182.0/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.182.0/examples/jsm/"
    }
  }
  </script>
  <script type="module" src="https://cdn.jsdelivr.net/gh/jmarrec/effibemviewer@v0.2.3/public/cdn/effibemviewer.js"></script>
  <script type="module">
    const viewer = new EffiBEMViewer('viewer');

    document.getElementById('fileInput').addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        document.getElementById('loaderPrompt').classList.add('hidden');
        viewer.loadFromFileObject(file);
      }
    });
  </script>
</body>
</html>
```

## Self-Hosting

Instead of using the CDN, you can self-host the library files. Generate them with the CLI:

```console
$ python -m effibemviewer --loader --output viewer.html
# Creates: viewer.html, effibemviewer.js, effibemviewer.css
```

Then reference the local files in your HTML:

```html
<link rel="stylesheet" href="./effibemviewer.css">
<script type="module" src="./effibemviewer.js"></script>
```
