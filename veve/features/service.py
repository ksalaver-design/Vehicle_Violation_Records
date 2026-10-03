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

    def delete_vehicle(self, platenum: str) -> None:
        self.repository.delete(platenum)