#!/usr/bin/env python3
"""
Drobo 5D3 Capacity Limit Patcher
================================

Patches 2TB capacity limits in Drobo firmware to specified larger values.
Uses the offsets module for precise memory locations.

Environment Variables:
    DROBO_FIRMWARE_PATH  - Default path to firmware files
    DROBO_EXTRACTED_PATH - Default path to extracted components

Usage:
    python3 capacity_patcher.py <firmware_file> [new_limit_tb]
    
    Default new_limit_tb is 32TB if not specified.

Examples:
    python3 capacity_patcher.py ../extracted/secondary.elf 64
    python3 capacity_patcher.py secondary.elf 64  # Uses DROBO_EXTRACTED_PATH
    DROBO_EXTRACTED_PATH=/path/to/extracted python3 capacity_patcher.py secondary.elf
"""

import sys
import os
import struct
import shutil
from offsets import DroboOffsets

# Default paths - can be overridden by environment variables
DEFAULT_EXTRACTED_PATH = os.environ.get('DROBO_EXTRACTED_PATH', '../extracted')
DEFAULT_FIRMWARE_PATH = os.environ.get('DROBO_FIRMWARE_PATH', '../firmware')

def resolve_firmware_path(filename):
    """Resolve firmware file path using environment variables or defaults"""
    
    # If absolute path or relative path that exists, use as-is
    if os.path.isabs(filename) or os.path.exists(filename):
        return filename
    
    # Try in extracted directory
    extracted_path = os.path.join(DEFAULT_EXTRACTED_PATH, filename)
    if os.path.exists(extracted_path):
        return extracted_path
    
    # Try in firmware directory
    firmware_path = os.path.join(DEFAULT_FIRMWARE_PATH, filename)
    if os.path.exists(firmware_path):
        return firmware_path
    
    # Return original filename (will cause error later if not found)
    return filename

def patch_capacity_limit(filename, new_limit_tb=32):
    """Patch 2TB capacity limits to specified TB value"""
    
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found")
        return False
    
    # Calculate new limits
    new_bytes = new_limit_tb * (1024**4)
    new_sectors = new_bytes // 512
    
    print(f"Patching {filename} to {new_limit_tb}TB limit...")
    print(f"  New bytes limit: {new_bytes:,} (0x{new_bytes:x})")
    print(f"  New sectors limit: {new_sectors:,} (0x{new_sectors:x})")
    
    # Create backup
    backup_file = f"{filename}.backup_capacity_patch"
    try:
        shutil.copy2(filename, backup_file)
        print(f"  ✓ Created backup: {backup_file}")
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
    
    try:
        with open(filename, 'r+b') as f:
            # Patch bytes-based limit
            f.seek(DroboOffsets.CAPACITY_LIMITS.BYTES_BASED)
            original_bytes = struct.unpack('<Q', f.read(8))[0]
            
            f.seek(DroboOffsets.CAPACITY_LIMITS.BYTES_BASED)
            f.write(struct.pack('<Q', new_bytes))
            
            # Patch sectors-based limit  
            f.seek(DroboOffsets.CAPACITY_LIMITS.SECTORS_BASED)
            original_sectors = struct.unpack('<Q', f.read(8))[0]
            
            f.seek(DroboOffsets.CAPACITY_LIMITS.SECTORS_BASED)
            f.write(struct.pack('<Q', new_sectors))
        
        # Verify patches
        with open(filename, 'rb') as f:
            f.seek(DroboOffsets.CAPACITY_LIMITS.BYTES_BASED)
            verify_bytes = struct.unpack('<Q', f.read(8))[0]
            
            f.seek(DroboOffsets.CAPACITY_LIMITS.SECTORS_BASED)
            verify_sectors = struct.unpack('<Q', f.read(8))[0]
        
        print(f"  ✓ Patched bytes limit: {original_bytes:,} → {verify_bytes:,}")
        print(f"  ✓ Patched sectors limit: {original_sectors:,} → {verify_sectors:,}")
        
        if verify_bytes == new_bytes and verify_sectors == new_sectors:
            print(f"✓ Successfully patched capacity limits to {new_limit_tb}TB")
            return True
        else:
            print("✗ Verification failed - patch may not have been applied correctly")
            return False
            
    except Exception as e:
        print(f"Error patching file: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 capacity_patcher.py <firmware_file> [new_limit_tb]")
        print("Examples:")
        print("  python3 capacity_patcher.py ../extracted/secondary.elf 64")
        print("  python3 capacity_patcher.py secondary.elf 64  # Uses DROBO_EXTRACTED_PATH")
        print("  DROBO_EXTRACTED_PATH=/path/to/extracted python3 capacity_patcher.py secondary.elf")
        print()
        print("Environment Variables:")
        print(f"  DROBO_EXTRACTED_PATH: {DEFAULT_EXTRACTED_PATH}")
        print(f"  DROBO_FIRMWARE_PATH:  {DEFAULT_FIRMWARE_PATH}")
        sys.exit(1)
    
    filename = resolve_firmware_path(sys.argv[1])
    new_limit_tb = int(sys.argv[2]) if len(sys.argv) > 2 else 32
    
    if new_limit_tb <= 2:
        print("Error: New limit must be greater than 2TB")
        sys.exit(1)
    
    print(f"Resolved firmware path: {filename}")
    success = patch_capacity_limit(filename, new_limit_tb)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()