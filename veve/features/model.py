from dataclasses import dataclass
from typing import List

@dataclass
class Driver:
    licensenum: str
    drivername: str
    has_license: bool
    phone: str
    email: str
    sex: str

@dataclass
class Violation:
    platenum: str
    licensenum: str
    vehicletype: str
    violations: List[str]
    fine: float
    date_created: str = ""

@dataclass
class VehicleRecord:
    driver: Driver
    violation: Violation