import yaml

def read_config(file):
    with open(file, "r") as stream:
        try:
            return yaml.safe_load(stream)
            

        except yaml.YAMLError as exc:
            print(exc)
        

config = read_config("primary_config.yaml")
print(config)
