
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///database.db', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
session = Session()
db = session

 
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Filter(Base):
    __tablename__ = 'filters'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    operation = Column(String)
    value_const = Column(String)

    def to_json(self):
        return {'id': self.id, 'name': self.name, 'operation': self.operation, 'value_const': self.value_const}


class Block(Base):
    __tablename__ = 'blocks'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    max_sum = Column(Integer)
    percent = Column(Float)
    years = Column(Integer)

    def to_json(self):
        return {'id': self.id, 'name': self.name, 'max_sum': self.max_sum, 'percent': self.percent, 'years': self.years}

class FilterBlock(Base):
    __tablename__ = 'filter_block'
    filter_id = Column(Integer, ForeignKey('filters.id'), primary_key=True)
    block_id = Column(Integer, ForeignKey('blocks.id'), primary_key=True)
    

class UserApplication(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    block_id = Column(Integer, ForeignKey('blocks.id'))
    name = Column(String)
    surname = Column(String)
    middle_name = Column(String)
    phone = Column(String)
    result = Column(String) # Accept / Reason to decline - hidden field
    accepted = Column(Boolean)

    def to_json(self):
        return {'id': self.id, 'block_id': self.block_id, 'name': self.name, 'surname': self.surname, 'middle_name': self.middle_name, 'phone': self.phone, 'result': self.result, 'accepted': self.accepted}


def create_user_application(block_id, name, surname, middle_name, phone, result, accepted):
    ua = UserApplication(block_id=block_id, name=name, surname=surname, middle_name=middle_name, phone=phone, result=result, accepted=accepted)
    db.add(ua)
    db.commit()
    return ua

def get_user_applications():
    return db.query(UserApplication).all()

# create filter, return filter id
def create_filter(name, operation, value_const):
    # cheeck if filter with same name and operation exists
    f = db.query(Filter).filter_by(name=name, operation=operation, value_const=value_const).first()
    if f is None:
        f = Filter(name=name, operation=operation, value_const=value_const)
        db.add(f)
        db.commit()
    return f

# create block, return block id
def create_block(name, max_sum, percent, years):
    b = Block(name=name, max_sum=max_sum, percent=percent, years=years)
    db.add(b)
    db.commit()
    return b

# add filter to block
def add_filter_to_block(filter_id, block_id):
    fb = FilterBlock(filter_id=filter_id, block_id=block_id)
    db.add(fb)
    db.commit()

# delete filter from block
def delete_filter_from_block(filter_id, block_id):
    fb = db.query(FilterBlock).filter_by(filter_id=filter_id, block_id=block_id).first()
    db.delete(fb)
    db.commit()

# get all filters
def get_filters():
    return db.query(Filter).all()

# get all filters by block
def get_filters_by_block(block_id):
    return db.query(Filter).join(FilterBlock).filter(FilterBlock.block_id == block_id).all()

# get all blocks
def get_blocks():
    return db.query(Block).all()

# get single block
def get_block_by_id(block_id):
    return db.query(Block).filter_by(id=block_id).first()

Base.metadata.create_all(engine)