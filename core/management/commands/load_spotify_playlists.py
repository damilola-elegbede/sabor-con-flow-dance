"""
Management command to load sample Spotify playlists.
SPEC_05 Group C Task 8 - Spotify playlists integration.

Usage:
    python manage.py load_spotify_playlists
    python manage.py load_spotify_playlists --clear  # Clear existing playlists first
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from core.models import SpotifyPlaylist
import os


class Command(BaseCommand):
    help = 'Load sample Spotify playlists for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing playlists before loading new ones',
        )
        parser.add_argument(
            '--fixture',
            type=str,
            default='spotify_playlists_sample.json',
            help='Fixture file to load (default: spotify_playlists_sample.json)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Loading Spotify playlists...')
        
        if options['clear']:
            self.stdout.write('Clearing existing playlists...')
            deleted_count = SpotifyPlaylist.objects.count()
            SpotifyPlaylist.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing playlists')
            )
        
        # Check if fixture file exists
        fixture_path = os.path.join('core', 'fixtures', options['fixture'])
        if not os.path.exists(fixture_path):
            raise CommandError(f'Fixture file not found: {fixture_path}')
        
        try:
            # Load the fixture
            call_command('loaddata', options['fixture'], verbosity=options['verbosity'])
            
            # Get the count of loaded playlists
            playlist_count = SpotifyPlaylist.objects.count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully loaded {playlist_count} Spotify playlists'
                )
            )
            
            # List the loaded playlists
            if options['verbosity'] >= 2:
                self.stdout.write('\nLoaded playlists:')
                for playlist in SpotifyPlaylist.objects.all():
                    status = "✓ Active" if playlist.is_active else "✗ Inactive"
                    self.stdout.write(
                        f'  {playlist.get_class_type_display()}: {playlist.title} [{status}]'
                    )
                    if options['verbosity'] >= 3:
                        self.stdout.write(f'    - Tracks: {playlist.tracks_count}')
                        self.stdout.write(f'    - Duration: {playlist.format_duration()}')
                        self.stdout.write(f'    - Playlist ID: {playlist.spotify_playlist_id}')
                        self.stdout.write(f'    - Theme: {playlist.theme_color}')
            
            # Provide helpful next steps
            self.stdout.write('\nNext steps:')
            self.stdout.write('1. Visit /admin/core/spotifyplaylist/ to manage playlists')
            self.stdout.write('2. Visit /resources/ to see playlists in action')
            self.stdout.write('3. Update playlist IDs with real Spotify playlist IDs')
            
        except Exception as e:
            raise CommandError(f'Error loading playlists: {str(e)}')