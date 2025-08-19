#!/usr/bin/env python3
"""
Drobo 5D3 Firmware Analyzer
===========================

Automated firmware analysis tool that reads configuration settings and
capacity limits from Drobo firmware using the offset tables.

Environment Variables:
    DROBO_FIRMWARE_PATH  - Default path to firmware files
    DROBO_EXTRACTED_PATH - Default path to extracted components

Usage:
    python3 firmware_analyzer.py <firmware_file>
    
Examples:
    python3 firmware_analyzer.py ../extracted/secondary.elf
    python3 firmware_analyzer.py secondary.elf  # Uses DROBO_EXTRACTED_PATH
    DROBO_EXTRACTED_PATH=/path/to/extracted python3 firmware_analyzer.py secondary.elf
"""

import sys
import os
import struct
from offsets import DroboOffsets, bytes_to_tb, sectors_to_tb, ProtectionModes

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

def analyze_firmware(filename):
    """Automated firmware analysis using offset tables"""
    
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found")
        return None
    
    print(f"Analyzing firmware: {filename}")
    print("=" * 50)
    
    try:
        with open(filename, 'rb') as f:
            results = {}
            
            # Check protection mode setting
            f.seek(DroboOffsets.CONFIG.PROTECTION_MODE)
            protection_mode = struct.unpack('<I', f.read(4))[0]
            results['protection_mode'] = protection_mode
            
            # Check capacity limits
            f.seek(DroboOffsets.CAPACITY_LIMITS.BYTES_BASED)
            bytes_limit = struct.unpack('<Q', f.read(8))[0]
            results['bytes_limit'] = bytes_limit
            results['bytes_limit_tb'] = bytes_to_tb(bytes_limit)
            
            f.seek(DroboOffsets.CAPACITY_LIMITS.SECTORS_BASED)
            sectors_limit = struct.unpack('<Q', f.read(8))[0]
            results['sectors_limit'] = sectors_limit
            results['sectors_limit_tb'] = sectors_to_tb(sectors_limit)
            
            # Check additional configuration flags
            f.seek(DroboOffsets.CONFIG.LARGE_PACK_MODE)
            large_pack_mode = struct.unpack('<I', f.read(4))[0]
            results['large_pack_mode'] = large_pack_mode
            
            f.seek(DroboOffsets.CONFIG.MANAGE_CAPACITY_LEDS)
            led_management = struct.unpack('<I', f.read(4))[0]
            results['led_management'] = led_management
            
            f.seek(DroboOffsets.CONFIG.SHOW_CAPACITY_HOST_VIEW)
            host_view = struct.unpack('<I', f.read(4))[0]
            results['host_view'] = host_view
            
            return results
            
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return None

def print_analysis_results(results):
    """Print formatted analysis results"""
    
    if not results:
        return
    
    print("\nConfiguration Analysis:")
    print("-" * 30)
    
    # Protection mode
    protection_mode = results['protection_mode']
    mode_name = ProtectionModes.MODE_NAMES.get(protection_mode, f"Unknown ({protection_mode})")
    print(f"Protection Mode: {mode_name} (value: {protection_mode})")
    
    # Capacity limits
    print(f"\nCapacity Limits:")
    print(f"  Bytes-based limit:   {results['bytes_limit_tb']:.1f} TB ({results['bytes_limit']:,} bytes)")
    print(f"  Sectors-based limit: {results['sectors_limit_tb']:.1f} TB ({results['sectors_limit']:,} sectors)")
    
    # Check if limits match expected values
    is_original_bytes = results['bytes_limit'] == DroboOffsets.CAPACITY_LIMITS.ORIGINAL_BYTES_LIMIT
    is_original_sectors = results['sectors_limit'] == DroboOffsets.CAPACITY_LIMITS.ORIGINAL_SECTORS_LIMIT
    
    if is_original_bytes and is_original_sectors:
        print("  Status: Original 2TB limits (not patched)")
    elif results['bytes_limit'] > DroboOffsets.CAPACITY_LIMITS.ORIGINAL_BYTES_LIMIT:
        print("  Status: Patched limits detected")
    else:
        print("  Status: Unusual limit values")
    
    # Configuration flags
    print(f"\nConfiguration Flags:")
    print(f"  Large Pack Mode:     {'Enabled' if results['large_pack_mode'] else 'Disabled'} ({results['large_pack_mode']})")
    print(f"  LED Management:      {results['led_management']}")
    print(f"  Host Capacity View:  {'Enabled' if results['host_view'] else 'Disabled'} ({results['host_view']})")
    
    # Memory locations
    print(f"\nMemory Locations:")
    print(f"  Protection Mode:     0x{DroboOffsets.CONFIG.PROTECTION_MODE:08x}")
    print(f"  Bytes Limit:         0x{DroboOffsets.CAPACITY_LIMITS.BYTES_BASED:08x}")
    print(f"  Sectors Limit:       0x{DroboOffsets.CAPACITY_LIMITS.SECTORS_BASED:08x}")
    print(f"  Large Pack Mode:     0x{DroboOffsets.CONFIG.LARGE_PACK_MODE:08x}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 firmware_analyzer.py <firmware_file>")
        print("Examples:")
        print("  python3 firmware_analyzer.py ../extracted/secondary.elf")
        print("  python3 firmware_analyzer.py secondary.elf  # Uses DROBO_EXTRACTED_PATH")
        print("  DROBO_EXTRACTED_PATH=/path/to/extracted python3 firmware_analyzer.py secondary.elf")
        print()
        print("Environment Variables:")
        print(f"  DROBO_EXTRACTED_PATH: {DEFAULT_EXTRACTED_PATH}")
        print(f"  DROBO_FIRMWARE_PATH:  {DEFAULT_FIRMWARE_PATH}")
        sys.exit(1)
    
    filename = resolve_firmware_path(sys.argv[1])
    print(f"Resolved firmware path: {filename}")
    
    results = analyze_firmware(filename)
    
    if results:
        print_analysis_results(results)
        print(f"\nAnalysis complete for: {os.path.basename(filename)}")
    else:
        print("Analysis failed")
        sys.exit(1)

if __name__ == "__main__":
    main()