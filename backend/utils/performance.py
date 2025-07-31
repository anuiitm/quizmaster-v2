"""
Performance Monitoring Middleware
Provides response time tracking and performance metrics
"""
import time
import functools
from flask import request, g, current_app
from backend.utils.cache import get_redis_client
import json

def track_performance(func):
    """Decorator to track API performance metrics"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Execute the function
        response = func(*args, **kwargs)
        
        # Calculate response time
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Store performance metrics
        store_performance_metrics(request.path, request.method, response_time, response)
        
        return response
    
    return wrapper

def store_performance_metrics(path, method, response_time, response):
    """Store performance metrics in Redis"""
    try:
        redis_client = get_redis_client()
        
        # Get response status code
        status_code = 200
        if isinstance(response, tuple):
            status_code = response[1] if len(response) > 1 else 200
        
        # Create metrics data
        metrics = {
            'path': path,
            'method': method,
            'response_time_ms': round(response_time, 2),
            'status_code': status_code,
            'timestamp': time.time(),
            'user_id': getattr(g, 'user_id', None),
            'is_admin': getattr(g, 'is_admin', False)
        }
        
        # Store in Redis with TTL (24 hours)
        key = f"perf:{path}:{method}:{int(time.time() // 3600)}"
        redis_client.lpush(key, json.dumps(metrics))
        redis_client.expire(key, 86400)  # 24 hours
        
        # Update aggregate statistics
        update_aggregate_stats(path, method, response_time, status_code)
        
    except Exception as e:
        current_app.logger.warning(f"Failed to store performance metrics: {e}")

def update_aggregate_stats(path, method, response_time, status_code):
    """Update aggregate performance statistics"""
    try:
        redis_client = get_redis_client()
        
        # Key for aggregate stats (daily)
        date_key = time.strftime("%Y-%m-%d")
        stats_key = f"stats:aggregate:{date_key}"
        
        # Get current stats
        current_stats = redis_client.get(stats_key)
        if current_stats:
            stats = json.loads(current_stats)
        else:
            stats = {
                'total_requests': 0,
                'total_response_time': 0,
                'avg_response_time': 0,
                'min_response_time': float('inf'),
                'max_response_time': 0,
                'status_codes': {},
                'endpoints': {}
            }
        
        # Update stats
        stats['total_requests'] += 1
        stats['total_response_time'] += response_time
        stats['avg_response_time'] = stats['total_response_time'] / stats['total_requests']
        stats['min_response_time'] = min(stats['min_response_time'], response_time)
        stats['max_response_time'] = max(stats['max_response_time'], response_time)
        
        # Update status code counts
        status_str = str(status_code)
        stats['status_codes'][status_str] = stats['status_codes'].get(status_str, 0) + 1
        
        # Update endpoint stats
        endpoint_key = f"{method}:{path}"
        if endpoint_key not in stats['endpoints']:
            stats['endpoints'][endpoint_key] = {
                'count': 0,
                'total_time': 0,
                'avg_time': 0
            }
        
        endpoint_stats = stats['endpoints'][endpoint_key]
        endpoint_stats['count'] += 1
        endpoint_stats['total_time'] += response_time
        endpoint_stats['avg_time'] = endpoint_stats['total_time'] / endpoint_stats['count']
        
        # Store updated stats
        redis_client.setex(stats_key, 86400, json.dumps(stats))
        
    except Exception as e:
        current_app.logger.warning(f"Failed to update aggregate stats: {e}")

def get_performance_stats(days: int = 7):
    """Get performance statistics for the last N days"""
    try:
        redis_client = get_redis_client()
        stats = []
        
        for i in range(days):
            date_key = time.strftime("%Y-%m-%d", time.localtime(time.time() - i * 86400))
            stats_key = f"stats:aggregate:{date_key}"
            
            daily_stats = redis_client.get(stats_key)
            if daily_stats:
                stats.append({
                    'date': date_key,
                    'stats': json.loads(daily_stats)
                })
        
        return stats
    except Exception as e:
        current_app.logger.error(f"Failed to get performance stats: {e}")
        return []

def get_slow_queries(limit: int = 10):
    """Get the slowest API queries"""
    try:
        redis_client = get_redis_client()
        slow_queries = []
        
        # Get all performance keys
        perf_keys = redis_client.keys("perf:*")
        
        for key in perf_keys:
            # Get recent entries for this endpoint
            entries = redis_client.lrange(key, 0, 99)  # Last 100 entries
            
            for entry in entries:
                try:
                    data = json.loads(entry)
                    if data['response_time_ms'] > 1000:  # Slower than 1 second
                        slow_queries.append(data)
                except:
                    continue
        
        # Sort by response time and return top N
        slow_queries.sort(key=lambda x: x['response_time_ms'], reverse=True)
        return slow_queries[:limit]
        
    except Exception as e:
        current_app.logger.error(f"Failed to get slow queries: {e}")
        return []

def get_cache_performance():
    """Get cache performance metrics"""
    try:
        redis_client = get_redis_client()
        
        # Get cache hit/miss statistics
        cache_keys = redis_client.keys("cache:*")
        rate_limit_keys = redis_client.keys("rate_limit:*")
        
        # Calculate cache efficiency (this would need to be tracked separately)
        cache_stats = {
            'total_cache_keys': len(cache_keys),
            'total_rate_limit_keys': len(rate_limit_keys),
            'memory_usage': redis_client.info()['used_memory_human'],
            'redis_version': redis_client.info()['redis_version']
        }
        
        return cache_stats
    except Exception as e:
        current_app.logger.error(f"Failed to get cache performance: {e}")
        return {}

def performance_middleware():
    """Flask middleware for performance tracking"""
    def before_request():
        g.start_time = time.time()
    
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            response.headers['X-Response-Time'] = str(duration)
        return response
    
    return before_request, after_request 