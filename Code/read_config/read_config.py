import yaml

def read_config(file):
    """
    Reads yaml files and attaches its parameters as strings in the keys of a dictionary and its corresponding values are also mapped to them. In case they are nested, we get a nested dictionary as well.

    Finally, it also distinguishes between floats and integers.

    Input:
        file - path of the yaml file to read

    Output:
        yaml.safe_load(stream) - dictionary with the properties of our file as keys and its values mapped to it in their correct type.

    """

    with open(file, "r") as stream:
        try:
            return yaml.safe_load(stream)
            

        except yaml.YAMLError as exc:
            print(exc)
        

#config = read_config("primary_config.yaml")
#print(config)
