from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.config.db_config import Base

class Gist(Base):
	__tablename__ = "gists"

	id = Column(Integer, primary_key=True, index=True)
	gist_id = Column(String(255), unique=True, index=True)
	description = Column(String(1024))
	user_id = Column(Integer, ForeignKey("users.id"))
	is_new = Column(Boolean, default=True)
	pipedrive_id = Column(Integer, index=True, nullable=True)

	user = relationship("User")

	def to_dict(self):
		return {
			"id": self.id,
			"gist_id": self.gist_id,
			"description": self.description,
			"user_id": self.user_id,
			"is_new": self.is_new,
			"user": self.user.to_dict() if self.user else None
		}