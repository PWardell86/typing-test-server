from jproperties import Properties

class DBProperties(Properties):
    def __init__(self):
        super().__init__(self)
        with open('../config/database.properties', 'rb') as config_file:
            self.load(config_file)
    
    def get_db_name(self):
        return self.get("db_name").data
    
    def get_db_user(self):
        return self.get("db_user").data
    
    def get_db_password(self):
        return self.get("db_password").data
    
    def get_db_host(self):
        return self.get("db_host").data
