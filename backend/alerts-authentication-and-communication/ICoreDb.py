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
            # Matches 'User' model from core.py
            return User(
                _id="u_1", 
                username="admin",
                # UPDATED: Matches the input password used in 'test_system.py'
                # This allows us to remove the hardcoded "secret" from the Service logic.
                password_hash="secret", 
                role=UserRole.ADMIN,
                full_name="System Administrator",
                email="admin@system.com"
            )
        return None