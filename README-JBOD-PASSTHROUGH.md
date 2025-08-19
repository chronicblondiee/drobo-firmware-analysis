# Drobo 5D3 JBOD/Passthrough Functionality Research

## Overview

This document outlines the complete discovery, analysis, and testing procedures for enabling JBOD (Just a Bunch of Disks) and passthrough functionality in Drobo 5D3 firmware. Through systematic firmware analysis, multiple bypass and passthrough mechanisms have been identified and documented.

## Executive Summary

The Drobo 5D3 firmware contains several built-in mechanisms for bypassing BeyondRAID protection and enabling direct disk access:

1. **Bypass Lock System** - Disables BeyondRAID protection locks
2. **ESA Passthrough System** - Direct command passthrough via Enclosure Services Agent
3. **USB Direct Access Mode** - SCSI passthrough to individual drives (currently disabled)
4. **J2 Journal Passthrough** - Bypass transaction journaling system (currently disabled)
5. **Disk Manager Bypass** - Sequential disk access bypassing normal queues

## Project Structure

```
drobo-fw/
├── docs/
│   ├── jbod-passthrough-testing.md     # Complete testing procedures
│   └── analysis/
│       ├── ghidra_jbod_analysis.py     # Automated Ghidra analysis script
│       ├── jbod_analysis_checklist.md  # Manual analysis checklist
│       └── analysis_targets.json       # Programmatic analysis targets
├── scripts/
│   ├── test-jbod-passthrough.sh        # Interactive testing script
│   └── analysis/
│       └── ghidra-analysis-targets.py  # Analysis file generator
├── logs/                               # Test results and documentation
└── extracted/
    ├── secondary.elf                   # Main application with JBOD logic
    ├── main_vxworks.elf               # Bootloader
    └── vxworks_kernel.bin             # VxWorks kernel
```

## Discovery Process

### Phase 1: String Analysis

Systematic analysis of firmware strings revealed multiple passthrough mechanisms:

```bash
# Primary discovery commands used:
strings secondary.elf | grep -i -E "(jbod|passthrough|bypass|direct)"
strings secondary.elf | grep -i "esa"
strings secondary.elf | grep -i -E "(enable|disable|mode)"
```

### Key Findings

**Bypass Lock System:**
- Command: `bypassLocks [true|false]`
- Status: "Diags bypass locks feature is ENABLED"
- Function: Disables BeyondRAID protection locks

**ESA Passthrough:**
- Commands: `esaPassthroughCommand`, `esapass`
- Functions: Direct command passthrough to drives
- Debug interface: "ESA: executing command"

**USB Direct Access:**
- Functions: `usb2MscDirectAccessScsiPassThrough`
- Status: "ERRR: usb2Msc - Direct Access not enabled"
- Target: Enable SCSI passthrough functionality

**J2 Journal Bypass:**
- Status: "J2 journal pass through mode is disabled"
- Function: Bypass transaction journaling system

**Disk Manager Bypass:**
- Command: `dm flushbypass`
- Function: "does sequential disk flush on all disks"
- Effect: Direct disk access bypassing normal queues

## Testing Procedures

### Hardware Requirements

- TTL Serial adapter (3.3V UART)
- Jumper wires
- Test drives (no production data)
- Serial terminal software (screen, minicom)

### Connection Setup

```
TTL Serial Adapter (3.3V) -> Drobo 5D3
GND (Black)  -> GND
TX  (White)  -> RX  (Drobo)
RX  (Green)  -> TX  (Drobo)
VCC          -> DO NOT CONNECT

WARNING: Use 3.3V adapter only, NOT 5V
```

### Serial Console Access

```bash
# Access VxWorks console
screen /dev/ttyUSB0 115200

# Alternative terminal programs:
minicom -D /dev/ttyUSB0 -b 115200
picocom /dev/ttyUSB0 -b 115200
```

### Testing Protocol

#### Phase 1: Console Access Verification
```bash
# Boot sequence verification:
# 1. Bootloader messages
# 2. VxWorks kernel loading  
# 3. Drobo application startup
# 4. VxWorks shell prompt: ->

# Basic console verification:
-> help                    # List available commands
-> version                 # Check firmware version
-> taskShow               # Show running tasks
-> memShow                # Show memory usage
```

#### Phase 2: Bypass Lock Testing (Safest)
```bash
# Check current bypass status:
-> bypassLocks            # Show current state

# Enable bypass mode:
-> bypassLocks true       # Enable lock bypass
# Expected: "Setting lock bypass to true"

# Test disk manager bypass:
-> dm flushbypass         # Sequential disk flush
# Expected: Direct disk access without queue

# Verify bypass status:
-> dm                     # Show disk manager info
```

#### Phase 3: ESA Passthrough Testing
```bash
# Access ESA system:
-> esa                    # Show ESA commands
-> esapass               # Test passthrough command

# ESA diagnostic commands:
-> esa disDump <slot> <LBA> <records>    # Direct disk diagnostics
-> esa wipeDisk <slot>                   # Direct disk access
-> esa seekTest <slot>                   # Direct seek testing
```

#### Phase 4: Advanced Command Discovery
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

### Safety Protocols

**Pre-Testing Checklist:**
- TTL serial adapter verified at 3.3V
- Backup important data from Drobo
- Test drives only (no production data)
- Serial console connection tested
- Recovery procedure understood

**During Testing:**
- Monitor all command outputs
- Document unexpected behavior
- Test one command at a time
- Verify system stability after each test

**Recovery Procedures:**
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

## Automated Testing Tools

### Interactive Testing Script

```bash
# Run the automated setup and testing script:
cd /home/brown/drobo-fw
./scripts/test-jbod-passthrough.sh

# Available options:
./scripts/test-jbod-passthrough.sh setup      # Hardware setup guide
./scripts/test-jbod-passthrough.sh commands   # Show test commands
./scripts/test-jbod-passthrough.sh console    # Start serial session
```

### Features:
- Hardware connection verification
- Dependency checking
- Safety warnings and protocols
- Test command reference
- Automatic logging
- Recovery procedures

## Ghidra Analysis

### Automated Analysis

```bash
# Generate analysis files:
cd scripts/analysis
python3 ghidra-analysis-targets.py

# This creates:
# - docs/analysis/ghidra_jbod_analysis.py
# - docs/analysis/jbod_analysis_checklist.md  
# - docs/analysis/analysis_targets.json
```

### Ghidra Workflow

1. **Import Firmware:**
   - Load: `extracted/secondary.elf`
   - Processor: ARM (little endian)
   - Auto-analyze: Enable all options

2. **Run Analysis Script:**
   - Execute: `docs/analysis/ghidra_jbod_analysis.py`
   - Creates bookmarks for target functions
   - Exports results to JSON

3. **Manual Analysis:**
   - Follow: `docs/analysis/jbod_analysis_checklist.md`
   - Focus on high-priority targets
   - Document function flows and dependencies

### Analysis Targets

**High Priority:**
- `bypassLocksCommand` - Bypass lock system
- `esaPassthroughCommand` - ESA passthrough system

**Medium Priority:**
- `usb2MscDirectAccessScsiPassThrough` - USB direct access
- `J2Manager` - Journal bypass system
- `DiskManager::FlushAllDisksBypassQueue` - Disk manager bypass

## Expected Results

### Command Testing Outcomes

**bypassLocks true:**
```
Expected Output: "Setting lock bypass to true"
Effect: Disables BeyondRAID protection locks
```

**dm flushbypass:**
```
Expected Output: "Finished DiskManager::GetInstance().FlushAllDisksBypassQueue()"
Effect: Sequential disk access bypassing normal queue
```

**esapass [parameters]:**
```
Expected Output: 
esaPassthroughCommand: parseCommandLine->
esaPassthroughCommand: ExecuteCommand start,argc=X
esaPassthroughCommand: ExecuteCommand done, time=X
Effect: Direct command passthrough to drives
```

### Success Scenarios

**Best Case:**
- `bypassLocks true` enables JBOD mode immediately
- Individual drives become accessible via host OS
- No firmware modification needed

**Partial Success:**
- Commands work but need additional configuration
- Some drives accessible, others need more work
- Provides foundation for targeted patches

**Needs Patches:**
- Commands exist but features disabled
- Use Ghidra analysis to find enable flags
- Apply binary patches similar to 2TB limit removal

## Implementation Strategy

### Phase 1: Command Interface Testing
1. TTL Serial Access (Safest method)
   - Connect to VxWorks debug console
   - Access ESA command interface
   - Test commands without firmware modification

2. Enable Debug Interface
   - Look for debug interface enablement flags
   - May require firmware patch to unlock

### Phase 2: Enable Bypass Features
```bash
# Via VxWorks console:
-> bypassLocks true
-> dm flushbypass
-> esapass [parameters]
```

### Phase 3: USB Direct Access Enablement
**Target:** Remove "Direct Access not enabled" restriction
- Binary patch approach: NOP out the check that returns this error
- Flag approach: Find configuration flag that enables direct access

### Phase 4: J2 Journal Bypass
**Target:** Enable "J2 journal pass through mode"
- Search for J2 configuration flags
- Patch journal bypass enable/disable logic

## Binary Patch Targets

### Likely Patch Locations

```c
// USB Direct Access check:
if (!directAccessEnabled) {  // <- Patch this check
    return "Direct Access not enabled";
}

// Bypass locks mode:
if (!bypassLocksMode) {      // <- Or enable this flag
    return error;
}

// J2 journal passthrough:
if (!j2PassthroughEnabled) { // <- Enable this mode
    return "J2 journal pass through mode is disabled";
}
```

### Patch Development Process

1. **Locate Functions:**
   - Use Ghidra to find exact function addresses
   - Identify conditional checks and boolean flags
   - Map string references to code locations

2. **Create Patches:**
   - NOP out restriction checks
   - Set enable flags to true
   - Modify boolean constants

3. **Apply Patches:**
   - Use existing patching framework from 2TB limit removal
   - Backup original firmware
   - Test incrementally

## Risk Assessment

**Low Risk (Serial console testing):**
- Test existing commands via TTL without firmware modification
- `bypassLocks true/false` - Reversible setting
- No permanent changes to firmware

**Medium Risk (Configuration patches):**
- Enable direct access by patching boolean flags
- J2 journal bypass enablement
- Reversible through firmware re-flash

**High Risk (Deep modifications):**
- Removing core BeyondRAID protections
- May affect data integrity if not done carefully
- Requires thorough testing and validation

## Troubleshooting

### Common Issues

**No console output:**
- Check TTL voltage (3.3V), connections
- Verify GND connection
- Test with multimeter

**Garbled text:**
- Verify baud rate (115200)
- Check TX/RX pin assignment
- Test different terminal programs

**Command not found:**
- Check spelling, try variations
- Commands may be case-sensitive
- Use tab completion if available

**Permission denied:**
- Look for authentication mechanisms
- Check if debug mode needs enablement
- Verify system boot state

### Debug Commands

```bash
# Check task status:
-> taskShow | grep -i debug
-> taskShow | grep -i esa

# Memory/system info:
-> memShow
-> iosFdShow
-> devs

# Network and I/O:
-> netstat
-> routeShow
-> ifShow
```

## Documentation and Logging

### Test Log Format

```
Date: [YYYY-MM-DD]
Time: [HH:MM:SS]
Firmware Version: [Get from device]
Test Objective: [What are you testing?]

Console Session Log:
[Paste VxWorks console output here]

Test Results:
Command: [command tested]
Result: [SUCCESS/FAIL/PARTIAL]
Output: [console output]
Notes: [observations, side effects, etc.]

Next Steps:
[What to test next based on results]
```

### Files Created During Testing

- `logs/jbod-test-YYYYMMDD-HHMMSS.log` - Timestamped test logs
- `logs/test-template.txt` - Template for manual logging
- `/tmp/ghidra_analysis_results.json` - Ghidra analysis output

## Advantages of This Approach

**Existing Framework:**
- 2TB patch methodology applies directly
- VxWorks experience from previous analysis
- Established toolchain and procedures

**Multiple Vectors:**
- Several different approaches to achieve JBOD
- Redundant methods increase success probability
- Incremental testing reduces risk

**Safety First:**
- Serial console testing before firmware mods
- Reversible commands and settings
- Comprehensive recovery procedures

## Next Steps

### Immediate Actions

1. **Serial Console Testing:**
   - Connect TTL adapter to test commands safely
   - Document current command responses
   - Verify bypass functionality

2. **Ghidra Analysis:**
   - Load `secondary.elf` in Ghidra
   - Run automated analysis script
   - Follow manual analysis checklist

3. **Binary Analysis:**
   - Locate "Direct Access not enabled" check
   - Find bypass lock configuration flags
   - Identify J2 passthrough toggle mechanisms

### Long-term Goals

1. **Firmware Patches:**
   - Develop permanent enablement patches
   - Create automated patching tools
   - Integrate with existing patch framework

2. **Validation:**
   - Test with >2TB drives in JBOD mode
   - Verify host OS recognition
   - Performance and stability testing

3. **Documentation:**
   - Complete user guide for JBOD enablement
   - Technical reference for developers
   - Safety and recovery procedures

## Legal and Safety Considerations

**Legal Compliance:**
- Firmware modification may void warranty
- Follow responsible disclosure for vulnerabilities
- Respect intellectual property rights
- Consider DMCA exemptions for repair purposes

**Safety Precautions:**
- Always backup original firmware
- Test on non-production systems first
- Have recovery procedures ready
- Understand risks of firmware modification

**Data Protection:**
- Use test drives without important data
- Backup all data before testing
- Verify data integrity after modifications
- Document all changes for reversal

## Conclusion

The Drobo 5D3 firmware contains comprehensive JBOD and passthrough functionality that can be accessed through multiple mechanisms. The safest approach is serial console testing of existing commands, followed by targeted binary patches for permanent enablement.

This research provides a complete framework for:
- Safe discovery and testing of hidden functionality
- Systematic analysis using professional tools
- Risk-managed implementation with recovery procedures
- Documentation for reproducible results

The combination of existing bypass commands and potential firmware patches offers multiple paths to achieving JBOD functionality while maintaining system stability and data integrity.
