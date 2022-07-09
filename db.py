import sqlalchemy as sa
from sqlalchemy import Integer, String, Column, ForeignKey, Boolean
from sqlalchemy.ext import declarative
from sqlalchemy.orm import relationship

engine = sa.create_engine('sqlite:///:memory:', echo=True)
Base = declarative.declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False, unique=True)
    telegram_chat_id = Column(Integer)
    status = Column(String)
    vk_token = Column(String)
    vk_page_id = Column(Integer)
    vk_page_name = Column(String)
    has_valid_token = Column(Boolean)
    chat = relationship("Chat")


class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), alias="Id of user that added this chat")
    chat_id = Column(Integer, nullable=False, unique=True, alias="VK_CHAT_ID")
    last_message_id = Column(Integer, default=None)


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


Base.metadata.create_all(engine)
