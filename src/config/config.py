import json


class Config:
    """
    Configuration class
    """

    def __init__(self, config_file: str):
        """
        Configuration class
        """

        self.config = json.loads(open(config_file).read())
        self.config_file = config_file
