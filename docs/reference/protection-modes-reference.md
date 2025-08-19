# Drobo 5D3 Protection Modes Reference

## Overview
The Drobo 5D3 uses a zone-based protection system that dynamically adapts based on the number and configuration of installed drives. This document details the discovered protection modes and their configurations.

## Protection Mode Configuration

### Primary Setting: `mbProtectionMode`
**Memory Location**: `0x66d6f0` in `secondary.elf`
**Type**: Configuration flag/enumeration
**Function**: Controls the primary RAID protection algorithm

### Protection Mode Types

#### 1. Self-Mirrored Mode
**Command**: `useSelfMirrored [on]`
**Description**: Local mirroring within individual zones
**Drive Requirements**: Minimum 2 drives
**Protection Level**: Single drive failure tolerance

**Key Characteristics**:
- Each zone is independently mirrored
- Data exists in at least two copies
- Equivalent to RAID 1 behavior
- Can operate with mixed drive sizes

**Configuration Strings**:
```
Use of self-mirrored Zones is currently [status]
GetCachedSelfMirroredZoneCount
Zone 0 needs to be a type other than SelfMirrored to migrate the pack
```

#### 2. Dual Disk Redundancy
**Description**: Protection against simultaneous failure of two drives
**Drive Requirements**: Minimum 3 drives (recommended 4+)
**Protection Level**: Dual drive failure tolerance

**Key Characteristics**:
- Can lose any two drives without data loss
- Equivalent to RAID 6 behavior
- More CPU intensive than single redundancy
- Automatically enabled/disabled based on drive count

**Configuration Strings**:
```
Dual Disk Redundancy is [status]
HAM: Use of Dual Disk Redundancy is being [enabled/disabled]
```

#### 3. No Redundancy Mode
**Description**: Fallback mode when insufficient drives for protection
**Drive Requirements**: Single drive
**Protection Level**: No redundancy (RAID 0 equivalent)

**Key Characteristics**:
- Maximum capacity utilization
- No protection against drive failure
- Used during degraded states
- Temporary mode during rebuilds

**Status Indicators**:
```
GetStatusInfo: NoRedundancy or Degraded Zones
redundancy loss
```

## Zone Protection Behavior

### Zone 0 (System Zone)
- **Special Requirements**: Cannot be self-mirrored during pack migration
- **Contains**: System metadata, boot information, configuration
- **Protection**: Always maintains highest available protection level

### Data Zones
- **Variable Protection**: Can mix protection levels within same array
- **Dynamic Adaptation**: Protection level can change based on available capacity
- **Migration Support**: Zones can be migrated between protection modes

## Protection Mode Commands

### Interactive Commands
```bash
# Enable/disable self-mirroring
useSelfMirrored [on]

# Query current protection status  
GetStatusInfo: NoRedundancy or Degraded Zones

# Performance impact control
redmodeslowdown on|off
```

### System Status Queries
```bash
# Zone information
zm = ZONE MANAGER INFORMATION
z0it = ZONE 0 INFORMATION TABLE

# Protection counters
GetCachedSelfMirroredZoneCount

# Redundancy status
[Manager]: Dual Disk Redundancy is [status]
```

## Configuration Persistence

### Flash Storage
Protection mode settings are stored in flash memory:
```
FlashConfigData: [various protection settings]
- Survives power cycles
- Maintained during firmware updates
- Can be reset via ClearDisk operation
```

### Runtime Configuration
```
mTotalClustersTrans     : [Total available clusters]
mUsedClustersTrans      : [Currently used clusters] 
mFreeClustersTrans      : [Available free clusters]
mbProtectionMode        : [Active protection mode]
mbLargePackMode         : [Large drive support mode]
```

## Protection Mode Transitions

### Drive Addition
1. **Single → Dual Drive**: Enables self-mirroring
2. **Dual → Triple Drive**: Enables dual redundancy option
3. **Background Migration**: Zones gradually migrated to higher protection

### Drive Removal  
1. **Degraded Operation**: Continue with reduced protection
2. **Emergency Mode**: Switch to no redundancy if necessary
3. **Rebuild Process**: Restore protection when replacement added

### Mode Switching
- **Zone Migration Required**: Cannot instantly switch protection modes
- **Background Process**: Migration occurs during idle periods
- **Capacity Impact**: May temporarily reduce available space during migration

## Protection Performance Impact

### Self-Mirrored Mode
- **Write Penalty**: ~2x (must write to mirror)
- **Read Benefit**: Can read from either copy
- **CPU Impact**: Minimal additional processing

### Dual Redundancy Mode
- **Write Penalty**: ~3-4x (parity calculation + multiple writes)
- **Read Performance**: Minimal impact during normal operation
- **CPU Impact**: Significant during writes and rebuilds
- **Rebuild Time**: Longer recovery from drive failures

### Red Mode Slowdown
- **Purpose**: Reduce performance to manage temperature/power
- **Control**: `redmodeslowdown on|off`
- **Impact**: Affects all protection modes equally

## Troubleshooting Protection Issues

### Common Problems
1. **Zone Migration Stuck**: Check available free space
2. **Protection Downgrade**: Verify all drives are healthy
3. **Performance Issues**: Consider red mode slowdown settings

### Diagnostic Commands
```
'module' can be dpm,rm,zm,zoit,cm,catm for external metadata check
zm = ZONE MANAGER INFORMATION
ham = HOST ACCESS MANAGER INFORMATION
dpm = DISK PACK MANAGER INFORMATION
```

### Recovery Procedures
1. **Clear Configuration**: Use ClearDisk to reset protection settings
2. **Force Rebuild**: Power cycle with drives to force reconfiguration  
3. **Migration Reset**: May require zone migration restart

This protection system provides flexibility beyond traditional RAID while maintaining data safety through zone-based redundancy management.