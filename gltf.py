from pathlib import Path
import json

import openstudio


def model_to_gltf_json(model: openstudio.model.Model) -> dict:
    ft = openstudio.gltf.GltfForwardTranslator()
    return ft.modelToGLTFJSON(model)

def model_to_gltf_script(model: openstudio.model.Model, height: str = "500px", use_iframe: bool = False) -> str:
    """Generate HTML/JS fragment to render an OpenStudio model as GLTF.

    Args:
        model: OpenStudio model to render
        height: CSS height value (default "500px", use "100vh" for full viewport)
        use_iframe: If True, wrap in iframe for better Jupyter compatibility
    """
    data = model_to_gltf_json(model=model)

    fragment = f"""
<script type="importmap">
{{
  "imports": {{
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }}
}}
</script>

<style>
  #viewer {{ width: 100%; height: {height}; position: relative; }}
  #controls {{
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(255,255,255,0.9);
    padding: 10px;
    border-radius: 4px;
    font-family: sans-serif;
    font-size: 12px;
    z-index: 100;
  }}
  #controls label {{ display: block; margin: 4px 0; cursor: pointer; }}
  #controls input {{ margin-right: 6px; }}
</style>

<div id="viewer">
  <div id="controls">
    <strong>Surface Filters</strong>
    <label><input type="checkbox" id="showFloors" checked> Floors</label>
    <label><input type="checkbox" id="showWalls" checked> Walls</label>
    <label><input type="checkbox" id="showRoofs" checked> Roofs/Ceilings</label>
    <label><input type="checkbox" id="showWindows" checked> Windows</label>
    <label><input type="checkbox" id="showDoors" checked> Doors</label>
    <label><input type="checkbox" id="showShading" checked> Shading</label>
    <label><input type="checkbox" id="showPartitions" checked> Partitions</label>
  </div>
</div>

<script type="module">
import * as THREE from "three";
import {{ GLTFLoader }} from "three/addons/loaders/GLTFLoader.js";
import {{ OrbitControls }} from "three/addons/controls/OrbitControls.js";

const container = document.getElementById("viewer");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf5f5f5);

const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 5000);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);

window.addEventListener('resize', () => {{
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}});

scene.add(new THREE.AmbientLight(0xbbbbbb));
scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 0.6));

const gltfData = {json.dumps(data, indent=2)};

// Collect all meshes for filtering
const sceneObjects = [];

function updateVisibility() {{
  const showFloors = document.getElementById('showFloors').checked;
  const showWalls = document.getElementById('showWalls').checked;
  const showRoofs = document.getElementById('showRoofs').checked;
  const showWindows = document.getElementById('showWindows').checked;
  const showDoors = document.getElementById('showDoors').checked;
  const showShading = document.getElementById('showShading').checked;
  const showPartitions = document.getElementById('showPartitions').checked;

  sceneObjects.forEach(obj => {{
    const surfaceType = obj.userData?.surfaceType || '';
    let visible = true;

    if (surfaceType === 'Floor') visible = showFloors;
    else if (surfaceType === 'Wall') visible = showWalls;
    else if (surfaceType === 'RoofCeiling') visible = showRoofs;
    else if (surfaceType.includes('Window') || surfaceType.includes('Skylight') || surfaceType.includes('TubularDaylight') || surfaceType === 'GlassDoor') visible = showWindows;
    else if (surfaceType.includes('Door')) visible = showDoors;
    else if (surfaceType.includes('Shading')) visible = showShading;
    else if (surfaceType === 'InteriorPartitionSurface') visible = showPartitions;

    obj.visible = visible;
  }});
}}

// Add event listeners to checkboxes
['showFloors', 'showWalls', 'showRoofs', 'showWindows', 'showDoors', 'showShading', 'showPartitions'].forEach(id => {{
  document.getElementById(id).addEventListener('change', updateVisibility);
}});

const loader = new GLTFLoader();
loader.parse(
  JSON.stringify(gltfData),
  "",
  (gltf) => {{
    scene.add(gltf.scene);

    // Collect all meshes with userData for filtering
    gltf.scene.traverse(obj => {{
      if (obj.isMesh && obj.userData?.surfaceType) {{
        sceneObjects.push(obj);
      }}
    }});

    // Position camera using bounding box from GLTF metadata
    const bbox = gltfData.scenes?.[0]?.extras?.boundingbox;
    if (bbox) {{
      // Convert from OpenStudio coords (Z-up) to Three.js coords (Y-up)
      const lookAt = new THREE.Vector3(bbox.lookAtX, bbox.lookAtZ, -bbox.lookAtY);
      const radius = 2.5 * bbox.lookAtR;

      // Position camera at an angle (similar to -30, 30 degrees)
      const theta = -30 * Math.PI / 180;
      const phi = 30 * Math.PI / 180;
      camera.position.set(
        radius * Math.cos(theta) * Math.cos(phi) + lookAt.x,
        radius * Math.sin(phi) + lookAt.y,
        -radius * Math.sin(theta) * Math.cos(phi) + lookAt.z
      );

      controls.target.copy(lookAt);
      controls.update();
    }}

    animate();
  }},
  (e) => console.error(e)
);

function animate() {{
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}}
</script>
"""

    if use_iframe:
        import base64
        full_html = f"<!DOCTYPE html><html><head></head><body style='margin:0'>{fragment}</body></html>"
        encoded = base64.b64encode(full_html.encode()).decode()
        return f'<iframe src="data:text/html;base64,{encoded}" style="width:100%;height:{height};border:none;"></iframe>'

    return fragment


def model_to_gltf_html(model: openstudio.model.Model) -> str:
    """Generate a full standalone HTML page for viewing an OpenStudio model."""
    fragment = model_to_gltf_script(model=model, height="100vh")
    return f"<!DOCTYPE html><html><head></head><body style='margin:0'>{fragment}</body></html>"


if __name__ == "__main__":
    model = openstudio.model.exampleModel()
    Path('test.html').write_text(model_to_gltf_html(model=model))
