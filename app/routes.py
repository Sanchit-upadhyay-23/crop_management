from app import app
from functools import wraps
from datetime import datetime
import jwt
from flask import Flask, request, jsonify
import json
import traceback
from sqlalchemy import create_engine, text
from utils.helper import user_creation_validator
from flask_bcrypt import Bcrypt
import os
from auth.authorization import authorize, generate_token
from utils.helper import check_hash, generate_hash, execute_query
import hashlib


bcrypt = Bcrypt()
engine = create_engine("postgresql+psycopg2://sanchit:sanchit@localhost:5432/postgres")
secret_key = os.getenv("SECRET_KEY", None)

@app.route("/welcome")
def welcome():
    return "fmgc management system"

@app.route("/get_inventory_admin", methods = ["GET"])
def get_all_crops():
    query = text(f"select * from trace_inventory")
    inventory_data = []
    with engine.connect() as conn:
        result = conn.execute(query)
        conn.commit()
    for item in result.mappings():# sqlalchemy method which giveds mapping of the rows to the columns because this query will give the rows in a without mapped with column. 
        inventory_data.append(dict(item))
    return inventory_data, 200

@app.route("/get_specific_product_details", methods = ['GET'])
def get_specific_product_details():
    payload = request.get_json(silent=True)
    data = payload['data']
    
    name = data[0]['product_name']
    type = data[0]['product_type']
    query = text(f"select product_name, product_type, brand, product_quantity, quantity_unit, mfg_date, exp_date, selling_price from trace_inventory where product_name = '{name}' and product_type = '{type}' ")
    print(str(query))
    product_data = []
    with engine.connect() as con:
        result = con.execute(query)
        con.commit()
    for item in result.mappings():
        product_data.append(dict(item))
    print(product_data)
    return json.dumps(product_data)


@app.route("/add_trace_inventory", methods = ['POST'])
#@authorize
def add_trace_inventory():
    data = request.get_json(silent=True)
    for item in data["data"]:
        pro_id, exist = check_hash(**item)
        if exist:
            select_query = text(f"select total_quantity from trace_inventory where product_id = '{pro_id}'")
            result = execute_query(engine, query=select_query)
            total_quantity = result.fetchone()[0]
            if item["operation"].lower() == 'buy': #buy = reduce inventory
                if item['total_quantity'] > total_quantity:
                    return f" we only have {total_quantity} quantity of this product but you have requested for {item['total_quantity']} quantity "
                update_query = text(f"update trace_inventory set total_quantity = total_quantity - {int(item['total_quantity'])}, last_updated = '{datetime.now()}' where product_id = '{pro_id}' ;")
            else:
                update_query = text(f"update trace_inventory set total_quantity = total_quantity + {int(item['total_quantity'])}, last_updated = '{datetime.now()}' where product_id = '{pro_id}' ;")

            # if int(item['total_quantiy']) > total_quantity:
            #     response = f"Requested Quantity {item['total_quantity']} is not available. Available Quanity : {total_quantity}"
            #     return response, 404
        else:
            if item["operation"].lower() == 'buy':
                return f" {item['product_name']} {item['product_type']} is not available "
            else:
                items = {
                    "product_id" : generate_hash(**item),
                    "product_name" : item["product_name"],
                    "product_type" : item["product_type"],
                    "brand" : item["brand"],
                    "product_quantity" : item["product_quantity"],
                    "quantity_unit" : item["quantity_unit"],
                    "mfg_date" : item["mfg_date"],
                    "exp_date" : item["exp_date"],
                    "total_quantity" : item["total_quantity"],
                    "buying_price" : item["buying_price"],
                    "selling_price" : item["selling_price"]
                }
                columns, values = tuple(items.keys()), tuple(items.values())
                columns = str(columns).replace("'", "")
                update_query = text(f"insert into trace_inventory {columns} VALUES {values}")
        execute_query(engine, query=update_query)
    return f" thanks for your love", 201

@app.route("/update_inventory", methods = ['POST'])

def update_inventory():
    payload = request.get_json(silent=True) #payload contains list of 
    
    crop_name,quantity,operation = payload.get('name',''), payload.get('quantity', 0), payload.get('operation','')

    if not crop_name or not quantity or not operation:
        raise ValueError("Crop name, quantity and operation is required!!!")
    
    params = {'crop_name':crop_name,'quantity':quantity}
    if operation.lower() == 'sell':
        query = text(f" update current_crop_inventory set quantity = quantity - :quantity where crop_name= :crop_name returning quantity;")
    else:
        query = text(f" update current_crop_inventory set quantity = quantity + :quantity where crop_name= :crop_name returning quantity;")

    try:
        with engine.connect() as con: 
            result = con.execute(query,params)
            result=result.fetchone()
            con.commit()
    except Exception as e:
        print('Exception while executing postgres query, message: ',str(e))
    return f"Quantity has been updated by operation {operation.lower()} in {quantity} quntity for crop name: {crop_name} now updated quantity is {result[0]}",200
    
@app.route("/register", methods = ["POST"])
def register():
    payload = request.get_json(silent=True)
    #username = payload["username"]
    payload['password'] = bcrypt.generate_password_hash(payload['password']).decode('utf-8')
    nulls = user_creation_validator(payload)
    if nulls:
        return f"Please provide {nulls.keys()} entry !!", 400

    hash_id = '' 
    hash_id == hash_id + payload['username']
    hash_id == hash_id + payload['user_type']
    hash_id == hash_id + payload['password']
    user_id = hashlib.md5(str(hash_id).encode()).hexdigest()

    existing_user = None
    check_user_query = text(f"Select * from users where user_id = '{user_id}'")
    with engine.connect() as con:
        check_user_result = con.execute(check_user_query)
        con.commit()
    for item in check_user_result.mappings():
        existing_user = dict(item)["username"] # to convert sql alchemy object into dictionary and extract value of username from it.
    if existing_user:
        return f"User already exists {payload['username']} !!", 400 
    payload['user_id']=user_id
    columns, values = tuple(payload.keys()), tuple(payload.values())
    columns = str(columns).replace("'", "") # removing single quotes from columns list converting it to string since writing insert query there should'nt be quotes in columns string
    query = text(f"insert into users {columns} values {values}")
    with engine.connect() as con:
        result = con.execute(query)
        con.commit()
    return f"User {payload['username']} is registered successfully", 201

@app.route("/login", methods = ["GET"])
def login():
    payload = request.get_json(silent=True)
    if not payload["user_id"] or not payload["password"]:
        raise ValueError("No username or password entered")
    query = text(f"select * from users where user_id = :user_id")
    with engine.connect() as con:
        result = con.execute(query, payload)
        con.commit()
    query_result = None
    for item in result.mappings():
        query_result = dict(item)
    check = bcrypt.check_password_hash(query_result["password"], payload["password"])
    if not check:
        return ("Invalid UserID or Password"),404
    else:
        success_response = {
            "result" : "success",
            "status_code" : 200,
            "token" : generate_token(payload, secret_key)
        }
        return success_response
    

def generate_token(payload, secret_key):
    #payload = {
        #"user_id": "sanchit_23", 
        #"password": "Sanchit23@"
    #'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  
            # }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    print("Generated Token:", token)
    return token

def validate_token(token):
        decoded_payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        query = text(f"select user_id from users where user_id = :user_id")
        with engine.connect() as con:
            result = con.execute(query, payload)
        user_id = decoded_payload.get('user_id')
        print(f"Token is valid. User ID: {user_id}")

# is_valid = validate_token(token, secret_key)
# print("Is the token valid?", is_valid)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if the token is provided in the headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            # Decode the token
            decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
            # You can add more checks here (e.g., user roles, etc.)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return decorated #return decorated allows the decorator to replace the original function with the wrapper function that contains the added behavior.



