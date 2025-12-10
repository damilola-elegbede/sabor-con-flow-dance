#!/usr/bin/env python3
"""
CSS Build and Optimization Script
SPEC_06 Group A Task 2

This script optimizes CSS for production by:
1. Extracting and optimizing critical CSS
2. Minifying all CSS files
3. Creating CSS bundles by priority
4. Generating performance reports
5. Validating performance budgets
"""

import os
import sys
import gzip
import json
from pathlib import Path
from typing import Dict, List
import csscompressor
import argparse


class CSSBuilder:
    """
    CSS build and optimization system
    """
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.static_dir = self.base_dir / 'static'
        self.css_dir = self.static_dir / 'css'
        self.build_dir = self.static_dir / 'build'
        
        # Performance budgets (bytes)
        self.critical_budget = 14000  # 14KB
        self.total_budget = 50000     # 50KB
        
        # CSS file priorities
        self.priorities = {
            'critical': ['critical.css'],
            'high': ['navigation.css', 'hero.css'],
            'medium': ['styles.css', 'forms.css', 'pricing.css'],
            'low': [
                'whatsapp.css', 'social_links.css', 'gallery.css',
                'testimonials.css', 'instructors.css', 'schedule.css',
                'spotify-playlists.css', 'google-maps.css', 'video-player.css'
            ]
        }
    
    def build_all(self, minify: bool = True, gzip_files: bool = True) -> Dict:
        """
        Build and optimize all CSS files
        
        Args:
            minify: Whether to minify CSS files
            gzip_files: Whether to create gzipped versions
            
        Returns:
            Build report dictionary
        """
        print("🎨 Starting CSS build and optimization...")
        
        # Create build directory
        self.build_dir.mkdir(exist_ok=True)
        
        build_report = {
            'timestamp': self._get_timestamp(),
            'files_processed': 0,
            'total_size_before': 0,
            'total_size_after': 0,
            'critical_size': 0,
            'bundles': {},
            'budget_check': {},
            'errors': []
        }
        
        try:
            # Process individual CSS files
            for css_file in self.css_dir.glob('*.css'):
                if css_file.name.startswith('.'):
                    continue
                    
                original_size = css_file.stat().st_size
                build_report['total_size_before'] += original_size
                build_report['files_processed'] += 1
                
                if minify:
                    optimized_content = self._optimize_css_file(css_file)
                    optimized_size = len(optimized_content.encode('utf-8'))
                    
                    # Write optimized file
                    output_file = self.build_dir / css_file.name
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(optimized_content)
                    
                    build_report['total_size_after'] += optimized_size
                    
                    # Create gzipped version
                    if gzip_files:
                        self._create_gzipped_file(output_file, optimized_content)
                    
                    if css_file.name == 'critical.css':
                        build_report['critical_size'] = optimized_size
                    
                    print(f"✅ Optimized {css_file.name}: {original_size} → {optimized_size} bytes "
                          f"({self._calculate_savings_percentage(original_size, optimized_size):.1f}% savings)")
                else:
                    build_report['total_size_after'] += original_size
            
            # Create priority bundles
            build_report['bundles'] = self._create_priority_bundles(minify, gzip_files)
            
            # Check performance budgets
            build_report['budget_check'] = self._check_performance_budgets(build_report)
            
            # Generate performance report
            self._generate_performance_report(build_report)
            
            print(f"\n🎯 Build complete!")
            print(f"   Files processed: {build_report['files_processed']}")
            print(f"   Total size: {build_report['total_size_before']} → {build_report['total_size_after']} bytes")
            print(f"   Total savings: {self._calculate_savings_percentage(build_report['total_size_before'], build_report['total_size_after']):.1f}%")
            print(f"   Critical CSS: {build_report['critical_size']} bytes")
            
            # Budget warnings
            if not build_report['budget_check'].get('critical_within_budget', True):
                print(f"⚠️  Critical CSS exceeds budget ({build_report['critical_size']} > {self.critical_budget} bytes)")
            
            if not build_report['budget_check'].get('total_within_budget', True):
                print(f"⚠️  Total CSS exceeds budget ({build_report['total_size_after']} > {self.total_budget} bytes)")
            
        except Exception as e:
            build_report['errors'].append(str(e))
            print(f"❌ Build error: {e}")
        
        return build_report
    
    def _optimize_css_file(self, css_file: Path) -> str:
        """Optimize a single CSS file"""
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            # Use csscompressor for minification
            optimized = csscompressor.compress(content)
        except Exception as e:
            print(f"⚠️  Failed to compress {css_file.name} with csscompressor: {e}")
            # Fallback to manual optimization
            optimized = self._manual_css_optimization(content)
        
        return optimized
    
    def _manual_css_optimization(self, css: str) -> str:
        """Manual CSS optimization fallback"""
        import re
        
        # Remove comments (except special ones starting with !)
        css = re.sub(r'/\*(?!\!)[^*]*\*+(?:[^/*][^*]*\*+)*/', '', css)
        
        # Remove unnecessary whitespace
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r';\s*}', '}', css)
        css = re.sub(r'{\s*', '{', css)
        css = re.sub(r'}\s*', '}', css)
        css = re.sub(r':\s*', ':', css)
        css = re.sub(r';\s*', ';', css)
        css = re.sub(r',\s*', ',', css)
        
        # Remove trailing semicolon before closing brace
        css = re.sub(r';\s*}', '}', css)
        
        return css.strip()
    
    def _create_priority_bundles(self, minify: bool, gzip_files: bool) -> Dict:
        """Create CSS bundles by priority"""
        bundles = {}
        
        for priority, files in self.priorities.items():
            if priority == 'critical':
                continue  # Critical CSS is inlined
            
            bundle_content = []
            bundle_size = 0
            
            for filename in files:
                file_path = self.css_dir / filename
                if file_path.exists():
                    if minify:
                        content = self._optimize_css_file(file_path)
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    bundle_content.append(f'/* {filename} */\n{content}')
                    bundle_size += len(content.encode('utf-8'))
            
            if bundle_content:
                # Create bundle file
                bundle_filename = f'{priority}-bundle.css'
                bundle_path = self.build_dir / bundle_filename
                
                combined_content = '\n\n'.join(bundle_content)
                
                with open(bundle_path, 'w', encoding='utf-8') as f:
                    f.write(combined_content)
                
                if gzip_files:
                    self._create_gzipped_file(bundle_path, combined_content)
                
                bundles[priority] = {
                    'filename': bundle_filename,
                    'size': bundle_size,
                    'files_count': len([f for f in files if (self.css_dir / f).exists()])
                }
                
                print(f"📦 Created {priority} bundle: {bundle_size} bytes ({len(bundle_content)} files)")
        
        return bundles
    
    def _create_gzipped_file(self, file_path: Path, content: str):
        """Create gzipped version of file"""
        gzip_path = file_path.with_suffix(file_path.suffix + '.gz')
        with gzip.open(gzip_path, 'wt', encoding='utf-8') as f:
            f.write(content)
    
    def _check_performance_budgets(self, build_report: Dict) -> Dict:
        """Check if CSS files are within performance budgets"""
        return {
            'critical_size': build_report['critical_size'],
            'critical_budget': self.critical_budget,
            'critical_within_budget': build_report['critical_size'] <= self.critical_budget,
            'total_size': build_report['total_size_after'],
            'total_budget': self.total_budget,
            'total_within_budget': build_report['total_size_after'] <= self.total_budget,
            'savings_percentage': self._calculate_savings_percentage(
                build_report['total_size_before'], 
                build_report['total_size_after']
            )
        }
    
    def _generate_performance_report(self, build_report: Dict):
        """Generate detailed performance report"""
        report_path = self.build_dir / 'css-performance-report.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(build_report, f, indent=2)
        
        print(f"📊 Performance report saved: {report_path}")
    
    def _calculate_savings_percentage(self, before: int, after: int) -> float:
        """Calculate percentage savings"""
        if before == 0:
            return 0.0
        return ((before - after) / before) * 100
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def analyze_css_performance(self) -> Dict:
        """Analyze current CSS performance"""
        analysis = {
            'files': {},
            'total_size': 0,
            'critical_size': 0,
            'recommendations': []
        }
        
        for css_file in self.css_dir.glob('*.css'):
            if css_file.name.startswith('.'):
                continue
            
            size = css_file.stat().st_size
            
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis['files'][css_file.name] = {
                'size': size,
                'size_kb': round(size / 1024, 2),
                'rules_count': len([line for line in content.split('\n') if '{' in line]),
                'contains_important': '!important' in content,
                'contains_animations': '@keyframes' in content or 'animation:' in content
            }
            
            analysis['total_size'] += size
            
            if css_file.name == 'critical.css':
                analysis['critical_size'] = size
        
        # Generate recommendations
        if analysis['critical_size'] > self.critical_budget:
            analysis['recommendations'].append(
                f"Critical CSS ({analysis['critical_size']} bytes) exceeds 14KB budget"
            )
        
        if analysis['total_size'] > self.total_budget:
            analysis['recommendations'].append(
                f"Total CSS ({analysis['total_size']} bytes) exceeds 50KB budget"
            )
        
        # Check for optimization opportunities
        large_files = [name for name, info in analysis['files'].items() 
                      if info['size'] > 5000 and name != 'critical.css']
        if large_files:
            analysis['recommendations'].append(
                f"Consider optimizing large files: {', '.join(large_files)}"
            )
        
        return analysis


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='CSS Build and Optimization')
    parser.add_argument('--no-minify', action='store_true', help='Skip minification')
    parser.add_argument('--no-gzip', action='store_true', help='Skip gzip compression')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze current CSS')
    parser.add_argument('--base-dir', type=str, help='Base directory path')
    
    args = parser.parse_args()
    
    builder = CSSBuilder(args.base_dir)
    
    if args.analyze_only:
        print("🔍 Analyzing CSS performance...")
        analysis = builder.analyze_css_performance()
        
        print(f"\n📊 CSS Analysis Report")
        print(f"Total files: {len(analysis['files'])}")
        print(f"Total size: {analysis['total_size']} bytes ({analysis['total_size'] / 1024:.1f} KB)")
        print(f"Critical CSS: {analysis['critical_size']} bytes")
        
        print(f"\n📁 File Details:")
        for filename, info in analysis['files'].items():
            print(f"  {filename}: {info['size_kb']} KB ({info['rules_count']} rules)")
        
        if analysis['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in analysis['recommendations']:
                print(f"  • {rec}")
    else:
        minify = not args.no_minify
        gzip_files = not args.no_gzip
        
        build_report = builder.build_all(minify=minify, gzip_files=gzip_files)
        
        if build_report['errors']:
            print(f"\n❌ Build completed with errors:")
            for error in build_report['errors']:
                print(f"  • {error}")
            sys.exit(1)
        else:
            print(f"\n✅ Build completed successfully!")


if __name__ == '__main__':
    main()