import argparse
from pathlib import Path

from effibemviewer.gltf import create_example_model, model_to_gltf_html


def main():
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

    model = create_example_model(include_geometry_diagnostics=args.geometry_diagnostics)

    args.output.write_text(
        model_to_gltf_html(model=model, pretty_json=True, include_geometry_diagnostics=args.geometry_diagnostics)
    )
    model.save("model.osm", True)


if __name__ == "__main__":
    main()
