#!/usr/bin/env python3
"""
Drobo 5D3 Memory Offsets and Constants
======================================

This module provides programmatic access to memory offsets, configuration locations,
and other constants discovered through firmware analysis of the Drobo 5D3.

Usage:
    from offsets import DroboOffsets, ProtectionModes
    
    # Access configuration offsets
    protection_mode_addr = DroboOffsets.CONFIG.PROTECTION_MODE
    
    # Get capacity limit locations
    bytes_limit_addr = DroboOffsets.CAPACITY_LIMITS.BYTES_BASED
    
    # Load from JSON for dynamic usage
    offsets = DroboOffsets.load_from_json('memory-offsets.json')
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Firmware Component Offsets
@dataclass
class FirmwareComponents:
    """TDF container component offsets"""
    MAIN_VXWORKS_ELF = 0x22C              # Bootloader (556 decimal)
    SECONDARY_ELF = 0x303124               # Main application (3158308 decimal)  
    VXWORKS_KERNEL_BIN = 0xF59BFC         # VxWorks kernel (16096252 decimal)

# Configuration Block Offsets (secondary.elf)
@dataclass
class ConfigurationOffsets:
    """Main configuration block offsets in secondary.elf"""
    BASE_OFFSET = 0x66d6f0                 # Configuration block base
    PROTECTION_MODE = 0x66d6f0             # mbProtectionMode
    MANAGE_CAPACITY_LEDS = 0x66d710        # mManageCapacityLEDs
    SHOW_CAPACITY_HOST_VIEW = 0x66d730     # mbShowCapacityHostView
    LARGE_PACK_MODE = 0x66d750             # mbLargePackMode  
    LAST_UI_CALL_TIME = 0x66d770           # mLastUICallTime

# Capacity Limit Offsets
@dataclass
class CapacityLimits:
    """Known capacity limit locations for patching"""
    BYTES_BASED = 0x65b097                 # 2TB bytes limit
    SECTORS_BASED = 0x65ada8               # 2TB sectors limit
    
    # Original values
    ORIGINAL_BYTES_LIMIT = 2199023255552   # 2TB in bytes
    ORIGINAL_SECTORS_LIMIT = 4294967296    # 2TB in sectors
    
    # Patch values (32TB)
    PATCH_BYTES_LIMIT = 35184372088832     # 32TB in bytes  
    PATCH_SECTORS_LIMIT = 68719476736      # 32TB in sectors

# String Reference Offsets
@dataclass
class StringOffsets:
    """Key string locations in secondary.elf"""
    ZMDT_TRACKER = 0x656d30                # "zmdt = ZONE METADATA TRACKER"
    SELF_MIRRORED_ZONES = 0x656d50         # "Use of self-mirrored Zones is currently"
    ZONE_MANAGER = 0x6573c0                # "zm..ZoneManager:"
    DISK_PACK_MANAGER = 0x657390           # "dpm.DiskPackManager:"
    REGION_SIZE = 0x657690                 # "RegionSize"
    SELF_MIRROR_USAGE = 0x656d80           # "usage: useSelfMirrored [on]"
    PROTECTION_MODE_LABEL = 0x66d700       # "mbProtectionMode        :"

# Management Module Information
class ManagementModules:
    """Management module identifiers and commands"""
    DPM = "dpm"      # Disk Pack Manager
    HAM = "ham"      # Host Access Manager  
    ZM = "zm"        # Zone Manager
    RM = "rm"        # Region Manager
    CM = "cm"        # Cluster Manager
    CATM = "catm"    # Catalog Manager
    
    ALL_MODULES = [DPM, HAM, ZM, RM, CM, CATM]
    
    # Performance info strings
    PERF_STRINGS = {
        DPM: "DiskPackManager Perf info",
        HAM: "HAManager Perf info", 
        ZM: "ZoneManager Perf info",
        RM: "RegionManager Perf info",
        CM: "ClusterManager Perf info", 
        CATM: "CatManager Perf info"
    }

# Protection Mode Constants
class ProtectionModes:
    """Protection mode identifiers and settings"""
    NO_REDUNDANCY = 0      # RAID 0 equivalent
    SELF_MIRRORED = 1      # RAID 1 equivalent  
    DUAL_REDUNDANCY = 2    # RAID 6 equivalent
    
    MODE_NAMES = {
        NO_REDUNDANCY: "No Redundancy",
        SELF_MIRRORED: "Self-Mirrored", 
        DUAL_REDUNDANCY: "Dual Redundancy"
    }
    
    MIN_DRIVES = {
        NO_REDUNDANCY: 1,
        SELF_MIRRORED: 2,
        DUAL_REDUNDANCY: 3
    }

# Debug Interface Constants  
class DebugInterfaces:
    """Debug command and interface constants"""
    
    # Performance counters
    HOST_LBA_CACHE = "hlbat = HOST LBA CACHE TRACKER"
    ZONE_METADATA = "zmdt = ZONE META DATA TRACKER" 
    DISK_LBA_CACHE = "dlbat = DISK LBA CACHE TRACKER"
    
    # Command patterns
    DISK_COMMANDS = [
        "k disk",         # General disk commands
        "k disk cfg",     # Dump disk configuration
        "k disk sense",   # Disk sense information
        "k disk freeAll"  # Free all disk resources
    ]
    
    # Protection commands
    PROTECTION_COMMANDS = [
        "useSelfMirrored [on]",    # Enable/disable self-mirroring
        "redmodeslowdown on|off"   # Red mode performance control
    ]

# Main offset container class
class DroboOffsets:
    """Container for all Drobo firmware offsets and constants"""
    
    FIRMWARE = FirmwareComponents()
    CONFIG = ConfigurationOffsets()
    CAPACITY_LIMITS = CapacityLimits()
    STRINGS = StringOffsets()
    MODULES = ManagementModules()
    PROTECTION = ProtectionModes()
    DEBUG = DebugInterfaces()
    
    # Metadata
    FIRMWARE_VERSION = "4.2.3"
    DEVICE_MODEL = "Drobo 5D3" 
    ARCHITECTURE = "ARM 32-bit LSB"
    ENDIANNESS = "little"
    
    @classmethod
    def load_from_json(cls, json_path: str = None) -> Optional[Dict[str, Any]]:
        """Load offset data from JSON file"""
        if json_path is None:
            # Default to data directory relative to this file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(script_dir, '..', 'docs', 'data', 'memory-offsets.json')
        
        try:
            with open(json_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    @classmethod
    def get_offset_by_name(cls, name: str) -> Optional[int]:
        """Get offset by symbolic name"""
        offset_map = {
            'protection_mode': cls.CONFIG.PROTECTION_MODE,
            'large_pack_mode': cls.CONFIG.LARGE_PACK_MODE,
            'bytes_limit': cls.CAPACITY_LIMITS.BYTES_BASED,
            'sectors_limit': cls.CAPACITY_LIMITS.SECTORS_BASED,
            'secondary_elf': cls.FIRMWARE.SECONDARY_ELF,
        }
        return offset_map.get(name.lower())
    
    @classmethod
    def is_patchable_offset(cls, offset: int) -> bool:
        """Check if offset is in a patchable region"""
        patchable_ranges = [
            # Configuration block
            (cls.CONFIG.BASE_OFFSET, cls.CONFIG.BASE_OFFSET + 0x100),
            # Capacity limits  
            (cls.CAPACITY_LIMITS.BYTES_BASED, cls.CAPACITY_LIMITS.BYTES_BASED + 8),
            (cls.CAPACITY_LIMITS.SECTORS_BASED, cls.CAPACITY_LIMITS.SECTORS_BASED + 8)
        ]
        
        return any(start <= offset < end for start, end in patchable_ranges)
    
    @classmethod 
    def get_module_command(cls, module: str) -> Optional[str]:
        """Get debug command for management module"""
        return module if module in cls.MODULES.ALL_MODULES else None

# Utility functions
def hex_to_int(hex_str: str) -> int:
    """Convert hex string to integer"""
    return int(hex_str, 16) if hex_str.startswith('0x') else int(hex_str)

def int_to_hex(value: int) -> str:
    """Convert integer to hex string"""
    return f"0x{value:x}"

def bytes_to_tb(byte_value: int) -> float:
    """Convert bytes to terabytes"""
    return byte_value / (1024 ** 4)

def sectors_to_tb(sector_value: int) -> float:
    """Convert sectors to terabytes (assuming 512-byte sectors)"""
    return (sector_value * 512) / (1024 ** 4)

# Example usage and testing
if __name__ == "__main__":
    print("Drobo 5D3 Firmware Offsets")
    print("=" * 30)
    
    # Display key offsets
    print(f"Protection Mode: {int_to_hex(DroboOffsets.CONFIG.PROTECTION_MODE)}")
    print(f"Large Pack Mode: {int_to_hex(DroboOffsets.CONFIG.LARGE_PACK_MODE)}")  
    print(f"Bytes Limit: {int_to_hex(DroboOffsets.CAPACITY_LIMITS.BYTES_BASED)}")
    print(f"Sectors Limit: {int_to_hex(DroboOffsets.CAPACITY_LIMITS.SECTORS_BASED)}")
    
    # Show capacity conversions
    print(f"\nOriginal Limits:")
    print(f"  Bytes: {bytes_to_tb(DroboOffsets.CAPACITY_LIMITS.ORIGINAL_BYTES_LIMIT):.1f} TB")
    print(f"  Sectors: {sectors_to_tb(DroboOffsets.CAPACITY_LIMITS.ORIGINAL_SECTORS_LIMIT):.1f} TB")
    
    print(f"\nPatch Limits:")  
    print(f"  Bytes: {bytes_to_tb(DroboOffsets.CAPACITY_LIMITS.PATCH_BYTES_LIMIT):.1f} TB")
    print(f"  Sectors: {sectors_to_tb(DroboOffsets.CAPACITY_LIMITS.PATCH_SECTORS_LIMIT):.1f} TB")
    
    # Test patchable regions
    print(f"\nPatchable Regions:")
    test_offsets = [
        DroboOffsets.CONFIG.PROTECTION_MODE,
        DroboOffsets.CAPACITY_LIMITS.BYTES_BASED,
        DroboOffsets.FIRMWARE.MAIN_VXWORKS_ELF
    ]
    
    for offset in test_offsets:
        patchable = DroboOffsets.is_patchable_offset(offset)
        print(f"  {int_to_hex(offset)}: {'✓' if patchable else '✗'}")