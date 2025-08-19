# Drobo 5D3 JBOD/Passthrough Analysis Checklist

## Bypass Lock System
Priority: HIGH
Description: Bypass lock system - most promising for JBOD enablement

### Functions to Analyze:
- [ ] bypassLocksCommand
- [ ] bypassLocksCommandHandler
- [ ] SetLockBypass
- [ ] bypassLocks

### Target Strings:
- [ ] "Usage: bypassLocks [true|false]"
- [ ] "Setting lock bypass to"
- [ ] "Diags bypass locks feature is ENABLED"
- [ ] "Bypass of CATM lock is ENABLED"

### Analysis Focus:
- [ ] Find function that processes bypassLocks command
- [ ] Locate boolean flag that controls bypass state
- [ ] Identify what locks are bypassed when enabled
- [ ] Check if bypass affects disk access mode

---

## Esa Passthrough
Priority: HIGH
Description: ESA (Enclosure Services Agent) passthrough system

### Functions to Analyze:
- [ ] esaPassthroughCommand
- [ ] esaPassthroughCommand::parseCommandLine
- [ ] esaPassthroughCommand::ExecuteCommand
- [ ] DebugClass::esaPassthroughCommand

### Target Strings:
- [ ] "esaPassthroughCommand: parseCommandLine->"
- [ ] "esaPassthroughCommand: ExecuteCommand start,argc="
- [ ] "esaPassthroughCommand: ExecuteCommand done, time="
- [ ] "ESA: executing command"

### Analysis Focus:
- [ ] Understand ESA command structure and parameters
- [ ] Find how esapass command routes to individual drives
- [ ] Identify authentication/permission checks
- [ ] Map command flow from console to drive hardware

---

## Usb Direct Access
Priority: MEDIUM
Description: USB Direct Access mode for SCSI passthrough

### Functions to Analyze:
- [ ] usb2MscDirectAccessScsiPassThrough
- [ ] usb2MscDirectAccessIoctl
- [ ] USB2_MSC_DA_SCSI_PASS_THROUGH

### Target Strings:
- [ ] "ERRR: usb2Msc - Direct Access not enabled"
- [ ] "usb2Msc - USB2_MSC_DA_SCSI_PASS_THROUGH"
- [ ] "ERRR: usb2Msc - PassThrough failed, can not allow IO"

### Analysis Focus:
- [ ] Find the check that returns 'Direct Access not enabled'
- [ ] Locate the flag/condition that enables direct access
- [ ] Understand USB mass storage device passthrough flow
- [ ] Identify how to enable compliance test mode

---

## J2 Journal Bypass
Priority: MEDIUM
Description: J2 journal passthrough mode

### Functions to Analyze:
- [ ] J2Manager
- [ ] J2PassthroughMode
- [ ] SetJ2PassthroughMode

### Target Strings:
- [ ] "J2 journal pass through mode is disabled"
- [ ] "J2Manager Perf info"
- [ ] "j2 = J2Manager Perf info"

### Analysis Focus:
- [ ] Find J2 journal bypass enable/disable mechanism
- [ ] Understand how journal bypass affects disk I/O
- [ ] Locate configuration storage for passthrough mode
- [ ] Check interaction with RAID protection

---

## Disk Manager Bypass
Priority: MEDIUM
Description: Disk Manager bypass queue functionality

### Functions to Analyze:
- [ ] DiskManager::FlushAllDisksBypassQueue
- [ ] dm_flushbypass_handler
- [ ] flushbypass

### Target Strings:
- [ ] "Usage:  dm  flushbypass  - does sequential disk flush on all disks"
- [ ] "Finished DiskManager::GetInstance().FlushAllDisksBypassQueue()"
- [ ] "ERROR: unmapBlocksBypassQueue on disk"

### Analysis Focus:
- [ ] Understand bypass queue vs normal queue differences
- [ ] Find how flushbypass enables sequential disk access
- [ ] Check if bypass queue can be used for general I/O
- [ ] Identify performance and protection trade-offs

---