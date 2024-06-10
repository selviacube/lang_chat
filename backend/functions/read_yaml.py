# Read values from a YAML file and store the values in individual global variables.

import yaml


def read_yaml(file_path):
    global introduction
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

        for key, value in data.items():
            globals()[
                key
            ] = value  # Set the variable name to the key and the value to the variable
            print(f"{key}: {value}")
        print("\nIntroduction inside read_yaml: ", introduction)
