import yaml

# Define function to merge global and personal configuration files
def merge_yaml_files(file_paths):
    merged_data = {}
    for file_path in file_paths:
        with open(file_path, "r", encoding='utf-8') as f:
            data = yaml.safe_load(f)
            for key, value in data.items():
                if key not in merged_data:
                    merged_data[key] = value
                else:
                    if value is None:  # If the value is None, do nothing.
                        pass
                    elif isinstance(value, list):
                        if merged_data[key] is None:
                            merged_data[key] = value
                        else:
                            merged_data[key] += value
                    elif isinstance(value, dict):
                        if merged_data[key] is None:
                            merged_data[key] = value
                        else:
                            merged_data[key].update(value)
                    else:  # If the value is not None, list, or dict, set the value.
                        merged_data[key] = value
    return merged_data