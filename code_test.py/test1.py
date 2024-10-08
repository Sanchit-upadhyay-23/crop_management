import hashlib
data = {'name':'sanchit','type':'admin'}
hash_id = '' 
hash_id == hash_id + data['name']
hash_id == hash_id + data['type']
user_id = hashlib.md5(str(hash_id).encode()).hexdigest()

print(user_id)