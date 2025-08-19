#!/bin/bash
#
# Drobo Firmware Analysis Environment Setup Script
# ================================================
#
# This script helps set up the environment for Drobo firmware analysis,
# checks dependencies, validates directory structure, and configures
# environment variables for optimal workflow.
#
# Usage:
#   ./setup-env.sh [--check-only] [--interactive] [--help]
#
# Options:
#   --check-only    Only perform checks, don't modify anything
#   --interactive   Interactive setup wizard
#   --help         Show this help message

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_ONLY=false
INTERACTIVE=false
SETUP_COMPLETE=true

# Default paths
DEFAULT_FIRMWARE_PATH="$SCRIPT_DIR/firmware"
DEFAULT_EXTRACTED_PATH="$SCRIPT_DIR/extracted"
DEFAULT_BACKUPS_PATH="$SCRIPT_DIR/backups"

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --check-only)
                CHECK_ONLY=true
                shift
                ;;
            --interactive)
                INTERACTIVE=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Show help message
show_help() {
    cat << EOF
Drobo Firmware Analysis Environment Setup Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --check-only    Only perform environment checks, don't modify anything
    --interactive   Run interactive setup wizard
    --help         Show this help message

DESCRIPTION:
    This script helps set up the environment for Drobo firmware analysis by:
    
    • Checking for required tools and dependencies
    • Validating directory structure
    • Configuring environment variables
    • Setting up shell integration
    • Testing tool functionality

EXAMPLES:
    $0                    # Run full setup
    $0 --check-only       # Only check current state
    $0 --interactive      # Interactive configuration

For more information, see docs/environment-variables.md
EOF
}

# Print section header
print_header() {
    echo -e "\n${CYAN}=== $1 ===${NC}"
}

# Print status messages
print_ok() {
    echo -e "  ${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "  ${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "  ${RED}✗${NC} $1"
    SETUP_COMPLETE=false
}

print_info() {
    echo -e "  ${BLUE}ℹ${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required tools
check_dependencies() {
    print_header "Checking Dependencies"
    
    local missing_tools=()
    
    # Required tools
    local required_tools=(
        "python3:Python 3 (required for all analysis tools)"
        "hexdump:Hex dump utility (usually in util-linux package)"
        "strings:String extraction utility (usually in binutils package)"
        "file:File type detection utility"
    )
    
    for tool_desc in "${required_tools[@]}"; do
        IFS=':' read -r tool desc <<< "$tool_desc"
        if command_exists "$tool"; then
            print_ok "$desc: $(which "$tool")"
        else
            print_error "$desc: NOT FOUND"
            missing_tools+=("$tool")
        fi
    done
    
    # Optional tools
    local optional_tools=(
        "binwalk:Binary analysis tool (pip3 install binwalk)"
        "git:Version control (for repository management)"
        "ghidra:Reverse engineering platform"
    )
    
    echo -e "\n  ${BLUE}Optional Tools:${NC}"
    for tool_desc in "${optional_tools[@]}"; do
        IFS=':' read -r tool desc <<< "$tool_desc"
        if command_exists "$tool"; then
            print_ok "$desc: $(which "$tool")"
        else
            print_warning "$desc: not found (optional)"
        fi
    done
    
    # Installation suggestions
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        echo -e "\n  ${YELLOW}Missing Required Tools:${NC}"
        echo -e "  Install missing tools with:"
        
        if command_exists "apt-get"; then
            echo -e "    ${CYAN}sudo apt-get install binutils util-linux file${NC}"
        elif command_exists "yum"; then
            echo -e "    ${CYAN}sudo yum install binutils util-linux file${NC}"
        elif command_exists "brew"; then
            echo -e "    ${CYAN}brew install binutils util-linux file${NC}"
        else
            echo -e "    Install using your system's package manager"
        fi
        
        if ! command_exists "binwalk"; then
            echo -e "    ${CYAN}pip3 install binwalk${NC}"
        fi
    fi
}

# Check Python modules
check_python_modules() {
    print_header "Checking Python Environment"
    
    # Check Python version
    if command_exists python3; then
        local python_version
        python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_ok "Python version: $python_version"
        
        # Check if version is adequate (3.6+)
        local major minor
        IFS='.' read -r major minor _ <<< "$python_version"
        if [[ $major -eq 3 && $minor -ge 6 ]] || [[ $major -gt 3 ]]; then
            print_ok "Python version is adequate (>= 3.6)"
        else
            print_warning "Python version may be too old (recommend >= 3.6)"
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
    
    # Test offsets module
    if python3 -c "import sys; sys.path.append('$SCRIPT_DIR/tools'); from offsets import DroboOffsets" 2>/dev/null; then
        print_ok "Offsets module imports successfully"
    else
        print_error "Offsets module import failed"
        print_info "Make sure you're running from the project root directory"
    fi
    
    # Test struct module (should be standard)
    if python3 -c "import struct" 2>/dev/null; then
        print_ok "Struct module available"
    else
        print_error "Struct module not available (this shouldn't happen)"
    fi
}

# Check directory structure
check_directory_structure() {
    print_header "Checking Directory Structure"
    
    local directories=(
        "docs:Documentation directory"
        "tools:Utility tools and modules"
        "scripts:Analysis and modification scripts"
        "firmware:Original firmware files (may be empty)"
        "extracted:Extracted firmware components (may be empty)"
        "backups:Backup files (may be empty)"
    )
    
    for dir_desc in "${directories[@]}"; do
        IFS=':' read -r dir desc <<< "$dir_desc"
        local dir_path="$SCRIPT_DIR/$dir"
        
        if [[ -d "$dir_path" ]]; then
            local file_count
            file_count=$(find "$dir_path" -type f | wc -l)
            print_ok "$desc: exists ($file_count files)"
        else
            print_warning "$desc: missing"
            if [[ "$CHECK_ONLY" == false ]]; then
                mkdir -p "$dir_path"
                print_info "Created directory: $dir_path"
            fi
        fi
    done
    
    # Check key files
    local key_files=(
        "tools/offsets.py:Core offsets module"
        "tools/capacity_patcher.py:Capacity patching tool"
        "tools/firmware_analyzer.py:Firmware analysis tool"
        "scripts/extraction/extract_all_components.py:Component extraction script"
        "README.md:Main documentation"
    )
    
    echo -e "\n  ${BLUE}Key Files:${NC}"
    for file_desc in "${key_files[@]}"; do
        IFS=':' read -r file desc <<< "$file_desc"
        local file_path="$SCRIPT_DIR/$file"
        
        if [[ -f "$file_path" ]]; then
            if [[ -x "$file_path" ]]; then
                print_ok "$desc: exists (executable)"
            else
                print_ok "$desc: exists"
            fi
        else
            print_error "$desc: missing"
        fi
    done
}

# Check current environment variables
check_environment_variables() {
    print_header "Checking Environment Variables"
    
    local env_vars=(
        "DROBO_FIRMWARE_PATH:Default firmware directory"
        "DROBO_EXTRACTED_PATH:Default extracted components directory"
    )
    
    for var_desc in "${env_vars[@]}"; do
        IFS=':' read -r var desc <<< "$var_desc"
        local value="${!var}"
        
        if [[ -n "$value" ]]; then
            if [[ -d "$value" ]]; then
                print_ok "$desc: $value (directory exists)"
            else
                print_warning "$desc: $value (directory does not exist)"
            fi
        else
            print_info "$desc: not set (will use defaults)"
        fi
    done
    
    # Show current working directory context
    echo -e "\n  ${BLUE}Current Context:${NC}"
    print_info "Working directory: $(pwd)"
    print_info "Script directory: $SCRIPT_DIR"
    
    # Test path resolution
    echo -e "\n  ${BLUE}Path Resolution Test:${NC}"
    if [[ -f "$SCRIPT_DIR/tools/firmware_analyzer.py" ]]; then
        local test_output
        test_output=$(cd "$SCRIPT_DIR/tools" && python3 firmware_analyzer.py secondary.elf 2>&1 | head -1 || true)
        if [[ "$test_output" == *"Resolved firmware path:"* ]]; then
            print_ok "Path resolution working: ${test_output#*: }"
        else
            print_info "Path resolution test: $test_output"
        fi
    fi
}

# Test tool functionality
test_tools() {
    print_header "Testing Tool Functionality"
    
    # Test offsets module
    if python3 -c "
import sys
sys.path.append('$SCRIPT_DIR/tools')
from offsets import DroboOffsets
print(f'Protection mode offset: 0x{DroboOffsets.CONFIG.PROTECTION_MODE:08x}')
print(f'Capacity limit offset: 0x{DroboOffsets.CAPACITY_LIMITS.BYTES_BASED:08x}')
" 2>/dev/null; then
        print_ok "Offsets module functional"
    else
        print_error "Offsets module test failed"
    fi
    
    # Test tools help output
    local tools=(
        "capacity_patcher.py"
        "firmware_analyzer.py"
        "header_generator.py"
    )
    
    for tool in "${tools[@]}"; do
        local tool_path="$SCRIPT_DIR/tools/$tool"
        if [[ -f "$tool_path" ]]; then
            if python3 "$tool_path" --help >/dev/null 2>&1 || python3 "$tool_path" >/dev/null 2>&1; then
                print_ok "$tool: help/usage accessible"
            else
                print_warning "$tool: may have issues"
            fi
        fi
    done
}

# Interactive setup wizard
interactive_setup() {
    print_header "Interactive Setup Wizard"
    
    echo -e "${BLUE}This wizard will help configure your Drobo analysis environment.${NC}\n"
    
    # Configure firmware path
    echo -e "${CYAN}Firmware Directory Configuration:${NC}"
    echo "Where are your firmware files (.tdf, .zip) located?"
    echo "Current: ${DROBO_FIRMWARE_PATH:-$DEFAULT_FIRMWARE_PATH}"
    read -r -p "Enter path (or press Enter for default): " firmware_path
    
    if [[ -n "$firmware_path" ]]; then
        # Expand tilde
        firmware_path="${firmware_path/#\~/$HOME}"
        export DROBO_FIRMWARE_PATH="$firmware_path"
    else
        export DROBO_FIRMWARE_PATH="$DEFAULT_FIRMWARE_PATH"
    fi
    
    # Configure extracted path
    echo -e "\n${CYAN}Extracted Directory Configuration:${NC}"
    echo "Where should extracted firmware components be stored?"
    echo "Current: ${DROBO_EXTRACTED_PATH:-$DEFAULT_EXTRACTED_PATH}"
    read -r -p "Enter path (or press Enter for default): " extracted_path
    
    if [[ -n "$extracted_path" ]]; then
        # Expand tilde
        extracted_path="${extracted_path/#\~/$HOME}"
        export DROBO_EXTRACTED_PATH="$extracted_path"
    else
        export DROBO_EXTRACTED_PATH="$DEFAULT_EXTRACTED_PATH"
    fi
    
    # Create directories if they don't exist
    echo -e "\n${CYAN}Creating directories...${NC}"
    for dir in "$DROBO_FIRMWARE_PATH" "$DROBO_EXTRACTED_PATH" "$DEFAULT_BACKUPS_PATH"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            print_ok "Created: $dir"
        else
            print_info "Exists: $dir"
        fi
    done
    
    # Generate shell configuration
    echo -e "\n${CYAN}Shell Configuration:${NC}"
    echo "Would you like to add environment variables to your shell profile?"
    read -r -p "Add to ~/.bashrc? [y/N]: " add_to_bashrc
    
    if [[ "$add_to_bashrc" =~ ^[Yy]$ ]]; then
        {
            echo ""
            echo "# Drobo Firmware Analysis Environment"
            echo "export DROBO_FIRMWARE_PATH=\"$DROBO_FIRMWARE_PATH\""
            echo "export DROBO_EXTRACTED_PATH=\"$DROBO_EXTRACTED_PATH\""
        } >> ~/.bashrc
        print_ok "Added environment variables to ~/.bashrc"
        print_info "Run 'source ~/.bashrc' or start a new terminal to apply changes"
    fi
    
    # Offer to copy sample firmware
    if [[ -d "$DROBO_FIRMWARE_PATH" ]] && [[ $(find "$DROBO_FIRMWARE_PATH" -name "*.tdf" | wc -l) -eq 0 ]]; then
        echo -e "\n${CYAN}Firmware Files:${NC}"
        echo "No .tdf files found in firmware directory."
        echo "Please copy your Drobo firmware files to: $DROBO_FIRMWARE_PATH"
        print_info "Supported files: *.tdf (firmware images), *.zip (firmware packages)"
    fi
}

# Generate environment setup script
generate_env_script() {
    if [[ "$CHECK_ONLY" == true ]]; then
        return 0
    fi
    
    print_header "Generating Environment Script"
    
    local env_script="$SCRIPT_DIR/env.sh"
    
    cat > "$env_script" << EOF
#!/bin/bash
# Drobo Firmware Analysis Environment
# Source this file to set up environment variables:
#   source env.sh

export DROBO_FIRMWARE_PATH="${DROBO_FIRMWARE_PATH:-$DEFAULT_FIRMWARE_PATH}"
export DROBO_EXTRACTED_PATH="${DROBO_EXTRACTED_PATH:-$DEFAULT_EXTRACTED_PATH}"
export DROBO_BACKUPS_PATH="${DROBO_BACKUPS_PATH:-$DEFAULT_BACKUPS_PATH}"

# Add tools to PATH
export PATH="\$PATH:$SCRIPT_DIR/tools"

echo "Drobo Firmware Analysis Environment Loaded"
echo "  Firmware Path:  \$DROBO_FIRMWARE_PATH"
echo "  Extracted Path: \$DROBO_EXTRACTED_PATH"
echo "  Backups Path:   \$DROBO_BACKUPS_PATH"
EOF
    
    chmod +x "$env_script"
    print_ok "Created environment script: $env_script"
    print_info "Source with: source env.sh"
}

# Show final summary
show_summary() {
    print_header "Setup Summary"
    
    if [[ "$SETUP_COMPLETE" == true ]]; then
        print_ok "Environment setup completed successfully!"
        
        echo -e "\n${BLUE}Next Steps:${NC}"
        echo "  1. Source environment: ${CYAN}source env.sh${NC}"
        echo "  2. Copy firmware files to: ${CYAN}$DROBO_FIRMWARE_PATH${NC}"
        echo "  3. Extract components: ${CYAN}cd scripts/extraction && python3 extract_all_components.py${NC}"
        echo "  4. Analyze firmware: ${CYAN}cd tools && python3 firmware_analyzer.py secondary.elf${NC}"
        
        echo -e "\n${BLUE}Documentation:${NC}"
        echo "  • Project overview: ${CYAN}README.md${NC}"
        echo "  • Environment guide: ${CYAN}docs/environment-variables.md${NC}"
        echo "  • Tool reference: ${CYAN}tools/README.md${NC}"
        
    else
        print_error "Setup completed with issues"
        echo -e "\n${YELLOW}Please resolve the issues above before proceeding.${NC}"
        echo "Run with --check-only to verify fixes."
    fi
    
    if [[ "$CHECK_ONLY" == true ]]; then
        echo -e "\n${BLUE}Check-only mode: No changes made${NC}"
    fi
}

# Main execution
main() {
    parse_args "$@"
    
    echo -e "${CYAN}"
    cat << 'EOF'
 ____            _             _____ _                                     
|  _ \ _ __ ___ | |__   ___   |  ___(_)_ __ _ __ ___   __ _ _ __ ___        
| | | | '__/ _ \| '_ \ / _ \  | |_  | | '__| '_ ` _ \ / _` | '__/ _ \       
| |_| | | | (_) | |_) | (_) | |  _| | | |  | | | | | | (_| | | |  __/       
|____/|_|  \___/|_.__/ \___/  |_|   |_|_|  |_| |_| |_|\__,_|_|  \___|       
                                                                           
    _                _           _       ____       _                      
   / \   _ __   __ _| |_   _ ___(_)___  / ___|  ___| |_ _   _ _ __           
  / _ \ | '_ \ / _` | | | | / __| / __| \___ \ / _ \ __| | | | '_ \          
 / ___ \| | | | (_| | | |_| \__ \ \__ \  ___) |  __/ |_| |_| | |_) |        
/_/   \_\_| |_|\__,_|_|\__, |___/_|___/ |____/ \___|\__|\__,_| .__/         
                       |___/                                |_|            
EOF
    echo -e "${NC}"
    
    if [[ "$INTERACTIVE" == true ]]; then
        interactive_setup
        echo ""
    fi
    
    check_dependencies
    check_python_modules
    check_directory_structure
    check_environment_variables
    test_tools
    
    if [[ "$CHECK_ONLY" == false ]]; then
        generate_env_script
    fi
    
    show_summary
    
    # Exit with error code if setup failed
    if [[ "$SETUP_COMPLETE" == false ]]; then
        exit 1
    fi
}

# Run main function with all arguments
main "$@"