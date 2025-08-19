# Drobo 5D3 JBOD/Passthrough Testing Guide

## Overview
This guide provides step-by-step procedures to safely test discovered JBOD/passthrough functionality in Drobo 5D3 firmware without modifying the firmware binary.

## Discovered Passthrough Mechanisms

### 1. **ESA Passthrough System** ⭐
- **Commands**: `esaPassthroughCommand`, `esapass`
- **Function**: Direct command passthrough via ESA interface
- **Status**: Active command system

### 2. **Bypass Lock System** ⭐⭐⭐ (Primary Target)
- **Command**: `bypassLocks [true|false]`
- **Function**: Disables BeyondRAID protection locks
- **Features**:
  - Diags bypass locks (currently ENABLED)
  - CATM lock bypass (currently ENABLED)
  - `dm flushbypass` - Sequential disk access

### 3. **USB Direct Access Mode** ⭐⭐
- **Commands**: USB2_MSC_DA_* series
- **Status**: Currently disabled
- **Target**: Enable for SCSI passthrough

### 4. **J2 Journal Passthrough** ⭐
- **Status**: Currently disabled
- **Function**: Bypass transaction journaling

## TTL Serial Console Setup

### Hardware Connection
```bash
# TTL Serial Adapter (3.3V) Connections:
# Drobo Pin -> TTL Adapter
# GND       -> GND
# TX        -> RX  
# RX        -> TX
# 
# DO NOT CONNECT VCC (Power supplied by Drobo)
```

### Console Access
```bash
# Access VxWorks console
screen /dev/ttyUSB0 115200

# Alternative terminal programs:
# minicom -D /dev/ttyUSB0 -b 115200
# picocom /dev/ttyUSB0 -b 115200
```

## Testing Protocol

### Phase 1: Console Access Verification
```bash
# Boot sequence - you should see:
# 1. Bootloader messages
# 2. VxWorks kernel loading
# 3. Drobo application startup
# 4. Final: VxWorks shell prompt: ->

# Basic console verification:
-> help                    # List available commands
-> version                 # Check firmware version  
-> taskShow               # Show running tasks
-> memShow                # Show memory usage
```

### Phase 2: Bypass Lock Testing (SAFEST)
```bash
# Check current bypass status:
-> bypassLocks            # Should show current state

# Enable bypass mode:
-> bypassLocks true       # Enable lock bypass
# Expected: "Setting lock bypass to true"

# Test disk manager bypass:
-> dm flushbypass         # Sequential disk flush
# Expected: Direct disk access without queue

# Verify bypass status:
-> dm                     # Show disk manager info
```

### Phase 3: ESA Passthrough Testing  
```bash
# Access ESA system:
-> esa                    # Show ESA commands
-> esapass               # Test passthrough command

# ESA diagnostic commands:
-> esa disDump <slot> <LBA> <records>    # Direct disk diagnostics
-> esa wipeDisk <slot>                   # Direct disk access
-> esa seekTest <slot>                   # Direct seek testing
```

### Phase 4: Advanced Command Discovery
```bash
# Test discovered command patterns:
-> j2                     # J2 Manager commands
-> dm                     # Disk Manager commands  
-> usb2Msc               # USB Mass Storage commands

# Look for hidden debug commands:
-> ?                     # Alternative help
-> debug                 # Debug interface
-> diag                  # Diagnostic commands
```

## Safety Protocols

### Pre-Testing Checklist
- [ ] TTL serial adapter verified at 3.3V
- [ ] Backup important data from Drobo
- [ ] Test drives only (no production data)
- [ ] Serial console connection tested
- [ ] Recovery procedure understood

### During Testing
- [ ] Monitor all command outputs
- [ ] Document unexpected behavior
- [ ] Test one command at a time
- [ ] Verify system stability after each test

### Recovery Procedures
```bash
# If system becomes unstable:
-> reboot                # Soft reboot
# Power cycle if soft reboot fails

# Reset bypass locks:
-> bypassLocks false     # Disable bypass mode

# Emergency shell access:
# Power cycle with serial connected
# Interrupt boot if necessary
```

## Expected Results by Command

### `bypassLocks true`
**Expected Output:**
```
Setting lock bypass to true
Diags bypass locks feature is ENABLED
```
**Effect**: Disables BeyondRAID protection locks, allowing direct disk access

### `dm flushbypass`  
**Expected Output:**
```
Usage: dm flushbypass - does sequential disk flush on all disks
Finished DiskManager::GetInstance().FlushAllDisksBypassQueue()
```
**Effect**: Sequential disk access bypassing normal queue

### `esapass [parameters]`
**Expected Output:**
```
esaPassthroughCommand: parseCommandLine->
esaPassthroughCommand: ExecuteCommand start,argc=X
esaPassthroughCommand: ExecuteCommand done, time=X
```
**Effect**: Direct command passthrough to drives

## Documentation Template

### Test Log Format
```
Date: [DATE]
Firmware: [VERSION]
Test: [COMMAND]
Result: [SUCCESS/FAIL]
Output: [CONSOLE_OUTPUT]
Notes: [OBSERVATIONS]
```

### Example Entry
```
Date: 2024-01-XX
Firmware: 4.2.3
Test: bypassLocks true
Result: SUCCESS
Output: Setting lock bypass to true
Notes: Command executed successfully, no error messages
```

## Next Steps After Testing

### If Commands Work:
1. Document full command syntax and parameters
2. Test with actual >2TB drives
3. Verify JBOD functionality through host OS
4. Consider firmware patches for permanent enablement

### If Commands Fail:
1. Check for authentication/privilege requirements
2. Look for additional enable flags
3. Consider firmware modification approach
4. Analyze command handler functions in Ghidra

## Troubleshooting

### Common Issues
- **No console output**: Check TTL voltage (3.3V), connections
- **Garbled text**: Verify baud rate (115200)
- **Command not found**: Check spelling, try variations
- **Permission denied**: Look for authentication mechanisms

### Debug Tips
```bash
# Check task status:
-> taskShow | grep -i debug
-> taskShow | grep -i esa

# Memory/system info:
-> memShow
-> iosFdShow
-> devs
```

This testing approach allows us to explore JBOD functionality safely before making any firmware modifications.
