#!/usr/bin/env python3
import shutil
import tempfile
from pathlib import Path
from optimize import ImageOptimizer

def run_tests():
    """Run the optimization tests."""
    test_dir = Path("/test/")
    cache_dir = Path("/cache/")
    test_images_dir = Path("/test_images/")

    print(f"Test directory: {test_dir}")
    print(f"Cache directory: {cache_dir}")

    # Reset test directory
    for image in test_images_dir.glob("*"):
        if image.is_file():
            shutil.copy2(image, test_dir)

    # First pass
    print("\nRunning first pass...")
    optimizer = ImageOptimizer(str(cache_dir))
    optimizer.process_directory(test_dir)

    # Verify first pass stats
    assert optimizer.stats['cache_misses'] > 0, "Expected cache misses in first pass"
    assert optimizer.stats['cache_hits'] == 0, "Unexpected cache hits in first pass"
    first_pass_misses = optimizer.stats['cache_misses']

    # Reset test directory
    for image in test_images_dir.glob("*"):
        if image.is_file():
            shutil.copy2(image, test_dir)

    # Second pass
    print("\nRunning second pass...")
    optimizer = ImageOptimizer(str(cache_dir))
    optimizer.process_directory(test_dir)

    # Verify second pass stats
    assert optimizer.stats['cache_hits'] == first_pass_misses, "Expected all cache hits in second pass"
    assert optimizer.stats['cache_misses'] == 0, "Unexpected cache misses in second pass"

    print("\nAll tests passed successfully!")
    return True

if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        print(f"Test failed: {e}")
        exit(1)
