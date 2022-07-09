import sqlalchemy as sa
from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.ext import declarative

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
