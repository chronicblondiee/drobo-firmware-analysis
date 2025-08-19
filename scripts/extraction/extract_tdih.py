#!/usr/bin/env python3
import struct
import os

def parse_tdih_header(data):
    """Parse TDIH header structure"""
    
    # Extract header fields
    offset_or_size = struct.unpack('<I', data[0:4])[0]
    unknown1 = struct.unpack('<I', data[4:8])[0]
    magic = data[8:12]
    identifier = struct.unpack('<I', data[12:16])[0]
    target_name = data[16:32].rstrip(b'\x00').decode('ascii', errors='ignore')
    
    print(f"TDIH Header Analysis:")
    print(f"  Offset/Size: 0x{offset_or_size:x} ({offset_or_size})")
    print(f"  Unknown1: 0x{unknown1:x}")
    print(f"  Magic: {magic}")
    print(f"  Identifier: 0x{identifier:x}")
    print(f"  Target: {target_name}")
    
    # Look for firmware string
    fw_string_start = 48  # 0x30
    fw_string = data[fw_string_start:fw_string_start+32].rstrip(b'\x00').decode('ascii', errors='ignore')
    print(f"  Firmware: {fw_string}")
    
    return offset_or_size

def extract_tdih_firmware(filename):
    """Extract VxWorks firmware from TDIH container"""
    
    with open(filename, 'rb') as f:
        # Read and parse header
        header = f.read(512)
        payload_offset = parse_tdih_header(header)
        
        print(f"\nExtracting payload from offset: 0x{payload_offset:x}")
        
        # Extract the VxWorks image starting at the calculated offset
        f.seek(payload_offset)
        
        # Read a reasonable chunk to start with
        vxworks_data = f.read(10 * 1024 * 1024)  # 10MB should be enough
        
        # Save the extracted VxWorks image
        with open('vxworks_image.bin', 'wb') as out:
            out.write(vxworks_data)
        
        print(f"Extracted {len(vxworks_data)} bytes to vxworks_image.bin")
        
        # Check if it's an ELF
        if vxworks_data[:4] == b'\x7fELF':
            print("✓ Extracted data is a valid ELF file")
            
            # Also save as ELF for easier analysis
            with open('vxworks_image.elf', 'wb') as out:
                out.write(vxworks_data)
        else:
            print(f"? Extracted data starts with: {vxworks_data[:16].hex()}")
            
        return vxworks_data

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = '../../firmware/release.Drobo5D3.4-2-3.tdf'
    
    extract_tdih_firmware(filename)
