from functools import wraps
import jwt
import os
from sqlalchemy import create_engine, text
from flask import request, jsonify
engine = create_engine("postgresql+psycopg2://postgres:sanchit@localhost:5432/postgres")
secret_key = os.getenv("SECRET_KEY", None)

def generate_token(payload, secret_key):
    user_id = payload["password"]
    user_type = payload["user_type"]
    token_payload = {'user_id':user_id,'user_type':user_type}
    token = jwt.encode(token_payload, secret_key, algorithm='HS256')
    print("Generated Token:", token)
    return token


def authorize(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if the token is provided in the headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1] #"Authorization: Bearer <your_token>", this is token syntax of jwt token.

        if not token:
            return jsonify({'message': 'forbidden!'}), 404

        try:
            decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = decoded.get('user_id') #this line retrieves the user_id from the decoded payload.
            user_type = decoded.get('user_type')
            query = text(f"select user_type from users where user_id = '{user_id}' and user_type = '{user_type}'")
            with engine.connect() as con:
                result = con.execute(query)
                result=result.fetchone()
                con.commit()
            if not result:
                print("Invalid login credentials ")
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 404
        return f(*args, **kwargs)
    return decorated #return decorated allows the decorator to replace the original function with the wrapper function that contains the added behavior.


# @app.route('/protected', methods=['GET'])
# @authorize
# def protected_route():
#     return jsonify({'message': 'This is a protected route!'})
#curl -H "Authorization: Bearer <your_token>" http://127.0.0.1:5000/protected
# is_valid = validate_token(token, secret_key)
# print("Is the token valid?", is_valid)









