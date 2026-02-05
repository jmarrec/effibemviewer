from __future__ import annotations

from typing import TYPE_CHECKING

import openstudio
from jinja2 import Environment, PackageLoader

from effibemviewer import __version__

if TYPE_CHECKING:
    from IPython.display import HTML, IFrame

env = Environment(loader=PackageLoader("effibemviewer", "templates"))

CDN_BASE_URL = f"https://cdn.jsdelivr.net/gh/jmarrec/effibemviewer@v{__version__}/public/cdn"


def model_to_gltf_json(model: openstudio.model.Model, include_geometry_diagnostics: bool = False) -> dict:
    """Convert an OpenStudio model to GLTF JSON format (dict).

    Args:
        model: OpenStudio model to convert
        include_geometry_diagnostics: If True, include geometry diagnostic info in the output

    Returns:
        dict: GLTF JSON data representing the model

    Raises:
        ValueError: If geometry diagnostics are requested but not supported by the OpenStudio version
    """
    ft = openstudio.gltf.GltfForwardTranslator()
    if include_geometry_diagnostics:
        if not callable(getattr(openstudio.gltf.GltfForwardTranslator, "setIncludeGeometryDiagnostics", None)):
            raise ValueError(
                "Geometry diagnostics not supported in this version of OpenStudio. Please update to use this feature."
            )
        ft.setIncludeGeometryDiagnostics(True)
    return ft.modelToGLTFJSON(model)


def get_js_library() -> str:
    """Get the EffiBEMViewer JavaScript library content.

    Returns:
        str: The JavaScript library content (uses bare specifiers, requires importmap)
    """
    template = env.get_template("effibemviewer.js.j2")
    return template.render()


def get_css_library(height: str = "100vh") -> str:
    """Get the EffiBEMViewer CSS library content.

    Returns:
        str: The CSS library content
    """
    template = env.get_template("effibemviewer.css.j2")
    return template.render(height=height)


def model_to_gltf_html(
    model: openstudio.model.Model,
    height: str = "100vh",
    pretty_json: bool = False,
    include_geometry_diagnostics: bool = False,
    embedded: bool = True,
    loader_mode: bool = False,
    script_only: bool = False,
    cdn: bool = False,
) -> str:
    """Generate a full standalone HTML page for viewing an OpenStudio model.

    Args:
        model: OpenStudio model to render
        height: CSS height value (default "100vh" for full viewport)
        pretty_json: If True, format JSON with indentation
        include_geometry_diagnostics: If True, include geometry diagnostic info
        embedded: If True, inline the JS library. If False, reference external JS file.
        loader_mode: If True, generate file-input loader instead of embedding model data
        script_only: If True, generate only the script fragment (for Jupyter)
        cdn: If True, reference JS/CSS from jsDelivr CDN (overrides embedded)
    """
    data = model_to_gltf_json(model=model, include_geometry_diagnostics=include_geometry_diagnostics)

    template = env.get_template("effibemviewer.html.j2")
    indent = 2 if pretty_json else None

    return template.render(
        height=height,
        gltf_data=data,
        indent=indent,
        include_geometry_diagnostics=include_geometry_diagnostics,
        embedded=embedded,
        loader_mode=loader_mode,
        script_only=script_only,
        cdn_base_url=CDN_BASE_URL if cdn else None,
    )


def display_model(
    model: openstudio.model.Model,
    height: str = "500px",
    use_iframe: bool = False,
    include_geometry_diagnostics: bool = False,
    cdn: bool = False,
) -> HTML | IFrame:
    """Display an OpenStudio model in a Jupyter notebook.

    Args:
        model: OpenStudio model to render
        height: CSS height value (default "500px")
        use_iframe: If True, use IFrame for nbclassic compatibility
        include_geometry_diagnostics: If True, include geometry diagnostic info
        cdn: If True, load JS/CSS from CDN (better caching on re-runs)

    Returns:
        IPython display object (HTML or IFrame)
    """
    fragment = model_to_gltf_html(
        model=model,
        height=height,
        pretty_json=False,
        include_geometry_diagnostics=include_geometry_diagnostics,
        embedded=True,
        loader_mode=False,
        script_only=True,
        cdn=cdn,
    )
    if not use_iframe:
        from IPython.display import HTML

        return HTML(fragment)

    import base64
    import datetime

    from IPython.display import IFrame

    current_year = datetime.datetime.now().year
    footer = f"""<p>
      Copyright &copy; 2026 - {current_year} <a href="https://effibem.com" target="_blank">EffiBEM EURL</a>
    </p>"""
    full_html = f"""<!DOCTYPE html>
<html>
  <head>
  </head>
  <body style='margin:0'>
{fragment}

  <footer>
    {footer}
  </footer>
  </body>
</html>"""
    data_url = f"data:text/html;base64,{base64.b64encode(full_html.encode()).decode()}"
    # Parse height for IFrame (needs integer pixels)
    h = int(height.replace("px", "")) if height.endswith("px") else 500
    return IFrame(src=data_url, width="100%", height=h)


def generate_loader_html(
    height: str = "100vh",
    include_geometry_diagnostics: bool = False,
    embedded: bool = True,
    cdn: bool = False,
) -> str:
    """Generate a standalone HTML page with a file input for loading GLTF files.

    Args:
        height: CSS height value (default "100vh" for full viewport)
        include_geometry_diagnostics: If True, enable geometry diagnostic display
        embedded: If True, inline the JS library. If False, reference external JS file.
        cdn: If True, reference JS/CSS from jsDelivr CDN (overrides embedded)

    Returns:
        str: Full HTML page with file input for loading GLTF files
    """
    template = env.get_template("effibemviewer.html.j2")

    html = template.render(
        height=height,
        gltf_data=None,
        indent=None,
        include_geometry_diagnostics=include_geometry_diagnostics,
        embedded=embedded,
        loader_mode=True,
        script_only=False,
        cdn_base_url=CDN_BASE_URL if cdn else None,
    )
    return html


def create_example_model(include_geometry_diagnostics: bool = False) -> openstudio.model.Model:
    """Create an example OpenStudio model with two stories and optionally geometry diagnostics.

    Args:
        include_geometry_diagnostics: If True, will reverse a surface on purpose

    Returns:
        model (openstudio.model.Model): Example model
    """
    model = openstudio.model.exampleModel()
    space = model.getSpaceByName("Space 1").get()
    # Move space type assignment from Building to Space, so I can have one without it
    space_type = space.spaceType().get()
    [space.setSpaceType(space_type) for space in model.getSpaces()]
    b = model.getBuilding()
    b.setNorthAxis(45)
    b.resetSpaceType()

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

    if include_geometry_diagnostics:
        surface = next(s for s in space_clone.surfaces() if s.surfaceType() == "Wall")
        # Make one surface incorrectly oriented
        surface.setVertices(openstudio.reverse(surface.vertices()))

    return model
