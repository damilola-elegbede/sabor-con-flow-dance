#!/usr/bin/env python3
"""
Production CSS Optimization Deployment Script
SPEC_06 Group A Task 2

This script prepares and deploys optimized CSS for production:
1. Builds and minifies all CSS files
2. Generates critical CSS for different page types
3. Creates performance-optimized bundles
4. Updates template configurations
5. Validates performance budgets
6. Generates deployment report
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
import subprocess
import hashlib


class CSSOptimizationDeployment:
    """
    Production CSS optimization and deployment system
    """
    
    def __init__(self, base_dir: str = None, environment: str = 'production'):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.environment = environment
        self.static_dir = self.base_dir / 'static'
        self.css_dir = self.static_dir / 'css'
        self.build_dir = self.static_dir / 'build'
        self.deploy_dir = self.static_dir / 'deploy'
        
        # Deployment configuration
        self.config = {
            'enable_compression': True,
            'enable_versioning': True,
            'enable_cdn_headers': True,
            'performance_budget_critical': 14000,  # 14KB
            'performance_budget_total': 50000,     # 50KB
            'cache_duration': 31536000,            # 1 year in seconds
        }
        
        # Page-specific critical CSS mapping
        self.page_critical_css = {
            'home': ['critical.css', 'hero.css'],
            'pricing': ['critical.css', 'pricing.css'],
            'events': ['critical.css', 'schedule.css'],
            'contact': ['critical.css', 'forms.css'],
            'gallery': ['critical.css', 'gallery.css'],
            'default': ['critical.css']
        }
    
    def deploy(self) -> dict:
        """
        Execute full CSS optimization deployment
        
        Returns:
            Deployment report dictionary
        """
        print("🚀 Starting CSS optimization deployment...")
        
        deployment_report = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.environment,
            'steps': [],
            'performance': {},
            'files': {},
            'errors': [],
            'success': False
        }
        
        try:
            # Step 1: Clean and prepare
            self._add_step(deployment_report, "Cleaning and preparing directories")
            self._prepare_directories()
            
            # Step 2: Build CSS files
            self._add_step(deployment_report, "Building and optimizing CSS files")
            build_result = self._build_css_files()
            deployment_report['performance'].update(build_result)
            
            # Step 3: Generate page-specific critical CSS
            self._add_step(deployment_report, "Generating page-specific critical CSS")
            critical_css_result = self._generate_page_critical_css()
            deployment_report['files'].update(critical_css_result)
            
            # Step 4: Create versioned files
            if self.config['enable_versioning']:
                self._add_step(deployment_report, "Creating versioned files")
                versioning_result = self._create_versioned_files()
                deployment_report['files'].update(versioning_result)
            
            # Step 5: Generate service worker cache manifest
            self._add_step(deployment_report, "Generating cache manifest")
            cache_manifest = self._generate_cache_manifest()
            deployment_report['files']['cache_manifest'] = cache_manifest
            
            # Step 6: Create deployment package
            self._add_step(deployment_report, "Creating deployment package")
            package_info = self._create_deployment_package()
            deployment_report['files']['package'] = package_info
            
            # Step 7: Validate performance budgets
            self._add_step(deployment_report, "Validating performance budgets")
            budget_check = self._validate_performance_budgets()
            deployment_report['performance']['budget_check'] = budget_check
            
            # Step 8: Generate deployment instructions
            self._add_step(deployment_report, "Generating deployment instructions")
            instructions = self._generate_deployment_instructions()
            deployment_report['instructions'] = instructions
            
            deployment_report['success'] = True
            print("✅ CSS optimization deployment completed successfully!")
            
        except Exception as e:
            deployment_report['errors'].append(str(e))
            print(f"❌ Deployment failed: {e}")
        
        # Save deployment report
        self._save_deployment_report(deployment_report)
        
        return deployment_report
    
    def _prepare_directories(self):
        """Prepare deployment directories"""
        # Create deploy directory
        if self.deploy_dir.exists():
            shutil.rmtree(self.deploy_dir)
        self.deploy_dir.mkdir(parents=True)
        
        # Create subdirectories
        (self.deploy_dir / 'css').mkdir()
        (self.deploy_dir / 'js').mkdir()
        (self.deploy_dir / 'critical').mkdir()
        
        print("📁 Directories prepared")
    
    def _build_css_files(self) -> dict:
        """Build and optimize CSS files"""
        try:
            # Run CSS build script
            build_script = self.base_dir / 'build_css.py'
            if build_script.exists():
                result = subprocess.run([
                    sys.executable, str(build_script),
                    '--base-dir', str(self.base_dir)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise Exception(f"CSS build failed: {result.stderr}")
                
                print("🔧 CSS files built and optimized")
            
            # Copy optimized files to deploy directory
            if self.build_dir.exists():
                for css_file in self.build_dir.glob('*.css'):
                    shutil.copy2(css_file, self.deploy_dir / 'css')
            
            # Calculate performance metrics
            total_size = 0
            critical_size = 0
            
            for css_file in (self.deploy_dir / 'css').glob('*.css'):
                size = css_file.stat().st_size
                total_size += size
                
                if 'critical' in css_file.name:
                    critical_size += size
            
            return {
                'total_css_size': total_size,
                'critical_css_size': critical_size,
                'compression_ratio': self._calculate_compression_ratio()
            }
            
        except Exception as e:
            print(f"⚠️ CSS build warning: {e}")
            return {}
    
    def _generate_page_critical_css(self) -> dict:
        """Generate page-specific critical CSS files"""
        critical_files = {}
        
        base_critical_path = self.css_dir / 'critical.css'
        if not base_critical_path.exists():
            print("⚠️ Base critical.css not found")
            return critical_files
        
        with open(base_critical_path, 'r', encoding='utf-8') as f:
            base_critical = f.read()
        
        for page, css_files in self.page_critical_css.items():
            combined_css = [base_critical]
            
            for css_file in css_files[1:]:  # Skip base critical.css
                css_path = self.css_dir / css_file
                if css_path.exists():
                    with open(css_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        combined_css.append(f'/* {css_file} */\\n{content}')
            
            # Combine and optimize
            page_critical = '\\n\\n'.join(combined_css)
            page_critical = self._optimize_css_content(page_critical)
            
            # Save page-specific critical CSS
            output_file = self.deploy_dir / 'critical' / f'{page}-critical.css'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(page_critical)
            
            critical_files[page] = {
                'file': str(output_file.relative_to(self.deploy_dir)),
                'size': len(page_critical.encode('utf-8'))
            }
            
            print(f"📄 Generated critical CSS for {page}: {critical_files[page]['size']} bytes")
        
        return critical_files
    
    def _create_versioned_files(self) -> dict:
        """Create versioned files with content hashes"""
        versioned_files = {}
        
        for css_file in (self.deploy_dir / 'css').glob('*.css'):
            # Calculate content hash
            with open(css_file, 'rb') as f:
                content_hash = hashlib.md5(f.read()).hexdigest()[:8]
            
            # Create versioned filename
            stem = css_file.stem
            suffix = css_file.suffix
            versioned_name = f'{stem}.{content_hash}{suffix}'
            versioned_path = css_file.parent / versioned_name
            
            # Copy to versioned filename
            shutil.copy2(css_file, versioned_path)
            
            versioned_files[stem] = {
                'original': css_file.name,
                'versioned': versioned_name,
                'hash': content_hash
            }
        
        # Create version manifest
        manifest_path = self.deploy_dir / 'css-manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(versioned_files, f, indent=2)
        
        print(f"🏷️ Created {len(versioned_files)} versioned CSS files")
        return versioned_files
    
    def _generate_cache_manifest(self) -> dict:
        """Generate service worker cache manifest"""
        manifest = {
            'version': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'critical_css': [],
            'css_files': [],
            'cache_strategy': {
                'critical': 'cache-first',
                'css': 'stale-while-revalidate',
                'max_age': self.config['cache_duration']
            }
        }
        
        # Add critical CSS files
        for critical_file in (self.deploy_dir / 'critical').glob('*.css'):
            manifest['critical_css'].append({
                'url': f'/static/critical/{critical_file.name}',
                'size': critical_file.stat().st_size
            })
        
        # Add regular CSS files
        for css_file in (self.deploy_dir / 'css').glob('*.css'):
            manifest['css_files'].append({
                'url': f'/static/css/{css_file.name}',
                'size': css_file.stat().st_size
            })
        
        # Save manifest
        manifest_path = self.deploy_dir / 'css-cache-manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"📋 Generated cache manifest with {len(manifest['css_files'])} CSS files")
        return manifest
    
    def _create_deployment_package(self) -> dict:
        """Create deployment package"""
        package_info = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.environment,
            'files_count': 0,
            'total_size': 0
        }
        
        # Count files and calculate total size
        for file_path in self.deploy_dir.rglob('*'):
            if file_path.is_file():
                package_info['files_count'] += 1
                package_info['total_size'] += file_path.stat().st_size
        
        # Create package metadata
        metadata_path = self.deploy_dir / 'package.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(package_info, f, indent=2)
        
        print(f"📦 Created deployment package: {package_info['files_count']} files, "
              f"{package_info['total_size']} bytes")
        
        return package_info
    
    def _validate_performance_budgets(self) -> dict:
        """Validate performance budgets"""
        budget_check = {
            'critical_budget': self.config['performance_budget_critical'],
            'total_budget': self.config['performance_budget_total'],
            'critical_size': 0,
            'total_size': 0,
            'critical_within_budget': True,
            'total_within_budget': True,
            'violations': []
        }
        
        # Check critical CSS sizes
        for critical_file in (self.deploy_dir / 'critical').glob('*.css'):
            size = critical_file.stat().st_size
            budget_check['critical_size'] += size
            
            if size > self.config['performance_budget_critical']:
                budget_check['violations'].append(
                    f"{critical_file.name} exceeds critical budget: {size} > {self.config['performance_budget_critical']}"
                )
        
        # Check total CSS size
        for css_file in (self.deploy_dir / 'css').glob('*.css'):
            budget_check['total_size'] += css_file.stat().st_size
        
        budget_check['critical_within_budget'] = budget_check['critical_size'] <= budget_check['critical_budget']
        budget_check['total_within_budget'] = budget_check['total_size'] <= budget_check['total_budget']
        
        if not budget_check['critical_within_budget']:
            budget_check['violations'].append(
                f"Total critical CSS exceeds budget: {budget_check['critical_size']} > {budget_check['critical_budget']}"
            )
        
        if not budget_check['total_within_budget']:
            budget_check['violations'].append(
                f"Total CSS exceeds budget: {budget_check['total_size']} > {budget_check['total_budget']}"
            )
        
        if budget_check['violations']:
            print("⚠️ Performance budget violations:")
            for violation in budget_check['violations']:
                print(f"  • {violation}")
        else:
            print("✅ All performance budgets satisfied")
        
        return budget_check
    
    def _generate_deployment_instructions(self) -> dict:
        """Generate deployment instructions"""
        instructions = {
            'server_setup': [
                "Enable gzip compression for CSS files",
                "Set appropriate cache headers (Cache-Control: max-age=31536000)",
                "Configure HTTP/2 Server Push for critical CSS",
                "Enable Brotli compression if available"
            ],
            'cdn_setup': [
                "Upload CSS files to CDN",
                "Configure edge caching with long TTL",
                "Enable HTTP/2 and HTTP/3 if available",
                "Set up geographic distribution"
            ],
            'monitoring': [
                "Set up Real User Monitoring (RUM)",
                "Monitor Core Web Vitals",
                "Track CSS loading performance",
                "Set up alerts for performance regressions"
            ],
            'rollback': [
                "Keep previous version for quick rollback",
                "Test critical CSS loading on key pages",
                "Monitor error rates after deployment",
                "Have rollback plan ready"
            ]
        }
        
        # Save instructions
        instructions_path = self.deploy_dir / 'DEPLOYMENT_INSTRUCTIONS.md'
        with open(instructions_path, 'w', encoding='utf-8') as f:
            f.write("# CSS Optimization Deployment Instructions\\n\\n")
            
            for section, items in instructions.items():
                f.write(f"## {section.replace('_', ' ').title()}\\n\\n")
                for item in items:
                    f.write(f"- {item}\\n")
                f.write("\\n")
        
        print("📝 Generated deployment instructions")
        return instructions
    
    def _optimize_css_content(self, css: str) -> str:
        """Optimize CSS content"""
        try:
            import csscompressor
            return csscompressor.compress(css)
        except ImportError:
            # Fallback manual optimization
            import re
            css = re.sub(r'/\\*[^*]*\\*+(?:[^/*][^*]*\\*+)*/', '', css)  # Remove comments
            css = re.sub(r'\\s+', ' ', css)  # Normalize whitespace
            css = re.sub(r';\\s*}', '}', css)  # Remove trailing semicolons
            return css.strip()
    
    def _calculate_compression_ratio(self) -> float:
        """Calculate CSS compression ratio"""
        original_size = 0
        compressed_size = 0
        
        for css_file in self.css_dir.glob('*.css'):
            original_size += css_file.stat().st_size
        
        for css_file in (self.deploy_dir / 'css').glob('*.css'):
            compressed_size += css_file.stat().st_size
        
        if original_size > 0:
            return (original_size - compressed_size) / original_size
        return 0.0
    
    def _add_step(self, report: dict, step: str):
        """Add step to deployment report"""
        report['steps'].append({
            'step': step,
            'timestamp': datetime.now().isoformat()
        })
        print(f"📋 {step}")
    
    def _save_deployment_report(self, report: dict):
        """Save deployment report"""
        report_path = self.deploy_dir / 'deployment-report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Deployment report saved: {report_path}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CSS Optimization Deployment')
    parser.add_argument('--environment', default='production', choices=['production', 'staging'],
                       help='Deployment environment')
    parser.add_argument('--base-dir', type=str, help='Base directory path')
    parser.add_argument('--no-versioning', action='store_true', help='Disable file versioning')
    
    args = parser.parse_args()
    
    deployment = CSSOptimizationDeployment(args.base_dir, args.environment)
    
    if args.no_versioning:
        deployment.config['enable_versioning'] = False
    
    report = deployment.deploy()
    
    if report['success']:
        print(f"\\n🎉 Deployment successful!")
        print(f"   Deploy directory: {deployment.deploy_dir}")
        print(f"   Files: {report.get('files', {}).get('package', {}).get('files_count', 'N/A')}")
        print(f"   Total size: {report.get('files', {}).get('package', {}).get('total_size', 'N/A')} bytes")
        
        budget_check = report.get('performance', {}).get('budget_check', {})
        if budget_check.get('violations'):
            print(f"\\n⚠️  Performance budget violations detected!")
            sys.exit(1)
    else:
        print(f"\\n❌ Deployment failed!")
        if report['errors']:
            for error in report['errors']:
                print(f"   Error: {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()