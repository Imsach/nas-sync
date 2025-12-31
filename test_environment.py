#!/usr/bin/env python3
"""
NAS Auto Sync - Environment Test Script
Run this to verify your system is ready to run the application
"""

import sys
import platform

def test_python_version():
    """Check Python version"""
    print("=" * 60)
    print("Testing Python Version...")
    print("=" * 60)

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print(f"✓ Python {version_str} detected")
    print(f"  Platform: {platform.system()} {platform.release()}")
    print(f"  Architecture: {platform.machine()}")

    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("✗ ERROR: Python 3.7 or higher is required")
        print(f"  You have: Python {version_str}")
        return False

    print("✓ Python version is compatible")
    return True

def test_tkinter():
    """Check if tkinter is available"""
    print("\n" + "=" * 60)
    print("Testing Tkinter (GUI Library)...")
    print("=" * 60)

    try:
        import tkinter as tk
        print("✓ tkinter is installed and available")

        # Try to get tkinter version
        try:
            root = tk.Tk()
            tk_version = root.tk.call('info', 'patchlevel')
            root.destroy()
            print(f"  Version: Tk {tk_version}")
        except:
            pass

        return True
    except ImportError:
        print("✗ ERROR: tkinter is not installed")
        print("\nInstallation instructions:")

        if platform.system() == "Linux":
            print("  Ubuntu/Debian: sudo apt-get install python3-tk")
            print("  Fedora: sudo dnf install python3-tkinter")
            print("  Arch: sudo pacman -S tk")
        elif platform.system() == "Windows":
            print("  Reinstall Python and make sure 'tcl/tk and IDLE' is selected")
        elif platform.system() == "Darwin":
            print("  tkinter should be included with Python on macOS")
            print("  If missing, reinstall Python from python.org")

        return False

def test_required_modules():
    """Check if all required standard library modules are available"""
    print("\n" + "=" * 60)
    print("Testing Required Modules...")
    print("=" * 60)

    modules = [
        'os',
        'sys',
        'pathlib',
        'shutil',
        'hashlib',
        'json',
        'fnmatch',
        'threading',
        'time',
        'datetime'
    ]

    all_ok = True

    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} - NOT FOUND")
            all_ok = False

    if all_ok:
        print("\n✓ All required modules are available")
    else:
        print("\n✗ Some modules are missing (this is unusual for standard Python)")

    return all_ok

def test_file_system():
    """Test basic file system operations"""
    print("\n" + "=" * 60)
    print("Testing File System Access...")
    print("=" * 60)

    import tempfile
    import os

    try:
        # Test write access
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            test_file = f.name
            f.write("test")

        # Test read access
        with open(test_file, 'r') as f:
            content = f.read()

        # Cleanup
        os.unlink(test_file)

        print("✓ File system read/write operations work correctly")
        return True

    except Exception as e:
        print(f"✗ File system test failed: {e}")
        return False

def test_home_directory():
    """Test access to home directory for config storage"""
    print("\n" + "=" * 60)
    print("Testing Configuration Directory...")
    print("=" * 60)

    from pathlib import Path

    try:
        home = Path.home()
        config_dir = home / '.nassync'

        print(f"✓ Home directory: {home}")
        print(f"  Config will be stored in: {config_dir}")

        # Test if we can create the config directory
        config_dir.mkdir(exist_ok=True)

        if config_dir.exists():
            print("✓ Configuration directory is accessible")
            return True
        else:
            print("✗ Could not create configuration directory")
            return False

    except Exception as e:
        print(f"✗ Error accessing home directory: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "NAS AUTO SYNC - ENVIRONMENT TEST" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    results = []

    # Run tests
    results.append(("Python Version", test_python_version()))
    results.append(("Tkinter", test_tkinter()))
    results.append(("Required Modules", test_required_modules()))
    results.append(("File System", test_file_system()))
    results.append(("Config Directory", test_home_directory()))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = all(result[1] for result in results)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:10} {test_name}")

    print("=" * 60)

    if all_passed:
        print("\n🎉 SUCCESS! Your system is ready to run NAS Auto Sync Manager")
        print("\nTo start the application, run:")
        print("  python nas_sync_app.py")
        print("\nOr use the launcher scripts:")
        print("  Windows: run_nassync.bat")
        print("  Linux/Mac: ./run_nassync.sh")
    else:
        print("\n⚠ WARNING! Some tests failed.")
        print("Please fix the issues above before running the application.")
        print("\nFor help, see README_NAS_SYNC.md")

    print()

    return 0 if all_passed else 1

if __name__ == "__main__":
    try:
        exit_code = main()

        # Keep window open on Windows if double-clicked
        if platform.system() == "Windows":
            input("\nPress Enter to exit...")

        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")

        if platform.system() == "Windows":
            input("\nPress Enter to exit...")

        sys.exit(1)
