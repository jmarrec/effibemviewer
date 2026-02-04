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
  #viewer {{ width: 100%; height: {height}; }}
</style>

<div id="viewer"></div>

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

const gltfData = {json.dumps(data)};

const loader = new GLTFLoader();
loader.parse(
  JSON.stringify(gltfData),
  "",
  (gltf) => {{
    scene.add(gltf.scene);

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
