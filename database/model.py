from sqlalchemy import create_engine, Column, Integer, VARCHAR, FLOAT, TIMESTAMP, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# Create an in-memory SQLite database engine
engine = create_engine('postgresql+psycopg2://postgres:sanchit@localhost:5432/postgres')

# Define Table Classes
Base = declarative_base()

class crop_inventory(Base):
    __tablename__ = 'crop_inventory'
    __table_args__ = {'schema': 'public'}

    crop_name = Column(VARCHAR(64), primary_key=True)
    room_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    quantity_unit = Column(VARCHAR(64), nullable=False)
    current_price = Column(FLOAT, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=text('NOW()'))
    last_updated = Column(DateTime(timezone=True), default=func.now(), server_default=text('NOW()'), onupdate=func.current_timestamp())
    
class selling_history(Base):
    __tablename__ = 'crop_history'
    __table_args__ = {'schema': 'public'}

    order_id = Column(Integer, autoincrement=True, primary_key=True)
    crop_name = Column(VARCHAR(64), nullable=False)
    quantity = Column(Integer, nullable=False)
    sold_price = Column(FLOAT, nullable=False)
    sold_unit = Column(Integer, nullable=False)
    sold_time = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=text('NOW()'))

class inventory_history(Base):
    __tablename__ = 'inventory_history'
    __table_args__ = {'schema': 'public'}

    product_id = Column(VARCHAR(64), primary_key=True)
    crop_name = Column(VARCHAR(64), primary_key=True)
    room_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    quantity_unit = Column(VARCHAR(64), nullable=False)
    total_quantity = Column(FLOAT, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=text('NOW()'))
    last_updated = Column(DateTime(timezone=True), default=func.now(), server_default=text('NOW()'), onupdate=func.current_timestamp())


class users(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'public'}
    user_id = Column(VARCHAR(255), primary_key=True)
    username = Column(VARCHAR(64), nullable=False)
    password = Column(VARCHAR(64), nullable=False)
    user_type = Column(VARCHAR(64), nullable=False)
    email = Column(VARCHAR(64), nullable=False)
    mobile_number = Column(VARCHAR(64), nullable=False)

class crop_dashboard(Base):
    __tablename__ = 'crop_dashboard'
    __table_args__ = {'schema': 'public'}

    crop_name = Column(VARCHAR(64), primary_key=True)
    quantity = Column(Integer, nullable=False)
    quantity_unit = Column(VARCHAR(64), nullable=False)
    selling_price = Column(FLOAT, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=text('NOW()'))
    last_updated = Column(DateTime(timezone=True), default=func.now(), server_default=text('NOW()'), onupdate=func.current_timestamp())
    
# Create the tables in the in-memory database
Base.metadata.create_all(engine) 
