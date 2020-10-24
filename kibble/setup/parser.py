from configparser import ConfigParser

class KibbleConfigParser(ConfigParser):

    def __init__(self, ini_file="kibble.ini"):
        # Let me know how you'd like me to handle incorrectly
        # configured ini file
        super().__init__()
        self.read(ini_file)

        # merge elasticsearch url
        # Let me know if this is the format you were looking for 
        dbname = self["elasticsearch"]['dbname']
        host = self["elasticsearch"]['host']
        port = self["elasticsearch"]['port']
        self.uri = "{}://{}:{}".format(dbname, host, port)