# Drone Image Optimizer

A Drone CI plugin that optimizes images in your repository using various optimization tools while maintaining a cache to prevent re-optimization of unchanged images.

## Features

- Supports PNG, JPG, JPEG, WebP, and GIF formats
- Caches optimized images allowing for long first-time builds for heavy optimization and speeding up future builds
- Provides optimization statistics
- Uses high-quality optimization tools:
  - ECT (Efficient Compression Tool) for PNG/JPG/JPEG
  - cwebp for WebP
  - gifsicle for GIF

## Usage

Add this step to your Drone pipeline:

```yaml
steps:
  - name: optimize-images
    image: haylinmoore/drone-image-optimizer:latest
    settings:
      cache_dir: /drone/src/.image-cache
      source_dir: /drone/src/assets
```

### Important Note About Caching

The cache directory is not persistent between pipeline runs by default. To maintain the cache between runs, you need to set that up in your pipeline.

For example using a volume cache plugin like `drillster/drone-volume-cache`:
```yaml
steps:
  - name: restore-cache
    image: drillster/drone-volume-cache
    volumes:
      - name: cache:/cache
    settings:
      restore: true
      mount:
        - .image-cache

  - name: optimize-images
    image: haylinmoore/drone-image-optimizer:latest
    settings:
      cache_dir: /drone/src/.image-cache
      source_dir: /drone/src/assets

  - name: rebuild-cache
    image: drillster/drone-volume-cache
    volumes:
      - name: cache:/cache
    settings:
      rebuild: true
      mount:
        - .image-cache

volumes:
  - name: cache
    host:
      path: /tmp/cache
```

## Settings

| Setting | Description | Default |
|---------|-------------|---------|
| cache_dir | Directory to store optimized image cache | `/cache` |
| source_dir | Directory containing images to optimize | `/drone/src` |

## How It Works

1. Recursively finds all supported image files in the source directory
2. For each image:
   - Calculates a hash of the image content and optimization settings
   - Checks if an optimized version exists in cache
   - If cached: uses cached version
   - If not cached: optimizes image and stores in cache
3. Provides statistics about cache hits/misses and optimization failures

## Development

### Testing

```bash
# Add test images to test_images directory
make test
```

### Building

```bash
make build
```
