#!/usr/bin/env python3
"""
Auto-cleanup script for temp files and caches.
Returns JSON with what was cleaned and space freed.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def get_size(path):
    """Get size of directory in bytes."""
    total = 0
    try:
        if path.is_file():
            return path.stat().st_size
        for entry in path.rglob("*"):
            if entry.is_file():
                try:
                    total += entry.stat().st_size
                except:
                    pass
    except:
        pass
    return total

def human_size(bytes_val):
    """Convert bytes to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"

def clean_directory(path, dry_run=False):
    """Clean a directory, return bytes freed."""
    path = Path(path).expanduser()
    if not path.exists():
        return 0, []
    
    freed = 0
    items = []
    
    try:
        for item in path.iterdir():
            try:
                size = get_size(item)
                if not dry_run:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                freed += size
                items.append(item.name)
            except Exception as e:
                pass
    except:
        pass
    
    return freed, items[:10]  # Limit items reported

def empty_trash(dry_run=False):
    """Empty user trash."""
    trash = Path.home() / ".Trash"
    return clean_directory(trash, dry_run)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show what would be cleaned without doing it")
    parser.add_argument("--include-xcode", action="store_true", help="Also clean Xcode derived data")
    args = parser.parse_args()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": args.dry_run,
        "cleaned": [],
        "total_freed_bytes": 0,
        "total_freed_human": ""
    }
    
    # Paths to clean (NOT Downloads, NOT Trash - per user preference)
    paths = [
        ("System Temp", "/tmp"),
        ("Var Temp", "/private/var/tmp"),
        ("User Caches", "~/Library/Caches"),
        ("Log Files", "~/Library/Logs"),
    ]
    
    if args.include_xcode:
        paths.append(("Xcode DerivedData", "~/Library/Developer/Xcode/DerivedData"))
    
    for name, path in paths:
        freed, items = clean_directory(path, args.dry_run)
        if freed > 0:
            results["cleaned"].append({
                "name": name,
                "path": path,
                "freed_bytes": freed,
                "freed_human": human_size(freed),
                "sample_items": items
            })
            results["total_freed_bytes"] += freed
    
    results["total_freed_human"] = human_size(results["total_freed_bytes"])
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
