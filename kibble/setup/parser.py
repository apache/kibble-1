from configparser import ConfigParser

class KibbleConfigParser(ConfigParser):

    def __init__(self, ini_file="kibble.ini"):
        super().__init__()
        self.read(ini_file)

        # merge elasticsearch url
        dbname = self["elasticsearch"]['dbname']
        host = self["elasticsearch"]['host']
        port = self["elasticsearch"]['port']
        self.uri = "{}://{}:{}".format(dbname, host, port)
        