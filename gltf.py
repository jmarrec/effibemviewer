from pathlib import Path

import openstudio
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def model_to_gltf_json(model: openstudio.model.Model) -> dict:
    ft = openstudio.gltf.GltfForwardTranslator()
    return ft.modelToGLTFJSON(model)


def model_to_gltf_script(
    model: openstudio.model.Model, height: str = "500px", use_iframe: bool = False, pretty_json: bool = False
) -> str:
    """Generate HTML/JS fragment to render an OpenStudio model as GLTF.

    Args:
        model: OpenStudio model to render
        height: CSS height value (default "500px", use "100vh" for full viewport)
        use_iframe: If True, wrap in iframe for better Jupyter compatibility
    """
    data = model_to_gltf_json(model=model)

    template = env.get_template("gltf_viewer.html.j2")
    indent = 2 if pretty_json else None
    fragment = template.render(height=height, gltf_data=data, indent=indent)

    if use_iframe:
        import base64

        full_html = f"<!DOCTYPE html><html><head></head><body style='margin:0'>{fragment}</body></html>"
        encoded = base64.b64encode(full_html.encode()).decode()
        return (
            f'<iframe src="data:text/html;base64,{encoded}" style="width:100%;height:{height};border:none;"></iframe>'
        )

    return fragment


def model_to_gltf_html(model: openstudio.model.Model, pretty_json: bool = False) -> str:
    """Generate a full standalone HTML page for viewing an OpenStudio model."""
    fragment = model_to_gltf_script(model=model, height="100vh", pretty_json=pretty_json)
    return f"<!DOCTYPE html><html><head></head><body style='margin:0'>{fragment}</body></html>"


if __name__ == "__main__":
    model = openstudio.model.exampleModel()
    Path("test.html").write_text(model_to_gltf_html(model=model, pretty_json=True))
