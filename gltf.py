from pathlib import Path
import json

import openstudio


def model_to_gltf_json(model: openstudio.model.Model) -> dict:
    ft = openstudio.gltf.GltfForwardTranslator()
    return ft.modelToGLTFJSON(model)

def model_to_gltf_script(model: openstudio.model.Model, height: int = 500, use_iframe: bool = False) -> str:
    """Generate HTML/JS to render an OpenStudio model as GLTF.

    Args:
        model: OpenStudio model to render
        height: Height in pixels (default 500)
        use_iframe: If True, wrap in iframe for better Jupyter compatibility
    """
    data = model_to_gltf_json(model=model)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<script type="importmap">
{{
  "imports": {{
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }}
}}
</script>
<style>
  body {{ margin: 0; }}
  #viewer {{ width: 100%; height: {height}px; }}
</style>
</head>
<body>
<div id="viewer"></div>
<script type="module">
import * as THREE from "three";
import {{ GLTFLoader }} from "three/addons/loaders/GLTFLoader.js";
import {{ OrbitControls }} from "three/addons/controls/OrbitControls.js";

const container = document.getElementById("viewer");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf5f5f5);

const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
camera.position.set(5, 5, 5);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

window.addEventListener('resize', () => {{
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}});

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1, 0);
controls.update();

scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 1.2));
scene.add(new THREE.DirectionalLight(0xffffff, 0.8));

const gltf = {json.dumps(data)};

const loader = new GLTFLoader();
loader.parse(
  JSON.stringify(gltf),
  "",
  (g) => {{
    scene.add(g.scene);
    animate();
  }},
  (e) => console.error(e)
);

function animate() {{
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}}
</script>
</body>
</html>"""

    if use_iframe:
        import base64
        encoded = base64.b64encode(html_content.encode()).decode()
        return f'<iframe src="data:text/html;base64,{encoded}" style="width:100%;height:{height}px;border:none;"></iframe>'

    return html_content


if __name__ == "__main__":
    # Create a simple OpenStudio model
    model = openstudio.model.exampleModel()

    # Generate the GLTF viewer HTML
    template = model_to_gltf_script(model=model)

    # Write to an HTML file
    Path('test.html').write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
{template}
</body>
</html>
""")
