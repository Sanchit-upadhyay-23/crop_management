import redis
 
redis_client = redis.StrictRedis.from_url('redis://localhost:6379/0')
 
redis_client.set('key', 'value')
data = redis_client.get('key')
print(data) 