"""
Django management command to optimize database performance.
SPEC_06 Group B Task 6 - Database query and performance optimization.

Usage:
    python manage.py optimize_database
    python manage.py optimize_database --create-indexes
    python manage.py optimize_database --analyze-queries
    python manage.py optimize_database --all
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.conf import settings
from django.core.cache import cache
import logging
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Optimize database performance with indexes and settings'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-indexes',
            action='store_true',
            help='Create recommended database indexes',
        )
        parser.add_argument(
            '--optimize-settings',
            action='store_true',
            help='Apply database optimization settings',
        )
        parser.add_argument(
            '--analyze-queries',
            action='store_true',
            help='Analyze and report slow queries',
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear application cache',
        )
        parser.add_argument(
            '--benchmark',
            action='store_true',
            help='Run performance benchmarks',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all optimization tasks',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting database optimization...')
        )
        
        if options['all']:
            self.create_indexes()
            self.optimize_settings()
            self.analyze_queries()
            self.clear_cache()
            self.run_benchmarks()
        else:
            if options['create_indexes']:
                self.create_indexes()
            
            if options['optimize_settings']:
                self.optimize_settings()
            
            if options['analyze_queries']:
                self.analyze_queries()
            
            if options['clear_cache']:
                self.clear_cache()
            
            if options['benchmark']:
                self.run_benchmarks()
        
        self.stdout.write(
            self.style.SUCCESS('Database optimization completed!')
        )
    
    def create_indexes(self):
        """Create recommended database indexes."""
        self.stdout.write('Creating database indexes...')
        
        from core.db_optimization import DatabaseIndexManager
        
        sql_statements = DatabaseIndexManager.generate_index_sql()
        
        with connection.cursor() as cursor:
            for sql in sql_statements:
                try:
                    cursor.execute(sql)
                    self.stdout.write(f'✓ Created index: {sql.split()[4]}')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to create index: {sql}, Error: {e}')
                    )
        
        # Analyze tables after creating indexes
        self.stdout.write('Analyzing tables...')
        with connection.cursor() as cursor:
            cursor.execute("ANALYZE;")
        
        self.stdout.write(self.style.SUCCESS('Database indexes created successfully!'))
    
    def optimize_settings(self):
        """Apply database optimization settings."""
        self.stdout.write('Applying database optimization settings...')
        
        with connection.cursor() as cursor:
            # SQLite optimization settings
            settings_queries = [
                "PRAGMA journal_mode=WAL;",
                "PRAGMA cache_size=2000;",  # 8MB cache
                "PRAGMA temp_store=MEMORY;",
                "PRAGMA synchronous=NORMAL;",
                "PRAGMA auto_vacuum=INCREMENTAL;",
                "PRAGMA foreign_keys=ON;",
                "PRAGMA case_sensitive_like=true;",
            ]
            
            for setting in settings_queries:
                try:
                    cursor.execute(setting)
                    self.stdout.write(f'✓ Applied: {setting}')
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to apply: {setting}, Error: {e}')
                    )
        
        self.stdout.write(self.style.SUCCESS('Database settings optimized!'))
    
    def analyze_queries(self):
        """Analyze and report on database queries."""
        self.stdout.write('Analyzing database queries...')
        
        # Enable query logging if in debug mode
        if not settings.DEBUG:
            self.stdout.write(
                self.style.WARNING('Query analysis only available in DEBUG mode')
            )
            return
        
        # Import models to trigger some queries
        from core.models import (
            Testimonial, Class, Instructor, MediaGallery, 
            FacebookEvent, SpotifyPlaylist, RSVPSubmission
        )
        
        # Reset query log
        connection.queries.clear()
        
        # Run sample queries to analyze
        sample_queries = [
            lambda: list(Testimonial.objects.filter(status='approved')[:10]),
            lambda: list(Class.objects.select_related('instructor').filter(day_of_week='Sunday')),
            lambda: list(Instructor.objects.all()[:5]),
            lambda: list(MediaGallery.objects.filter(media_type='image')[:10]),
            lambda: list(FacebookEvent.objects.filter(is_active=True)[:5]),
            lambda: list(SpotifyPlaylist.objects.filter(is_active=True)),
            lambda: list(RSVPSubmission.objects.filter(status='confirmed')[:10]),
        ]
        
        total_time = 0
        slow_queries = []
        
        for i, query_func in enumerate(sample_queries, 1):
            start_time = time.time()
            start_query_count = len(connection.queries)
            
            try:
                query_func()
                end_time = time.time()
                end_query_count = len(connection.queries)
                
                execution_time = (end_time - start_time) * 1000  # Convert to ms
                query_count = end_query_count - start_query_count
                
                total_time += execution_time
                
                self.stdout.write(
                    f'Query {i}: {execution_time:.2f}ms ({query_count} queries)'
                )
                
                # Check for slow queries
                if execution_time > 100:  # Slow threshold: 100ms
                    slow_queries.append({
                        'query_num': i,
                        'time': execution_time,
                        'count': query_count
                    })
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Query {i} failed: {e}')
                )
        
        # Report summary
        self.stdout.write(f'\nQuery Analysis Summary:')
        self.stdout.write(f'Total execution time: {total_time:.2f}ms')
        self.stdout.write(f'Average per query: {total_time/len(sample_queries):.2f}ms')
        
        if slow_queries:
            self.stdout.write(
                self.style.WARNING(f'\nSlow queries detected: {len(slow_queries)}')
            )
            for query in slow_queries:
                self.stdout.write(
                    f'  Query {query["query_num"]}: {query["time"]:.2f}ms '
                    f'({query["count"]} DB queries)'
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✓ No slow queries detected!')
            )
    
    def clear_cache(self):
        """Clear application cache."""
        self.stdout.write('Clearing application cache...')
        
        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✓ Cache cleared successfully'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to clear cache: {e}')
            )
    
    def run_benchmarks(self):
        """Run performance benchmarks."""
        self.stdout.write('Running performance benchmarks...')
        
        from core.models import Testimonial, Class, Instructor
        
        # Benchmark queries
        benchmarks = [
            {
                'name': 'Testimonials (unoptimized)',
                'query': lambda: list(Testimonial.objects.filter(status='approved')),
            },
            {
                'name': 'Testimonials (optimized)',
                'query': lambda: list(
                    Testimonial.objects.filter(status='approved')
                    .only('id', 'student_name', 'rating', 'content', 'class_type')
                ),
            },
            {
                'name': 'Classes (unoptimized)',
                'query': lambda: list(Class.objects.filter(day_of_week='Sunday')),
            },
            {
                'name': 'Classes (optimized)',
                'query': lambda: list(
                    Class.objects.filter(day_of_week='Sunday')
                    .select_related('instructor')
                    .only('name', 'start_time', 'instructor__name')
                ),
            },
            {
                'name': 'Instructors (unoptimized)',
                'query': lambda: list(Instructor.objects.all()),
            },
            {
                'name': 'Instructors (optimized)',
                'query': lambda: list(
                    Instructor.objects.only('id', 'name', 'photo_url', 'specialties')
                ),
            },
        ]
        
        results = []
        
        for benchmark in benchmarks:
            # Warm up
            benchmark['query']()
            
            # Benchmark (run 3 times and take average)
            times = []
            for _ in range(3):
                start_time = time.time()
                benchmark['query']()
                end_time = time.time()
                times.append((end_time - start_time) * 1000)
            
            avg_time = sum(times) / len(times)
            results.append({
                'name': benchmark['name'],
                'time': avg_time
            })
            
            self.stdout.write(f'{benchmark["name"]}: {avg_time:.2f}ms')
        
        # Calculate improvements
        self.stdout.write('\nPerformance Improvements:')
        for i in range(0, len(results), 2):
            if i + 1 < len(results):
                unoptimized = results[i]
                optimized = results[i + 1]
                improvement = ((unoptimized['time'] - optimized['time']) / unoptimized['time']) * 100
                
                self.stdout.write(
                    f'{unoptimized["name"].split(" (")[0]}: '
                    f'{improvement:.1f}% faster'
                )
    
    def get_database_info(self):
        """Get database information."""
        with connection.cursor() as cursor:
            # Get SQLite version
            cursor.execute("SELECT sqlite_version();")
            sqlite_version = cursor.fetchone()[0]
            
            # Get database size
            cursor.execute("PRAGMA page_count;")
            page_count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA page_size;")
            page_size = cursor.fetchone()[0]
            
            db_size_mb = (page_count * page_size) / (1024 * 1024)
            
            # Get table information
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            self.stdout.write(f'\nDatabase Information:')
            self.stdout.write(f'SQLite Version: {sqlite_version}')
            self.stdout.write(f'Database Size: {db_size_mb:.2f} MB')
            self.stdout.write(f'Tables: {len(tables)}')
            
            # Get index information
            indexes = []
            for table in tables:
                cursor.execute(f"PRAGMA index_list({table});")
                table_indexes = cursor.fetchall()
                indexes.extend(table_indexes)
            
            self.stdout.write(f'Indexes: {len(indexes)}')