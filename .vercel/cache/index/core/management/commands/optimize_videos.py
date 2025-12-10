"""
Management command for video optimization and compression.
Optimizes hero videos and other video content for web delivery.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
import time

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Optimize videos for web delivery with compression and format conversion'

    # Video optimization settings
    TARGET_SIZE_MB = 5  # Target file size in MB
    QUALITY_SETTINGS = {
        'high': {'crf': 23, 'preset': 'medium'},
        'medium': {'crf': 28, 'preset': 'fast'},
        'low': {'crf': 32, 'preset': 'veryfast'}
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-dir',
            type=str,
            default='static/videos',
            help='Source directory containing videos to optimize'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='static/videos/optimized',
            help='Output directory for optimized videos'
        )
        parser.add_argument(
            '--quality',
            type=str,
            choices=['high', 'medium', 'low'],
            default='medium',
            help='Video quality setting'
        )
        parser.add_argument(
            '--target-size',
            type=float,
            default=5.0,
            help='Target file size in MB'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-optimization of existing files'
        )
        parser.add_argument(
            '--generate-poster',
            action='store_true',
            default=True,
            help='Generate poster images from videos'
        )

    def handle(self, *args, **options):
        # Check if ffmpeg is available
        if not self._check_ffmpeg():
            raise CommandError(
                'FFmpeg is not installed or not available in PATH. '
                'Please install FFmpeg: https://ffmpeg.org/download.html'
            )
        
        start_time = time.time()
        
        source_dir = Path(options['source_dir'])
        output_dir = Path(options['output_dir'])
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all video files
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v'}
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(source_dir.rglob(f'*{ext}'))
            video_files.extend(source_dir.rglob(f'*{ext.upper()}'))
        
        if not video_files:
            self.stdout.write(
                self.style.WARNING(f'No videos found in {source_dir}')
            )
            return
        
        self.stdout.write(f'Found {len(video_files)} videos to optimize')
        
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        for video_path in video_files:
            try:
                result = self._optimize_video(
                    video_path, 
                    output_dir, 
                    options
                )
                
                if result['processed']:
                    processed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Optimized: {video_path.name} '
                            f'({result["original_size"]} → {result["optimized_size"]})'
                        )
                    )
                else:
                    skipped_count += 1
                    if options['verbosity'] > 1:
                        self.stdout.write(f'- Skipped: {video_path.name}')
                        
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing {video_path.name}: {e}')
                )
                logger.error(f'Video optimization error for {video_path}: {e}')
        
        # Generate optimization report
        elapsed_time = time.time() - start_time
        self._generate_report(processed_count, skipped_count, error_count, elapsed_time)

    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available."""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _optimize_video(self, video_path: Path, output_dir: Path, options: Dict) -> Dict:
        """Optimize a single video file."""
        
        # Skip if already optimized and not forcing
        output_subdir = output_dir / video_path.parent.relative_to(Path(options['source_dir']))
        output_subdir.mkdir(parents=True, exist_ok=True)
        
        base_name = video_path.stem
        output_path = output_subdir / f'{base_name}_optimized.mp4'
        
        if not options['force'] and output_path.exists():
            return {
                'processed': False,
                'reason': 'already_exists'
            }
        
        original_size = video_path.stat().st_size
        
        # Get video info
        video_info = self._get_video_info(video_path)
        if not video_info:
            raise CommandError(f'Could not get video information for {video_path}')
        
        # Calculate target bitrate based on file size
        target_size_bytes = options['target_size'] * 1024 * 1024
        duration = video_info.get('duration', 0)
        
        if duration > 0:
            # Calculate target bitrate (leaving 10% buffer for audio)
            target_video_bitrate = int((target_size_bytes * 8 * 0.9) / duration)
        else:
            target_video_bitrate = 1000000  # 1 Mbps fallback
        
        # Optimize video
        success = self._compress_video(
            video_path, 
            output_path, 
            target_video_bitrate,
            options
        )
        
        if success:
            optimized_size = output_path.stat().st_size
            
            # Generate poster image if requested
            if options['generate_poster']:
                self._generate_poster(output_path, output_subdir, base_name)
            
            return {
                'processed': True,
                'original_size': self._format_size(original_size),
                'optimized_size': self._format_size(optimized_size),
                'compression_ratio': (1 - optimized_size / original_size) * 100 if original_size > 0 else 0
            }
        else:
            raise CommandError(f'Video compression failed for {video_path}')

    def _get_video_info(self, video_path: Path) -> Optional[Dict]:
        """Get video information using ffprobe."""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            import json
            data = json.loads(result.stdout)
            
            # Extract video stream info
            video_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            if video_stream:
                return {
                    'duration': float(data.get('format', {}).get('duration', 0)),
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0)),
                    'bitrate': int(data.get('format', {}).get('bit_rate', 0))
                }
            
        except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError):
            pass
        
        return None

    def _compress_video(self, input_path: Path, output_path: Path, 
                       target_bitrate: int, options: Dict) -> bool:
        """Compress video using FFmpeg."""
        
        quality_settings = self.QUALITY_SETTINGS[options['quality']]
        
        # Build FFmpeg command
        cmd = [
            'ffmpeg', '-i', str(input_path),
            '-c:v', 'libx264',  # H.264 codec
            '-preset', quality_settings['preset'],
            '-crf', str(quality_settings['crf']),
            '-maxrate', f'{target_bitrate}',
            '-bufsize', f'{target_bitrate * 2}',
            '-c:a', 'aac',  # AAC audio codec
            '-b:a', '128k',  # 128kbps audio bitrate
            '-movflags', '+faststart',  # Enable fast start for web
            '-pix_fmt', 'yuv420p',  # Ensure compatibility
            '-y',  # Overwrite output file
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f'FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}')
            return False

    def _generate_poster(self, video_path: Path, output_dir: Path, base_name: str):
        """Generate poster image from video."""
        
        poster_path = output_dir / f'{base_name}_poster.jpg'
        
        cmd = [
            'ffmpeg', '-i', str(video_path),
            '-ss', '00:00:01',  # Take frame at 1 second
            '-vframes', '1',  # Extract only 1 frame
            '-q:v', '2',  # High quality
            '-y',  # Overwrite
            str(poster_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            self.stdout.write(f'Generated poster: {poster_path.name}')
        except subprocess.CalledProcessError:
            logger.warning(f'Could not generate poster for {video_path}')

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
        self.stdout.write(self.style.SUCCESS('VIDEO OPTIMIZATION COMPLETE'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total videos: {total}')
        self.stdout.write(f'Processed: {processed}')
        self.stdout.write(f'Skipped: {skipped}')
        self.stdout.write(f'Errors: {errors}')
        self.stdout.write(f'Time elapsed: {elapsed_time:.2f}s')
        
        if processed > 0:
            self.stdout.write(f'Average time per video: {elapsed_time/processed:.2f}s')
        
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Update video tags to use optimized versions')
        self.stdout.write('2. Add poster attributes for faster loading')
        self.stdout.write('3. Configure proper video serving with CDN')
        self.stdout.write('\nFFmpeg installation:')
        self.stdout.write('macOS: brew install ffmpeg')
        self.stdout.write('Ubuntu: sudo apt install ffmpeg')
        self.stdout.write('Windows: Download from https://ffmpeg.org/download.html')