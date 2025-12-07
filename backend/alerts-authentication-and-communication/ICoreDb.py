from abc import ABC, abstractmethod
from typing import Optional
from .DataModels4DAC import User, UserRole

class ICoreDb(ABC):
    """
    Interface provided by DAC for accessing SQL Core Data (Users, Buildings).
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
                user_id="u_1",
                username="admin",
                password_hash="hashed_secret", # In real app, use bcrypt verify
                role=UserRole.ADMIN,
                full_name="System Administrator"
            )
        return None