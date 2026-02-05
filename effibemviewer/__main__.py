import argparse
from pathlib import Path

from effibemviewer.gltf import (
    create_example_model,
    generate_loader_html,
    get_css_library,
    get_js_library,
    model_to_gltf_html,
    model_to_gltf_json,
)

# Asset paths within the package
ASSETS_DIR = Path(__file__).parent.parent / "docs" / "assets"

BASE_NAME = "effibemviewer"
JS_LIB_NAME = f"{BASE_NAME}.js"
CSS_LIB_NAME = f"{BASE_NAME}.css"


def main():
    """Command-line interface for generating GLTF viewer HTML from an OpenStudio model."""
    parser = argparse.ArgumentParser(description="Generate GLTF viewer HTML from OpenStudio model")
    # -m, --model: Path to the OpenStudio model file (optional, defaults to an example model)
    parser.add_argument(
        "-m",
        "--model",
        type=Path,
        help="Path to the OpenStudio model file (optional, defaults to an example model)",
    )
    parser.add_argument(
        "-g",
        "--geometry-diagnostics",
        action="store_true",
        help="Include geometry diagnostics (convex, correctly oriented, etc.)",
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("viewer.html"), help="Output HTML file path (default: viewer.html)"
    )
    # --embedded and --cdn are mutually exclusive options for how to include the JS library
    lib_mode = parser.add_mutually_exclusive_group()
    lib_mode.add_argument(
        "--embedded",
        action="store_true",
        help="Embed JS library inline in HTML (default: generate separate effibemviewer.js file)",
    )
    lib_mode.add_argument(
        "--cdn",
        action="store_true",
        help="Reference JS library from CDN instead of embedding or generating local file",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output in the HTML (default: compact JSON)",
    )
    parser.add_argument(
        "--loader",
        action="store_true",
        help="Generate a loader HTML with file input instead of embedding model data",
    )
    args = parser.parse_args()

    # Determine paths (relative to output HTML)
    output_dir = args.output.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.embedded and not args.cdn:
        js_lib_path = output_dir / JS_LIB_NAME
        js_lib_path.write_text(get_js_library())
        css_lib_path = output_dir / CSS_LIB_NAME
        css_lib_path.write_text(get_css_library())

        print(f"Generated: {js_lib_path} and {css_lib_path}")

    if args.loader:
        # Loader mode: generate HTML with file input, no model data
        html_content = generate_loader_html(
            include_geometry_diagnostics=args.geometry_diagnostics,
            embedded=args.embedded,
            cdn=args.cdn,
        )
        args.output.write_text(html_content)
        print(f"Generated: {args.output}")
        return

    if args.model:
        import openstudio

        if not args.model.is_file():
            raise ValueError(f"Error: Model file '{args.model}' does not exist.")
        model = openstudio.model.Model.load(args.model).get()
    else:
        print("No model file provided, using example model")
        model = create_example_model(include_geometry_diagnostics=args.geometry_diagnostics)
        model.save(output_dir / "example_model.osm", True)
        gltf_data = model_to_gltf_json(model=model, include_geometry_diagnostics=args.geometry_diagnostics)
        indent = 2 if args.pretty else None
        import json

        (output_dir / "example_model.gltf").write_text(json.dumps(gltf_data, indent=indent))

    html_content = model_to_gltf_html(
        model=model,
        pretty_json=args.pretty,
        include_geometry_diagnostics=args.geometry_diagnostics,
        embedded=args.embedded,
        cdn=args.cdn,
    )
    args.output.write_text(html_content)
    print(f"Generated: {args.output}")


if __name__ == "__main__":
    main()
