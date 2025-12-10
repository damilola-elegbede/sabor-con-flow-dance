# Video Files

## hero-loop.mp4
This is a placeholder for the hero section background video.

### Recommended specifications for optimal performance:
- **Format**: MP4 (H.264 codec)
- **Resolution**: 1920x1080 (Full HD) or 1280x720 (HD)
- **Bitrate**: 2-5 Mbps for web
- **Duration**: 10-30 seconds (looping)
- **File size**: < 10MB for fast loading
- **Frame rate**: 24-30 fps

### Optimization tips:
1. Use HandBrake or FFmpeg to compress the video
2. Consider creating multiple versions for different screen sizes
3. Remove audio track if not needed
4. Use poster image for first frame

### Example FFmpeg command for optimization:
```bash
ffmpeg -i input.mp4 -c:v libx264 -preset slow -crf 22 -vf "scale=1280:720" -an hero-loop.mp4
```

For now, the site will fallback to the logo image.