from sqlalchemy import Column, Integer, String, Boolean, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.sqltypes import TIMESTAMP

Base = declarative_base()


class Post(Base):
    __tablename__ = "posts"

    id: int = Column(Integer, primary_key=True, nullable=False)
    title: str = Column(String, nullable=False)
    content: str = Column(String, nullable=False)
    published: bool = Column(Boolean, server_default='TRUE', nullable=False)
    created_at: str = Column(TIMESTAMP(timezone=True),
                             nullable=False, server_default=text('now()'))

