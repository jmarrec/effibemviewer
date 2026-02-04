import argparse
import sys
from pathlib import Path

sys.path.insert(0, "/Users/julien/Software/Others/OS-build-release/Products/python")
import openstudio

sys.path.pop(0)

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def model_to_gltf_json(model: openstudio.model.Model, include_geometry_diagnostics: bool = False) -> dict:
    ft = openstudio.gltf.GltfForwardTranslator()
    if include_geometry_diagnostics:
        ft.setIncludeGeometryDiagnostics(True)
    return ft.modelToGLTFJSON(model)


def model_to_gltf_script(
    model: openstudio.model.Model,
    height: str = "500px",
    pretty_json: bool = False,
    include_geometry_diagnostics: bool = False,
) -> str:
    """Generate HTML/JS fragment to render an OpenStudio model as GLTF.

    Args:
        model: OpenStudio model to render
        height: CSS height value (default "500px", use "100vh" for full viewport)
        pretty_json: If True, format JSON with indentation
        include_geometry_diagnostics: If True, include geometry diagnostic info
    """
    data = model_to_gltf_json(model=model, include_geometry_diagnostics=include_geometry_diagnostics)

    template = env.get_template("gltf_viewer.html.j2")
    indent = 2 if pretty_json else None
    return template.render(
        height=height,
        gltf_data=data,
        indent=indent,
        include_geometry_diagnostics=include_geometry_diagnostics,
    )


def model_to_gltf_html(
    model: openstudio.model.Model,
    height: str = "100vh",
    pretty_json: bool = False,
    include_geometry_diagnostics: bool = False,
) -> str:
    """Generate a full standalone HTML page for viewing an OpenStudio model."""
    fragment = model_to_gltf_script(
        model=model, height=height, pretty_json=pretty_json, include_geometry_diagnostics=include_geometry_diagnostics
    )
    return f"<!DOCTYPE html><html><head></head><body style='margin:0'>{fragment}</body></html>"


def display_model(
    model: openstudio.model.Model,
    height: str = "500px",
    use_iframe: bool = False,
    include_geometry_diagnostics: bool = False,
):
    """Display an OpenStudio model in a Jupyter notebook.

    Args:
        model: OpenStudio model to render
        height: CSS height value (default "500px")
        use_iframe: If True, use IFrame for nbclassic compatibility
        include_geometry_diagnostics: If True, include geometry diagnostic info

    Returns:
        IPython display object (HTML or IFrame)
    """
    from IPython.display import HTML, IFrame
    import base64

    if use_iframe:
        full_html = model_to_gltf_html(model=model, height=height, include_geometry_diagnostics=include_geometry_diagnostics)
        data_url = f"data:text/html;base64,{base64.b64encode(full_html.encode()).decode()}"
        # Parse height for IFrame (needs integer pixels)
        h = int(height.replace("px", "")) if height.endswith("px") else 500
        return IFrame(src=data_url, width="100%", height=h)

    fragment = model_to_gltf_script(model=model, height=height, include_geometry_diagnostics=include_geometry_diagnostics)
    return HTML(fragment)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate GLTF viewer HTML from OpenStudio model")
    parser.add_argument(
        "-g",
        "--geometry-diagnostics",
        action="store_true",
        help="Include geometry diagnostics (convex, correctly oriented, etc.)",
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("test.html"), help="Output HTML file path (default: test.html)"
    )
    args = parser.parse_args()

    model = openstudio.model.exampleModel()
    space = model.getSpaceByName("Space 1").get()
    # Move space type assignment from Building to Space, so I can have one without it
    space_type = space.spaceType().get()
    [space.setSpaceType(space_type) for space in model.getSpaces()]
    model.getBuilding().resetSpaceType()

    space_clone = space.clone(model).to_Space().get()
    space_clone.setName("Space Level 2")
    space_clone.resetSpaceType()
    # Set it above the original space for better viewing
    z = space.boundingBox().maxZ().get()
    assert z == 3.0
    space_clone.setZOrigin(z)
    story2 = openstudio.model.BuildingStory(model)
    story2.setName("Second Story")
    story2.setNominalZCoordinate(z)
    story2.setNominalFloortoFloorHeight(z)
    space_clone.setBuildingStory(story2)

    if args.geometry_diagnostics:
        if not callable(getattr(openstudio.gltf.GltfForwardTranslator, "setIncludeGeometryDiagnostics", None)):
            print(
                "Geometry diagnostics not supported in this version of OpenStudio. Please update to use this feature."
            )
            sys.exit(1)
        surface = next(s for s in space_clone.surfaces() if s.surfaceType() == "Wall")
        surface.setVertices(openstudio.reverse(surface.vertices()))  # Make one surface incorrectly oriented

    args.output.write_text(
        model_to_gltf_html(model=model, pretty_json=True, include_geometry_diagnostics=args.geometry_diagnostics)
    )
