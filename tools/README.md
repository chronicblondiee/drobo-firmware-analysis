# Tools Directory

This directory contains utility tools and modules for working with Drobo firmware analysis.

## Available Tools

### Core Module
#### `offsets.py`
Python module providing programmatic access to memory offsets and firmware constants.

**Features:**
- Type-safe offset constants using dataclasses
- Utility functions for hex conversion and capacity calculations
- Built-in validation for patchable memory regions
- Integration helpers for automated analysis

**Usage:**
```python
from offsets import DroboOffsets, ProtectionModes

# Access configuration offsets
protection_addr = DroboOffsets.CONFIG.PROTECTION_MODE
capacity_limit = DroboOffsets.CAPACITY_LIMITS.BYTES_BASED

# Utility functions
is_safe = DroboOffsets.is_patchable_offset(protection_addr)
tb_value = bytes_to_tb(capacity_limit)
```

**Testing:**
```bash
cd tools/
python3 offsets.py
```

### Utility Scripts

#### `capacity_patcher.py`
Patches 2TB capacity limits in Drobo firmware to specified larger values.

**Usage:**
```bash
python3 capacity_patcher.py <firmware_file> [new_limit_tb]
python3 capacity_patcher.py ../extracted/secondary.elf 64
```

**Features:**
- Automatic backup creation
- Precise offset-based patching using offsets.py
- Verification of applied patches
- Support for custom capacity limits

#### `firmware_analyzer.py`
Automated firmware analysis tool that reads configuration settings and capacity limits.

**Usage:**
```bash
python3 firmware_analyzer.py <firmware_file>
python3 firmware_analyzer.py ../extracted/secondary.elf
```

**Output:**
- Protection mode settings
- Current capacity limits
- Configuration flags (large pack mode, LED management)
- Memory locations of key settings
- Patch status detection

#### `header_generator.py`
Generates C/C++ header files with offset constants for integration with C-based tools.

**Usage:**
```bash
python3 header_generator.py [output_file]
python3 header_generator.py ../firmware_offsets.h
```

**Features:**
- Complete offset definitions as C macros
- Utility macros for capacity conversions
- Validation macros for patchable regions
- Module identifier constants

#### `ghidra_bookmarks.py`
Creates bookmarks in Ghidra at key firmware locations for analysis.

**Usage:**
- In Ghidra: Run via Script Manager
- Standalone: Prints bookmark locations for manual creation

**Features:**
- Automatic bookmark creation at critical offsets
- Organized by categories (Config, Limits, Strings)
- Ghidra Python API integration
- Fallback mode for manual bookmark creation

## Integration with Scripts

The tools in this directory are designed to work with the analysis scripts in `../scripts/`:

### Example Integration
```python
import sys
sys.path.append('../tools')
from offsets import DroboOffsets

# Use in patching script
def patch_protection_mode(filename, mode):
    with open(filename, 'r+b') as f:
        f.seek(DroboOffsets.CONFIG.PROTECTION_MODE)
        f.write(struct.pack('<I', mode))
```

## Future Tools

Planned additions:
- **Configuration editor**: GUI tool for protection mode management
- **Firmware validator**: Checksum and integrity verification
- **Offset finder**: Automated offset discovery for new firmware versions
- **Patch generator**: Template-based patch creation system

## Dependencies

- **Python 3.6+** for offsets.py
- **Standard library only** - no external dependencies required