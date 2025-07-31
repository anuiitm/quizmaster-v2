"""
Cache Management API
Provides endpoints for cache monitoring and management
"""
from flask import Blueprint, jsonify, request
from backend.utils.decorators import admin_secure_endpoint
from backend.utils.cache import (
    clear_all_cache, 
    get_cache_stats, 
    warm_cache,
    get_redis_client
)
from backend.utils.performance import (
    get_performance_stats,
    get_slow_queries,
    get_cache_performance
)
import redis

cache_bp = Blueprint('cache', __name__)

@cache_bp.route('/stats', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=30)
def get_cache_statistics():
    """Get cache statistics and Redis info"""
    try:
        stats = get_cache_stats()
        return jsonify({
            'success': True,
            'cache_stats': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cache_bp.route('/clear', methods=['POST'])
@admin_secure_endpoint(rate_limit_requests=10)
def clear_cache():
    """Clear all cache entries"""
    try:
        cleared_count = clear_all_cache()
        return jsonify({
            'success': True,
            'message': f'Cleared {cleared_count} cache entries',
            'cleared_count': cleared_count
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cache_bp.route('/warm', methods=['POST'])
@admin_secure_endpoint(rate_limit_requests=10)
def warm_cache_endpoint():
    """Warm cache with frequently accessed data"""
    try:
        # Common cache patterns to warm
        patterns = [
            "cache:backend.api.admin.get_subjects*",
            "cache:backend.api.user.get_quizzes*",
            "cache:backend.api.admin.get_users*"
        ]
        
        result = warm_cache(patterns)
        return jsonify({
            'success': True,
            'message': 'Cache warming initiated',
            'warmed_keys': result.get('warmed_keys', 0),
            'patterns': result.get('patterns', [])
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cache_bp.route('/health', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=60)
def cache_health_check():
    """Check Redis connection and cache health"""
    try:
        redis_client = get_redis_client()
        
        # Test Redis connection
        redis_client.ping()
        
        # Get Redis info
        info = redis_client.info()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'redis_version': info.get('redis_version'),
            'connected_clients': info.get('connected_clients'),
            'used_memory_human': info.get('used_memory_human'),
            'uptime_in_seconds': info.get('uptime_in_seconds')
        }), 200
    except redis.ConnectionError:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': 'Redis connection failed'
        }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@cache_bp.route('/keys', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=30)
def list_cache_keys():
    """List all cache keys (for debugging)"""
    try:
        redis_client = get_redis_client()
        
        # Get all cache keys
        cache_keys = redis_client.keys("cache:*")
        rate_limit_keys = redis_client.keys("rate_limit:*")
        
        # Get key details (limit to first 50 for performance)
        cache_details = []
        for key in cache_keys[:50]:
            ttl = redis_client.ttl(key)
            cache_details.append({
                'key': key,
                'ttl': ttl if ttl > 0 else 'no expiry'
            })
        
        return jsonify({
            'success': True,
            'cache_keys_count': len(cache_keys),
            'rate_limit_keys_count': len(rate_limit_keys),
            'cache_keys_sample': cache_details,
            'total_keys_shown': min(50, len(cache_keys))
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cache_bp.route('/performance', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=30)
def get_performance_metrics():
    """Get performance metrics and statistics"""
    try:
        # Get query parameters
        days = request.args.get('days', 7, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Get various performance metrics
        performance_stats = get_performance_stats(days)
        slow_queries = get_slow_queries(limit)
        cache_performance = get_cache_performance()
        
        return jsonify({
            'success': True,
            'performance_stats': performance_stats,
            'slow_queries': slow_queries,
            'cache_performance': cache_performance,
            'query_params': {
                'days': days,
                'limit': limit
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cache_bp.route('/performance/slow', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=30)
def get_slow_queries_endpoint():
    """Get slowest API queries"""
    try:
        limit = request.args.get('limit', 10, type=int)
        slow_queries = get_slow_queries(limit)
        
        return jsonify({
            'success': True,
            'slow_queries': slow_queries,
            'total_slow_queries': len(slow_queries)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cache_bp.route('/performance/stats', methods=['GET'])
@admin_secure_endpoint(rate_limit_requests=30)
def get_performance_stats_endpoint():
    """Get performance statistics"""
    try:
        days = request.args.get('days', 7, type=int)
        performance_stats = get_performance_stats(days)
        
        return jsonify({
            'success': True,
            'performance_stats': performance_stats,
            'days_requested': days
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 