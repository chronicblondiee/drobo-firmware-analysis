# Drobo 5D3 Management Modules Reference

## Overview
The Drobo 5D3 firmware uses a modular architecture with specialized management components that handle different aspects of the RAID system. This document details each module's function, interfaces, and interaction patterns.

## Module Architecture

### Core Management Stack
```
┌─────────────────────────────────────┐
│           Host Interface            │
├─────────────────────────────────────┤
│    HAM (Host Access Manager)       │
├─────────────────────────────────────┤
│    DPM (Disk Pack Manager)         │
├─────────────────────────────────────┤
│    ZM (Zone Manager)                │
├─────────────────────────────────────┤  
│    RM (Region Manager)              │
├─────────────────────────────────────┤
│    CM (Cluster Manager)             │
├─────────────────────────────────────┤
│         Physical Drives             │
└─────────────────────────────────────┘
```

## Module Detailed Reference

### 1. DPM - Disk Pack Manager
**Primary Function**: Core disk management and coordination
**Location**: Main controller in `secondary.elf`

#### Responsibilities
- Physical drive detection and management
- Hot-plug event handling
- Drive health monitoring
- Disk pack assembly and coordination
- Metadata LBA management

#### Key Functions
```
DiskPackManager Initialize/Shutdown
Drive hot-plug detection: ): calling DPM::hotPlug(REMOVE)
Metadata management: getDPMMetaDataLBA.DNP
Performance tracking: dpm = DiskPackManager Perf info
```

#### Debug Commands
```bash
dpm                    # DPM performance information
k disk                 # Drobo specific disk commands  
k disk cfg             # Dump static disk configuration
k disk sense           # Disk sense information
k disk freeAll         # Free all disk resources
```

#### Status Indicators
```
"DiskPackManager:"                 # Module identifier
"No diskpack loaded"               # Pack status
"STANDALONE: diskpack cleared"     # Clear operation status
```

### 2. HAM - Host Access Manager  
**Primary Function**: Interface between host and internal RAID system
**Location**: Host interface controller

#### Responsibilities
- Host I/O request processing
- LBA translation and mapping
- Cache management coordination
- Protection mode enforcement
- Host capacity reporting

#### Key Functions
```
Host LBA management: hlbat = HOST LBA CACHE TRACKER
Protection control: HAM: Use of Dual Disk Redundancy is being
Performance tracking: ham = HAManager Perf info
```

#### Cache Systems
```
Host LBA Cache: hlbat = HOST LBA CACHE TRACKER
- Tracks host logical block addresses
- Manages read/write cache coherency
- Optimizes sequential access patterns
```

#### Debug Interface
```bash  
ham                    # HAM performance information
hlbat                  # Host LBA cache tracker info
```

### 3. ZM - Zone Manager
**Primary Function**: Zone-based data layout and protection
**Location**: Zone layout controller

#### Responsibilities
- Zone creation and management
- Zone protection mode assignment
- Zone migration between protection levels
- Zone 0 (system zone) special handling
- Zone metadata tracking

#### Key Functions
```
Zone layout: ZoneManager initialization
Zone info: zm = ZONE MANAGER INFORMATION  
Zone 0 management: z0it = ZONE 0 INFORMATION TABLE
Zone metadata: zmdt = ZONE METADATA TRACKER
```

#### Zone Operations
```
Zone creation and sizing: ZoneSize configuration
Zone protection: Self-mirrored zone management
Zone migration: Protection level transitions
Zone tracking: mZoneSet structure management
```

#### Debug Commands
```bash
zm                     # Zone Manager performance info
z0it                   # Zone 0 Information Table  
zmdt                   # Zone metadata tracker
```

#### Status Information
```
"ZONE MANAGER INFORMATION"         # Module status
"ZONE 0 INFORMATION TABLE"         # System zone info
"Zone Meta Data Tracker perf info" # Performance data
```

### 4. RM - Region Manager
**Primary Function**: Storage region allocation and management
**Location**: Storage region allocator

#### Responsibilities
- Storage region allocation
- Capacity management
- Region size optimization
- Free space tracking
- Region metadata management

#### Key Functions
```
Region management: RegionManager initialization
Region sizing: RegionSize configuration and tracking
Capacity tracking: Region-based capacity calculations
```

#### Debug Interface
```bash
rm                     # Region Manager information
RegionSize             # Current region configuration
```

### 5. CM - Cluster Manager
**Primary Function**: Data clustering and organization
**Location**: Data clustering controller

#### Responsibilities
- Data cluster organization
- Cluster allocation and deallocation
- Cluster-level metadata management
- Performance optimization through clustering

#### Key Functions
```
Cluster management: ClusterManager operations
Cluster tracking: mTotalClustersTrans, mUsedClustersTrans, mFreeClustersTrans  
Stripe management: StripeCTOPtrs SlabAllocator
```

#### Configuration Data
```
mTotalClustersTrans     : Total available clusters
mUsedClustersTrans      : Currently allocated clusters
mFreeClustersTrans      : Available free clusters
```

#### Debug Commands
```bash
cm                     # Cluster Manager information
```

### 6. CatManager - Catalog Manager
**Primary Function**: Metadata catalog and filesystem management
**Location**: Metadata management controller  

#### Responsibilities
- Filesystem metadata management
- Directory and file catalog maintenance
- Metadata consistency checking
- Index management

#### Key Functions
```
Catalog operations: CatManager initialization
Metadata checking: External consistency checks
Performance tracking: Catalog performance monitoring
```

#### Debug Interface
```bash
catm                   # Catalog Manager information
MetaCheck              # Metadata consistency check
```

## Module Interaction Patterns

### Initialization Sequence
1. **VxWorks Kernel**: Basic OS services
2. **DPM**: Drive detection and disk pack assembly
3. **ZM/RM**: Zone and region layout establishment  
4. **CM/CatManager**: Data organization and metadata
5. **HAM**: Host interface activation

### I/O Flow
```
Host Request → HAM → ZM → RM → CM → DPM → Physical Drives
             ↑                                        ↓
             ←─── Cache/Metadata Updates ←─────────────
```

### Protection Mode Changes
```
User Command → HAM → ZM (zone migration) → RM (capacity recalc) → CM (cluster reorg)
```

### Hot-Plug Events
```
Drive Change → DPM → ZM (protection recalc) → HAM (host notification)
```

## Performance Monitoring

### Module Performance Commands
```bash
# Individual module performance
dpm                    # Disk Pack Manager
ham                    # Host Access Manager  
zm                     # Zone Manager
rm                     # Region Manager (inferred)
cm                     # Cluster Manager (inferred)
catm                   # Catalog Manager

# Combined performance info
all                    # All manager performance data
```

### Performance Metrics
Each module provides:
- **Operation counts**: Read/write statistics
- **Timing data**: Average operation times
- **Error rates**: Failure and retry statistics
- **Resource usage**: Memory and cache utilization

## Error Handling and Recovery

### Module-Level Error Handling
- **DPM**: Drive failure detection and isolation
- **HAM**: Host I/O error management and retry
- **ZM**: Zone degradation and recovery
- **RM**: Region corruption detection
- **CM**: Cluster consistency verification

### Cross-Module Recovery
- **Protection Degradation**: ZM→HAM notification of reduced redundancy
- **Drive Replacement**: DPM→ZM→RM coordination for rebuild
- **Metadata Recovery**: CatManager→All modules for consistency restore

## Configuration Interface

### Module Configuration
Most module settings are controlled through:
- **Flash Configuration**: Persistent settings
- **Runtime Commands**: Dynamic configuration changes
- **Protection Mode**: Cross-module configuration updates

### External Consistency Checks
```bash
# Module-specific consistency checks
'module' can be dpm,rm,zm,zoit,cm,catm for external metadata check
```

This modular architecture allows the Drobo to provide flexible RAID functionality while maintaining clear separation of concerns between storage layers.