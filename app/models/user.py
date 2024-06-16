from sqlalchemy import Column, Integer, String
from app.config.db_config import Base

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	username = Column(String(255), unique=True, index=True)

	def to_dict(self):
		return {
			"id": self.id,
			"username": self.username
		}