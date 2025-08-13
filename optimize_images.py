#!/usr/bin/env python
"""
Image Optimization Script for Sabor Con Flow Dance
Converts images to WebP format with fallbacks and creates placeholders
"""

import os
from pathlib import Path
from PIL import Image
import hashlib

def create_webp_versions(image_path, quality=85):
    """Convert image to WebP format"""
    try:
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Create WebP version
        webp_path = image_path.with_suffix('.webp')
        img.save(webp_path, 'WEBP', quality=quality, method=6)
        print(f"Created WebP: {webp_path}")
        
        # Create placeholder (tiny, blurred version)
        placeholder = img.copy()
        placeholder.thumbnail((20, 20), Image.Resampling.LANCZOS)
        placeholder = placeholder.resize(img.size, Image.Resampling.LANCZOS)
        
        placeholder_path = image_path.parent / f"{image_path.stem}_placeholder{image_path.suffix}"
        placeholder.save(placeholder_path, quality=20, optimize=True)
        print(f"Created placeholder: {placeholder_path}")
        
        # Create responsive sizes
        sizes = [
            (320, 'small'),
            (768, 'medium'),
            (1200, 'large')
        ]
        
        for width, suffix in sizes:
            if img.width > width:
                ratio = width / img.width
                height = int(img.height * ratio)
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                
                # Save as WebP
                resized_webp_path = image_path.parent / f"{image_path.stem}_{suffix}.webp"
                resized.save(resized_webp_path, 'WEBP', quality=quality, method=6)
                print(f"Created {suffix} WebP: {resized_webp_path}")
                
                # Save as original format
                resized_path = image_path.parent / f"{image_path.stem}_{suffix}{image_path.suffix}"
                if image_path.suffix.lower() == '.png':
                    resized.save(resized_path, 'PNG', optimize=True)
                else:
                    resized.save(resized_path, quality=quality, optimize=True)
                print(f"Created {suffix}: {resized_path}")
        
        return True
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False

def optimize_existing_images(directory):
    """Optimize all images in a directory"""
    image_extensions = {'.png', '.jpg', '.jpeg'}
    image_dir = Path(directory)
    
    if not image_dir.exists():
        print(f"Directory {directory} does not exist")
        return
    
    processed = 0
    for image_file in image_dir.iterdir():
        if image_file.suffix.lower() in image_extensions:
            # Skip if already processed (has webp version)
            webp_version = image_file.with_suffix('.webp')
            if not webp_version.exists():
                print(f"\nProcessing: {image_file}")
                if create_webp_versions(image_file):
                    processed += 1
            else:
                print(f"Skipping {image_file} (already processed)")
    
    print(f"\n✅ Processed {processed} images")

if __name__ == "__main__":
    # Process static images
    static_images_dir = "/Users/damilola/Documents/Projects/sabor-con-flow-dance/static/images"
    print("Optimizing static images...")
    optimize_existing_images(static_images_dir)
    
    # Process favicon directory
    favicon_dir = "/Users/damilola/Documents/Projects/sabor-con-flow-dance/static/images/favicon"
    print("\nOptimizing favicon images...")
    optimize_existing_images(favicon_dir)