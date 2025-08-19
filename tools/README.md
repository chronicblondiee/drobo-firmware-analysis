# Tools Directory

This directory contains utility tools and modules for working with Drobo firmware analysis.

## Available Tools

### `offsets.py`
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