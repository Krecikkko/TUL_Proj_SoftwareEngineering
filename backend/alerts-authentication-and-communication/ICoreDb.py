from abc import ABC, abstractmethod
from typing import Optional
from DataModels4DAC import User, UserRole

class ICoreDb(ABC):
    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        pass

class MockCoreDb(ICoreDb):
    async def get_user_by_username(self, username: str) -> Optional[User]:
        if username == "admin":
            return User(
                _id="u_1", 
                username="admin",
                password_hash="secret", 
                role=UserRole.ADMIN,
                full_name="System Administrator",
                email="admin@system.com"
            )
        return None