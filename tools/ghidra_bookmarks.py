#!/usr/bin/env python3
"""
Drobo 5D3 Ghidra Bookmarks Script
=================================

Ghidra Python script that creates bookmarks at key firmware locations
for easier analysis and navigation.

Usage in Ghidra:
1. Open secondary.elf in Ghidra
2. Run this script via Window > Script Manager
3. Or copy the create_bookmarks() function into Ghidra's Python console

Note: This script uses Ghidra's Python API when run within Ghidra.
When run standalone, it prints the bookmark locations for reference.
"""

import sys
import os

# Add tools directory to path for offsets import
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

try:
    from offsets import DroboOffsets
except ImportError:
    print("Error: Could not import offsets module")
    print("Make sure this script is in the same directory as offsets.py")
    sys.exit(1)

def create_bookmarks():
    """Create bookmarks at key locations in Ghidra"""
    
    bookmarks = [
        # Configuration Block
        (DroboOffsets.CONFIG.PROTECTION_MODE, "Config", "Protection Mode Setting"),
        (DroboOffsets.CONFIG.LARGE_PACK_MODE, "Config", "Large Pack Mode Flag"),
        (DroboOffsets.CONFIG.MANAGE_CAPACITY_LEDS, "Config", "LED Management Setting"),
        (DroboOffsets.CONFIG.SHOW_CAPACITY_HOST_VIEW, "Config", "Host Capacity View Setting"),
        (DroboOffsets.CONFIG.LAST_UI_CALL_TIME, "Config", "Last UI Call Timestamp"),
        
        # Capacity Limits
        (DroboOffsets.CAPACITY_LIMITS.BYTES_BASED, "Limits", "2TB Bytes Limit (Patchable)"),
        (DroboOffsets.CAPACITY_LIMITS.SECTORS_BASED, "Limits", "2TB Sectors Limit (Patchable)"),
        
        # String References
        (DroboOffsets.STRINGS.ZMDT_TRACKER, "Strings", "Zone Metadata Tracker String"),
        (DroboOffsets.STRINGS.SELF_MIRRORED_ZONES, "Strings", "Self-Mirrored Zones String"),
        (DroboOffsets.STRINGS.ZONE_MANAGER, "Strings", "Zone Manager String"),
        (DroboOffsets.STRINGS.DISK_PACK_MANAGER, "Strings", "Disk Pack Manager String"),
        (DroboOffsets.STRINGS.REGION_SIZE, "Strings", "Region Size String"),
        (DroboOffsets.STRINGS.SELF_MIRROR_USAGE, "Strings", "Self Mirror Usage String"),
        (DroboOffsets.STRINGS.PROTECTION_MODE_LABEL, "Strings", "Protection Mode Label String"),
    ]
    
    # Check if running in Ghidra environment
    try:
        # Ghidra-specific imports and functions
        from ghidra.program.model.address import AddressFactory
        from ghidra.app.services import BookmarkService
        
        # Get current program and address factory
        program = getCurrentProgram()
        if program is None:
            print("Error: No program loaded in Ghidra")
            return False
        
        address_factory = program.getAddressFactory()
        default_space = address_factory.getDefaultAddressSpace()
        
        bookmark_count = 0
        
        for offset, category, description in bookmarks:
            try:
                # Create address object
                addr = default_space.getAddress(offset)
                
                # Create bookmark
                createBookmark(addr, category, description)
                bookmark_count += 1
                
                print(f"✓ Created bookmark: {description} at 0x{offset:08x}")
                
            except Exception as e:
                print(f"✗ Failed to create bookmark at 0x{offset:08x}: {e}")
        
        print(f"\\nCreated {bookmark_count} bookmarks successfully")
        return True
        
    except ImportError:
        # Not running in Ghidra - print bookmark information for reference
        print("Drobo 5D3 Firmware Analysis Bookmarks")
        print("=" * 50)
        print("Copy this information for manual bookmark creation in Ghidra:")
        print()
        
        current_category = ""
        for offset, category, description in bookmarks:
            if category != current_category:
                print(f"\\n{category} Bookmarks:")
                print("-" * 20)
                current_category = category
            
            print(f"  0x{offset:08x} - {description}")
        
        print(f"\\nTotal bookmarks: {len(bookmarks)}")
        print("\\nTo use in Ghidra:")
        print("1. Open secondary.elf in Ghidra")
        print("2. Go to each address and create a bookmark")
        print("3. Or run this script from Ghidra's Script Manager")
        
        return False

def print_ghidra_script():
    """Print the Ghidra script code for copy-paste"""
    
    print("\\nGhidra Script Code (copy-paste into Ghidra Python console):")
    print("=" * 60)
    print("""
# Drobo 5D3 Bookmarks Script for Ghidra
from ghidra.program.model.address import AddressFactory

# Bookmark definitions
bookmarks = [""")
    
    bookmarks = [
        (DroboOffsets.CONFIG.PROTECTION_MODE, "Config", "Protection Mode Setting"),
        (DroboOffsets.CONFIG.LARGE_PACK_MODE, "Config", "Large Pack Mode Flag"),
        (DroboOffsets.CAPACITY_LIMITS.BYTES_BASED, "Limits", "2TB Bytes Limit (Patchable)"),
        (DroboOffsets.CAPACITY_LIMITS.SECTORS_BASED, "Limits", "2TB Sectors Limit (Patchable)"),
        (DroboOffsets.STRINGS.PROTECTION_MODE_LABEL, "Strings", "Protection Mode Label String"),
    ]
    
    for offset, category, description in bookmarks:
        print(f'    (0x{offset:08x}, "{category}", "{description}"),')
    
    print("""]

# Create bookmarks
program = getCurrentProgram()
address_factory = program.getAddressFactory()
default_space = address_factory.getDefaultAddressSpace()

for offset, category, description in bookmarks:
    addr = default_space.getAddress(offset)
    createBookmark(addr, category, description)
    print("Created bookmark: " + description + " at " + hex(offset))

print("Drobo bookmarks created successfully!")
""")

def main():
    print("Drobo 5D3 Ghidra Bookmarks Generator")
    print("=" * 40)
    
    success = create_bookmarks()
    
    if not success:
        print_ghidra_script()

if __name__ == "__main__":
    main()