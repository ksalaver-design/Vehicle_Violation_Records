import sqlite3

class Database:
    def __init__(self, db_name: str = "vehicle_violations.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS drivers (
                    licensenum TEXT PRIMARY KEY,
                    drivername TEXT,
                    has_license BOOLEAN,
                    phone TEXT,
                    email TEXT,
                    sex TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS violations (
                    platenum TEXT PRIMARY KEY,
                    licensenum TEXT,
                    vehicletype TEXT,
                    violations TEXT,
                    fine REAL,
                    date_created TEXT,
                    FOREIGN KEY(licensenum) REFERENCES drivers(licensenum)
                )
            """)
            conn.commit()