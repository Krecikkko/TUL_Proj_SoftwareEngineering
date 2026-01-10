from abc import ABC, abstractmethod
from typing import Optional
from DataModels4DAC import User, UserRole

class ICoreDb(ABC):
    """
    Interface provided by DAC for accessing SQL Core Data (Users).
    """
    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        pass

# --- MOCK FOR AAC TESTING ---
class MockCoreDb(ICoreDb):
    async def get_user_by_username(self, username: str) -> Optional[User]:
        # Simulates a successful DB lookup
        if username == "admin":
            return User(
                _id="u_1",  # Use alias '_id' (or 'id') to match new model
                username="admin",
                password_hash="hashed_secret",
                role=UserRole.ADMIN,
                full_name="System Administrator",
                email="admin@system.com" # NEW FIELD added in DAC schema
            )
        return None