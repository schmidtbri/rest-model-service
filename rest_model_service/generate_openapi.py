"""Script that generates an OpenAPI schema."""
import os
import sys
import traceback
import argparse
import yaml

from rest_model_service.helpers import create_app
from rest_model_service.configuration import Configuration


def main() -> None:
    """Entry point for the cli tool."""
    argument_parser = argparse.ArgumentParser(description="Generate an OpenAPI schema.")
    argument_parser.add_argument("--configuration_file",  type=str, help="Path of configuration file.",
                                 default="rest_config.yaml")
    argument_parser.add_argument("--output_file", type=str, help="Path of output file.", default="openapi.yaml")

    args = argument_parser.parse_args()

    try:
        with open(args.configuration_file, "r") as file:
            configuration_dict = yaml.full_load(file)
        configuration = Configuration(**configuration_dict)

        # create application object, waiting for model creation to finish in order to have all the model endpoints in
        # the OpenAPI document
        app = create_app(configuration, wait_for_model_creation=True)

        # save OpenAPI document
        with open(args.output_file, "w") as file:
            yaml.dump(app.openapi(), file)
    except Exception:
        traceback.print_exc()
        sys.exit(os.EX_SOFTWARE)
    else:
        sys.exit(os.EX_OK)


if __name__ == "__main__":
    main()
