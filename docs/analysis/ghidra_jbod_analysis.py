# Drobo 5D3 JBOD/Passthrough Analysis Script for Ghidra
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
