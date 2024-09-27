from app import app
from functools import wraps
import jwt
from flask import Flask, request, jsonify
import json
import traceback
from sqlalchemy import create_engine, text
from utils.helper import user_creation_validator
from flask_bcrypt import Bcrypt
import os
from auth.authorization import authorize, generate_token

bcrypt = Bcrypt()
engine = create_engine("postgresql+psycopg2://postgres:sanchit@localhost:5432/postgres")
secret_key = os.getenv("SECRET_KEY", None)

@app.route("/welcome")
def welcome():
    return "crop management system"

def execute_query(engine, query, params=None):
    if type(query) == str:
        query = text(query)
    result = []
    try:
        with engine.connect() as conn:
            result = conn.execute(query, params)
            conn.commit()
    except Exception as e:
        print(f"Exception while executing postgres query, message:{str(e)}")
        print(traceback.format_exc())
    return result

@app.route("/get_all_crop", methods = ["GET"])
def get_all_crops():
    query = text(f"select * from crop_inventory")
    crop_data = []
    with engine.connect() as conn:
        result = conn.execute(query)
        conn.commit()
    for item in result.mappings():# sqlalchemy method which giveds mapping of the rows to the columns because this query will give the rows in a without mapped with column. 
        crop_data.append(dict(item))
    return crop_data, 200

@app.route("/get_specific_crops", methods = ['POST'])
def get_specific_crops():
    data = request.get_json(silent=True)
    name = data["name"]
    query = text(f"select * from public.current_crop_inventory where crop_name = '{name}'")
    print(str(query))
    crop_data = []
    with engine.connect() as con:
        result = con.execute(query)
        con.commit()
    for item in result.mappings():
        crop_data.append(dict(item))
    print(crop_data)
    return json.dumps(crop_data)

@app.route("/add_crops", methods = ["POST"])
def add_crops():
    payload = request.get_json(silent=True)
    crop_data = payload["data"]
    for item in crop_data:
        columns, values = tuple(item.keys()), tuple(item.values())
        columns = str(columns).replace("'", "")
        query = text(f"insert into crop_inventory {columns} values {values}")
        execute_query(engine, query=query, params=item)
    
    return {"msg": "Crops added sucessfully"}, 201

@app.route("/add_crop_stocks", methods = ['POST'])
def put_crop_stock():
    data = request.get_json(silent=True)
    for item in data["data"]:
        items = {
            "crop_name" : item["name"],
            "room_id" : item["room"],
            "quantity" : item["quantity"],
            "current_price" : item["price"]
        }
        columns, values = tuple(items.keys()), tuple(items.values())
        columns = str(columns).replace("'", "")
        query = text(f"insert into public.current_crop_inventory {columns} VALUES {values}")
        with engine.connect() as con:
            result = con.execute(query)
    con.commit()
    return f"Data succesfully added {data}"

@app.route("/update_inventory", methods = ['POST'])
@authorize
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
    user_id = payload["user_id"]
    username = payload["username"]
    payload["password"] = bcrypt.generate_password_hash(payload["password"]).decode('utf-8')
    nulls = user_creation_validator(payload)
    if nulls:
        return f"Please provide {nulls.keys()} entry !!", 400
    
    existing_user = None
    check_user_query = text(f"Select * from users where user_id = '{user_id}'")
    with engine.connect() as con:
        check_user_result = con.execute(check_user_query)
        con.commit()
    for item in check_user_result.mappings():
        existing_user = dict(item)["username"]
    if existing_user:
        return f"User already exists {username} !!", 400 
    
    columns, values = tuple(payload.keys()), tuple(payload.values())
    columns = str(columns).replace("'", "") # removing single quotes from columns list converting it to string since writing insert query there should'nt be quotes in columns string
    query = text(f"insert into users {columns} values {values}")
    with engine.connect() as con:
        result = con.execute(query)
        con.commit()
    return f"User {username} is registered successfully", 201

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
    
@app.route("/crop_dashboard", methods = ['POST'])
def crop_dashboard():
    data = request.get_json(silent=True)
    for items in data["data"]:
        # login_api_url = 'http://127.0.0.1:5000/login'
        # response = request.get(login_api_url)
        # if response.status_code == 200:
        items = {
            "crop_name" : items["name"],
            "quantity" : items["quantity"],
            "quantity_unit" : items["quantity_unit"],
            "selling_price" : items["selling_price"]
        }
        columns, values = tuple(items.keys()), tuple(items.values())
        columns = str(columns).replace("'", "")
        query = text(f"insert into public.crop_dashboard {columns} VALUES {values}")
        with engine.connect() as con:
            result = con.execute(query)
        con.commit()
        return f"Data succesfully added {data}"
    
        # else:
        #     return ("Failed to access and update crop_dashboard")

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

@app.route("/testing_auth", methods = ["GET"])
@authorize
def testing():
    return f"Successful authentication"



