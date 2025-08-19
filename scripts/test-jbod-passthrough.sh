#!/bin/bash
# Drobo 5D3 JBOD/Passthrough Testing Script
# This script helps set up serial console testing for discovered passthrough commands

set -euo pipefail

# Configuration
SERIAL_PORT="${SERIAL_PORT:-/dev/ttyUSB0}"
BAUD_RATE="115200"
LOG_DIR="logs"
TEST_LOG="$LOG_DIR/jbod-test-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local msg="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${msg}" | tee -a "$TEST_LOG"
}

info() { log "${BLUE}INFO${NC}" "$@"; }
warn() { log "${YELLOW}WARN${NC}" "$@"; }
error() { log "${RED}ERROR${NC}" "$@"; }
success() { log "${GREEN}SUCCESS${NC}" "$@"; }

# Create log directory
mkdir -p "$LOG_DIR"

show_banner() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                Drobo 5D3 JBOD/Passthrough Tester            ║
║                                                              ║
║  Testing discovered bypass and passthrough functionality     ║
║  via TTL serial console (safe, no firmware modification)    ║
╚══════════════════════════════════════════════════════════════╝
EOF
}

check_dependencies() {
    info "Checking dependencies..."
    
    local missing=()
    
    # Check for serial terminal programs
    if ! command -v screen >/dev/null 2>&1; then
        if ! command -v minicom >/dev/null 2>&1; then
            missing+=("screen or minicom")
        fi
    fi
    
    # Check for serial port
    if [ ! -e "$SERIAL_PORT" ]; then
        missing+=("serial port $SERIAL_PORT")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        error "Missing dependencies: ${missing[*]}"
        echo
        echo "Install missing dependencies:"
        echo "  sudo apt-get install screen minicom"
        echo "  Check TTL serial adapter connection"
        exit 1
    fi
    
    success "All dependencies found"
}

show_hardware_setup() {
    cat << 'EOF'

Hardware Setup Required:
╔════════════════════════════════════════════════════════════╗
║  TTL Serial Adapter (3.3V) -> Drobo 5D3                   ║
║                                                            ║
║  GND (Black)  -> GND                                       ║
║  TX  (White)  -> RX  (Drobo)                              ║
║  RX  (Green)  -> TX  (Drobo)                              ║
║  VCC          -> DO NOT CONNECT                            ║
║                                                            ║
║  ⚠️  WARNING: Use 3.3V adapter only, NOT 5V!              ║
╚════════════════════════════════════════════════════════════╝

EOF
}

show_test_commands() {
    cat << 'EOF'

JBOD/Passthrough Test Commands:
╔════════════════════════════════════════════════════════════╗
║  Phase 1: Bypass Lock Testing (Safest)                    ║
║    -> bypassLocks                  # Check current state   ║
║    -> bypassLocks true            # Enable bypass mode    ║
║    -> dm flushbypass              # Test direct disk flush ║
║                                                            ║
║  Phase 2: ESA Passthrough Testing                         ║
║    -> esa                         # List ESA commands     ║
║    -> esapass                     # Test passthrough      ║
║    -> esa disDump <slot> 0 10     # Direct disk access    ║
║                                                            ║
║  Phase 3: System Information                              ║
║    -> help                        # Available commands    ║
║    -> taskShow                    # Running tasks         ║
║    -> dm                          # Disk manager info     ║
║                                                            ║
║  Recovery Commands:                                        ║
║    -> bypassLocks false           # Disable bypass        ║
║    -> reboot                      # Restart system        ║
╚════════════════════════════════════════════════════════════╝

EOF
}

start_serial_session() {
    info "Starting serial console session on $SERIAL_PORT"
    warn "This will open an interactive session - press Ctrl+A, K to exit screen"
    echo
    
    # Check if screen is available
    if command -v screen >/dev/null 2>&1; then
        info "Using screen for serial console..."
        echo "Command: screen $SERIAL_PORT $BAUD_RATE"
        echo "To exit: Press Ctrl+A, then K, then Y"
        echo
        read -p "Press Enter to start serial console session..."
        screen "$SERIAL_PORT" "$BAUD_RATE"
    elif command -v minicom >/dev/null 2>&1; then
        info "Using minicom for serial console..."
        echo "Command: minicom -D $SERIAL_PORT -b $BAUD_RATE"
        echo "To exit: Press Ctrl+A, then X"
        echo
        read -p "Press Enter to start serial console session..."
        minicom -D "$SERIAL_PORT" -b "$BAUD_RATE"
    else
        error "No serial terminal program found!"
        exit 1
    fi
}

create_test_log_template() {
    cat > "$LOG_DIR/test-template.txt" << 'EOF'
# Drobo 5D3 JBOD/Passthrough Test Log
# Copy this template for each test session

Date: [YYYY-MM-DD]
Time: [HH:MM:SS]
Firmware Version: [Get from device]
Test Objective: [What are you testing?]

## Console Session Log:
[Paste VxWorks console output here]

## Test Results:
Command: [command tested]
Result: [SUCCESS/FAIL/PARTIAL]
Output: [console output]
Notes: [observations, side effects, etc.]

## Next Steps:
[What to test next based on results]
EOF
    
    info "Created test log template: $LOG_DIR/test-template.txt"
}

show_safety_warnings() {
    cat << 'EOF'

⚠️  SAFETY WARNINGS:
╔════════════════════════════════════════════════════════════╗
║  • Use 3.3V TTL adapter ONLY (5V can damage device)       ║
║  • Test with spare drives only (no production data)       ║
║  • Keep serial console connected for recovery             ║
║  • Power cycle if system becomes unresponsive             ║
║  • Document all commands and outputs                      ║
║  • Can always disable bypass with: bypassLocks false     ║
╚════════════════════════════════════════════════════════════╝

EOF
}

main() {
    show_banner
    show_safety_warnings
    
    # Check if user wants to proceed
    echo
    read -p "Have you connected TTL serial adapter correctly? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        show_hardware_setup
        echo "Connect hardware and run script again."
        exit 0
    fi
    
    check_dependencies
    create_test_log_template
    show_test_commands
    
    echo
    read -p "Ready to start serial console testing? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_serial_session
    else
        info "Serial console ready. Manual connection:"
        echo "  screen $SERIAL_PORT $BAUD_RATE"
        echo "  OR"
        echo "  minicom -D $SERIAL_PORT -b $BAUD_RATE"
    fi
    
    success "Test session complete. Check logs in: $LOG_DIR/"
}

# Handle script arguments
case "${1:-main}" in
    "setup")
        show_hardware_setup
        ;;
    "commands")
        show_test_commands
        ;;
    "console")
        start_serial_session
        ;;
    "main"|*)
        main
        ;;
esac
EOF
