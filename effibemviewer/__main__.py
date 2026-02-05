import argparse
from pathlib import Path

from effibemviewer.gltf import create_example_model, get_js_library, model_to_gltf_html


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
    parser.add_argument(
        "--embedded",
        action="store_true",
        help="Embed JS library inline in HTML (default: generate separate effibemviewer.js file)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output in the HTML (default: compact JSON)",
    )
    args = parser.parse_args()

    if args.model:
        import openstudio

        if not args.model.is_file():
            raise ValueError(f"Error: Model file '{args.model}' does not exist.")
        model = openstudio.model.Model.load(args.model).get()
    else:
        print("No model file provided, using example model")
        model = create_example_model(include_geometry_diagnostics=args.geometry_diagnostics)

    # Determine JS library path (relative to output HTML)
    js_lib_path = "./effibemviewer.js"

    html_content = model_to_gltf_html(
        model=model,
        pretty_json=args.pretty,
        include_geometry_diagnostics=args.geometry_diagnostics,
        embedded=args.embedded,
        js_lib_path=js_lib_path,
    )
    args.output.write_text(html_content)
    print(f"Generated: {args.output}")

    # If not embedded, also generate the JS library file
    if not args.embedded:
        js_output = args.output.parent / js_lib_path
        js_output.write_text(get_js_library())
        print(f"Generated: {js_output}")


if __name__ == "__main__":
    main()
