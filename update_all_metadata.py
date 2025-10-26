#!/usr/bin/env python3
"""
Bulk update script to enrich all existing metadata files with screenshot URLs.

This script scans all data directories and adds screenshot URLs from JSON files 
to their corresponding metadata files.
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from services.data_enrichment_service import create_data_enrichment_service


def find_all_data_directories() -> List[Tuple[str, str, Path]]:
    """
    Find all data directories and extract subject/year information.
    
    Returns:
        List of tuples (subject, year, directory_path)
    """
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ Data directory not found!")
        return []
    
    directories = []
    for item in data_dir.iterdir():
        if item.is_dir() and "_" in item.name:
            # Parse subject_year format
            parts = item.name.split("_")
            if len(parts) >= 2:
                subject = "_".join(parts[:-1])  # Handle subjects with hyphens
                year = parts[-1]
                directories.append((subject, year, item))
    
    return sorted(directories)


def extract_screenshot_url_from_json(json_path: Path) -> str:
    """Extract screenshot URL from JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('page_screenshot', '')
    except Exception as e:
        print(f"   ❌ Error reading JSON file: {e}")
        return ''


def check_metadata_has_screenshot(metadata_path: Path) -> Tuple[bool, str]:
    """
    Check if metadata file already has a screenshot URL.
    
    Returns:
        Tuple of (has_screenshot, existing_url)
    """
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        existing_url = metadata.get('spider_stats', {}).get('page_screenshot', '')
        return bool(existing_url), existing_url
    except Exception as e:
        print(f"   ❌ Error reading metadata file: {e}")
        return False, ''


def update_all_metadata():
    """Update all metadata files with screenshot URLs from JSON files."""
    print("🚀 Bulk updating all metadata files with screenshot URLs...\n")
    
    # Find all data directories
    directories = find_all_data_directories()
    if not directories:
        print("❌ No data directories found!")
        return False
    
    print(f"📁 Found {len(directories)} data directories")
    
    # Initialize counters
    total_processed = 0
    successful_updates = 0
    already_updated = 0
    skipped = 0
    
    # Create enrichment service
    enrichment_service = create_data_enrichment_service()
    
    # Process each directory
    for subject, year, dir_path in directories:
        print(f"\n📚 Processing {subject.title()} {year}...")
        total_processed += 1
        
        # Define file paths
        json_path = dir_path / f"{subject}_{year}.json"
        metadata_path = dir_path / f"{subject}_{year}_metadata.json"
        
        # Check if files exist
        if not json_path.exists():
            print(f"   ⚠️  JSON file not found: {json_path.name}")
            skipped += 1
            continue
        
        if not metadata_path.exists():
            print(f"   ⚠️  Metadata file not found: {metadata_path.name}")
            skipped += 1
            continue
        
        # Extract screenshot URL from JSON
        screenshot_url = extract_screenshot_url_from_json(json_path)
        if not screenshot_url:
            print(f"   ⚠️  No screenshot URL found in JSON file")
            skipped += 1
            continue
        
        # Check if metadata already has screenshot URL
        has_screenshot, existing_url = check_metadata_has_screenshot(metadata_path)
        if has_screenshot:
            if existing_url == screenshot_url:
                print(f"   ✅ Already up to date")
                already_updated += 1
                continue
            else:
                print(f"   🔄 Updating existing URL")
        else:
            print(f"   📝 Adding new screenshot URL")
        
        # Update metadata
        success = enrichment_service.enrich_metadata_file(
            metadata_path=str(metadata_path),
            screenshot_url=screenshot_url,
            field_name="page_screenshot"
        )
        
        if success:
            print(f"   ✅ Successfully updated metadata")
            successful_updates += 1
        else:
            print(f"   ❌ Failed to update metadata")
    
    # Print summary
    print("\n" + "="*70)
    print("📊 BULK UPDATE SUMMARY")
    print("="*70)
    print(f"Total directories processed: {total_processed}")
    print(f"Successfully updated: {successful_updates}")
    print(f"Already up to date: {already_updated}")
    print(f"Skipped (missing files/URLs): {skipped}")
    print(f"Failed updates: {total_processed - successful_updates - already_updated - skipped}")
    
    success_rate = ((successful_updates + already_updated) / total_processed * 100) if total_processed > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if successful_updates > 0:
        print(f"\n🎉 Successfully updated {successful_updates} metadata files!")
    
    if already_updated > 0:
        print(f"ℹ️  {already_updated} files were already up to date")
    
    if skipped > 0:
        print(f"⚠️  {skipped} files were skipped (missing JSON files or screenshot URLs)")
    
    return (successful_updates + already_updated) == total_processed


def preview_updates():
    """Preview what updates would be made without actually updating files."""
    print("🔍 PREVIEW MODE: Scanning for metadata files that need updates...\n")
    
    directories = find_all_data_directories()
    if not directories:
        print("❌ No data directories found!")
        return
    
    print(f"📁 Found {len(directories)} data directories\n")
    
    needs_update = []
    already_updated = []
    missing_files = []
    no_screenshot_url = []
    
    for subject, year, dir_path in directories:
        json_path = dir_path / f"{subject}_{year}.json"
        metadata_path = dir_path / f"{subject}_{year}_metadata.json"
        
        # Check file existence
        if not json_path.exists() or not metadata_path.exists():
            missing_files.append((subject, year))
            continue
        
        # Check for screenshot URL in JSON
        screenshot_url = extract_screenshot_url_from_json(json_path)
        if not screenshot_url:
            no_screenshot_url.append((subject, year))
            continue
        
        # Check metadata status
        has_screenshot, existing_url = check_metadata_has_screenshot(metadata_path)
        if has_screenshot and existing_url == screenshot_url:
            already_updated.append((subject, year))
        else:
            needs_update.append((subject, year, screenshot_url))
    
    # Print preview results
    print("📋 PREVIEW RESULTS:")
    print("="*50)
    
    if needs_update:
        print(f"\n✏️  Files that WILL BE UPDATED ({len(needs_update)}):")
        for subject, year, url in needs_update:
            print(f"   • {subject.title()} {year}")
    
    if already_updated:
        print(f"\n✅ Files already up to date ({len(already_updated)}):")
        for subject, year in already_updated:
            print(f"   • {subject.title()} {year}")
    
    if no_screenshot_url:
        print(f"\n⚠️  Files with no screenshot URL in JSON ({len(no_screenshot_url)}):")
        for subject, year in no_screenshot_url:
            print(f"   • {subject.title()} {year}")
    
    if missing_files:
        print(f"\n❌ Files with missing JSON/metadata ({len(missing_files)}):")
        for subject, year in missing_files:
            print(f"   • {subject.title()} {year}")
    
    print(f"\n📊 Summary:")
    print(f"   Will update: {len(needs_update)}")
    print(f"   Already updated: {len(already_updated)}")
    print(f"   No screenshot URL: {len(no_screenshot_url)}")
    print(f"   Missing files: {len(missing_files)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Bulk update metadata files with screenshot URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python update_all_metadata.py --preview    # Preview what will be updated
  python update_all_metadata.py --update     # Actually update the files
        """
    )
    
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview what updates would be made without changing files"
    )
    
    parser.add_argument(
        "--update",
        action="store_true",
        help="Actually update the metadata files"
    )
    
    args = parser.parse_args()
    
    if args.preview:
        preview_updates()
    elif args.update:
        success = update_all_metadata()
        sys.exit(0 if success else 1)
    else:
        print("❌ Please specify either --preview or --update")
        print("Use --help for more information")
        sys.exit(1)