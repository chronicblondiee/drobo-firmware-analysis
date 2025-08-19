#!/usr/bin/env python3
"""
Drobo 5D3 C Header Generator
============================

Generates C/C++ header files with offset constants for integration
with C-based analysis tools and firmware modification utilities.

Usage:
    python3 header_generator.py [output_file]
    
Default output file is 'drobo_offsets.h' if not specified.

Example:
    python3 header_generator.py ../firmware_offsets.h
"""

import sys
import os
from offsets import DroboOffsets

def generate_c_header(output_file="drobo_offsets.h"):
    """Generate C header file with offset constants"""
    
    header_content = f"""/* Drobo 5D3 Firmware Offsets - Auto-generated */
#ifndef DROBO_OFFSETS_H
#define DROBO_OFFSETS_H

/*
 * Drobo 5D3 Firmware Analysis Offsets
 * Generated from firmware version {DroboOffsets.FIRMWARE_VERSION}
 * Device: {DroboOffsets.DEVICE_MODEL}
 * Architecture: {DroboOffsets.ARCHITECTURE}
 * Endianness: {DroboOffsets.ENDIANNESS}
 */

/* Firmware Component Offsets (TDF Container) */
#define MAIN_VXWORKS_ELF_OFFSET     0x{DroboOffsets.FIRMWARE.MAIN_VXWORKS_ELF:08X}
#define SECONDARY_ELF_OFFSET        0x{DroboOffsets.FIRMWARE.SECONDARY_ELF:08X}  
#define VXWORKS_KERNEL_BIN_OFFSET   0x{DroboOffsets.FIRMWARE.VXWORKS_KERNEL_BIN:08X}

/* Configuration Block Offsets (secondary.elf) */
#define CONFIG_BASE_OFFSET          0x{DroboOffsets.CONFIG.BASE_OFFSET:08X}
#define PROTECTION_MODE_OFFSET      0x{DroboOffsets.CONFIG.PROTECTION_MODE:08X}
#define MANAGE_CAPACITY_LEDS_OFFSET 0x{DroboOffsets.CONFIG.MANAGE_CAPACITY_LEDS:08X}
#define SHOW_CAPACITY_HOST_VIEW_OFFSET 0x{DroboOffsets.CONFIG.SHOW_CAPACITY_HOST_VIEW:08X}
#define LARGE_PACK_MODE_OFFSET      0x{DroboOffsets.CONFIG.LARGE_PACK_MODE:08X}
#define LAST_UI_CALL_TIME_OFFSET    0x{DroboOffsets.CONFIG.LAST_UI_CALL_TIME:08X}

/* Capacity Limit Offsets */
#define BYTES_LIMIT_OFFSET          0x{DroboOffsets.CAPACITY_LIMITS.BYTES_BASED:08X}
#define SECTORS_LIMIT_OFFSET        0x{DroboOffsets.CAPACITY_LIMITS.SECTORS_BASED:08X}

/* Original Capacity Limit Values */
#define ORIGINAL_BYTES_LIMIT        {DroboOffsets.CAPACITY_LIMITS.ORIGINAL_BYTES_LIMIT}ULL
#define ORIGINAL_SECTORS_LIMIT      {DroboOffsets.CAPACITY_LIMITS.ORIGINAL_SECTORS_LIMIT}ULL

/* Patched Capacity Limit Values (32TB) */
#define PATCH_BYTES_LIMIT           {DroboOffsets.CAPACITY_LIMITS.PATCH_BYTES_LIMIT}ULL
#define PATCH_SECTORS_LIMIT         {DroboOffsets.CAPACITY_LIMITS.PATCH_SECTORS_LIMIT}ULL

/* String Reference Offsets */
#define ZMDT_TRACKER_STRING_OFFSET  0x{DroboOffsets.STRINGS.ZMDT_TRACKER:08X}
#define SELF_MIRRORED_ZONES_STRING_OFFSET 0x{DroboOffsets.STRINGS.SELF_MIRRORED_ZONES:08X}
#define ZONE_MANAGER_STRING_OFFSET  0x{DroboOffsets.STRINGS.ZONE_MANAGER:08X}
#define DISK_PACK_MANAGER_STRING_OFFSET 0x{DroboOffsets.STRINGS.DISK_PACK_MANAGER:08X}
#define REGION_SIZE_STRING_OFFSET   0x{DroboOffsets.STRINGS.REGION_SIZE:08X}
#define SELF_MIRROR_USAGE_STRING_OFFSET 0x{DroboOffsets.STRINGS.SELF_MIRROR_USAGE:08X}
#define PROTECTION_MODE_LABEL_STRING_OFFSET 0x{DroboOffsets.STRINGS.PROTECTION_MODE_LABEL:08X}

/* Protection Mode Constants */
#define PROTECTION_MODE_NO_REDUNDANCY   {DroboOffsets.PROTECTION.NO_REDUNDANCY}
#define PROTECTION_MODE_SELF_MIRRORED   {DroboOffsets.PROTECTION.SELF_MIRRORED}
#define PROTECTION_MODE_DUAL_REDUNDANCY {DroboOffsets.PROTECTION.DUAL_REDUNDANCY}

/* Utility Macros */
#define BYTES_TO_TB(bytes)          ((double)(bytes) / (1024.0 * 1024.0 * 1024.0 * 1024.0))
#define SECTORS_TO_TB(sectors)      ((double)((sectors) * 512) / (1024.0 * 1024.0 * 1024.0 * 1024.0))
#define TB_TO_BYTES(tb)             ((uint64_t)((tb) * 1024ULL * 1024ULL * 1024ULL * 1024ULL))
#define TB_TO_SECTORS(tb)           ((uint64_t)(TB_TO_BYTES(tb) / 512))

/* Validation Macros */
#define IS_PATCHABLE_CONFIG_OFFSET(offset) \\
    ((offset) >= CONFIG_BASE_OFFSET && (offset) < (CONFIG_BASE_OFFSET + 0x100))

#define IS_PATCHABLE_CAPACITY_OFFSET(offset) \\
    ((offset) == BYTES_LIMIT_OFFSET || (offset) == SECTORS_LIMIT_OFFSET)

#define IS_PATCHABLE_OFFSET(offset) \\
    (IS_PATCHABLE_CONFIG_OFFSET(offset) || IS_PATCHABLE_CAPACITY_OFFSET(offset))

/* Management Module Identifiers */
#define MODULE_DPM                  "dpm"      /* Disk Pack Manager */
#define MODULE_HAM                  "ham"      /* Host Access Manager */
#define MODULE_ZM                   "zm"       /* Zone Manager */
#define MODULE_RM                   "rm"       /* Region Manager */
#define MODULE_CM                   "cm"       /* Cluster Manager */
#define MODULE_CATM                 "catm"     /* Catalog Manager */

#endif /* DROBO_OFFSETS_H */
"""
    
    try:
        with open(output_file, 'w') as f:
            f.write(header_content)
        
        print(f"✓ Generated C header file: {output_file}")
        print(f"  Firmware version: {DroboOffsets.FIRMWARE_VERSION}")
        print(f"  Device model: {DroboOffsets.DEVICE_MODEL}")
        print(f"  Architecture: {DroboOffsets.ARCHITECTURE}")
        
        # Show file size
        file_size = os.path.getsize(output_file)
        print(f"  File size: {file_size:,} bytes")
        
        return True
        
    except Exception as e:
        print(f"Error generating header file: {e}")
        return False

def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "drobo_offsets.h"
    
    print(f"Generating C header file with Drobo offsets...")
    success = generate_c_header(output_file)
    
    if success:
        print(f"\\nHeader file ready for use in C/C++ projects:")
        print(f'  #include "{output_file}"')
        print(f"  uint32_t protection_offset = PROTECTION_MODE_OFFSET;")
        print(f"  uint64_t original_limit = ORIGINAL_BYTES_LIMIT;")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()