#!/usr/bin/env python3
import os

def extract_all_drobo_components(filename):
    """Extract all identified components from Drobo firmware"""
    
    # Components identified by binwalk
    components = [
        (556, "main_vxworks.elf", "Main VxWorks ELF binary"),
        (3158308, "secondary.elf", "Secondary ELF binary"),
        (16096252, "vxworks_kernel.bin", "VxWorks WIND kernel")
    ]
    
    file_size = os.path.getsize(filename)
    
    with open(filename, 'rb') as f:
        for i, (offset, output_name, description) in enumerate(components):
            print(f"\nExtracting: {description}")
            print(f"Offset: 0x{offset:x} ({offset})")
            
            if offset >= file_size:
                print(f"  ⚠ Offset beyond file size, skipping")
                continue
            
            f.seek(offset)
            
            # Determine size to extract
            if i < len(components) - 1:
                next_offset = components[i + 1][0]
                size = min(next_offset - offset, 50 * 1024 * 1024)  # Max 50MB
            else:
                size = min(file_size - offset, 50 * 1024 * 1024)
            
            # Extract the data
            data = f.read(size)
            
            # Save to file
            with open(output_name, 'wb') as out:
                out.write(data)
            
            print(f"  Extracted {len(data)} bytes to {output_name}")
            
            # Analyze the extracted data
            if data[:4] == b'\x7fELF':
                print(f"  ✓ Valid ELF file")
            elif b'VxWorks' in data[:1024]:
                print(f"  ✓ Contains VxWorks signatures")
            elif b'WIND' in data[:1024]:
                print(f"  ✓ Contains WIND kernel signatures")
            else:
                print(f"  ? Unknown format, starts with: {data[:8].hex()}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = '../../firmware/release.Drobo5D3.4-2-3.tdf'
    
    extract_all_drobo_components(filename)
