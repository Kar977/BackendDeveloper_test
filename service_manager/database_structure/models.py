from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import LargeBinary
import time

Base = declarative_base()

class User(Base):
    """
    SQLAlchemy model for a User. Represents the users which register and login.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

    posts = relationship("Post", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

class Post(Base):
    """
    SQLAlchemy model for a Post. Represents a user's post.
    """
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(Integer, default=int(time.time()))  # Store timestamp as Unix time

    owner = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post(id={self.id}, user_id={self.user_id}, text={self.text[:30]})>"

