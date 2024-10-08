import pandas as pd
import names
import random
import uuid
from datetime import datetime, timedelta

# Function to generate random dates within the last year
def random_date():
    start_date = datetime.now() - timedelta(days=365)
    return start_date + timedelta(days=random.randint(0, 365))
  # Example output: 'hszkdfwe'

# Create User Data
def generate_users(num_users=100):
    for i in range(num_users):
        full_name = names.get_full_name()
        user_data = {
            'user_id': uuid.uuid4().hex,
            'username': full_name,
            'email': f'{full_name}@example.com',
            'created_at': random_date().strftime('%Y-%m-%d %H:%M:%S')
        }
    df_users = pd.DataFrame(user_data)
    df_users.to_csv('users.csv', index=False)
    print("Generated users.csv")
    df = pd.read_csv("users.csv")
    print(df)
    return df_users

# Create Product Data
def generate_products(num_products=100):
    categories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Sports', 'Books']
    product_data = {
        'product_id': [uuid.uuid4().hex for _ in range(num_products)],
        'product_name': [f'Product_{i}' for i in range(num_products)],
        'category': [random.choice(categories) for _ in range(num_products)],
        'price': [round(random.uniform(5, 1000), 2) for _ in range(num_products)], # returns a random floating-point number such that a <= number <= b.
        'stock_level': [random.randint(10, 500) for _ in range(num_products)],
        'created_at': [random_date().strftime('%Y-%m-%d %H:%M:%S') for _ in range(num_products)],
    }
    df_products = pd.DataFrame(product_data)
    df_products.to_csv('products.csv', index=False)
    print("Generated products.csv")
    return df_products

# Create Orders Data
# def generate_orders(num_orders=100):
#     df_users = pd.read_csv('users.csv')
#     df_products = pd.read_csv('products.csv')

#     order_data = {
#         'order_id': [uuid.uuid4().hex for _ in range(num_orders)],
#         'user_id': [random.choice(df_users['user_id']) for _ in range(num_orders)],
#         'product_id': [random.choice(df_products['product_id']) for _ in range(num_orders)],
#         'quantity': [random.randint(1, 5) for _ in range(num_orders)],
#         'order_date': [random_date().strftime('%Y-%m-%d %H:%M:%S') for _ in range(num_orders)],
#         'total_price': [round(random.uniform(10, 2000), 2) for _ in range(num_orders)]
#     }
    
#     df_orders = pd.DataFrame(order_data)
#     df_orders.to_csv('orders.csv', index=False)
#     print("Generated orders.csv")
#     return df_orders

if __name__ == "__main__":
    # Generate data
    generate_users(100)      # Generating 100 users
    #generate_products(100)   # Generating 100 products
    # generate_orders(200)     # Generating 200 orders

# Create all users from users.csv to DB :
from sqlalchemy import create_engine, text
import pandas as pd
import hashlib, json
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
engine = create_engine("postgresql+psycopg2://sanchit:sanchit@localhost:5432/postgres")
df = pd.read_csv("/Users/sanchit/Documents/Projects/crop_management/users.csv", usecols=["username","password","user_type","email","mobile_number","address", "user_id"])
payload = df.to_dict(orient='records')
for user in payload:
    user['password'] = bcrypt.generate_password_hash(str(user['password'])).decode('utf-8')
    columns, values = tuple(user.keys()), tuple(user.values())
    columns = str(columns).replace("'", "") # removing single quotes from columns list converting it to string since writing insert query there should'nt be quotes in columns string
    query = text(f"insert into users {columns} values {values}")
    print(f"Query : {query}")
    with engine.connect() as con:
        result = con.execute(query)
        con.commit()
    print(f"Created user : {user['username']} in DB")
print("Created all Users")