import configparser


class ConfigParse():
    def __init__(self, path_to_config):
        self.config = configparser.ConfigParser()
        self.config.read(path_to_config)

    def ConfigSectionMap(self, section):
        conf_dict = {}
        options = self.config.options(section)
        for option in options:
            try:
                conf_dict[option] = self.config.get(section, option)
                if conf_dict[option] == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                conf_dict[option] = None
        return conf_dict