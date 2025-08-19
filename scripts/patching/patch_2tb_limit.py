#!/usr/bin/env python3
import struct
import shutil

def analyze_current_state():
    """Analyze current patch state"""
    
    print("=== CURRENT STATE ANALYSIS ===\n")
    
    locations = [
        ("bytes_location", 0x65b097),
        ("sectors_location", 0x65ada8),
    ]
    
    with open('../../extracted/secondary.elf', 'rb') as f:
        for name, offset in locations:
            f.seek(offset)
            value = struct.unpack('<Q', f.read(8))[0]
            
            print(f"{name} (0x{offset:x}):")
            print(f"  Current value: 0x{value:x}")
            print(f"  As TB (bytes): {value / (1024**4):.1f} TB")
            print(f"  As TB (sectors): {(value * 512) / (1024**4):.1f} TB")
            print()

def patch_drobo_2tb_limit(target_tb=32):
    """Smart patch that adapts to current values"""
    
    print(f"=== PATCHING TO {target_tb}TB ===\n")
    
    # Backup
    shutil.copy('../../extracted/secondary.elf', f'../../backups/secondary.elf.backup_{target_tb}tb')
    print(f"✓ Created backup: secondary.elf.backup_{target_tb}tb")
    
    target_bytes = target_tb * 1024**4
    target_sectors = target_bytes // 512
    
    print(f"Target: {target_tb}TB")
    print(f"  Bytes: 0x{target_bytes:x}")
    print(f"  Sectors: 0x{target_sectors:x}")
    
    patches_applied = 0
    
    with open('../../extracted/secondary.elf', 'r+b') as f:
        # Location 1: bytes-based
        f.seek(0x65b097)
        current_1 = struct.unpack('<Q', f.read(8))[0]
        
        print(f"\nLocation 1 (0x65b097):")
        print(f"  Current: 0x{current_1:x} ({current_1 / (1024**4):.1f} TB)")
        
        if current_1 > 0 and current_1 < target_bytes:
            f.seek(0x65b097)
            f.write(struct.pack('<Q', target_bytes))
            print(f"  ✓ Patched to: 0x{target_bytes:x} ({target_tb} TB)")
            patches_applied += 1
        else:
            print(f"  - Skipped (already larger or invalid)")
        
        # Location 2: sectors-based  
        f.seek(0x65ada8)
        current_2 = struct.unpack('<Q', f.read(8))[0]
        
        print(f"\nLocation 2 (0x65ada8):")
        print(f"  Current: 0x{current_2:x} ({(current_2 * 512) / (1024**4):.1f} TB if sectors)")
        
        if current_2 > 0 and current_2 < target_sectors:
            f.seek(0x65ada8)
            f.write(struct.pack('<Q', target_sectors))
            print(f"  ✓ Patched to: 0x{target_sectors:x} ({target_tb} TB)")
            patches_applied += 1
        else:
            print(f"  - Skipped (already larger or invalid)")
    
    print(f"\n✓ Applied {patches_applied} patches")
    return patches_applied > 0

if __name__ == "__main__":
    analyze_current_state()
    
    # Try patching to 32TB
    target_tb = 32
    if patch_drobo_2tb_limit(target_tb):
        print("\n=== VERIFICATION ===")
        analyze_current_state()
    else:
        print("\nNo patches were needed or applied.")
