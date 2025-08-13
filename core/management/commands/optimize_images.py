"""
Management command for comprehensive image optimization pipeline.
Converts images to WebP format with JPEG fallbacks and generates responsive sizes.
"""

import os
import sys
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.staticfiles.finders import find
from PIL import Image, ImageFilter, ImageOps
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Optimize images for web delivery with WebP conversion and responsive sizes'

    # Responsive breakpoints for srcset generation
    RESPONSIVE_SIZES = [320, 640, 1024, 1920]
    
    # Quality settings for different formats
    WEBP_QUALITY = 85
    JPEG_QUALITY = 90
    PNG_QUALITY = 95
    
    # Blur radius for placeholder generation
    BLUR_RADIUS = 10
    PLACEHOLDER_SCALE = 0.1

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-dir',
            type=str,
            default='static/images',
            help='Source directory containing images to optimize'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='static/images/optimized',
            help='Output directory for optimized images'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-optimization of existing files'
        )
        parser.add_argument(
            '--generate-placeholders',
            action='store_true',
            default=True,
            help='Generate blur-up placeholders'
        )
        parser.add_argument(
            '--max-width',
            type=int,
            default=1920,
            help='Maximum width for responsive images'
        )

    def handle(self, *args, **options):
        start_time = time.time()
        
        source_dir = Path(options['source_dir'])
        output_dir = Path(options['output_dir'])
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff'}
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(source_dir.rglob(f'*{ext}'))
            image_files.extend(source_dir.rglob(f'*{ext.upper()}'))
        
        if not image_files:
            self.stdout.write(
                self.style.WARNING(f'No images found in {source_dir}')
            )
            return
        
        self.stdout.write(f'Found {len(image_files)} images to optimize')
        
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        for image_path in image_files:
            try:
                result = self._optimize_image(
                    image_path, 
                    output_dir, 
                    options
                )
                
                if result['processed']:
                    processed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Optimized: {image_path.name} '
                            f'({result["original_size"]} → {result["optimized_size"]})'
                        )
                    )
                else:
                    skipped_count += 1
                    if options['verbosity'] > 1:
                        self.stdout.write(f'- Skipped: {image_path.name}')
                        
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing {image_path.name}: {e}')
                )
                logger.error(f'Image optimization error for {image_path}: {e}')
        
        # Generate optimization report
        elapsed_time = time.time() - start_time
        self._generate_report(processed_count, skipped_count, error_count, elapsed_time)

    def _optimize_image(self, image_path: Path, output_dir: Path, options: Dict) -> Dict:
        """Optimize a single image with responsive sizes and WebP conversion."""
        
        # Skip if already optimized and not forcing
        output_subdir = output_dir / image_path.parent.relative_to(Path(options['source_dir']))
        output_subdir.mkdir(parents=True, exist_ok=True)
        
        base_name = image_path.stem
        webp_path = output_subdir / f'{base_name}.webp'
        
        if not options['force'] and webp_path.exists():
            return {
                'processed': False,
                'reason': 'already_exists'
            }
        
        # Load and validate image
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                original_size = image_path.stat().st_size
                optimized_sizes = []
                
                # Generate responsive sizes
                original_width, original_height = img.size
                max_width = min(original_width, options['max_width'])
                
                for width in self.RESPONSIVE_SIZES:
                    if width <= max_width:
                        optimized_sizes.extend(
                            self._generate_responsive_image(
                                img, base_name, width, output_subdir, options
                            )
                        )
                
                # Generate original size in WebP if not already covered
                if original_width not in self.RESPONSIVE_SIZES:
                    optimized_sizes.extend(
                        self._generate_responsive_image(
                            img, base_name, original_width, output_subdir, options
                        )
                    )
                
                # Generate blur placeholder if requested
                if options['generate_placeholders']:
                    self._generate_blur_placeholder(img, base_name, output_subdir)
                
                total_optimized_size = sum(optimized_sizes)
                
                return {
                    'processed': True,
                    'original_size': self._format_size(original_size),
                    'optimized_size': self._format_size(total_optimized_size),
                    'compression_ratio': (1 - total_optimized_size / original_size) * 100 if original_size > 0 else 0
                }
                
        except Exception as e:
            raise CommandError(f'Failed to process {image_path}: {e}')

    def _generate_responsive_image(self, img: Image.Image, base_name: str, 
                                 width: int, output_dir: Path, options: Dict) -> List[int]:
        """Generate responsive image sizes in WebP and JPEG formats."""
        
        sizes = []
        
        # Calculate proportional height
        original_width, original_height = img.size
        height = int((width / original_width) * original_height)
        
        # Resize image
        resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Optimize image using Pillow's built-in optimization
        resized_img = ImageOps.exif_transpose(resized_img)
        
        # Generate WebP version
        webp_path = output_dir / f'{base_name}_{width}w.webp'
        resized_img.save(
            webp_path, 
            'WEBP', 
            quality=self.WEBP_QUALITY,
            method=6,  # Best compression
            optimize=True
        )
        sizes.append(webp_path.stat().st_size)
        
        # Generate JPEG fallback
        jpeg_path = output_dir / f'{base_name}_{width}w.jpg'
        resized_img.save(
            jpeg_path, 
            'JPEG', 
            quality=self.JPEG_QUALITY,
            optimize=True,
            progressive=True
        )
        sizes.append(jpeg_path.stat().st_size)
        
        return sizes

    def _generate_blur_placeholder(self, img: Image.Image, base_name: str, output_dir: Path):
        """Generate a small, blurred placeholder image."""
        
        original_width, original_height = img.size
        placeholder_width = max(int(original_width * self.PLACEHOLDER_SCALE), 20)
        placeholder_height = max(int(original_height * self.PLACEHOLDER_SCALE), 20)
        
        # Create small, blurred version
        placeholder = img.resize((placeholder_width, placeholder_height), Image.Resampling.LANCZOS)
        placeholder = placeholder.filter(ImageFilter.GaussianBlur(radius=self.BLUR_RADIUS))
        
        # Save as low-quality JPEG
        placeholder_path = output_dir / f'{base_name}_placeholder.jpg'
        placeholder.save(
            placeholder_path,
            'JPEG',
            quality=20,
            optimize=True
        )

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f'{size_bytes:.1f}{unit}'
            size_bytes /= 1024
        return f'{size_bytes:.1f}TB'

    def _generate_report(self, processed: int, skipped: int, errors: int, elapsed_time: float):
        """Generate optimization summary report."""
        
        total = processed + skipped + errors
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('IMAGE OPTIMIZATION COMPLETE'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total images: {total}')
        self.stdout.write(f'Processed: {processed}')
        self.stdout.write(f'Skipped: {skipped}')
        self.stdout.write(f'Errors: {errors}')
        self.stdout.write(f'Time elapsed: {elapsed_time:.2f}s')
        
        if processed > 0:
            self.stdout.write(f'Average time per image: {elapsed_time/processed:.2f}s')
        
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Update templates to use responsive_image template tag')
        self.stdout.write('2. Enable lazy loading for improved performance')
        self.stdout.write('3. Configure static file serving with proper cache headers')