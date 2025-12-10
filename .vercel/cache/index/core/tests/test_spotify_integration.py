"""
Comprehensive tests for Spotify Playlists Integration - SPEC_05 Group C Task 8

Tests SpotifyPlaylist model functionality, view integration, template rendering,
and playlist management features.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from core.models import SpotifyPlaylist


class SpotifyPlaylistModelTestCase(TestCase):
    """Test cases for the SpotifyPlaylist model."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_playlist_data = {
            'class_type': 'choreo_team',
            'title': 'SCF Choreo Team - High Energy Mix',
            'description': 'High-energy Latin tracks perfect for choreography practice and performance.',
            'spotify_playlist_id': '37i9dQZF1DXbYM3nMM0oPk',
            'spotify_embed_url': 'https://open.spotify.com/embed/playlist/37i9dQZF1DXbYM3nMM0oPk?utm_source=generator',
            'is_active': True,
            'order': 1,
            'theme_color': '#FF6B6B',
            'tracks_count': 25,
            'duration_minutes': 90
        }
    
    def test_spotify_playlist_creation(self):
        """Test creating a Spotify playlist with valid data."""
        playlist = SpotifyPlaylist.objects.create(**self.valid_playlist_data)
        
        self.assertEqual(playlist.class_type, 'choreo_team')
        self.assertEqual(playlist.title, 'SCF Choreo Team - High Energy Mix')
        self.assertEqual(playlist.description, 'High-energy Latin tracks perfect for choreography practice and performance.')
        self.assertEqual(playlist.spotify_playlist_id, '37i9dQZF1DXbYM3nMM0oPk')
        self.assertEqual(playlist.spotify_embed_url, 'https://open.spotify.com/embed/playlist/37i9dQZF1DXbYM3nMM0oPk?utm_source=generator')
        self.assertTrue(playlist.is_active)
        self.assertEqual(playlist.order, 1)
        self.assertEqual(playlist.theme_color, '#FF6B6B')
        self.assertEqual(playlist.tracks_count, 25)
        self.assertEqual(playlist.duration_minutes, 90)
    
    def test_spotify_playlist_str_representation(self):
        """Test the string representation of a Spotify playlist."""
        playlist = SpotifyPlaylist.objects.create(**self.valid_playlist_data)
        expected_str = "SCF Choreo Team - SCF Choreo Team - High Energy Mix"
        self.assertEqual(str(playlist), expected_str)
    
    def test_spotify_playlist_unique_class_type(self):
        """Test that class_type must be unique."""
        SpotifyPlaylist.objects.create(**self.valid_playlist_data)
        
        # Try to create another playlist with same class_type
        duplicate_data = self.valid_playlist_data.copy()
        duplicate_data['title'] = 'Different Title'
        duplicate_data['spotify_playlist_id'] = 'different_id'
        
        with self.assertRaises(IntegrityError):
            SpotifyPlaylist.objects.create(**duplicate_data)
    
    def test_spotify_playlist_class_type_choices(self):
        """Test that class_type field accepts only valid choices."""
        valid_types = ['choreo_team', 'pasos_basicos', 'casino_royale', 'general', 'warm_up', 'cool_down']
        
        for class_type in valid_types:
            playlist_data = self.valid_playlist_data.copy()
            playlist_data['class_type'] = class_type
            playlist_data['spotify_playlist_id'] = f'test_id_{class_type}'
            
            playlist = SpotifyPlaylist.objects.create(**playlist_data)
            self.assertEqual(playlist.class_type, class_type)
    
    def test_spotify_playlist_invalid_class_type(self):
        """Test that invalid class_type choices raise validation error."""
        invalid_playlist = SpotifyPlaylist(
            class_type='invalid_type',
            title='Invalid Type Playlist',
            description='Test description',
            spotify_playlist_id='test123'
        )
        with self.assertRaises(ValidationError):
            invalid_playlist.full_clean()
    
    def test_spotify_playlist_default_values(self):
        """Test default values for playlist fields."""
        minimal_data = {
            'class_type': 'general',
            'title': 'Test Playlist',
            'description': 'Test description',
            'spotify_playlist_id': 'test123'
        }
        
        playlist = SpotifyPlaylist.objects.create(**minimal_data)
        
        self.assertTrue(playlist.is_active)
        self.assertEqual(playlist.order, 0)
        self.assertEqual(playlist.theme_color, '#C7B375')
        self.assertEqual(playlist.tracks_count, 0)
        self.assertEqual(playlist.duration_minutes, 0)
        self.assertIsNotNone(playlist.created_at)
        self.assertIsNotNone(playlist.last_updated)
    
    def test_get_embed_url_method(self):
        """Test the get_embed_url method."""
        # Test with spotify_embed_url provided
        playlist = SpotifyPlaylist.objects.create(**self.valid_playlist_data)
        embed_url = playlist.get_embed_url()
        self.assertEqual(embed_url, self.valid_playlist_data['spotify_embed_url'])
        
        # Test with only spotify_playlist_id
        playlist_data = self.valid_playlist_data.copy()
        playlist_data['class_type'] = 'pasos_basicos'
        playlist_data['spotify_embed_url'] = ''
        playlist = SpotifyPlaylist.objects.create(**playlist_data)
        
        embed_url = playlist.get_embed_url()
        expected_url = f"https://open.spotify.com/embed/playlist/{playlist.spotify_playlist_id}?utm_source=generator&theme=0"
        self.assertEqual(embed_url, expected_url)
        
        # Test with no URLs
        playlist_data = self.valid_playlist_data.copy()
        playlist_data['class_type'] = 'casino_royale'
        playlist_data['spotify_embed_url'] = ''
        playlist_data['spotify_playlist_id'] = ''
        playlist = SpotifyPlaylist.objects.create(**playlist_data)
        
        embed_url = playlist.get_embed_url()
        self.assertIsNone(embed_url)
    
    def test_get_compact_embed_url_method(self):
        """Test the get_compact_embed_url method."""
        playlist = SpotifyPlaylist.objects.create(**self.valid_playlist_data)
        compact_url = playlist.get_compact_embed_url()
        
        self.assertIn('theme=0', compact_url)
        self.assertIn('view=compact', compact_url)
        self.assertIn('height=380', compact_url)
        self.assertIn(playlist.spotify_playlist_id, compact_url)
    
    def test_get_playlist_url_method(self):
        """Test the get_playlist_url method."""
        playlist = SpotifyPlaylist.objects.create(**self.valid_playlist_data)
        playlist_url = playlist.get_playlist_url()
        
        expected_url = f"https://open.spotify.com/playlist/{playlist.spotify_playlist_id}"
        self.assertEqual(playlist_url, expected_url)
        
        # Test with no playlist ID
        playlist_data = self.valid_playlist_data.copy()
        playlist_data['class_type'] = 'warm_up'
        playlist_data['spotify_playlist_id'] = ''
        playlist = SpotifyPlaylist.objects.create(**playlist_data)
        
        playlist_url = playlist.get_playlist_url()
        self.assertIsNone(playlist_url)
    
    def test_format_duration_method(self):
        """Test the format_duration method."""
        # Test with minutes only
        playlist_data = self.valid_playlist_data.copy()
        playlist_data['duration_minutes'] = 45
        playlist = SpotifyPlaylist.objects.create(**playlist_data)
        
        self.assertEqual(playlist.format_duration(), "45 min")
        
        # Test with hours and minutes
        playlist_data['class_type'] = 'cool_down'
        playlist_data['duration_minutes'] = 125  # 2 hours 5 minutes
        playlist = SpotifyPlaylist.objects.create(**playlist_data)
        
        self.assertEqual(playlist.format_duration(), "2h 5m")
        
        # Test with exact hours
        playlist_data['class_type'] = 'general'
        playlist_data['duration_minutes'] = 120  # 2 hours exactly
        playlist = SpotifyPlaylist.objects.create(**playlist_data)
        
        self.assertEqual(playlist.format_duration(), "2h 0m")
        
        # Test with zero duration
        playlist_data['class_type'] = 'warm_up'
        playlist_data['duration_minutes'] = 0
        playlist = SpotifyPlaylist.objects.create(**playlist_data)
        
        self.assertEqual(playlist.format_duration(), "Unknown")
    
    def test_get_active_playlists_classmethod(self):
        """Test the get_active_playlists class method."""
        # Create active playlists with different orders
        SpotifyPlaylist.objects.create(
            class_type='choreo_team',
            title='Active Playlist 1',
            description='Test',
            spotify_playlist_id='active1',
            is_active=True,
            order=2
        )
        SpotifyPlaylist.objects.create(
            class_type='pasos_basicos',
            title='Active Playlist 2',
            description='Test',
            spotify_playlist_id='active2',
            is_active=True,
            order=1
        )
        SpotifyPlaylist.objects.create(
            class_type='casino_royale',
            title='Inactive Playlist',
            description='Test',
            spotify_playlist_id='inactive1',
            is_active=False,
            order=0
        )
        
        active_playlists = SpotifyPlaylist.get_active_playlists()
        
        # Should only return active playlists, ordered by order field
        self.assertEqual(len(active_playlists), 2)
        self.assertEqual(active_playlists[0].title, 'Active Playlist 2')  # order=1
        self.assertEqual(active_playlists[1].title, 'Active Playlist 1')  # order=2
        
        for playlist in active_playlists:
            self.assertTrue(playlist.is_active)
    
    def test_get_playlist_for_class_classmethod(self):
        """Test the get_playlist_for_class class method."""
        # Create test playlists
        choreo_playlist = SpotifyPlaylist.objects.create(
            class_type='choreo_team',
            title='Choreo Playlist',
            description='Test',
            spotify_playlist_id='choreo123',
            is_active=True
        )
        
        SpotifyPlaylist.objects.create(
            class_type='pasos_basicos',
            title='Inactive Pasos Playlist',
            description='Test',
            spotify_playlist_id='pasos123',
            is_active=False
        )
        
        # Test finding active playlist
        found_playlist = SpotifyPlaylist.get_playlist_for_class('choreo_team')
        self.assertEqual(found_playlist.title, 'Choreo Playlist')
        
        # Test finding inactive playlist (should return None)
        found_playlist = SpotifyPlaylist.get_playlist_for_class('pasos_basicos')
        self.assertIsNone(found_playlist)
        
        # Test non-existent class type
        found_playlist = SpotifyPlaylist.get_playlist_for_class('non_existent')
        self.assertIsNone(found_playlist)
    
    def test_spotify_playlist_ordering(self):
        """Test that playlists are ordered by order field, then class_type."""
        # Create playlists with different orders
        playlist1 = SpotifyPlaylist.objects.create(
            class_type='casino_royale',
            title='Third Playlist',
            description='Test',
            spotify_playlist_id='third',
            order=3
        )
        playlist2 = SpotifyPlaylist.objects.create(
            class_type='choreo_team',
            title='First Playlist',
            description='Test',
            spotify_playlist_id='first',
            order=1
        )
        playlist3 = SpotifyPlaylist.objects.create(
            class_type='pasos_basicos',
            title='Second Playlist A',
            description='Test',
            spotify_playlist_id='second_a',
            order=2
        )
        playlist4 = SpotifyPlaylist.objects.create(
            class_type='general',
            title='Second Playlist B',
            description='Test',
            spotify_playlist_id='second_b',
            order=2
        )
        
        playlists = list(SpotifyPlaylist.objects.all())
        
        # Should be ordered by order field first, then class_type
        self.assertEqual(playlists[0].title, 'First Playlist')
        self.assertEqual(playlists[1].title, 'Second Playlist B')  # 'general' comes before 'pasos_basicos'
        self.assertEqual(playlists[2].title, 'Second Playlist A')
        self.assertEqual(playlists[3].title, 'Third Playlist')
    
    def test_spotify_playlist_validation(self):
        """Test field validation for Spotify playlists."""
        # Test required fields
        with self.assertRaises(ValidationError):
            playlist = SpotifyPlaylist(description='No title')
            playlist.full_clean()
        
        # Test max length validation
        long_title = 'x' * 201  # Exceeds max_length=200
        playlist = SpotifyPlaylist(
            class_type='general',
            title=long_title,
            description='Test',
            spotify_playlist_id='test'
        )
        with self.assertRaises(ValidationError):
            playlist.full_clean()
        
        # Test color field validation (should accept hex colors)
        playlist = SpotifyPlaylist.objects.create(
            class_type='general',
            title='Color Test',
            description='Test',
            spotify_playlist_id='color_test',
            theme_color='#FF0000'
        )
        self.assertEqual(playlist.theme_color, '#FF0000')
    
    def test_spotify_playlist_auto_timestamps(self):
        """Test automatic timestamp creation and updates."""
        from django.utils import timezone
        import time
        
        before_creation = timezone.now()
        playlist = SpotifyPlaylist.objects.create(**self.valid_playlist_data)
        after_creation = timezone.now()
        
        self.assertGreaterEqual(playlist.created_at, before_creation)
        self.assertLessEqual(playlist.created_at, after_creation)
        self.assertGreaterEqual(playlist.last_updated, before_creation)
        self.assertLessEqual(playlist.last_updated, after_creation)
        
        # Test that last_updated changes on save
        original_updated = playlist.last_updated
        time.sleep(0.01)  # Small delay
        playlist.title = 'Updated Title'
        playlist.save()
        
        self.assertGreater(playlist.last_updated, original_updated)


class SpotifyPlaylistViewsTestCase(TestCase):
    """Test cases for Spotify playlist integration with views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test playlists
        self.choreo_playlist = SpotifyPlaylist.objects.create(
            class_type='choreo_team',
            title='SCF Choreo Team Mix',
            description='High-energy tracks for choreo practice',
            spotify_playlist_id='choreo123',
            spotify_embed_url='https://open.spotify.com/embed/playlist/choreo123',
            is_active=True,
            order=1,
            tracks_count=20,
            duration_minutes=75
        )
        
        self.pasos_playlist = SpotifyPlaylist.objects.create(
            class_type='pasos_basicos',
            title='Pasos Básicos Essentials',
            description='Perfect tempo for learning basic steps',
            spotify_playlist_id='pasos123',
            spotify_embed_url='https://open.spotify.com/embed/playlist/pasos123',
            is_active=True,
            order=2,
            tracks_count=15,
            duration_minutes=60
        )
        
        self.inactive_playlist = SpotifyPlaylist.objects.create(
            class_type='casino_royale',
            title='Inactive Casino Mix',
            description='This playlist is inactive',
            spotify_playlist_id='inactive123',
            is_active=False,
            order=3
        )
    
    def test_home_view_includes_spotify_playlists(self):
        """Test that home view includes Spotify playlists in context."""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('spotify_playlists', response.context)
        
        playlists = response.context['spotify_playlists']
        self.assertGreaterEqual(len(playlists), 2)  # At least our active playlists
        
        # Should only include active playlists
        for playlist in playlists:
            self.assertTrue(playlist.is_active)
    
    def test_resources_view_includes_spotify_playlists(self):
        """Test that resources view includes Spotify playlists."""
        response = self.client.get('/resources/')
        
        self.assertEqual(response.status_code, 200)
        
        # Check context variables
        self.assertIn('main_class_playlists', response.context)
        self.assertIn('practice_playlists', response.context)
        self.assertIn('all_playlists', response.context)
        
        main_playlists = response.context['main_class_playlists']
        all_playlists = response.context['all_playlists']
        
        # Should include our main class playlists
        self.assertGreaterEqual(len(main_playlists), 2)
        self.assertGreaterEqual(len(all_playlists), 2)
        
        # Check that playlists are properly categorized
        main_class_types = [p.class_type for p in main_playlists]
        self.assertIn('choreo_team', main_class_types)
        self.assertIn('pasos_basicos', main_class_types)
    
    def test_resources_view_playlist_grouping(self):
        """Test that resources view properly groups playlists."""
        # Add practice playlists
        SpotifyPlaylist.objects.create(
            class_type='warm_up',
            title='Warm Up Mix',
            description='Perfect for warming up',
            spotify_playlist_id='warmup123',
            is_active=True,
            order=10
        )
        
        response = self.client.get('/resources/')
        
        main_playlists = response.context['main_class_playlists']
        practice_playlists = response.context['practice_playlists']
        
        # Main class playlists should only include choreo_team, pasos_basicos, casino_royale
        main_types = [p.class_type for p in main_playlists]
        for playlist_type in main_types:
            self.assertIn(playlist_type, ['choreo_team', 'pasos_basicos', 'casino_royale'])
        
        # Practice playlists should include others
        practice_types = [p.class_type for p in practice_playlists]
        self.assertIn('warm_up', practice_types)
    
    def test_spotify_playlist_caching_in_views(self):
        """Test caching behavior for Spotify playlists in views."""
        # Clear cache first
        cache.clear()
        
        # First request should hit database
        response1 = self.client.get('/resources/')
        self.assertEqual(response1.status_code, 200)
        
        # Modify playlist in database
        self.choreo_playlist.title = 'Modified Title'
        self.choreo_playlist.save()
        
        # Second request should use cache (won't see modification)
        response2 = self.client.get('/resources/')
        self.assertEqual(response2.status_code, 200)
        
        # Clear cache
        cache.clear()
        
        # Third request should hit database again
        response3 = self.client.get('/resources/')
        self.assertEqual(response3.status_code, 200)
    
    def test_spotify_playlist_template_rendering(self):
        """Test that Spotify playlists render correctly in templates."""
        response = self.client.get('/resources/')
        
        # Check that playlist data is in the rendered content
        self.assertContains(response, 'SCF Choreo Team Mix')
        self.assertContains(response, 'Pasos Básicos Essentials')
        self.assertContains(response, 'High-energy tracks')
        
        # Check that Spotify embed URLs are present
        self.assertContains(response, 'spotify.com/embed/playlist/choreo123')
        self.assertContains(response, 'spotify.com/embed/playlist/pasos123')
        
        # Check that inactive playlists are not shown
        self.assertNotContains(response, 'Inactive Casino Mix')
    
    def test_resources_view_performance_queries(self):
        """Test query performance for resources view with playlists."""
        # Create additional playlists
        for i in range(10):
            SpotifyPlaylist.objects.create(
                class_type='general',
                title=f'Performance Test Playlist {i}',
                description='Performance test',
                spotify_playlist_id=f'perf{i}',
                is_active=True,
                order=i
            )
        
        # Clear cache to ensure fresh queries
        cache.clear()
        
        # Should be efficient even with many playlists
        with self.assertNumQueries(3):  # Reasonable number of queries
            response = self.client.get('/resources/')
            
        self.assertEqual(response.status_code, 200)


class SpotifyPlaylistAdminTestCase(TestCase):
    """Test cases for Spotify playlist admin functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.playlist = SpotifyPlaylist.objects.create(
            class_type='choreo_team',
            title='Admin Test Playlist',
            description='Test playlist for admin',
            spotify_playlist_id='admin123',
            is_active=True,
            tracks_count=10,
            duration_minutes=40
        )
    
    def test_spotify_playlist_admin_str(self):
        """Test admin string representation."""
        self.assertEqual(str(self.playlist), 'SCF Choreo Team - Admin Test Playlist')
    
    def test_spotify_playlist_admin_fields(self):
        """Test that all expected fields are accessible."""
        # Test that we can access all fields without errors
        self.assertEqual(self.playlist.class_type, 'choreo_team')
        self.assertEqual(self.playlist.title, 'Admin Test Playlist')
        self.assertEqual(self.playlist.spotify_playlist_id, 'admin123')
        self.assertTrue(self.playlist.is_active)
        self.assertEqual(self.playlist.tracks_count, 10)
        self.assertEqual(self.playlist.duration_minutes, 40)
    
    def test_spotify_playlist_bulk_admin_operations(self):
        """Test bulk operations that might be used in admin."""
        # Create multiple playlists
        playlists = []
        for i in range(5):
            playlist = SpotifyPlaylist.objects.create(
                class_type='general',
                title=f'Bulk Test Playlist {i}',
                description='Bulk test',
                spotify_playlist_id=f'bulk{i}',
                is_active=(i % 2 == 0)  # Alternate active status
            )
            playlists.append(playlist)
        
        # Test bulk activation
        SpotifyPlaylist.objects.filter(
            spotify_playlist_id__startswith='bulk'
        ).update(is_active=True)
        
        # Verify all are now active
        bulk_playlists = SpotifyPlaylist.objects.filter(
            spotify_playlist_id__startswith='bulk'
        )
        for playlist in bulk_playlists:
            self.assertTrue(playlist.is_active)
        
        # Test bulk ordering
        SpotifyPlaylist.objects.filter(
            spotify_playlist_id__startswith='bulk'
        ).update(order=10)
        
        # Verify order was updated
        bulk_playlists = SpotifyPlaylist.objects.filter(
            spotify_playlist_id__startswith='bulk'
        )
        for playlist in bulk_playlists:
            self.assertEqual(playlist.order, 10)


class SpotifyPlaylistIntegrationTestCase(TestCase):
    """Integration tests for Spotify playlist functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create a complete set of playlists for different class types
        self.class_playlists = []
        class_data = [
            ('choreo_team', 'SCF Choreo Team Power Mix', 25, 95),
            ('pasos_basicos', 'Pasos Básicos Learning Mix', 18, 70),
            ('casino_royale', 'Casino Royale Advanced Mix', 22, 85),
            ('general', 'General Practice Mix', 30, 120),
            ('warm_up', 'Warm Up Essentials', 12, 35),
            ('cool_down', 'Cool Down & Stretch', 10, 30)
        ]
        
        for i, (class_type, title, tracks, duration) in enumerate(class_data):
            playlist = SpotifyPlaylist.objects.create(
                class_type=class_type,
                title=title,
                description=f'Perfect playlist for {class_type.replace("_", " ")} sessions',
                spotify_playlist_id=f'playlist_{class_type}',
                spotify_embed_url=f'https://open.spotify.com/embed/playlist/playlist_{class_type}',
                is_active=True,
                order=i,
                tracks_count=tracks,
                duration_minutes=duration,
                theme_color=f'#{"ABCDEF"[i % 6]}{"123456"[i % 6]}{"789ABC"[i % 6]}{"DEF012"[i % 6]}{"345678"[i % 6]}{"9ABCDE"[i % 6]}'
            )
            self.class_playlists.append(playlist)
    
    def test_complete_playlist_ecosystem(self):
        """Test the complete playlist ecosystem functionality."""
        # Test that all class types have playlists
        for class_type, _ in SpotifyPlaylist.CLASS_TYPE_CHOICES:
            playlist = SpotifyPlaylist.get_playlist_for_class(class_type)
            self.assertIsNotNone(playlist, f"No playlist found for {class_type}")
        
        # Test that all playlists are active
        active_playlists = SpotifyPlaylist.get_active_playlists()
        self.assertEqual(len(active_playlists), 6)
        
        # Test playlist ordering
        for i, playlist in enumerate(active_playlists):
            self.assertEqual(playlist.order, i)
    
    def test_playlist_url_generation(self):
        """Test URL generation for all playlists."""
        for playlist in self.class_playlists:
            # Test embed URL
            embed_url = playlist.get_embed_url()
            self.assertIsNotNone(embed_url)
            self.assertIn('spotify.com/embed', embed_url)
            self.assertIn(playlist.spotify_playlist_id, embed_url)
            
            # Test compact embed URL
            compact_url = playlist.get_compact_embed_url()
            self.assertIsNotNone(compact_url)
            self.assertIn('theme=0', compact_url)
            self.assertIn('view=compact', compact_url)
            
            # Test playlist URL
            playlist_url = playlist.get_playlist_url()
            self.assertIsNotNone(playlist_url)
            self.assertIn('spotify.com/playlist', playlist_url)
            self.assertIn(playlist.spotify_playlist_id, playlist_url)
    
    def test_playlist_duration_formatting(self):
        """Test duration formatting for all playlists."""
        duration_tests = [
            (35, "35 min"),    # warm_up
            (30, "30 min"),    # cool_down
            (70, "1h 10m"),    # pasos_basicos
            (85, "1h 25m"),    # casino_royale
            (95, "1h 35m"),    # choreo_team
            (120, "2h 0m")     # general
        ]
        
        for duration, expected in duration_tests:
            playlist = next(p for p in self.class_playlists if p.duration_minutes == duration)
            self.assertEqual(playlist.format_duration(), expected)
    
    def test_view_integration_with_full_playlist_set(self):
        """Test view integration with complete playlist set."""
        # Test home view
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        playlists = response.context.get('spotify_playlists', [])
        self.assertGreaterEqual(len(playlists), 6)
        
        # Test resources view
        response = self.client.get('/resources/')
        self.assertEqual(response.status_code, 200)
        
        main_playlists = response.context.get('main_class_playlists', [])
        practice_playlists = response.context.get('practice_playlists', [])
        
        # Should have 3 main class playlists
        self.assertEqual(len(main_playlists), 3)
        main_types = [p.class_type for p in main_playlists]
        self.assertIn('choreo_team', main_types)
        self.assertIn('pasos_basicos', main_types)
        self.assertIn('casino_royale', main_types)
        
        # Should have 3 practice playlists
        self.assertEqual(len(practice_playlists), 3)
        practice_types = [p.class_type for p in practice_playlists]
        self.assertIn('general', practice_types)
        self.assertIn('warm_up', practice_types)
        self.assertIn('cool_down', practice_types)
    
    def test_playlist_performance_with_many_playlists(self):
        """Test performance when dealing with many playlists."""
        # Create additional playlists (simulating a large collection)
        for i in range(50):
            SpotifyPlaylist.objects.create(
                class_type='general',
                title=f'Performance Test Playlist {i}',
                description='Performance testing',
                spotify_playlist_id=f'perf_test_{i}',
                is_active=(i % 3 != 0),  # Most are active
                order=100 + i
            )
        
        # Test that queries remain efficient
        with self.assertNumQueries(1):
            list(SpotifyPlaylist.get_active_playlists())
        
        with self.assertNumQueries(1):
            SpotifyPlaylist.get_playlist_for_class('choreo_team')
        
        # Test view performance
        cache.clear()
        with self.assertNumQueries(3):  # Should remain efficient
            response = self.client.get('/resources/')
            self.assertEqual(response.status_code, 200)