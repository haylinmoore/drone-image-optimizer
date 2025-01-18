#!/usr/bin/env python3
import os
import hashlib
import shutil
import subprocess
import json
from pathlib import Path
from typing import Dict, Set

class ImageOptimizer:
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'failures': 0
        }
        self.optimize_commands = {
            '.png': ['ect', '-9', '--mt-deflate', '{input}'],
            '.jpg': ['ect', '-9', '--mt-deflate', '{input}'],
            '.jpeg': ['ect', '-9', '--mt-deflate', '{input}'],
            '.webp': ['cwebp', '-lossless', '-q', '100', '{input}', '-o', '{output}'],
            '.gif': ['gifsicle', '-O3', '-o', '{output}', '{input}']
        }
        # SUPPORTED_EXTENSIONS is now derived from optimize_commands
        self.SUPPORTED_EXTENSIONS = set(self.optimize_commands.keys())

    def get_command_hash(self, extension: str) -> str:
        """Calculate hash of optimization command for a file type."""
        command = self.optimize_commands.get(extension.lower(), [])
        command_str = json.dumps(command, sort_keys=True)
        return hashlib.sha256(command_str.encode()).hexdigest()[:8]

    def get_file_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def get_combined_hash(self, file_hash: str, extension: str) -> str:
        """Combine file hash with command hash."""
        command_hash = self.get_command_hash(extension)
        combined = f"{file_hash}_{command_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def get_cached_path(self, file_hash: str, extension: str) -> Path:
        """Get the path where an optimized file should be cached."""
        combined_hash = self.get_combined_hash(file_hash, extension)
        return self.cache_dir / f"{combined_hash}{extension.lower()}"

    def optimize_image(self, input_path: Path) -> None:
        """Optimize a single image file."""
        if input_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return

        file_hash = self.get_file_hash(input_path)
        cached_path = self.get_cached_path(file_hash, input_path.suffix)

        if cached_path.exists():
            print(f"Cache hit: {input_path} -> {cached_path}")
            shutil.copy2(cached_path, input_path)
            self.stats['cache_hits'] += 1
            return

        print(f"Cache miss: Optimizing {input_path}")
        self.stats['cache_misses'] += 1
        command = self.optimize_commands.get(input_path.suffix.lower())
        if not command:
            return

        temp_output = self.cache_dir / f"temp_{file_hash}{input_path.suffix}"

        try:
            shutil.copy2(input_path, temp_output)

            if input_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                formatted_command = [
                    arg.format(input=str(temp_output))
                    for arg in command
                ]
                subprocess.run(formatted_command, check=True)
                temp_output.rename(cached_path)
            else:
                formatted_command = [
                    arg.format(input=str(input_path), output=str(temp_output))
                    for arg in command
                ]
                subprocess.run(formatted_command, check=True)
                temp_output.rename(cached_path)

            shutil.copy2(cached_path, input_path)

        except subprocess.CalledProcessError as e:
            print(f"Failed to optimize {input_path}: {e}")
            self.stats['failures'] += 1
            if temp_output.exists():
                temp_output.unlink()

    def process_directory(self, directory: Path) -> None:
        """Process all supported image files in a directory recursively."""
        for filepath in directory.rglob("*"):
            if filepath.is_file() and filepath.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                self.optimize_image(filepath)

    def print_stats(self):
        """Print optimization statistics."""
        total = self.stats['cache_hits'] + self.stats['cache_misses']
        if total > 0:
            hit_rate = (self.stats['cache_hits'] / total) * 100
        else:
            hit_rate = 0

        print("\nOptimization Statistics:")
        print(f"Total images processed: {total}")
        print(f"Cache hits: {self.stats['cache_hits']}")
        print(f"Cache misses: {self.stats['cache_misses']}")
        print(f"Failures: {self.stats['failures']}")
        print(f"Cache hit rate: {hit_rate:.1f}%")

def main():
    cache_dir = os.environ.get('PLUGIN_CACHE_DIR', '/cache')
    source_dir = os.environ.get('PLUGIN_SOURCE_DIR', '/drone/src')

    print(f"Using cache directory: {cache_dir}")
    print(f"Processing source directory: {source_dir}")

    optimizer = ImageOptimizer(cache_dir)
    optimizer.process_directory(Path(source_dir))
    optimizer.print_stats()

if __name__ == "__main__":
    main()
