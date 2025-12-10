"""
Image Optimization Utilities for Performance
SPEC_04 Group D Implementation
"""

import os
import hashlib
from PIL import Image, ImageOpt
import subprocess
from django.conf import settings
from django.core.cache import cache
from django.utils.encoding import force_bytes
import logging

logger = logging.getLogger(__name__)


class ImageOptimizer:
    """
    Advanced image optimization for Core Web Vitals improvement
    """
    
    def __init__(self):
        self.optimization_levels = {
            'high': {'quality': 85, 'optimize': True, 'progressive': True},
            'medium': {'quality': 90, 'optimize': True, 'progressive': True},
            'low': {'quality': 95, 'optimize': False, 'progressive': False}
        }
        
        self.webp_quality = 80
        self.avif_quality = 70  # Future format support
        
    def optimize_image(self, image_path, output_path=None, optimization_level='medium', 
                      generate_webp=True, generate_sizes=True):
        """
        Optimize a single image with multiple format and size generation
        
        Args:
            image_path (str): Path to source image
            output_path (str): Path for optimized output
            optimization_level (str): 'high', 'medium', or 'low'
            generate_webp (bool): Generate WebP version
            generate_sizes (bool): Generate responsive sizes
            
        Returns:
            dict: Information about generated files
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image not found: {image_path}")
                return None
                
            # Create cache key for optimization results
            cache_key = self._get_cache_key(image_path, optimization_level)
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
                
            with Image.open(image_path) as img:
                # Get image info
                original_size = os.path.getsize(image_path)
                width, height = img.size
                
                result = {
                    'original': {
                        'path': image_path,
                        'size': original_size,
                        'dimensions': (width, height)
                    },
                    'optimized': {},
                    'webp': {},
                    'responsive_sizes': {}
                }
                
                # Determine output path
                if not output_path:
                    output_path = self._get_optimized_path(image_path)
                
                # Optimize original format
                optimized_info = self._optimize_original_format(
                    img, image_path, output_path, optimization_level
                )
                result['optimized'] = optimized_info
                
                # Generate WebP version
                if generate_webp:
                    webp_info = self._generate_webp(img, image_path)
                    result['webp'] = webp_info
                
                # Generate responsive sizes
                if generate_sizes:
                    responsive_info = self._generate_responsive_sizes(
                        img, image_path, optimization_level
                    )
                    result['responsive_sizes'] = responsive_info
                
                # Cache the result
                cache.set(cache_key, result, 60 * 60 * 24)  # Cache for 24 hours
                
                return result
                
        except Exception as e:
            logger.error(f"Error optimizing image {image_path}: {str(e)}")
            return None
    
    def _optimize_original_format(self, img, input_path, output_path, level):
        """Optimize image in original format"""
        try:
            opts = self.optimization_levels[level]
            
            # Convert RGBA to RGB if saving as JPEG
            if img.mode in ('RGBA', 'LA'):
                if output_path.lower().endswith(('.jpg', '.jpeg')):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
            
            # Save optimized image
            save_kwargs = {
                'optimize': opts['optimize'],
                'quality': opts['quality']
            }
            
            if img.format in ('JPEG', 'JPG') or output_path.lower().endswith(('.jpg', '.jpeg')):
                save_kwargs['progressive'] = opts['progressive']
                save_kwargs['format'] = 'JPEG'
            elif img.format == 'PNG' or output_path.lower().endswith('.png'):
                save_kwargs['format'] = 'PNG'
                if opts['optimize']:
                    save_kwargs['compress_level'] = 6
            
            img.save(output_path, **save_kwargs)
            
            optimized_size = os.path.getsize(output_path)
            original_size = os.path.getsize(input_path)
            
            return {
                'path': output_path,
                'size': optimized_size,
                'savings': original_size - optimized_size,
                'savings_percent': ((original_size - optimized_size) / original_size) * 100,
                'dimensions': img.size
            }
            
        except Exception as e:
            logger.error(f"Error optimizing original format: {str(e)}")
            return None
    
    def _generate_webp(self, img, input_path):
        """Generate WebP version of image"""
        try:
            webp_path = self._get_webp_path(input_path)
            
            # Convert RGBA to RGB if needed
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Save as WebP
            img.save(webp_path, 'WebP', quality=self.webp_quality, optimize=True)
            
            webp_size = os.path.getsize(webp_path)
            original_size = os.path.getsize(input_path)
            
            return {
                'path': webp_path,
                'size': webp_size,
                'savings': original_size - webp_size,
                'savings_percent': ((original_size - webp_size) / original_size) * 100,
                'dimensions': img.size
            }
            
        except Exception as e:
            logger.error(f"Error generating WebP: {str(e)}")
            return None
    
    def _generate_responsive_sizes(self, img, input_path, level):
        """Generate responsive image sizes"""
        try:
            # Standard responsive breakpoints
            breakpoints = [
                (320, 'small'),
                (640, 'medium'),
                (1024, 'large'),
                (1920, 'xlarge')
            ]
            
            original_width, original_height = img.size
            responsive_images = {}
            
            for width, size_name in breakpoints:
                # Skip if original is smaller than breakpoint
                if original_width <= width:
                    continue
                
                # Calculate proportional height
                height = int((width / original_width) * original_height)
                
                # Resize image
                resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
                
                # Generate paths
                base_path = self._get_base_path(input_path)
                ext = os.path.splitext(input_path)[1]
                
                # Save optimized version
                optimized_path = f"{base_path}_{size_name}{ext}"
                opts = self.optimization_levels[level]
                
                save_kwargs = {
                    'optimize': opts['optimize'],
                    'quality': opts['quality']
                }
                
                if ext.lower() in ['.jpg', '.jpeg']:
                    save_kwargs['progressive'] = opts['progressive']
                    save_kwargs['format'] = 'JPEG'
                elif ext.lower() == '.png':
                    save_kwargs['format'] = 'PNG'
                    if opts['optimize']:
                        save_kwargs['compress_level'] = 6
                
                resized_img.save(optimized_path, **save_kwargs)
                
                # Save WebP version
                webp_path = f"{base_path}_{size_name}.webp"
                resized_img.save(webp_path, 'WebP', quality=self.webp_quality, optimize=True)
                
                responsive_images[size_name] = {
                    'optimized': {
                        'path': optimized_path,
                        'size': os.path.getsize(optimized_path),
                        'dimensions': (width, height)
                    },
                    'webp': {
                        'path': webp_path,
                        'size': os.path.getsize(webp_path),
                        'dimensions': (width, height)
                    }
                }
            
            return responsive_images
            
        except Exception as e:
            logger.error(f"Error generating responsive sizes: {str(e)}")
            return {}
    
    def _get_cache_key(self, image_path, level):
        """Generate cache key for optimization result"""
        file_hash = hashlib.md5(force_bytes(image_path)).hexdigest()
        file_mtime = os.path.getmtime(image_path)
        return f"image_opt:{file_hash}:{level}:{file_mtime}"
    
    def _get_optimized_path(self, input_path):
        """Get path for optimized image"""
        base, ext = os.path.splitext(input_path)
        return f"{base}_optimized{ext}"
    
    def _get_webp_path(self, input_path):
        """Get path for WebP version"""
        base, _ = os.path.splitext(input_path)
        return f"{base}.webp"
    
    def _get_base_path(self, input_path):
        """Get base path without extension"""
        return os.path.splitext(input_path)[0]
    
    def batch_optimize_directory(self, directory_path, optimization_level='medium'):
        """
        Optimize all images in a directory
        
        Args:
            directory_path (str): Path to directory containing images
            optimization_level (str): Optimization level to apply
            
        Returns:
            dict: Summary of optimization results
        """
        supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
        results = {
            'processed': 0,
            'skipped': 0,
            'errors': 0,
            'total_savings': 0,
            'files': []
        }
        
        try:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file_path)
                    
                    if ext.lower() in supported_formats:
                        try:
                            result = self.optimize_image(
                                file_path,
                                optimization_level=optimization_level
                            )
                            
                            if result:
                                results['processed'] += 1
                                if result.get('optimized', {}).get('savings', 0) > 0:
                                    results['total_savings'] += result['optimized']['savings']
                                results['files'].append(result)
                            else:
                                results['skipped'] += 1
                                
                        except Exception as e:
                            logger.error(f"Error processing {file_path}: {str(e)}")
                            results['errors'] += 1
                    else:
                        results['skipped'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing directory {directory_path}: {str(e)}")
            return results
    
    def generate_srcset(self, base_image_path, breakpoints=None):
        """
        Generate srcset string for responsive images
        
        Args:
            base_image_path (str): Path to base image
            breakpoints (list): List of (width, descriptor) tuples
            
        Returns:
            str: srcset string for HTML
        """
        if not breakpoints:
            breakpoints = [
                (320, '320w'),
                (640, '640w'),
                (1024, '1024w'),
                (1920, '1920w')
            ]
        
        base_path = self._get_base_path(base_image_path)
        ext = os.path.splitext(base_image_path)[1]
        
        srcset_parts = []
        
        for width, descriptor in breakpoints:
            # Map width to size name
            size_name = {
                320: 'small',
                640: 'medium',
                1024: 'large',
                1920: 'xlarge'
            }.get(width, str(width))
            
            image_path = f"{base_path}_{size_name}{ext}"
            
            # Check if file exists
            if os.path.exists(image_path):
                # Convert to static URL path
                static_path = image_path.replace(settings.STATICFILES_DIRS[0], '/static')
                srcset_parts.append(f"{static_path} {descriptor}")
        
        return ', '.join(srcset_parts)
    
    def get_optimization_report(self, results):
        """
        Generate human-readable optimization report
        
        Args:
            results (dict): Results from optimization process
            
        Returns:
            str: Formatted report
        """
        if not results:
            return "No optimization results available."
        
        total_original_size = 0
        total_optimized_size = 0
        total_webp_size = 0
        
        for file_result in results.get('files', []):
            original = file_result.get('original', {})
            optimized = file_result.get('optimized', {})
            webp = file_result.get('webp', {})
            
            total_original_size += original.get('size', 0)
            total_optimized_size += optimized.get('size', 0)
            total_webp_size += webp.get('size', 0)
        
        total_savings = total_original_size - total_optimized_size
        webp_savings = total_original_size - total_webp_size
        
        savings_percent = (total_savings / total_original_size * 100) if total_original_size > 0 else 0
        webp_savings_percent = (webp_savings / total_original_size * 100) if total_original_size > 0 else 0
        
        report = f"""
Image Optimization Report
========================

Files Processed: {results.get('processed', 0)}
Files Skipped: {results.get('skipped', 0)}
Errors: {results.get('errors', 0)}

Size Analysis:
- Original Total: {self._format_bytes(total_original_size)}
- Optimized Total: {self._format_bytes(total_optimized_size)}
- WebP Total: {self._format_bytes(total_webp_size)}

Savings:
- Standard Optimization: {self._format_bytes(total_savings)} ({savings_percent:.1f}%)
- WebP Format: {self._format_bytes(webp_savings)} ({webp_savings_percent:.1f}%)

Performance Impact:
- Estimated Page Load Improvement: {self._estimate_load_improvement(savings_percent)}
- Core Web Vitals Impact: {self._estimate_cwv_impact(savings_percent)}
        """
        
        return report.strip()
    
    def _format_bytes(self, bytes_size):
        """Format bytes into human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    def _estimate_load_improvement(self, savings_percent):
        """Estimate page load improvement based on image savings"""
        if savings_percent > 50:
            return "Significant (20-40% faster)"
        elif savings_percent > 30:
            return "Moderate (10-20% faster)"
        elif savings_percent > 15:
            return "Minor (5-10% faster)"
        else:
            return "Minimal (<5% faster)"
    
    def _estimate_cwv_impact(self, savings_percent):
        """Estimate Core Web Vitals impact"""
        if savings_percent > 40:
            return "High positive impact on LCP"
        elif savings_percent > 25:
            return "Moderate positive impact on LCP"
        elif savings_percent > 15:
            return "Minor positive impact on LCP"
        else:
            return "Minimal impact on CWV"


# Convenience functions for template usage
def optimize_static_image(image_path, level='medium'):
    """Optimize a static image file"""
    optimizer = ImageOptimizer()
    return optimizer.optimize_image(image_path, optimization_level=level)


def get_responsive_srcset(image_path):
    """Get responsive srcset for template usage"""
    optimizer = ImageOptimizer()
    return optimizer.generate_srcset(image_path)


def batch_optimize_static_images(level='medium'):
    """Optimize all static images"""
    if not hasattr(settings, 'STATICFILES_DIRS') or not settings.STATICFILES_DIRS:
        return None
    
    static_dir = settings.STATICFILES_DIRS[0]
    images_dir = os.path.join(static_dir, 'images')
    
    if not os.path.exists(images_dir):
        return None
    
    optimizer = ImageOptimizer()
    return optimizer.batch_optimize_directory(images_dir, level)