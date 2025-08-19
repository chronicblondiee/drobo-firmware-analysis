#!/usr/bin/env python3
import re
import subprocess
import struct

def search_capacity_limits():
    """Search for potential capacity limits to patch"""
    
    print("=== SEARCHING FOR PATCH TARGETS ===\n")
    
    # Get strings from secondary.elf
    elf_path = '../../extracted/secondary.elf'
    result = subprocess.run(['strings', elf_path], capture_output=True, text=True)
    strings_output = result.stdout
    
    # Look for capacity-related patterns
    capacity_patterns = [
        r'.*[0-9]+\s*[TG]B.*',
        r'.*[Ll]imit.*[0-9]+.*',
        r'.*[Mm]ax.*[Cc]apacity.*',
        r'.*[Ee]xceed.*[Cc]apacity.*',
        r'.*[Tt]oo.*[Ll]arge.*',
        r'.*[Dd]rive.*[Ss]ize.*[Ll]imit.*',
    ]
    
    print("Potential capacity/size limits:")
    for pattern in capacity_patterns:
        matches = re.findall(pattern, strings_output, re.IGNORECASE)
        for match in matches[:5]:
            print(f"  {match.strip()}")

def find_2tb_constants():
    """Find 2TB constants in binary"""
    
    print("\n=== SEARCHING FOR 2TB CONSTANTS ===")
    
    with open('../../extracted/secondary.elf', 'rb') as f:
        data = f.read()
    
    constants = {
        "2TB_sectors": 4294967296,      # 0x100000000
        "2TB_binary": 2199023255552,    # 0x20000000000
        "2TB_decimal": 2000000000000,   # 0x1D1A94A200000
    }
    
    found_locations = []
    for name, value in constants.items():
        pattern = struct.pack('<Q', value) if value > 0xFFFFFFFF else struct.pack('<I', value)
        offset = data.find(pattern)
        if offset != -1:
            found_locations.append((name, value, offset))
            print(f"Found {name} (0x{value:x}) at offset: 0x{offset:x}")
    
    return found_locations

def search_near_2tb_message():
    """Search for constants near 2TB error message"""
    
    with open('../../extracted/secondary.elf', 'rb') as f:
        data = f.read()
    
    target_string = "DPM::discoverDis: >2TB drive: Setting dislocation to 2TB"
    message_offset = data.find(target_string.encode())
    
    if message_offset != -1:
        print(f"\n=== FOUND 2TB ERROR MESSAGE ===")
        print(f"Message at offset: 0x{message_offset:x}")
        
        # Search nearby for constants
        search_start = max(0, message_offset - 5000)
        search_end = min(len(data), message_offset + 5000)
        search_data = data[search_start:search_end]
        
        candidates = [4294967296, 2199023255552]  # Common 2TB values
        
        for value in candidates:
            pattern = struct.pack('<Q', value)
            pos = search_data.find(pattern)
            if pos != -1:
                actual_offset = search_start + pos
                distance = actual_offset - message_offset
                print(f"Found 0x{value:x} at 0x{actual_offset:x} (distance: {distance:+d})")

if __name__ == "__main__":
    search_capacity_limits()
    find_2tb_constants()
    search_near_2tb_message()
