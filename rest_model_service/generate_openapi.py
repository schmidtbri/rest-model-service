"""Script that generates an OpenAPI schema."""
import os
import sys
import traceback
import argparse
import yaml

from rest_model_service.main import app


def main() -> None:
    """Entry point for the cli tool."""
    argument_parser = argparse.ArgumentParser(description="Generate an OpenAPI schema.")
    argument_parser.add_argument("--output_file", type=str, help="Path of output file.")

    args = argument_parser.parse_args()

    try:
        with open(args.output_file, "w") as file:
            yaml.dump(app.openapi(), file)
    except Exception:
        traceback.print_exc()
        sys.exit(os.EX_SOFTWARE)

    sys.exit(os.EX_OK)


if __name__ == "__main__":
    main()
