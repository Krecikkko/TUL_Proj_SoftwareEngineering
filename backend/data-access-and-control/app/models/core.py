from beanie import Document
from typing import Optional, List
from enum import Enum
from datetime import datetime, date 

class UserRole(str, Enum):
    ADMIN = "admin"
    MAINTENANCE = "maintenance"
    USER = "user"

class DeviceStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class UserAccount(Document):
   
    email: str
    password_hash: str
    display_name: Optional[str] = None
    status: UserStatus = UserStatus.ACTIVE

    roles: List[UserRole] = [UserRole.USER]
    
    class Settings:
        name = "user_account"

class Building(Document):

    name: str
    address: Optional[str] = None
    timezone: str = "UTC"
    
    class Settings:
        name = "building"

class Room(Document):
  
    building_id: str  # Reference to Building
    floor_id: Optional[str] = None
    name: str
    area_m2: Optional[float] = None
    purpose: Optional[str] = None
    
    class Settings:
        name = "room"

class Device(Document):
 
    device_id: str         # The unique hardware ID (e.g., "dev_001")
    room_id: str
    building_id: str

    type: str              # "sensor", "hvac", "lighting"
    vendor: Optional[str] = None
    model: Optional[str] = None
    serial_no: Optional[str] = None

    rated_power_w: Optional[int] = None
    install_date: Optional[date] = None
    status: DeviceStatus = DeviceStatus.ACTIVE
    
    class Settings:
        name = "device"

class Alert(Document):
    device_id: Optional[str] = None
    severity: str   #high/medium/low
    code: str
    message: str
    raised_at: datetime
    acknoledged_by: Optional[str] = None
    status: str

    class Settings:
        name = "alert"

class Floor(Document):
    building_id: str
    name: str
    
    class Settings:
        name = "floor"