import sqlite3
from typing import List
from database.database import Database
from .model import Driver, Violation, VehicleRecord

class VehicleRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_offense_count_by_driver(self, licensenum: str) -> int:
        """Returns the total number of past violation records for a specific driver."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM violations WHERE licensenum = ?", (licensenum,))
            return cursor.fetchone()[0] or 0

    def add(self, record: VehicleRecord) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO drivers (licensenum, drivername, has_license, phone, email, sex)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(licensenum) DO UPDATE SET
                    drivername=excluded.drivername,
                    has_license=excluded.has_license,
                    phone=excluded.phone,
                    email=excluded.email,
                    sex=excluded.sex
                """,
                (
                    record.driver.licensenum,
                    record.driver.drivername,
                    record.driver.has_license,
                    record.driver.phone,
                    record.driver.email,
                    record.driver.sex,
                )
            )
            
            violations_str = ",".join(record.violation.violations)
            cursor.execute(
                """
                INSERT INTO violations (platenum, licensenum, vehicletype, violations, fine, date_created)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.violation.platenum,
                    record.violation.licensenum,
                    record.violation.vehicletype,
                    violations_str,
                    record.violation.fine,
                    record.violation.date_created
                )
            )
            conn.commit()

    def list(self) -> List[VehicleRecord]:
        records = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    d.licensenum, d.drivername, d.has_license, d.phone, d.email, d.sex,
                    v.platenum, v.vehicletype, v.violations, v.fine, v.date_created, v.id
                FROM violations v
                LEFT JOIN drivers d ON v.licensenum = d.licensenum
                ORDER BY v.id DESC
                """
            )
            rows = cursor.fetchall()

            for row in rows:
                driver = Driver(
                    licensenum=row[0] or "",
                    drivername=row[1] or "",
                    has_license=bool(row[2]), 
                    phone=row[3] or "",        
                    email=row[4] or "",        
                    sex=row[5] or ""   
                )
                
                raw_violations = row[8].split(",") if row[8] else []
                violations_list = [v.strip() for v in raw_violations if v.strip()]
                
                violation = Violation(
                    platenum=row[6] or "",
                    licensenum=row[0] or "",
                    vehicletype=row[7] or "",
                    violations=violations_list,
                    fine=float(row[9] or 0.0),
                    date_created=row[10] or "",
                    id=row[11]
                )
                records.append(VehicleRecord(driver=driver, violation=violation))
                
        return records

    def update(self, record: VehicleRecord) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE drivers 
                SET drivername=?, has_license=?, phone=?, email=?, sex=?
                WHERE licensenum=?
                """,
                (
                    record.driver.drivername,
                    record.driver.has_license,
                    record.driver.phone,
                    record.driver.email,
                    record.driver.sex,
                    record.driver.licensenum,
                )
            )

            violations_str = ",".join(record.violation.violations)
            cursor.execute(
                """
                UPDATE violations 
                SET platenum=?, licensenum=?, vehicletype=?, violations=?, fine=?
                WHERE id=?
                """,
                (
                    record.violation.platenum,
                    record.violation.licensenum,
                    record.violation.vehicletype,
                    violations_str,
                    record.violation.fine,
                    record.violation.id,
                )
            )
            conn.commit()

    def delete_by_id(self, record_id: int) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM violations WHERE id = ?", (record_id,))
            conn.commit()
