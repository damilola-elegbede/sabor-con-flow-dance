# Generated migration for Spotify Playlists - SPEC_05 Group C Task 8

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_create_contact_booking_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpotifyPlaylist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_type', models.CharField(choices=[('choreo_team', 'SCF Choreo Team'), ('pasos_basicos', 'Pasos Básicos'), ('casino_royale', 'Casino Royale'), ('general', 'General Practice'), ('warm_up', 'Warm Up'), ('cool_down', 'Cool Down')], max_length=20, unique=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('spotify_playlist_id', models.CharField(help_text='Spotify playlist ID (not full URL)', max_length=50)),
                ('spotify_embed_url', models.URLField(help_text='Full Spotify embed URL')),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
                ('theme_color', models.CharField(default='#C7B375', help_text='Hex color code for playlist theme', max_length=7)),
                ('tracks_count', models.IntegerField(default=0, help_text='Number of tracks in playlist')),
                ('duration_minutes', models.IntegerField(default=0, help_text='Total duration in minutes')),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Spotify Playlist',
                'verbose_name_plural': 'Spotify Playlists',
                'ordering': ['order', 'class_type'],
            },
        ),
    ]