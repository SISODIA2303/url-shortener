#Redis connection for storing the data in RAM instead of a disk. Using it as a cache for the data to speed up the access time.
import redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL") 
client=redis.from_url(REDIS_URL, decode_responses=True) #creates Redis client connected to the Redis Server, Redis returns Python strings instead of raw bytes
CACHE_EXPIRY = 3600 #cache URL expired time in seconds (1 hour)

def get_cached_url(short_code:str): #looks up for short code in Redis, if found returns the original url
    return client.get(f"url:{short_code}") 

def set_cached_url(short_code:str, original_url:str):
    client.setex(f"url:{short_code}",CACHE_EXPIRY,original_url) #stores a value in Redis with expiry time

def increment_clicks(short_code:str):
    client.incr(f"clicks:{short_code}") #increments a counter in Redis by 1

def get_cached_clicks(short_code:str): #reads the click counter from Redis
    count=client.get(f"clicks:{short_code}")
    return int(count) if count else 0

def is_rate_limited(ip:str, limit:int=10, window:int=60)->bool:
    key=f"ratelimit:{ip}"
    count=client.get(key)

    if count is None:
        client.setex(key,window,1)
        return False
    if int(count)>=limit:
        return True
    client.incr(key)
    return False

