import toml


class Config:
    def __init__(self, src):
        self.src = src

    def load(self):
        with open(self.src, 'r') as config_string:
            config = toml.load(config_string)
            env = config["env"]
            config["authApi"] = config["authApi"][env]
            config["orderApi"] = config["orderApi"][env]
            config["adminApi"] = config["adminApi"][env]
            config["analyzeApi"] = config["analyzeApi"][env]
            return config
