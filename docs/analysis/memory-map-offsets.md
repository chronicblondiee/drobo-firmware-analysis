# Drobo 5D3 Memory Map and Key Offsets

## Overview
This document maps the key memory locations, string offsets, and configuration structures found in the Drobo 5D3 firmware components.

## Firmware Component Layout

### TDF Container Structure
```
Offset      Size        Component           Description
0x22C       ~3MB        main_vxworks.elf    Bootloader/VxWorks loader
0x303124    ~12MB       secondary.elf       Main application logic  
0xF59BFC    ~4.6MB      vxworks_kernel.bin  VxWorks WIND kernel
```

## Secondary.elf Memory Map

### Configuration Structure Block
**Base Offset**: `0x66d6f0`
```
Offset      Field                   Description
0x66d6f0    mbProtectionMode        Primary RAID protection setting
0x66d710    mManageCapacityLEDs     LED status control flags
0x66d730    mbShowCapacityHostView  Host capacity display mode
0x66d750    mbLargePackMode         Large drive configuration mode  
0x66d770    mLastUICallTime         UI interaction timestamp
```

### Capacity Limit Locations
**Previously identified 2TB limit patches**:
```
Offset      Description             Original Value    Patch Value
0x65b097    Bytes-based limit       2TB (bytes)       32TB (bytes)
0x65ada8    Sectors-based limit     2TB (sectors)     32TB (sectors)
```

### String Reference Locations

#### Zone Management Strings
```
Offset      String                                  Context
0x656d30    "zmdt = ZONE METADATA TRACKER"         Zone metadata system
0x656d50    "Use of self-mirrored Zones is"        Protection mode status
0x657390    "dpm.DiskPackManager:"                 Disk management
0x6573c0    "zm..ZoneManager:"                     Zone controller
0x6573e0    "Z0IT:...ClusterManager:"              Zone 0 info table
```

#### Protection Mode Strings  
```
Offset      String                                  Function
0x656d80    "usage: useSelfMirrored [on]"          Self-mirror control
0x657690    "RegionSize"                           Storage region config
Near 0x66d700 "mbProtectionMode        :"          Protection setting label
```

#### Error and Status Messages
```
Offset      String                                  Purpose
~0x4xxxxx   "DPM::discoverDis: >2TB drive:"       2TB limit message
Various     "redundancy loss"                      Protection failure alert
Various     "NoRedundancy or Degraded Zones"      Status indicator
```

### Management Module Entry Points

#### DiskPackManager (DPM)
```
Function/String                     Approximate Offset
"DiskPackManager:"                  0x657390
"): calling DPM::hotPlug(REMOVE)"   Variable
"getDPMMetaDataLBA.DNP"            Variable
```

#### Host Access Manager (HAM)  
```
Function/String                     Approximate Offset
"HAManager Perf info"               Variable
"ham = HOST ACCESS MANAGER"         Variable
"HAM: Use of Dual Disk Redundancy"  Variable
```

#### Zone Manager
```
Function/String                     Approximate Offset
"ZoneManager:"                      0x6573c0
"zm = ZONE MANAGER INFORMATION"     Variable
"ZONE 0 INFORMATION TABLE"          Variable
```

## VxWorks Kernel Locations

### Kernel Signatures
```
Offset      Signature               Description
0xF59BFC    "WIND"                 VxWorks kernel identifier
Various     "VxWorks"              Kernel strings
Various     "j1DualPoolInit"       Dual memory pool init
```

### Protection Mechanisms
```
String/Function                     Purpose
"VX_NO_STACK_PROTECT"              Stack protection setting
"ESA_DMA_ACCESS_PROTECTED"         DMA access control
"ESA_DMA_WRITE_PROTECTED"          DMA write protection
```

## Main VxWorks ELF Locations

### Bootloader Functions
```
Component                   Purpose
ELF Header                 Standard ARM ELF executable
Boot sequences             VxWorks initialization
Hardware init              Platform-specific setup
```

## Flash Configuration Areas

### Persistent Settings
```
Setting                     Description
"FlashConfigData:"          Configuration storage identifier
"ClearDisk ="              Disk clearing configuration  
"DemoMode ="               Demo/test mode flag
Protection settings         RAID mode persistence
```

## Debug and Diagnostic Interfaces

### Performance Counters
```
Counter/Tracker                 Purpose
"hlbat = HOST LBA CACHE"       Host LBA cache tracking
"zmdt = ZONE META DATA"        Zone metadata tracking  
"dlbat = DISK LBA CACHE"       Disk LBA cache tracking
```

### Command Interfaces
```
Command Pattern                 Function
"usage: [command] [options]"   Interactive command help
"k disk [subcommand]"          Disk diagnostic commands
"dpm,rm,zm,zoit,cm,catm"      Module performance queries
```

## Critical Memory Regions

### Write-Protected Areas
- **Bootloader**: main_vxworks.elf should not be modified
- **Kernel**: vxworks_kernel.bin contains core OS functions
- **System Zone**: Zone 0 contains critical metadata

### Patchable Areas
- **Protection Settings**: 0x66d6f0 region in secondary.elf
- **Capacity Limits**: 0x65b097 and 0x65ada8 in secondary.elf  
- **Configuration Flags**: Flash configuration data areas

### Backup Recommended
- **Complete secondary.elf**: Contains all application logic
- **Flash configuration**: Protection mode persistence
- **Zone metadata**: Critical for data recovery

## Offset Calculation Notes

### Base Addresses
- All offsets relative to component start
- TDF container adds header offset
- ELF loading may relocate addresses at runtime

### String Searching
```bash
# Find string offset in secondary.elf  
strings -t x secondary.elf | grep "target_string"

# Find hex pattern
hexdump -C secondary.elf | grep "pattern"

# Binary search for specific values
python3 -c "
data = open('secondary.elf', 'rb').read()
offset = data.find(b'search_bytes')  
print(f'Found at: 0x{offset:x}')
"
```

### Verification
- Cross-reference string locations with hexdump output
- Verify offsets against binwalk analysis (Rust version recommended)
- Test modifications on backup files first

This memory map provides the foundation for targeted firmware modifications and deeper analysis of the Drobo's RAID controller implementation.