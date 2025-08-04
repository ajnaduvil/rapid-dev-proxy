#!/usr/bin/env python3
"""Build script for Rapid Dev Proxy executable."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_dirs():
    """Clean build and dist directories."""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name} directory...")
            shutil.rmtree(dir_name)


def build_executable():
    """Build the executable using PyInstaller."""
    print("Building Rapid Dev Proxy executable...")
    
    # Run PyInstaller with the spec file
    result = subprocess.run([
        "uv", "run", "python", "-m", "PyInstaller", "rapid_dev_proxy.spec",
        "--clean", "--noconfirm"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error building executable:")
        print(result.stderr)
        return False
    
    print("Build completed successfully!")
    return True


def verify_executable():
    """Verify the executable was created."""
    exe_path = Path("dist/rapid-dev-proxy.exe")
    if exe_path.exists():
        print(f"✓ Executable created: {exe_path}")
        print(f"  Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")
        return True
    else:
        print("✗ Executable not found!")
        return False


def main():
    """Main build function."""
    print("Rapid Dev Proxy - Build Script")
    print("=" * 40)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build executable
    if build_executable():
        # Verify the build
        if verify_executable():
            print("\n🎉 Build completed successfully!")
            print("\nYou can now run the proxy with:")
            print("  dist/rapid-dev-proxy.exe --help")
            print("  dist/rapid-dev-proxy.exe init")
            print("  dist/rapid-dev-proxy.exe start -c config.json")
        else:
            print("\n❌ Build verification failed!")
            sys.exit(1)
    else:
        print("\n❌ Build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 