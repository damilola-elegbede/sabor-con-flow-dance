"""
Django management command for cache maintenance operations.
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache, caches
from django.conf import settings
from core.utils.cache_utils import cache_manager, CacheBusting
import time


class Command(BaseCommand):
    help = 'Perform cache maintenance operations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'operation',
            choices=['clear', 'warm', 'stats', 'invalidate', 'test'],
            help='Cache operation to perform'
        )
        
        parser.add_argument(
            '--cache',
            choices=['all', 'default', 'page_cache', 'static_cache'],
            default='all',
            help='Which cache to operate on'
        )
        
        parser.add_argument(
            '--pattern',
            type=str,
            help='Pattern for selective cache operations'
        )
        
        parser.add_argument(
            '--urls',
            nargs='+',
            help='URLs to warm up (for warm operation)'
        )
    
    def handle(self, *args, **options):
        operation = options['operation']
        cache_type = options['cache']
        pattern = options.get('pattern')
        urls = options.get('urls', [])
        
        try:
            if operation == 'clear':
                self._clear_cache(cache_type, pattern)
            elif operation == 'warm':
                self._warm_cache(urls)
            elif operation == 'stats':
                self._show_stats()
            elif operation == 'invalidate':
                self._invalidate_cache(pattern)
            elif operation == 'test':
                self._test_cache()
            else:
                raise CommandError(f'Unknown operation: {operation}')
                
        except Exception as e:
            raise CommandError(f'Cache operation failed: {str(e)}')
    
    def _clear_cache(self, cache_type, pattern):
        """Clear cache based on type and pattern."""
        self.stdout.write(f'Clearing cache: {cache_type}')
        
        if cache_type == 'all':
            for cache_alias in settings.CACHES.keys():
                caches[cache_alias].clear()
                self.stdout.write(f'  Cleared {cache_alias} cache')
        else:
            if cache_type in settings.CACHES:
                caches[cache_type].clear()
                self.stdout.write(f'  Cleared {cache_type} cache')
            else:
                raise CommandError(f'Unknown cache type: {cache_type}')
        
        self.stdout.write(
            self.style.SUCCESS('Cache clearing completed successfully')
        )
    
    def _warm_cache(self, urls):
        """Warm up cache with specified URLs."""
        if not urls:
            # Default URLs to warm up
            urls = [
                '/',
                '/schedule/',
                '/gallery/',
                '/resources/',
                '/pricing/',
                '/private-lessons/',
                '/contact/',
            ]
        
        self.stdout.write(f'Warming cache for {len(urls)} URLs...')
        
        cache_manager.warm_cache(urls)
        
        for url in urls:
            self.stdout.write(f'  Warmed: {url}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Cache warming completed for {len(urls)} URLs')
        )
    
    def _show_stats(self):
        """Display cache statistics."""
        self.stdout.write('Cache Statistics:')
        self.stdout.write('=' * 50)
        
        stats = cache_manager.get_cache_stats()
        
        for cache_name, cache_info in stats.items():
            if cache_name == 'timestamp':
                continue
                
            self.stdout.write(f'\\n{cache_name.upper()}:')
            if 'error' in cache_info:
                self.stdout.write(f'  Error: {cache_info[\"error\"]}')
            else:
                self.stdout.write(f'  Backend: {cache_info.get(\"backend\", \"Unknown\")}')
                self.stdout.write(f'  Location: {cache_info.get(\"location\", \"Unknown\")}')
                self.stdout.write(f'  Timeout: {cache_info.get(\"timeout\", \"Unknown\")}')
        
        self.stdout.write(f'\\nStats generated at: {time.ctime(stats[\"timestamp\"])}')
    
    def _invalidate_cache(self, pattern):
        """Invalidate cache entries matching pattern."""
        if not pattern:
            raise CommandError('Pattern is required for invalidate operation')
        
        self.stdout.write(f'Invalidating cache entries matching: {pattern}')
        
        # Page cache invalidation
        cache_manager.invalidate_page_cache(pattern)
        
        # Static cache invalidation if pattern matches static files
        if any(ext in pattern for ext in ['.css', '.js', '.png', '.jpg', '.gif', '.svg']):
            cache_manager.invalidate_static_cache(pattern)
        
        self.stdout.write(
            self.style.SUCCESS(f'Cache invalidation completed for pattern: {pattern}')
        )
    
    def _test_cache(self):
        """Test cache functionality."""
        self.stdout.write('Testing cache functionality...')
        
        # Test default cache
        test_key = 'cache_test_key'
        test_value = f'test_value_{int(time.time())}'
        
        # Set test value
        cache.set(test_key, test_value, timeout=60)
        
        # Get test value
        retrieved_value = cache.get(test_key)
        
        if retrieved_value == test_value:
            self.stdout.write(
                self.style.SUCCESS('✓ Default cache: Working correctly')
            )
        else:
            self.stdout.write(
                self.style.ERROR('✗ Default cache: Not working correctly')
            )
        
        # Test page cache if available
        if 'page_cache' in settings.CACHES:
            page_cache = caches['page_cache']
            page_cache.set(test_key, test_value, timeout=60)
            retrieved_value = page_cache.get(test_key)
            
            if retrieved_value == test_value:
                self.stdout.write(
                    self.style.SUCCESS('✓ Page cache: Working correctly')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Page cache: Not working correctly')
                )
        
        # Test static cache if available
        if 'static_cache' in settings.CACHES:
            static_cache = caches['static_cache']
            static_cache.set(test_key, test_value, timeout=60)
            retrieved_value = static_cache.get(test_key)
            
            if retrieved_value == test_value:
                self.stdout.write(
                    self.style.SUCCESS('✓ Static cache: Working correctly')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Static cache: Not working correctly')
                )
        
        # Test cache busting
        test_file_path = '/static/css/styles.css'
        version_hash = CacheBusting.generate_version_hash(test_file_path)
        
        if version_hash:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Cache busting: Generated version {version_hash}')
            )
        else:
            self.stdout.write(
                self.style.ERROR('✗ Cache busting: Failed to generate version')
            )
        
        # Clean up test data
        cache.delete(test_key)
        if 'page_cache' in settings.CACHES:
            caches['page_cache'].delete(test_key)
        if 'static_cache' in settings.CACHES:
            caches['static_cache'].delete(test_key)
        
        self.stdout.write('\\nCache testing completed')