# Generated migration for Instagram integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_mediagallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediagallery',
            name='source',
            field=models.CharField(choices=[('local', 'Local Upload'), ('url', 'External URL'), ('instagram', 'Instagram')], default='local', max_length=10),
        ),
        migrations.AddField(
            model_name='mediagallery',
            name='instagram_id',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='mediagallery',
            name='instagram_permalink',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mediagallery',
            name='instagram_username',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='mediagallery',
            name='instagram_timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mediagallery',
            name='category',
            field=models.CharField(choices=[('class', 'Class'), ('performance', 'Performance'), ('social', 'Social Dance'), ('workshop', 'Workshop'), ('event', 'Event'), ('team', 'Team Photos'), ('instagram', 'Instagram Post')], max_length=20),
        ),
    ]