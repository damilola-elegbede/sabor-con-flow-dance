"""
Management command for comprehensive performance auditing.
Measures Core Web Vitals, image optimization, and loading performance.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.test import Client
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Comprehensive performance audit and optimization verification'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            nargs='+',
            default=['home', 'pricing', 'events', 'contact'],
            help='Pages to audit (URL names)'
        )
        parser.add_argument(
            '--output-format',
            choices=['json', 'html', 'console'],
            default='console',
            help='Output format for audit results'
        )
        parser.add_argument(
            '--output-file',
            type=str,
            help='Output file path (for json/html formats)'
        )
        parser.add_argument(
            '--lighthouse',
            action='store_true',
            help='Run Lighthouse audit (requires lighthouse CLI)'
        )
        parser.add_argument(
            '--check-images',
            action='store_true',
            default=True,
            help='Check image optimization status'
        )
        parser.add_argument(
            '--check-videos',
            action='store_true',
            default=True,
            help='Check video optimization status'
        )

    def handle(self, *args, **options):
        start_time = time.time()
        
        self.stdout.write('Starting Performance Audit...')
        
        audit_results = {
            'audit_timestamp': time.time(),
            'pages': {},
            'image_optimization': {},
            'video_optimization': {},
            'summary': {},
            'recommendations': []
        }
        
        # Audit pages
        for page_name in options['pages']:
            try:
                page_results = self._audit_page(page_name)
                audit_results['pages'][page_name] = page_results
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Audited page: {page_name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to audit {page_name}: {e}')
                )
                audit_results['pages'][page_name] = {'error': str(e)}
        
        # Check image optimization
        if options['check_images']:
            audit_results['image_optimization'] = self._audit_images()
        
        # Check video optimization
        if options['check_videos']:
            audit_results['video_optimization'] = self._audit_videos()
        
        # Run Lighthouse audit
        if options['lighthouse']:
            lighthouse_results = self._run_lighthouse_audit(options['pages'])
            audit_results['lighthouse'] = lighthouse_results
        
        # Generate summary and recommendations
        audit_results['summary'] = self._generate_summary(audit_results)
        audit_results['recommendations'] = self._generate_recommendations(audit_results)
        
        # Output results
        elapsed_time = time.time() - start_time
        audit_results['audit_duration'] = elapsed_time
        
        self._output_results(audit_results, options)
        
        # Display summary
        self._display_summary(audit_results)

    def _audit_page(self, page_name: str) -> Dict[str, Any]:
        """Audit a single page for performance metrics."""
        
        client = Client()
        
        try:
            url = reverse(f'core:{page_name}')
        except:
            # Fallback for pages that might not have the core: prefix
            try:
                url = reverse(page_name)
            except:
                raise CommandError(f'Could not resolve URL for page: {page_name}')
        
        # Measure response time
        start_time = time.time()
        response = client.get(url)
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        if response.status_code != 200:
            raise CommandError(f'Page {page_name} returned status {response.status_code}')
        
        content = response.content.decode()
        
        return {
            'url': url,
            'status_code': response.status_code,
            'response_time_ms': response_time,
            'content_size_bytes': len(content),
            'content_size_kb': len(content) / 1024,
            'html_analysis': self._analyze_html(content),
            'performance_hints': self._check_performance_hints(content)
        }

    def _analyze_html(self, content: str) -> Dict[str, Any]:
        """Analyze HTML content for performance issues."""
        
        import re
        
        analysis = {
            'total_images': len(re.findall(r'<img[^>]*>', content)),
            'lazy_images': len(re.findall(r'loading=["\']lazy["\']', content)),
            'webp_images': len(re.findall(r'\.webp', content)),
            'responsive_images': len(re.findall(r'srcset=', content)),
            'total_scripts': len(re.findall(r'<script[^>]*>', content)),
            'defer_scripts': len(re.findall(r'defer', content)),
            'total_stylesheets': len(re.findall(r'<link[^>]*stylesheet', content)),
            'preload_resources': len(re.findall(r'rel=["\']preload["\']', content)),
            'critical_css': 'critical-css' in content,
            'performance_monitoring': 'performance' in content.lower()
        }
        
        # Calculate optimization scores
        analysis['lazy_loading_score'] = (
            (analysis['lazy_images'] / analysis['total_images']) * 100
            if analysis['total_images'] > 0 else 100
        )
        
        analysis['webp_adoption_score'] = (
            (analysis['webp_images'] / max(analysis['total_images'], 1)) * 100
        )
        
        analysis['script_optimization_score'] = (
            (analysis['defer_scripts'] / max(analysis['total_scripts'], 1)) * 100
        )
        
        return analysis

    def _check_performance_hints(self, content: str) -> Dict[str, bool]:
        """Check for performance optimization hints in HTML."""
        
        return {
            'dns_prefetch': 'dns-prefetch' in content,
            'preconnect': 'preconnect' in content,
            'resource_hints': 'preload' in content,
            'font_display_swap': 'font-display' in content,
            'webp_detection': 'webp' in content.lower(),
            'lazy_loading': 'loading="lazy"' in content,
            'critical_css': 'critical-css' in content,
            'performance_monitoring': 'performance' in content.lower(),
            'service_worker': 'serviceWorker' in content or 'sw.js' in content
        }

    def _audit_images(self) -> Dict[str, Any]:
        """Audit image optimization status."""
        
        static_dir = Path(settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)
        images_dir = static_dir / 'images'
        optimized_dir = images_dir / 'optimized'
        
        if not images_dir.exists():
            return {'error': 'Images directory not found'}
        
        # Find all images
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
        original_images = []
        optimized_images = []
        
        for ext in image_extensions:
            original_images.extend(images_dir.rglob(f'*{ext}'))
            if optimized_dir.exists():
                optimized_images.extend(optimized_dir.rglob(f'*{ext}'))
        
        # Calculate optimization statistics
        total_original_size = sum(img.stat().st_size for img in original_images)
        total_optimized_size = sum(img.stat().st_size for img in optimized_images)
        
        webp_images = [img for img in optimized_images if img.suffix == '.webp']
        responsive_images = [img for img in optimized_images if '_320w' in img.name or '_640w' in img.name]
        placeholder_images = [img for img in optimized_images if '_placeholder' in img.name]
        
        return {
            'total_original_images': len(original_images),
            'total_optimized_images': len(optimized_images),
            'total_original_size_mb': total_original_size / (1024 * 1024),
            'total_optimized_size_mb': total_optimized_size / (1024 * 1024),
            'size_reduction_percent': (
                ((total_original_size - total_optimized_size) / total_original_size) * 100
                if total_original_size > 0 else 0
            ),
            'webp_images_count': len(webp_images),
            'responsive_images_count': len(responsive_images),
            'placeholder_images_count': len(placeholder_images),
            'optimization_directory_exists': optimized_dir.exists(),
            'optimization_coverage': (
                len(optimized_images) / len(original_images) * 100
                if len(original_images) > 0 else 0
            )
        }

    def _audit_videos(self) -> Dict[str, Any]:
        """Audit video optimization status."""
        
        static_dir = Path(settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)
        videos_dir = static_dir / 'videos'
        optimized_dir = videos_dir / 'optimized'
        
        if not videos_dir.exists():
            return {'error': 'Videos directory not found'}
        
        # Find all videos
        video_extensions = {'.mp4', '.mov', '.avi', '.webm'}
        original_videos = []
        optimized_videos = []
        
        for ext in video_extensions:
            original_videos.extend(videos_dir.rglob(f'*{ext}'))
            if optimized_dir.exists():
                optimized_videos.extend(optimized_dir.rglob(f'*{ext}'))
        
        # Calculate optimization statistics
        total_original_size = sum(video.stat().st_size for video in original_videos if video.stat().st_size > 0)
        total_optimized_size = sum(video.stat().st_size for video in optimized_videos)
        
        poster_images = []
        if optimized_dir.exists():
            poster_images = list(optimized_dir.glob('*_poster.jpg'))
        
        return {
            'total_original_videos': len(original_videos),
            'total_optimized_videos': len(optimized_videos),
            'total_original_size_mb': total_original_size / (1024 * 1024),
            'total_optimized_size_mb': total_optimized_size / (1024 * 1024),
            'size_reduction_percent': (
                ((total_original_size - total_optimized_size) / total_original_size) * 100
                if total_original_size > 0 else 0
            ),
            'poster_images_count': len(poster_images),
            'optimization_directory_exists': optimized_dir.exists(),
            'optimization_coverage': (
                len(optimized_videos) / len(original_videos) * 100
                if len(original_videos) > 0 else 0
            )
        }

    def _run_lighthouse_audit(self, pages: List[str]) -> Dict[str, Any]:
        """Run Lighthouse audit on specified pages."""
        
        # Check if lighthouse is available
        try:
            subprocess.run(['lighthouse', '--version'], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {'error': 'Lighthouse CLI not installed'}
        
        lighthouse_results = {}
        
        for page_name in pages:
            try:
                url = reverse(f'core:{page_name}')
                full_url = f'http://localhost:8000{url}'
                
                # Run lighthouse
                cmd = [
                    'lighthouse', full_url,
                    '--only-categories=performance',
                    '--output=json',
                    '--output-path=/tmp/lighthouse-result.json',
                    '--chrome-flags="--headless"'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    with open('/tmp/lighthouse-result.json', 'r') as f:
                        lighthouse_data = json.load(f)
                    
                    lighthouse_results[page_name] = {
                        'performance_score': lighthouse_data['categories']['performance']['score'] * 100,
                        'metrics': {
                            'first_contentful_paint': lighthouse_data['audits']['first-contentful-paint']['numericValue'],
                            'largest_contentful_paint': lighthouse_data['audits']['largest-contentful-paint']['numericValue'],
                            'cumulative_layout_shift': lighthouse_data['audits']['cumulative-layout-shift']['numericValue'],
                            'total_blocking_time': lighthouse_data['audits']['total-blocking-time']['numericValue']
                        }
                    }
                else:
                    lighthouse_results[page_name] = {'error': result.stderr}
                    
            except Exception as e:
                lighthouse_results[page_name] = {'error': str(e)}
        
        return lighthouse_results

    def _generate_summary(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from audit results."""
        
        summary = {
            'total_pages_audited': len(audit_results['pages']),
            'average_response_time': 0,
            'total_content_size_kb': 0,
            'optimization_scores': {},
            'issues_found': []
        }
        
        # Calculate averages from page audits
        valid_pages = [p for p in audit_results['pages'].values() if 'error' not in p]
        
        if valid_pages:
            summary['average_response_time'] = sum(p['response_time_ms'] for p in valid_pages) / len(valid_pages)
            summary['total_content_size_kb'] = sum(p['content_size_kb'] for p in valid_pages)
            
            # Calculate optimization scores
            html_analyses = [p['html_analysis'] for p in valid_pages]
            summary['optimization_scores'] = {
                'lazy_loading': sum(h['lazy_loading_score'] for h in html_analyses) / len(html_analyses),
                'webp_adoption': sum(h['webp_adoption_score'] for h in html_analyses) / len(html_analyses),
                'script_optimization': sum(h['script_optimization_score'] for h in html_analyses) / len(html_analyses)
            }
        
        # Add image optimization summary
        if 'image_optimization' in audit_results and 'error' not in audit_results['image_optimization']:
            img_opt = audit_results['image_optimization']
            summary['image_optimization'] = {
                'size_reduction_percent': img_opt['size_reduction_percent'],
                'optimization_coverage': img_opt['optimization_coverage'],
                'webp_images': img_opt['webp_images_count']
            }
        
        return summary

    def _generate_recommendations(self, audit_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate performance optimization recommendations."""
        
        recommendations = []
        
        # Check image optimization
        if 'image_optimization' in audit_results:
            img_opt = audit_results['image_optimization']
            if img_opt.get('optimization_coverage', 0) < 90:
                recommendations.append({
                    'category': 'Images',
                    'priority': 'High',
                    'issue': f'Only {img_opt.get("optimization_coverage", 0):.1f}% of images are optimized',
                    'solution': 'Run: python manage.py optimize_images --force'
                })
            
            if img_opt.get('webp_images_count', 0) == 0:
                recommendations.append({
                    'category': 'Images',
                    'priority': 'High',
                    'issue': 'No WebP images found',
                    'solution': 'Enable WebP conversion in image optimization'
                })
        
        # Check video optimization
        if 'video_optimization' in audit_results:
            vid_opt = audit_results['video_optimization']
            if vid_opt.get('optimization_coverage', 0) < 90:
                recommendations.append({
                    'category': 'Videos',
                    'priority': 'Medium',
                    'issue': f'Only {vid_opt.get("optimization_coverage", 0):.1f}% of videos are optimized',
                    'solution': 'Run: python manage.py optimize_videos --target-size 5'
                })
        
        # Check page performance
        for page_name, page_data in audit_results['pages'].items():
            if 'error' not in page_data:
                html_analysis = page_data['html_analysis']
                
                if html_analysis['lazy_loading_score'] < 80:
                    recommendations.append({
                        'category': 'Performance',
                        'priority': 'Medium',
                        'issue': f'Page {page_name} has low lazy loading adoption ({html_analysis["lazy_loading_score"]:.1f}%)',
                        'solution': 'Add loading="lazy" to more images'
                    })
                
                if page_data['response_time_ms'] > 500:
                    recommendations.append({
                        'category': 'Performance',
                        'priority': 'High',
                        'issue': f'Page {page_name} has slow response time ({page_data["response_time_ms"]:.1f}ms)',
                        'solution': 'Optimize server response time and database queries'
                    })
        
        return recommendations

    def _output_results(self, audit_results: Dict[str, Any], options: Dict[str, Any]):
        """Output audit results in the specified format."""
        
        if options['output_format'] == 'json':
            output_file = options.get('output_file', 'performance_audit.json')
            with open(output_file, 'w') as f:
                json.dump(audit_results, f, indent=2, default=str)
            self.stdout.write(f'Audit results saved to: {output_file}')
        
        elif options['output_format'] == 'html':
            output_file = options.get('output_file', 'performance_audit.html')
            html_content = self._generate_html_report(audit_results)
            with open(output_file, 'w') as f:
                f.write(html_content)
            self.stdout.write(f'HTML report saved to: {output_file}')

    def _generate_html_report(self, audit_results: Dict[str, Any]) -> str:
        """Generate HTML performance report."""
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance Audit Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .summary { background: #f5f5f5; padding: 20px; border-radius: 8px; }
                .score { font-size: 24px; font-weight: bold; }
                .good { color: #4CAF50; }
                .warning { color: #FF9800; }
                .poor { color: #F44336; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #f2f2f2; }
                .recommendation { background: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 4px; }
            </style>
        </head>
        <body>
            <h1>Performance Audit Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Audit completed in {:.2f} seconds</p>
                <p>Pages audited: {}</p>
                <p>Average response time: {:.1f}ms</p>
            </div>
        """.format(
            audit_results.get('audit_duration', 0),
            audit_results['summary'].get('total_pages_audited', 0),
            audit_results['summary'].get('average_response_time', 0)
        )
        
        # Add recommendations
        if audit_results.get('recommendations'):
            html += "<h2>Recommendations</h2>"
            for rec in audit_results['recommendations']:
                html += f"""
                <div class="recommendation">
                    <strong>{rec['category']} - {rec['priority']} Priority</strong><br>
                    Issue: {rec['issue']}<br>
                    Solution: {rec['solution']}
                </div>
                """
        
        html += "</body></html>"
        return html

    def _display_summary(self, audit_results: Dict[str, Any]):
        """Display audit summary to console."""
        
        summary = audit_results['summary']
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('PERFORMANCE AUDIT COMPLETE'))
        self.stdout.write('='*60)
        
        self.stdout.write(f'Pages audited: {summary.get("total_pages_audited", 0)}')
        self.stdout.write(f'Average response time: {summary.get("average_response_time", 0):.1f}ms')
        self.stdout.write(f'Total content size: {summary.get("total_content_size_kb", 0):.1f}KB')
        
        if 'optimization_scores' in summary:
            scores = summary['optimization_scores']
            self.stdout.write('\nOptimization Scores:')
            self.stdout.write(f'Lazy Loading: {scores.get("lazy_loading", 0):.1f}%')
            self.stdout.write(f'WebP Adoption: {scores.get("webp_adoption", 0):.1f}%')
            self.stdout.write(f'Script Optimization: {scores.get("script_optimization", 0):.1f}%')
        
        if audit_results.get('recommendations'):
            self.stdout.write(f'\nRecommendations: {len(audit_results["recommendations"])} issues found')
            for rec in audit_results['recommendations'][:3]:  # Show top 3
                self.stdout.write(f'• {rec["category"]}: {rec["issue"]}')
        
        self.stdout.write(f'\nAudit completed in {audit_results.get("audit_duration", 0):.2f}s')
        
        if audit_results.get('image_optimization'):
            img_opt = audit_results['image_optimization']
            if 'error' not in img_opt:
                self.stdout.write(f'\nImage Optimization:')
                self.stdout.write(f'Size reduction: {img_opt.get("size_reduction_percent", 0):.1f}%')
                self.stdout.write(f'Coverage: {img_opt.get("optimization_coverage", 0):.1f}%')
                self.stdout.write(f'WebP images: {img_opt.get("webp_images_count", 0)}')