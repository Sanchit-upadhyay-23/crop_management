from sqlalchemy import create_engine, Column, Integer, VARCHAR, FLOAT, TIMESTAMP, DateTime, text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# Create an in-memory SQLite database engine
engine = create_engine('postgresql+psycopg2://sanchit:sanchit@localhost:5432/postgres')

# Define Table Classes
Base = declarative_base()
metadata = Base.metadata

class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'public'}
    user_id = Column(VARCHAR(255), primary_key=True)
    username = Column(VARCHAR(64), nullable=False)
    password = Column(VARCHAR(64), nullable=False)
    user_type = Column(VARCHAR(20), nullable=False)
    email = Column(VARCHAR(64), nullable=False)
    mobile_number = Column(VARCHAR(64), nullable=False)
    address = Column(VARCHAR(255))

class TraceInventory(Base):
    __tablename__ = 'trace_inventory'
    __table_args__ = {'schema': 'public'}
    product_id = Column(VARCHAR(255), primary_key=True)
    product_name = Column(VARCHAR(64), nullable=False)
    product_type = Column(VARCHAR(64))
    brand = Column(VARCHAR(64))
    Category = Column(VARCHAR(64))
    product_quantity = Column(Integer, nullable=False)
    quantity_unit = Column(VARCHAR(64), nullable=False)
    mfg_date = Column(VARCHAR(64), nullable=False)
    exp_date = Column(VARCHAR(64), nullable=False)
    total_quantity = Column(Integer, nullable=False)
    buying_price = Column(FLOAT, nullable=False) #convert this buy price into average buy price in api
    selling_price = Column(FLOAT, nullable=False) 
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=text('NOW()'))
    updated_at = Column(DateTime(timezone=True), default=func.now(), server_default=text('NOW()'), onupdate=func.current_timestamp())
    
class BuyingHistory(Base):
    __tablename__ = 'buying_history'
    __table_args__ = {'schema': 'public'}

    order_id = Column(Integer, primary_key=True)
    user_id = Column(VARCHAR, ForeignKey(Users.user_id), nullable=False)
    product_id = Column(VARCHAR(255), ForeignKey(TraceInventory.product_id), nullable=False)
    product_quantity = Column(Integer, nullable=False)
    quantity_unit = Column(VARCHAR(64), nullable=False)
    buy_price = Column(FLOAT, nullable=False)
    adv_payment = Column(FLOAT, nullable=False)
    rest_payment = Column(FLOAT, nullable=False)
    buy_time = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=text('NOW()'))

class SellingHistory(Base):
    __tablename__ = 'selling_history'
    __table_args__ = {'schema': 'public'}

    order_id = Column(Integer, primary_key=True)
    user_id = Column(VARCHAR, ForeignKey(Users.user_id), nullable=False)
    product_id = Column(VARCHAR(255), ForeignKey(TraceInventory.product_id), nullable=False)
    product_quantity = Column(Integer, nullable=False)
    quantity_unit = Column(VARCHAR(64), nullable=False)
    sold_price = Column(FLOAT, nullable=False)
    adv_payment = Column(FLOAT, nullable=False)
    rest_payment = Column(FLOAT, nullable=False)
    sold_time = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=text('NOW()'))
    
# Create the tables in the in-memory database
# Base.metadata.create_all(engine) # not useing this any more because updating the data base with alembic.
