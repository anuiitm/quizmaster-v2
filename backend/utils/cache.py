"""
Redis Caching and Rate Limiting Module
Provides decorators for API optimization and security
"""
import redis
from redis.exceptions import RedisError
from functools import wraps
from flask import request, jsonify, g
import json
import time

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_redis_client():
    return redis_client

def get_client_identifier():
    ip = request.remote_addr
    user_id = getattr(g, 'user_id', 'anonymous') if hasattr(g, 'user_id') else 'anonymous'
    return f"{ip}:{user_id}"

def get_current_window():
    return int(time.time() // 60)

def cache_response(expire_time=300, key_prefix="cache"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{key_prefix}:{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            cached_response = redis_client.get(cache_key)
            if cached_response:
                cached_data = json.loads(cached_response)
                if isinstance(cached_data, dict) and 'data' in cached_data:
                    from flask import jsonify
                    return jsonify(cached_data['data']), cached_data.get('status_code', 200)
                else:
                    return cached_data
            
            result = f(*args, **kwargs)
            
            if isinstance(result, tuple):
                response_data, status_code = result
            else:
                response_data, status_code = result, 200
            
            cache_data = {
                'data': response_data.get_json() if hasattr(response_data, 'get_json') else response_data,
                'status_code': status_code
            }
            
            redis_client.setex(cache_key, expire_time, json.dumps(cache_data))
            
            return result
        return decorated_function
    return decorator

def cache_user_specific(expire_time=300):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = getattr(g, 'user_id', 'anonymous') if hasattr(g, 'user_id') else 'anonymous'
            cache_key = f"cache:user:{user_id}:{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            cached_response = redis_client.get(cache_key)
            if cached_response:
                cached_data = json.loads(cached_response)
                if isinstance(cached_data, dict) and 'data' in cached_data:
                    from flask import jsonify
                    return jsonify(cached_data['data']), cached_data.get('status_code', 200)
                else:
                    return cached_data
            
            result = f(*args, **kwargs)
            
            if isinstance(result, tuple):
                response_data, status_code = result
            else:
                response_data, status_code = result, 200
            
            cache_data = {
                'data': response_data.get_json() if hasattr(response_data, 'get_json') else response_data,
                'status_code': status_code
            }
            
            redis_client.setex(cache_key, expire_time, json.dumps(cache_data))
            
            return result
        return decorated_function
    return decorator

def invalidate_cache(pattern="cache:*"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            try:
                redis_client = get_redis_client()
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
            except RedisError:
                pass
            
            return result
        return decorated_function
    return decorator

def rate_limit(requests_per_minute=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                redis_client = get_redis_client()
                identifier = get_client_identifier()
                current_window = get_current_window()
                key = f"rate_limit:{identifier}:{current_window}"
                
                current_requests = redis_client.get(key)
                if current_requests and int(current_requests) >= requests_per_minute:
                    return jsonify({'message': 'Rate limit exceeded'}), 429
                
                pipe = redis_client.pipeline()
                pipe.incr(key)
                pipe.expire(key, 60)
                pipe.execute()
                
            except RedisError:
                pass
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def clear_all_cache():
    try:
        redis_client = get_redis_client()
        keys = redis_client.keys("cache:*")
        if keys:
            deleted = redis_client.delete(*keys)
            return deleted
        return 0
    except RedisError:
        return 0

def get_cache_stats():
    try:
        redis_client = get_redis_client()
        cache_keys = redis_client.keys("cache:*")
        rate_limit_keys = redis_client.keys("rate_limit:*")
        
        return {
            'cache_entries': len(cache_keys),
            'rate_limit_entries': len(rate_limit_keys),
            'total_memory': redis_client.info()['used_memory_human'],
            'redis_version': redis_client.info()['redis_version']
        }
    except RedisError:
        return {}

def warm_cache(patterns):
    try:
        redis_client = get_redis_client()
        warmed_keys = []
        
        for pattern in patterns:
            keys = redis_client.keys(pattern)
            warmed_keys.extend(keys)
        
        return {
            'warmed_keys': len(warmed_keys),
            'patterns': patterns
        }
    except RedisError:
        return {} 