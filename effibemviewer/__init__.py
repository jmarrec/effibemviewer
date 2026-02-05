"""Top-level package for EffiBEMViewer."""

__author__ = """Julien Marrec"""
__email__ = 'contact@effibem.com'
__version__ = '0.1.2'

from effibemviewer.gltf import (
    create_example_model,
    display_model,
    generate_loader_html,
    get_css_library,
    get_js_library,
    model_to_gltf_html,
    model_to_gltf_json,
)

__all__ = [
    "create_example_model",
    "display_model",
    "generate_loader_html",
    "get_css_library",
    "get_js_library",
    "model_to_gltf_html",
    "model_to_gltf_json",
]
