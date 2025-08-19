# Drobo 5D3 Firmware Analysis and Patching Guide

## Overview
This guide demonstrates how to analyze and patch VxWorks firmware in the Drobo 5D3 to remove the 2TB drive size limit. The process involves extracting firmware components, locating hardcoded limits, and applying binary patches.

## Project Structure
```
drobo-fw/
├── README.md                     # This guide
├── docs/                         # Complete documentation and analysis
│   ├── analysis/                 # Research findings and technical analysis
│   ├── reference/                # User and developer reference guides
│   └── data/                     # Machine-readable offset data
├── tools/                        # Utility modules (offsets.py, etc.)
├── scripts/                      # Analysis and modification tools
│   ├── extraction/               # Firmware extraction tools
│   ├── analysis/                 # Analysis and search tools
│   └── patching/                 # Binary patching tools
├── firmware/                     # Original firmware files
├── extracted/                    # Extracted firmware components
└── backups/                      # Backup files
```

## 📚 Documentation
- **[Complete Analysis](docs/analysis/analysis-summary.md)** - Executive summary of findings
- **[RAID Architecture](docs/analysis/raid-controller-analysis.md)** - Technical deep dive
- **[Programming Guide](docs/reference/offset-usage-guide.md)** - Integration examples
- **[Protection Modes](docs/reference/protection-modes-reference.md)** - RAID configuration

## Prerequisites

### Required Tools
```bash
# Install analysis tools
sudo apt-get install binwalk hexdump python3 build-essential
pip3 install binwalk

# Optional: Ghidra for advanced analysis
# Download from: https://ghidra-sre.org/
```

## Quick Start

### 1. Extract Firmware Components
```bash
# From scripts/extraction/ directory
cd scripts/extraction/
python3 extract_all_components.py [firmware_file.tdf]
```

### 2. Analyze for Patch Targets
```bash
# From scripts/analysis/ directory  
cd scripts/analysis/
python3 find_patch_targets.py
```

### 3. Apply 2TB Limit Patch
```bash
# From scripts/patching/ directory
cd scripts/patching/
python3 patch_2tb_limit.py
```

## Detailed Workflow

## Step 1: Firmware Structure Analysis

### Initial Reconnaissance
```bash
# Identify firmware structure
binwalk firmware/release.Drobo5D3.4-2-3.tdf

# Examine file header
hexdump -C firmware/release.Drobo5D3.4-2-3.tdf | head -10

# Check for strings and identify components
strings firmware/release.Drobo5D3.4-2-3.tdf | grep -i -E "(drobo|vxworks|wind)" | head -20
```

**Expected Output:**
- ELF binaries at offsets 0x22C and 0x303124
- VxWorks WIND kernel version 2.13 at 0xF59BFC
- TDIH header with "Marvin" target name

## Step 2: Component Extraction

### Extract Firmware Components
```bash
# From scripts/extraction/ directory
cd scripts/extraction/
python3 extract_all_components.py

# Verify extracted files in extracted/ directory
ls -la ../../extracted/
file ../../extracted/*.elf ../../extracted/*.bin
```

**Key Components:**
- `main_vxworks.elf` (3MB) - Bootloader
- `secondary.elf` (12MB) - **Main application with Drobo logic**
- `vxworks_kernel.bin` (4.6MB) - VxWorks kernel

## Step 3: Target Identification

### Search for Capacity Limits
```bash
# From scripts/analysis/ directory
cd scripts/analysis/
python3 find_patch_targets.py

# Look for the smoking gun
strings ../../extracted/secondary.elf | grep -i "2tb\|dislocation"
```

**Critical Finding:**
```
"DPM::discoverDis: >2TB drive: Setting dislocation to 2TB"
```

### Locate Binary Constants
```bash
# Search for 2TB constants in various formats
python3 -c "
constants = {
    '2TB_sectors': 4294967296,      # 0x100000000 (2TB / 512 bytes)
    '2TB_binary': 2199023255552,    # 0x20000000000 (2^41 bytes)  
    '2TB_decimal': 2000000000000,   # 2*10^12 bytes
}
for name, value in constants.items():
    print(f'{name}: 0x{value:x} ({value:,})')
"

# Find constants in binary
hexdump -C extracted/secondary.elf | grep -E "00 00 00 01 00 00 00 00|00 00 00 00 02 00 00 00"
```

## Step 4: Detailed Analysis with Ghidra

### Load in Ghidra
1. **Import:** `extracted/secondary.elf`
2. **Processor:** ARM (little endian)
3. **Auto-analyze:** Enable all options
4. **Search strings:** "DPM::discoverDis: >2TB drive"
5. **Find cross-references** to locate the comparison function

### Identify Patch Locations
Look for code patterns like:
```c
if (drive_capacity > 0x100000000) {  // 2TB in sectors
    printf("DPM::discoverDis: >2TB drive: Setting dislocation to 2TB");
    effective_capacity = 0x100000000;  // ← Patch this constant
}
```

## Step 5: Binary Patching

### Create Targeted Patch
```bash
# From scripts/patching/ directory
cd scripts/patching/
python3 patch_2tb_limit.py

# The script will:
# 1. Backup the original file to backups/
# 2. Locate 2TB constants in extracted/secondary.elf
# 3. Replace with larger limits (e.g., 32TB)
# 4. Verify the patch
```

**Manual Patching Alternative:**
```bash
# Find exact offset of 2TB constant
python3 -c "
import struct
with open('../../extracted/secondary.elf', 'rb') as f:
    data = f.read()
    pattern = struct.pack('<Q', 4294967296)  # 2TB sectors
    offset = data.find(pattern)
    print(f'2TB constant at: 0x{offset:x}')
"

# Patch with hexeditor or dd
# Replace 0x100000000 with 0x800000000 (32TB sectors)
```

## Step 6: Firmware Reconstruction

### Rebuild TDF Container
```bash
# Create rebuild script
cat > rebuild_tdf.py << 'EOF'
#!/usr/bin/env python3
import struct

def rebuild_firmware():
    # Read original TDF
    with open('../release.Drobo5D3.4-2-3.tdf', 'rb') as f:
        original = f.read()
    
    # Read patched secondary.elf
    with open('secondary.elf', 'rb') as f:
        patched = f.read()
    
    # Rebuild: header + patched_secondary + remaining_components
    before = original[:3158308]  # Before secondary.elf
    after = original[16096252:]  # After secondary.elf (VxWorks kernel)
    
    # Ensure proper padding
    padding = 16096252 - 3158308 - len(patched)
    if padding > 0:
        new_firmware = before + patched + b'\x00' * padding + after
    else:
        new_firmware = before + patched + after
    
    with open('release.Drobo5D3.4-2-3.PATCHED.tdf', 'wb') as f:
        f.write(new_firmware)
    
    print(f"✓ Created patched firmware: {len(new_firmware):,} bytes")

rebuild_firmware()
EOF

python3 rebuild_tdf.py
```

## Step 7: Verification and Testing

### Pre-Flash Verification
```bash
# Verify patched firmware structure
binwalk release.Drobo5D3.4-2-3.PATCHED.tdf

# Compare with original
diff <(binwalk release.Drobo5D3.4-2-3.tdf) \
     <(binwalk release.Drobo5D3.4-2-3.PATCHED.tdf)

# Check strings still exist
strings release.Drobo5D3.4-2-3.PATCHED.tdf | grep -i drobo | head -5
```

### Safe Testing Protocol
1. **Backup original firmware** from device
2. **Connect TTL serial cable** for recovery access
3. **Test with spare drives only** (no important data)
4. **Monitor boot process** via serial console
5. **Verify drive detection** with >2TB drives

## Step 8: Recovery Procedures

### TTL Serial Access
```bash
# Connect TTL adapter (3.3V):
# GND -> GND
# TX -> RX (device)  
# RX -> TX (device)

# Access VxWorks console
screen /dev/ttyUSB0 115200

# Available commands in VxWorks shell:
-> help
-> taskShow
-> driveShow
-> reboot
```

### Emergency Recovery
If device fails to boot:
1. **Power cycle** with TTL connected
2. **Interrupt boot process** (press any key during startup)
3. **Flash original firmware** via serial
4. **Use bootloader recovery mode** if available

## Tools Reference

### Essential Commands
```bash
# File analysis
file firmware.bin                    # Identify file type
hexdump -C firmware.bin | head      # View hex content
strings firmware.bin | grep text    # Extract strings
binwalk -E firmware.bin             # Entropy analysis
binwalk -A firmware.bin             # Architecture detection

# Binary editing
dd if=input of=output bs=1 skip=N   # Extract at offset
python3 -c "import struct; ..."     # Pack/unpack binary data
```

### Advanced Analysis
- **Ghidra:** Complete reverse engineering platform
- **Radare2:** Command-line binary analysis
- **IDA Pro:** Commercial disassembler (if available)
- **VxHunter:** VxWorks-specific analysis scripts

## Security Considerations

⚠️ **Legal Compliance:**
- Firmware modification may void warranty
- Follow responsible disclosure for vulnerabilities
- Respect intellectual property rights
- Consider DMCA exemptions for repair purposes

⚠️ **Safety Precautions:**
- Always backup original firmware
- Test on non-production systems
- Have recovery procedures ready
- Understand the risks of firmware modification

## Expected Results

After successful patching:
- Drobo 5D3 should accept drives >2TB
- Full capacity should be recognized and usable
- BeyondRAID should function normally with larger drives
- Performance should remain consistent

**Note:** This process requires technical expertise and carries inherent risks. Proceed only if you understand the implications and have appropriate recovery methods available.