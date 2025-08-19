# Environment Variables Configuration

This document describes the environment variables used by the Drobo firmware analysis tools to simplify file path management and improve workflow flexibility.

## Available Environment Variables

### Core Path Variables

#### `DROBO_FIRMWARE_PATH`
**Purpose**: Default directory containing original firmware files (TDF and ZIP formats)
**Default**: `../firmware` (relative to script location)
**Usage**: Used by extraction scripts and tools that process original firmware

```bash
export DROBO_FIRMWARE_PATH="/path/to/your/firmware/directory"
```

#### `DROBO_EXTRACTED_PATH`
**Purpose**: Default directory containing extracted firmware components (ELF and binary files)
**Default**: `../extracted` (relative to script location)
**Usage**: Used by analysis and patching tools that work with extracted components

```bash
export DROBO_EXTRACTED_PATH="/path/to/your/extracted/directory"
```

## Usage Examples

### Setting Environment Variables

#### Temporary (Current Session)
```bash
# Set for current terminal session
export DROBO_FIRMWARE_PATH="/home/user/drobo-firmware"
export DROBO_EXTRACTED_PATH="/home/user/drobo-extracted"

# Run tools with simplified paths
python3 capacity_patcher.py secondary.elf 64
python3 firmware_analyzer.py secondary.elf
```

#### Permanent (Shell Profile)
```bash
# Add to ~/.bashrc, ~/.zshrc, or ~/.profile
echo 'export DROBO_FIRMWARE_PATH="/home/user/drobo-firmware"' >> ~/.bashrc
echo 'export DROBO_EXTRACTED_PATH="/home/user/drobo-extracted"' >> ~/.bashrc
source ~/.bashrc
```

#### Per-Command
```bash
# Set for single command execution
DROBO_EXTRACTED_PATH="/custom/path" python3 firmware_analyzer.py secondary.elf
```

### Tool-Specific Usage

#### Extraction Scripts
```bash
# Default behavior (uses DROBO_FIRMWARE_PATH or ../firmware)
cd scripts/extraction/
python3 extract_all_components.py

# With custom firmware path
DROBO_FIRMWARE_PATH="/custom/firmware" python3 extract_all_components.py

# Specific file (absolute or relative paths still work)
python3 extract_all_components.py /absolute/path/to/firmware.tdf
python3 extract_all_components.py release.Drobo5D3.4-2-3.tdf
```

#### Analysis Tools
```bash
# Default behavior (searches DROBO_EXTRACTED_PATH, then DROBO_FIRMWARE_PATH)
cd tools/
python3 firmware_analyzer.py secondary.elf

# With custom extracted path
DROBO_EXTRACTED_PATH="/custom/extracted" python3 firmware_analyzer.py secondary.elf

# Absolute paths always work
python3 firmware_analyzer.py /full/path/to/secondary.elf
```

#### Patching Tools
```bash
# Simplified usage with environment variables
cd tools/
python3 capacity_patcher.py secondary.elf 64

# Override paths per command
DROBO_EXTRACTED_PATH="/backup/extracted" python3 capacity_patcher.py secondary.elf 32
```

## Path Resolution Logic

All tools follow this path resolution order:

1. **Absolute Path**: If provided path is absolute, use as-is
2. **Relative Path Exists**: If relative path exists from current directory, use as-is
3. **DROBO_EXTRACTED_PATH**: Try filename in extracted directory (analysis/patching tools)
4. **DROBO_FIRMWARE_PATH**: Try filename in firmware directory (all tools)
5. **Original Path**: Fall back to original filename (will cause error if not found)

### Example Resolution
```bash
# Given: python3 firmware_analyzer.py secondary.elf
# With: DROBO_EXTRACTED_PATH="/home/user/extracted"

# Resolution attempts:
# 1. /absolute/path/secondary.elf (if absolute)
# 2. ./secondary.elf (if exists in current dir)
# 3. /home/user/extracted/secondary.elf (DROBO_EXTRACTED_PATH)
# 4. ../firmware/secondary.elf (DROBO_FIRMWARE_PATH fallback)
# 5. secondary.elf (original, will likely fail)
```

## Tool Compatibility

### Tools with Environment Variable Support

#### Tools Directory (`tools/`)
- ✅ `capacity_patcher.py` - Uses both DROBO_EXTRACTED_PATH and DROBO_FIRMWARE_PATH
- ✅ `firmware_analyzer.py` - Uses both DROBO_EXTRACTED_PATH and DROBO_FIRMWARE_PATH
- ✅ `header_generator.py` - Inherits from offsets.py
- ✅ `ghidra_bookmarks.py` - Inherits from offsets.py

#### Scripts Directory (`scripts/`)
- ✅ `scripts/extraction/extract_all_components.py` - Uses DROBO_FIRMWARE_PATH
- ✅ `scripts/extraction/extract_tdih.py` - Uses DROBO_FIRMWARE_PATH
- ✅ `scripts/analysis/find_patch_targets.py` - Uses relative paths to extracted/
- ✅ `scripts/patching/patch_2tb_limit.py` - Uses relative paths to extracted/

### Legacy Compatibility
All tools maintain backward compatibility with existing scripts and workflows:
- Absolute paths work unchanged
- Relative paths work unchanged
- Default relative paths (`../firmware`, `../extracted`) work unchanged

## Workflow Recommendations

### Development Setup
```bash
# Set up environment for development
export DROBO_FIRMWARE_PATH="$HOME/drobo-analysis/firmware"
export DROBO_EXTRACTED_PATH="$HOME/drobo-analysis/extracted"
export DROBO_BACKUPS_PATH="$HOME/drobo-analysis/backups"

# Create directories
mkdir -p "$DROBO_FIRMWARE_PATH" "$DROBO_EXTRACTED_PATH" "$DROBO_BACKUPS_PATH"

# Copy firmware files to firmware directory
cp *.tdf "$DROBO_FIRMWARE_PATH/"

# Run extraction
cd scripts/extraction/
python3 extract_all_components.py release.Drobo5D3.4-2-3.tdf

# Analyze extracted firmware
cd ../../tools/
python3 firmware_analyzer.py secondary.elf
```

### Multiple Firmware Versions
```bash
# Analyze different firmware versions
export DROBO_FIRMWARE_PATH="/analysis/firmware-4.2.3"
export DROBO_EXTRACTED_PATH="/analysis/extracted-4.2.3"
python3 firmware_analyzer.py secondary.elf

export DROBO_FIRMWARE_PATH="/analysis/firmware-4.3.1"
export DROBO_EXTRACTED_PATH="/analysis/extracted-4.3.1"
python3 firmware_analyzer.py secondary.elf
```

### CI/CD Integration
```bash
# GitHub Actions / CI environment
export DROBO_FIRMWARE_PATH="/github/workspace/firmware"
export DROBO_EXTRACTED_PATH="/github/workspace/extracted"

# Tools work without path modifications
python3 tools/firmware_analyzer.py secondary.elf
```

## Troubleshooting

### Path Resolution Issues
```bash
# Check current environment variables
echo "DROBO_FIRMWARE_PATH: $DROBO_FIRMWARE_PATH"
echo "DROBO_EXTRACTED_PATH: $DROBO_EXTRACTED_PATH"

# Verify directory contents
ls -la "$DROBO_EXTRACTED_PATH"
ls -la "$DROBO_FIRMWARE_PATH"
```

### Debug Path Resolution
Most tools show the resolved path when run:
```bash
$ python3 firmware_analyzer.py secondary.elf
Resolved firmware path: /home/user/extracted/secondary.elf
Analyzing firmware: /home/user/extracted/secondary.elf
...
```

### Common Issues
1. **File Not Found**: Check that environment variables point to correct directories
2. **Permission Denied**: Ensure read permissions on firmware directories
3. **Wrong File**: Verify filename matches what's in the target directory

## Integration with IDEs

### VS Code
Add to workspace settings (`.vscode/settings.json`):
```json
{
    "terminal.integrated.env.linux": {
        "DROBO_FIRMWARE_PATH": "/workspace/firmware",
        "DROBO_EXTRACTED_PATH": "/workspace/extracted"
    },
    "terminal.integrated.env.osx": {
        "DROBO_FIRMWARE_PATH": "/workspace/firmware", 
        "DROBO_EXTRACTED_PATH": "/workspace/extracted"
    },
    "terminal.integrated.env.windows": {
        "DROBO_FIRMWARE_PATH": "C:\\workspace\\firmware",
        "DROBO_EXTRACTED_PATH": "C:\\workspace\\extracted"
    }
}
```

### PyCharm
Set in Run Configuration environment variables or in Settings > Build, Execution, Deployment > Console > Python Console > Environment variables.

This environment variable system makes the tools more flexible while maintaining full backward compatibility with existing workflows.