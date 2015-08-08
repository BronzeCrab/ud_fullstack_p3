import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()


class User(Base):
    __tablename__ = 'userinfo'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(320), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    item = relationship("Item", cascade="delete")
    user_id = Column(Integer, ForeignKey('userinfo.id'))
    user = relationship(User)

    @property
    def serialize(self):

        return {
            'name': self.name,
            'id': self.id,
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(700))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category")
    user_id = Column(Integer, ForeignKey('userinfo.id'))
    user = relationship(User)
    # We added this serialize function to be able to send JSON objects in a
    # serializable format

    @property
    def serialize(self):

        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
        }
# Parsing db.cfg for database role, pass and name of db
# to connect to
def parseCFG():
    data = []
    with open("db.cfg",'r') as cfg:
        for line in cfg:
            data.append(line.split("=")[1])
            # removing trailing '\n' character
            if data[-1][-1] == "\n":
                data[-1] = data[-1][::-1][1:][::-1]

    username = data[0]
    passwd = data[1]
    db = data[2]
    return (username, passwd, db)
    
res = parseCFG()
eng_str = 'postgresql://{}:{}@localhost/{}'.format(res[0], res[1], res[2])

engine = create_engine(eng_str)
if not database_exists(engine.url):
    create_database(engine.url)

# print(database_exists(engine.url))

Base.metadata.create_all(engine)
