#!/usr/bin/env python3
"""
🧹 PROXY-CHAIN DIRECTORY CLEANUP & ORGANIZATION TOOL
Organizes files, removes duplicates, and creates a clean project structure
"""

import os
import shutil
import json
from pathlib import Path
import glob

def cleanup_project_directory():
    """Clean up and organize the proxy-chain project directory"""
    
    print("🧹 Starting Pr0Xy-chaIN Directory Cleanup & Organization...")
    print("=" * 60)
    
    # Get current directory
    project_root = Path.cwd()
    
    # Create organized directory structure
    directories_to_create = [
        "logs",
        "reports", 
        "backup",
        "archive"
    ]
    
    print("📁 Creating organized directory structure...")
    for directory in directories_to_create:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)
        print(f"   ✅ Created: {directory}/")
    
    # Move log files to logs directory
    print("\n📄 Moving log files...")
    log_files = list(project_root.glob("*.log")) + list(project_root.glob("*.txt"))
    for log_file in log_files:
        if log_file.name not in ["README.txt", "requirements.txt"]:
            destination = project_root / "logs" / log_file.name
            try:
                shutil.move(str(log_file), str(destination))
                print(f"   📋 Moved: {log_file.name} → logs/")
            except Exception as e:
                print(f"   ❌ Failed to move {log_file.name}: {e}")
    
    # Move JSON reports to reports directory
    print("\n📊 Moving report files...")
    report_files = list(project_root.glob("test_report_*.json")) + \
                   list(project_root.glob("*_report_*.json")) + \
                   list(project_root.glob("benchmark_*.json"))
    
    for report_file in report_files:
        destination = project_root / "reports" / report_file.name
        try:
            shutil.move(str(report_file), str(destination))
            print(f"   📊 Moved: {report_file.name} → reports/")
        except Exception as e:
            print(f"   ❌ Failed to move {report_file.name}: {e}")
    
    # Archive old/backup files
    print("\n🗃️ Archiving backup files...")
    backup_patterns = ["*.bak", "*backup*", "*old*", "*.tmp"]
    for pattern in backup_patterns:
        files = list(project_root.glob(pattern))
        for file in files:
            if file.is_file():
                destination = project_root / "archive" / file.name
                try:
                    shutil.move(str(file), str(destination))
                    print(f"   🗃️ Archived: {file.name} → archive/")
                except Exception as e:
                    print(f"   ❌ Failed to archive {file.name}: {e}")
    
    # Remove duplicate proxy config files (keep only the main one)
    print("\n🔄 Removing duplicate configuration files...")
    proxy_configs = list(project_root.glob("proxy_config*.json"))
    main_config = project_root / "proxy_config.json"
    
    for config in proxy_configs:
        if config != main_config and config.exists():
            try:
                backup_dest = project_root / "backup" / config.name
                shutil.move(str(config), str(backup_dest))
                print(f"   🔄 Backup duplicate: {config.name} → backup/")
            except Exception as e:
                print(f"   ❌ Failed to backup {config.name}: {e}")
    
    # Clean up __pycache__ directories
    print("\n🧹 Cleaning Python cache files...")
    pycache_dirs = list(project_root.glob("**/__pycache__"))
    for cache_dir in pycache_dirs:
        try:
            shutil.rmtree(cache_dir)
            print(f"   🗑️ Removed: {cache_dir}")
        except Exception as e:
            print(f"   ❌ Failed to remove {cache_dir}: {e}")
    
    # Remove .pyc files
    pyc_files = list(project_root.glob("**/*.pyc"))
    for pyc_file in pyc_files:
        try:
            pyc_file.unlink()
            print(f"   🗑️ Removed: {pyc_file}")
        except Exception as e:
            print(f"   ❌ Failed to remove {pyc_file}: {e}")
    
    # Organize core project files
    print("\n📋 Core project files structure:")
    core_files = [
        "proxy_chain_setup.py",
        "proxy_scanner.py", 
        "proxy_status.py",
        "proxy_config.json",
        "README.md",
        "requirements.txt"
    ]
    
    for core_file in core_files:
        file_path = project_root / core_file
        if file_path.exists():
            print(f"   ✅ Core file: {core_file}")
        else:
            print(f"   ❌ Missing: {core_file}")
    
    # Create directory summary
    print("\n📁 Final Directory Structure:")
    print("   📂 Pr0Xy-chaIN/")
    print("   ├── 📄 Core Python files")
    print("   ├── 📁 scripts/       # Enhanced proxy scripts")
    print("   ├── 📁 tests/         # Test suites")
    print("   ├── 📁 benchmarks/    # Performance benchmarks")
    print("   ├── 📁 docs/          # Documentation")
    print("   ├── 📁 logs/          # Log files")
    print("   ├── 📁 reports/       # Test and benchmark reports")
    print("   ├── 📁 backup/        # Backup files")
    print("   └── 📁 archive/       # Archived old files")
    
    # Count working proxies
    config_file = project_root / "proxy_config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                working_proxies = len(config.get('working_proxies', []))
                print(f"\n🔗 Current working proxies: {working_proxies}")
        except Exception as e:
            print(f"\n❌ Could not read proxy config: {e}")
    
    print("\n✅ Directory cleanup and organization complete!")
    print("🎯 Your Pr0Xy-chaIN project is now organized and optimized!")

if __name__ == "__main__":
    cleanup_project_directory()
