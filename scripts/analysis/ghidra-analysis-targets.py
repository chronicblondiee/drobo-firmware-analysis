#!/usr/bin/env python3
"""
Ghidra Analysis Target Generator for Drobo 5D3 JBOD/Passthrough Research

This script generates a target list for Ghidra analysis based on our string analysis
findings. Use this to systematically analyze the bypass and passthrough functions.
"""

import json
import os

# Analysis targets discovered through string analysis
ANALYSIS_TARGETS = {
    "bypass_lock_system": {
        "priority": "HIGH",
        "description": "Bypass lock system - most promising for JBOD enablement",
        "functions": [
            "bypassLocksCommand",
            "bypassLocksCommandHandler", 
            "SetLockBypass",
            "bypassLocks"
        ],
        "strings": [
            "Usage: bypassLocks [true|false]",
            "Setting lock bypass to",
            "Diags bypass locks feature is ENABLED",
            "Bypass of CATM lock is ENABLED"
        ],
        "analysis_focus": [
            "Find function that processes bypassLocks command",
            "Locate boolean flag that controls bypass state",
            "Identify what locks are bypassed when enabled",
            "Check if bypass affects disk access mode"
        ]
    },
    
    "esa_passthrough": {
        "priority": "HIGH", 
        "description": "ESA (Enclosure Services Agent) passthrough system",
        "functions": [
            "esaPassthroughCommand",
            "esaPassthroughCommand::parseCommandLine",
            "esaPassthroughCommand::ExecuteCommand",
            "DebugClass::esaPassthroughCommand"
        ],
        "strings": [
            "esaPassthroughCommand: parseCommandLine->",
            "esaPassthroughCommand: ExecuteCommand start,argc=",
            "esaPassthroughCommand: ExecuteCommand done, time=",
            "ESA: executing command"
        ],
        "analysis_focus": [
            "Understand ESA command structure and parameters",
            "Find how esapass command routes to individual drives", 
            "Identify authentication/permission checks",
            "Map command flow from console to drive hardware"
        ]
    },
    
    "usb_direct_access": {
        "priority": "MEDIUM",
        "description": "USB Direct Access mode for SCSI passthrough",
        "functions": [
            "usb2MscDirectAccessScsiPassThrough",
            "usb2MscDirectAccessIoctl",
            "USB2_MSC_DA_SCSI_PASS_THROUGH"
        ],
        "strings": [
            "ERRR: usb2Msc - Direct Access not enabled",
            "usb2Msc - USB2_MSC_DA_SCSI_PASS_THROUGH",
            "ERRR: usb2Msc - PassThrough failed, can not allow IO"
        ],
        "analysis_focus": [
            "Find the check that returns 'Direct Access not enabled'",
            "Locate the flag/condition that enables direct access",
            "Understand USB mass storage device passthrough flow",
            "Identify how to enable compliance test mode"
        ]
    },
    
    "j2_journal_bypass": {
        "priority": "MEDIUM",
        "description": "J2 journal passthrough mode",
        "functions": [
            "J2Manager",
            "J2PassthroughMode", 
            "SetJ2PassthroughMode"
        ],
        "strings": [
            "J2 journal pass through mode is disabled",
            "J2Manager Perf info",
            "j2 = J2Manager Perf info"
        ],
        "analysis_focus": [
            "Find J2 journal bypass enable/disable mechanism",
            "Understand how journal bypass affects disk I/O",
            "Locate configuration storage for passthrough mode",
            "Check interaction with RAID protection"
        ]
    },
    
    "disk_manager_bypass": {
        "priority": "MEDIUM",
        "description": "Disk Manager bypass queue functionality",
        "functions": [
            "DiskManager::FlushAllDisksBypassQueue",
            "dm_flushbypass_handler",
            "flushbypass"
        ],
        "strings": [
            "Usage:  dm  flushbypass  - does sequential disk flush on all disks",
            "Finished DiskManager::GetInstance().FlushAllDisksBypassQueue()",
            "ERROR: unmapBlocksBypassQueue on disk"
        ],
        "analysis_focus": [
            "Understand bypass queue vs normal queue differences", 
            "Find how flushbypass enables sequential disk access",
            "Check if bypass queue can be used for general I/O",
            "Identify performance and protection trade-offs"
        ]
    }
}

def generate_ghidra_script():
    """Generate Ghidra Python script for automated analysis"""
    
    script_content = '''# Drobo 5D3 JBOD/Passthrough Analysis Script for Ghidra
# Auto-generated analysis targets based on string analysis

from ghidra.program.model.symbol import *
from ghidra.program.model.listing import *
from ghidra.app.script import GhidraScript

def find_functions_by_string(string_text):
    """Find functions that reference a specific string"""
    results = []
    
    # Search for string in program
    memory = currentProgram.getMemory()
    found = findBytes(memory.getMinAddress(), string_text.encode())
    
    if found:
        # Find cross-references to this string
        refs = getReferencesTo(found)
        for ref in refs:
            func = getFunctionContaining(ref.getFromAddress())
            if func:
                results.append({
                    'function': func.getName(),
                    'address': func.getEntryPoint(),
                    'string': string_text,
                    'reference': ref.getFromAddress()
                })
    
    return results

def analyze_bypass_functions():
    """Analyze bypass and passthrough functions"""
    
    print("=== Drobo 5D3 JBOD/Passthrough Analysis ===")
    print()
    
    # Target strings from our analysis
    target_strings = [
        "bypassLocks",
        "esaPassthroughCommand",
        "Direct Access not enabled", 
        "J2 journal pass through mode is disabled",
        "flushbypass"
    ]
    
    all_results = {}
    
    for target in target_strings:
        print(f"Searching for: {target}")
        results = find_functions_by_string(target)
        
        if results:
            all_results[target] = results
            for result in results:
                print(f"  Function: {result['function']} @ {result['address']}")
                
                # Create bookmark for manual analysis
                bookmark_mgr = currentProgram.getBookmarkManager()
                bookmark_mgr.setBookmark(
                    result['address'], 
                    BookmarkType.ANALYSIS,
                    "JBOD_Analysis", 
                    f"Target: {target}"
                )
        else:
            print(f"  No references found for: {target}")
        print()
    
    return all_results

# Run the analysis
if __name__ == "__main__":
    results = analyze_bypass_functions()
    
    # Export results
    import json
    result_file = "/tmp/ghidra_analysis_results.json"
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"Results exported to: {result_file}")
    print("Check bookmarks for manual analysis targets")
'''

    return script_content

def generate_analysis_checklist():
    """Generate analysis checklist for manual review"""
    
    checklist = []
    
    for category, details in ANALYSIS_TARGETS.items():
        checklist.append(f"\n## {category.replace('_', ' ').title()}")
        checklist.append(f"Priority: {details['priority']}")
        checklist.append(f"Description: {details['description']}")
        checklist.append("\n### Functions to Analyze:")
        
        for func in details['functions']:
            checklist.append(f"- [ ] {func}")
        
        checklist.append("\n### Target Strings:")
        for string in details['strings']:
            checklist.append(f"- [ ] \"{string}\"")
            
        checklist.append("\n### Analysis Focus:")
        for focus in details['analysis_focus']:
            checklist.append(f"- [ ] {focus}")
        
        checklist.append("\n---")
    
    return '\n'.join(checklist)

def main():
    """Main function to generate analysis files"""
    
    # Create analysis directory
    analysis_dir = "../../docs/analysis"
    os.makedirs(analysis_dir, exist_ok=True)
    
    # Generate Ghidra script
    script_content = generate_ghidra_script()
    with open(f"{analysis_dir}/ghidra_jbod_analysis.py", 'w') as f:
        f.write(script_content)
    
    # Generate analysis checklist
    checklist_content = generate_analysis_checklist()
    with open(f"{analysis_dir}/jbod_analysis_checklist.md", 'w') as f:
        f.write("# Drobo 5D3 JBOD/Passthrough Analysis Checklist\n")
        f.write(checklist_content)
    
    # Generate JSON targets for programmatic use
    with open(f"{analysis_dir}/analysis_targets.json", 'w') as f:
        json.dump(ANALYSIS_TARGETS, f, indent=2)
    
    print("Generated Ghidra analysis files:")
    print(f"  - {analysis_dir}/ghidra_jbod_analysis.py")
    print(f"  - {analysis_dir}/jbod_analysis_checklist.md") 
    print(f"  - {analysis_dir}/analysis_targets.json")
    
    print("\nNext steps:")
    print("1. Load secondary.elf in Ghidra")
    print("2. Run auto-analysis")
    print("3. Execute ghidra_jbod_analysis.py script")
    print("4. Follow manual analysis checklist")

if __name__ == "__main__":
    main()
