from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker

from occacc import sql_conf


Base = declarative_base()


class Occupancy(Base):
    __tablename__ = 'occupancy'
    id = Column(Integer, primary_key=True)
    occ = Column(Integer, nullable=False)
    diff = Column(Integer)
    location = Column(String(250))
    time = Column(DateTime, default=func.now())


engine = create_engine('{type}://{username}:{password}@{host}/{database}'.format(**sql_conf), encoding='utf-8')

Base.metadata.create_all(engine)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db = DBSession()
