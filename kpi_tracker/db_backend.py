from mssql.base import DatabaseWrapper as MSSQLDatabaseWrapper
from .utils import get_db_password

class DatabaseWrapper(MSSQLDatabaseWrapper):
    def get_connection_params(self):
        params = super().get_connection_params()
        # Fetch password from Key Vault
        params['password'] = get_db_password()
        return params 