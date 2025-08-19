# Memory Offset Lookup Tables Usage Guide

## Overview
This directory contains memory offset lookup tables in multiple formats for programmatic access to Drobo 5D3 firmware locations. These files enable easy integration with analysis tools, patching scripts, and custom applications.

## Available Formats

### 1. JSON Format (`memory-offsets.json`)
**Best for**: Web applications, REST APIs, configuration files

```json
{
  "secondary_elf_offsets": {
    "configuration_block": {
      "fields": {
        "mbProtectionMode": {
          "offset": "0x66d6f0",
          "offset_decimal": 6740720,
          "description": "Primary RAID protection setting"
        }
      }
    }
  }
}
```

**Usage Examples**:
```javascript
// JavaScript/Node.js
const offsets = require('./memory-offsets.json');
const protectionModeOffset = offsets.secondary_elf_offsets.configuration_block.fields.mbProtectionMode.offset_decimal;

// Python
import json
with open('memory-offsets.json') as f:
    offsets = json.load(f)
protection_offset = offsets['secondary_elf_offsets']['configuration_block']['fields']['mbProtectionMode']['offset_decimal']
```

### 2. CSV Format (`memory-offsets.csv`)
**Best for**: Spreadsheets, databases, data analysis tools

```csv
category,subcategory,name,offset_hex,offset_decimal,description
configuration,protection,mbProtectionMode,0x66d6f0,6740720,Primary RAID protection setting
capacity_limits,bytes,bytes_based_limit,0x65b097,6664343,2TB bytes-based capacity limit
```

**Usage Examples**:
```python
# Python pandas
import pandas as pd
df = pd.read_csv('memory-offsets.csv')
protection_offsets = df[df['category'] == 'configuration']

# SQL Database import
COPY memory_offsets FROM 'memory-offsets.csv' WITH CSV HEADER;
SELECT offset_decimal FROM memory_offsets WHERE name = 'mbProtectionMode';
```

### 3. Python Module (`offsets.py`)
**Best for**: Python scripts, firmware analysis tools, patching applications

```python
from offsets import DroboOffsets, ProtectionModes

# Direct constant access
protection_addr = DroboOffsets.CONFIG.PROTECTION_MODE  # 0x66d6f0
capacity_limit = DroboOffsets.CAPACITY_LIMITS.BYTES_BASED  # 0x65b097

# Utility functions
is_patchable = DroboOffsets.is_patchable_offset(protection_addr)  # True
module_cmd = DroboOffsets.get_module_command('dpm')  # 'dpm'
```

## Programming Examples

### Python Firmware Patcher
**Note**: A complete implementation is available as `tools/capacity_patcher.py`

```python
#!/usr/bin/env python3
from offsets import DroboOffsets
import struct

def patch_capacity_limit(filename, new_limit_tb=32):
    """Patch 2TB capacity limits to specified TB value"""
    
    # Calculate new limits
    new_bytes = new_limit_tb * (1024**4)
    new_sectors = new_bytes // 512
    
    with open(filename, 'r+b') as f:
        # Patch bytes-based limit
        f.seek(DroboOffsets.CAPACITY_LIMITS.BYTES_BASED)
        f.write(struct.pack('<Q', new_bytes))
        
        # Patch sectors-based limit  
        f.seek(DroboOffsets.CAPACITY_LIMITS.SECTORS_BASED)
        f.write(struct.pack('<Q', new_sectors))
    
    print(f"Patched capacity limits to {new_limit_tb}TB")

# Usage
patch_capacity_limit('secondary.elf', 32)
```

### JavaScript Offset Lookup
```javascript
const fs = require('fs');
const offsets = JSON.parse(fs.readFileSync('memory-offsets.json', 'utf8'));

class DroboAnalyzer {
    constructor(offsetData) {
        this.offsets = offsetData;
    }
    
    getConfigurationOffsets() {
        return this.offsets.secondary_elf_offsets.configuration_block.fields;
    }
    
    getCapacityLimits() {
        return this.offsets.secondary_elf_offsets.capacity_limits;
    }
    
    findOffset(name) {
        // Search through all categories for named offset
        const search = (obj, target) => {
            for (let key in obj) {
                if (key === target || (obj[key] && obj[key].name === target)) {
                    return obj[key];
                }
                if (typeof obj[key] === 'object') {
                    const result = search(obj[key], target);
                    if (result) return result;
                }
            }
            return null;
        };
        
        return search(this.offsets, name);
    }
}

const analyzer = new DroboAnalyzer(offsets);
const protectionMode = analyzer.findOffset('mbProtectionMode');
console.log(`Protection mode at: ${protectionMode.offset_hex}`);
```

### C/C++ Header Generation
**Note**: A complete implementation is available as `tools/header_generator.py`

```python
#!/usr/bin/env python3
from offsets import DroboOffsets

def generate_c_header():
    """Generate C header file with offset constants"""
    
    header = """/* Drobo 5D3 Firmware Offsets - Auto-generated */
#ifndef DROBO_OFFSETS_H
#define DROBO_OFFSETS_H

/* Firmware Components */
#define MAIN_VXWORKS_ELF_OFFSET     0x{:08X}
#define SECONDARY_ELF_OFFSET        0x{:08X}  
#define VXWORKS_KERNEL_BIN_OFFSET   0x{:08X}

/* Configuration Block */
#define CONFIG_BASE_OFFSET          0x{:08X}
#define PROTECTION_MODE_OFFSET      0x{:08X}
#define LARGE_PACK_MODE_OFFSET      0x{:08X}

/* Capacity Limits */
#define BYTES_LIMIT_OFFSET          0x{:08X}
#define SECTORS_LIMIT_OFFSET        0x{:08X}
#define ORIGINAL_BYTES_LIMIT        {}ULL
#define ORIGINAL_SECTORS_LIMIT      {}ULL

#endif /* DROBO_OFFSETS_H */
""".format(
        DroboOffsets.FIRMWARE.MAIN_VXWORKS_ELF,
        DroboOffsets.FIRMWARE.SECONDARY_ELF,
        DroboOffsets.FIRMWARE.VXWORKS_KERNEL_BIN,
        DroboOffsets.CONFIG.BASE_OFFSET,
        DroboOffsets.CONFIG.PROTECTION_MODE,
        DroboOffsets.CONFIG.LARGE_PACK_MODE,
        DroboOffsets.CAPACITY_LIMITS.BYTES_BASED,
        DroboOffsets.CAPACITY_LIMITS.SECTORS_BASED,
        DroboOffsets.CAPACITY_LIMITS.ORIGINAL_BYTES_LIMIT,
        DroboOffsets.CAPACITY_LIMITS.ORIGINAL_SECTORS_LIMIT
    )
    
    with open('drobo_offsets.h', 'w') as f:
        f.write(header)

generate_c_header()
```

### Database Integration
```sql
-- PostgreSQL table creation
CREATE TABLE drobo_offsets (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50),
    subcategory VARCHAR(50), 
    name VARCHAR(100),
    offset_hex VARCHAR(20),
    offset_decimal BIGINT,
    size_bytes INTEGER,
    description TEXT,
    data_type VARCHAR(20),
    original_value BIGINT,
    patch_value BIGINT
);

-- Load CSV data
COPY drobo_offsets FROM 'memory-offsets.csv' WITH CSV HEADER;

-- Query examples
SELECT offset_decimal FROM drobo_offsets WHERE name = 'mbProtectionMode';
SELECT * FROM drobo_offsets WHERE category = 'capacity_limits';
SELECT name, offset_hex FROM drobo_offsets WHERE patch_value IS NOT NULL;
```

## Integration Examples

### Ghidra Script Integration
**Note**: A complete implementation is available as `tools/ghidra_bookmarks.py`

```python
# Ghidra Python script using offsets
import sys
sys.path.append('/path/to/drobo-fw/tools')
from offsets import DroboOffsets

# Create bookmarks at key locations
def create_bookmarks():
    bookmarks = [
        (DroboOffsets.CONFIG.PROTECTION_MODE, "Protection Mode Setting"),
        (DroboOffsets.CAPACITY_LIMITS.BYTES_BASED, "2TB Bytes Limit"),  
        (DroboOffsets.CAPACITY_LIMITS.SECTORS_BASED, "2TB Sectors Limit")
    ]
    
    for offset, description in bookmarks:
        addr = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(offset)
        createBookmark(addr, "Drobo Analysis", description)

create_bookmarks()
```

### Binary Analysis Automation
**Note**: A complete implementation is available as `tools/firmware_analyzer.py`

```python
#!/usr/bin/env python3
from offsets import DroboOffsets, hex_to_int
import struct

def analyze_firmware(filename):
    """Automated firmware analysis using offset tables"""
    
    with open(filename, 'rb') as f:
        results = {}
        
        # Check protection mode setting
        f.seek(DroboOffsets.CONFIG.PROTECTION_MODE)
        protection_mode = struct.unpack('<I', f.read(4))[0]
        results['protection_mode'] = protection_mode
        
        # Check capacity limits
        f.seek(DroboOffsets.CAPACITY_LIMITS.BYTES_BASED)
        bytes_limit = struct.unpack('<Q', f.read(8))[0]
        results['bytes_limit_tb'] = bytes_limit / (1024**4)
        
        f.seek(DroboOffsets.CAPACITY_LIMITS.SECTORS_BASED) 
        sectors_limit = struct.unpack('<Q', f.read(8))[0]
        results['sectors_limit_tb'] = (sectors_limit * 512) / (1024**4)
        
        return results

# Usage
results = analyze_firmware('extracted/secondary.elf')
print(f"Current capacity limit: {results['bytes_limit_tb']:.1f} TB")
```

## Best Practices

### 1. Version Compatibility
- Always verify firmware version before using offsets
- Test offsets against known firmware checksums
- Backup original files before modification

### 2. Offset Validation
```python
def validate_offset(filename, offset, expected_pattern):
    """Validate offset contains expected data pattern"""
    with open(filename, 'rb') as f:
        f.seek(offset)
        data = f.read(len(expected_pattern))
        return data == expected_pattern

# Example validation
protection_pattern = b'mbProtectionMode'  # Expected near offset
is_valid = validate_offset('secondary.elf', 
                          DroboOffsets.STRINGS.PROTECTION_MODE_LABEL, 
                          protection_pattern)
```

### 3. Error Handling
```python
def safe_patch(filename, offset, data):
    """Safely patch firmware with validation"""
    try:
        # Validate offset is patchable
        if not DroboOffsets.is_patchable_offset(offset):
            raise ValueError(f"Offset {hex(offset)} is not in patchable region")
        
        # Create backup
        shutil.copy(filename, f"{filename}.backup")
        
        # Apply patch
        with open(filename, 'r+b') as f:
            f.seek(offset)
            f.write(data)
            
        return True
        
    except Exception as e:
        print(f"Patch failed: {e}")
        return False
```

## File Formats Summary

| Format | Use Case | Pros | Cons |
|--------|----------|------|------|
| JSON | Web apps, APIs | Human readable, widely supported | Larger file size |
| CSV | Databases, Excel | Easy import, flat structure | Limited nesting |
| Python | Scripts, automation | Type safety, utility functions | Language specific |

Choose the format that best fits your application's requirements and programming language ecosystem.