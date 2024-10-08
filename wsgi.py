 
from app import app # from app module import app variable/function/class.
# in app this function is in __init__ so we can access by app but if it is in module or any other folder then we have to use from app/module
if __name__ == "__main__":
    app.run(port=5001)