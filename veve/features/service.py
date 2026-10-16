from database.database import Database
from .model import VehicleRecord
from .respository import VehicleRepository

class VehicleService: 
    def __init__(self, database: Database):
        self.repository = VehicleRepository(database)
        
    def add_Vehicle(self, record: VehicleRecord) -> VehicleRecord:
        return self.repository.add(record)

    def update_vehicle(self, record: VehicleRecord) -> VehicleRecord:
        return self.repository.update(record)
    
    def get_Vehicle(self) -> list[VehicleRecord]:
        return self.repository.list()

    def delete_vehicle(self, record_id: int) -> None:
        self.repository.delete_by_id(record_id)

    def get_driver_offense_count(self, licensenum: str) -> int:
        return self.repository.get_offense_count_by_driver(licensenum)
