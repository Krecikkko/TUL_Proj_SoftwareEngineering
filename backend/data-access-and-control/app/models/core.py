from beanie import Document
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    MAINTENANCE = "maintenance"
    USER = "user"

class User(Document):
   
    username: str
    password_hash: str
    role: UserRole = UserRole.USER
    full_name: str
    email: Optional[str] = None
    
    class Settings:
        name = "Users"

class Building(Document):

    name: str
    address: Optional[str] = None
    timezone: str = "UTC"
    capacity_kw: Optional[float] = None  # Electrical capacity
    
    class Settings:
        name = "Buildings"

class Room(Document):
  
    building_id: str  # Reference to Building
    name: str
    floor_number: Optional[int] = None
    area_m2: Optional[float] = None
    
    class Settings:
        name = "Rooms"

class Device(Document):
 
    device_id: str         # The unique hardware ID (e.g., "dev_001")
    building_id: str
    room_id: Optional[str] = None
    type: str              # "sensor", "hvac", "lighting"
    status: str = "active" # "active", "maintenance", "inactive"
    
    class Settings:
        name = "Devices"