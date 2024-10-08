import hashlib, json
from sqlalchemy import create_engine, text
import traceback

engine = create_engine("postgresql+psycopg2://sanchit:sanchit@localhost:5432/postgres")

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


def user_creation_validator(payload = None):
    null_vars = {key: value for key, value in payload.items() if value is None}
    return null_vars


def check_hash(**payload):
    keys_to_remove = ["quantity_unit", "exp_date", "selling_price", "total_quantity", "operation"]
    for key in keys_to_remove:
        del payload[key]
   
    query = text(f"select product_id from public.trace_inventory")
    result = execute_query(engine, query=query)
    existing_id = []
    for id in result.mappings():
        existing_id.append(id.get("product_id", None))
    
    encoded_hash = json.dumps(payload).encode('utf-8') #convert the dict or tuple to jason string.
    product_id = hashlib.md5(encoded_hash).hexdigest()

    if product_id in existing_id:
        return product_id, True
    return product_id, False
    
def generate_hash(**payload):
    keys_to_remove = ["quantity_unit", "exp_date", "selling_price", "total_quantity","operation"]
    for key in keys_to_remove:
        del payload[key]
    encoded_hash = json.dumps(payload).encode('utf-8')
    product_id = hashlib.md5(encoded_hash).hexdigest()
    return product_id

    
