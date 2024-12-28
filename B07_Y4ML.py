# B07_Y4ML.py
import logging
import yaml
import json

class Y4ML:
    # Initialize a Y4ML instance.
    def __init__(self):
        pass
    """
    This class represents a YAML manager, providing functionalities related to YAML files. 
    These include merging multiple YAML files, loading a YAML file, and saving data to a YAML file.
    """
    
    def merge_yaml_files(self, file_paths):
        """
        Merges multiple YAML files into a single dictionary. 
        
        If a key is present in more than one file, the value from the last file in the list is used.

        Args:
            file_paths (list of str): A list of file paths of the YAML files to be merged.

        Returns:
            merged_data (dict): A dictionary that contains the merged data from all the YAML files.
        """
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
        logging.debug(f"Returning Dictionary of Merged YAML:\n{file_paths}")
        return merged_data

    def load_yaml_file(self, filename):
        """
        Loads a YAML file and returns its content as a dictionary. 
        
        If an error occurs during the loading or parsing of the file, an error message is logged.

        Args:
            filename (str): The file path of the YAML file to be loaded.

        Returns:
            data (dict or None): A dictionary that contains the data from the YAML file. 
                                 Returns None if an error occurs.
        """
        try:
            with open(filename, 'r') as f:
                logging.debug(f"Returning `safe_load` of '{filename}'")
                return yaml.safe_load(f)
        except FileNotFoundError:
            logging.error(f"The file {filename} was not found.")
            return None
        except yaml.YAMLError as e:
            logging.error(f"Error parsing the file {filename}: {str(e)}")
            return None

    def save_to_yaml_file(self, dictionary, filename):
        """
        Saves a dictionary to a YAML file. 

        Args:
            data (dict): The data to be saved to the YAML file.
            filename (str): The file path of the YAML file to be saved to.
        """
        with open(filename, 'w') as f:
            logging.debug(f"Dumping to YAML file: '{filename}'")
            yaml.dump(dictionary, f)

# In this version:

# The merge_yaml_files method combines the content of multiple YAML files into a single dictionary.

# The load_yaml_file method reads a YAML file and returns its content as a dictionary. 

# The save_yaml_file method dumps a dictionary to a YAML file.
