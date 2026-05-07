#!/bin/bash
# ORAN Stack Startup Script - Bash Version
# Starts each component in a separate terminal

set -e  # Exit on error

# Configuration
SRSRAN_PATH="/fyp/srsRAN_Project"
RIC_PATH="/fyp/oran-sc-ric"
CONFIGS_PATH="${SRSRAN_PATH}/configs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================================================="
echo "                    ORAN Stack Startup Script"
echo "=========================================================================="
echo ""

# Function to open new terminal with command
open_terminal() {
    local title="$1"
    local command="$2"
    
    echo -e "${BLUE}[*]${NC} Opening terminal: ${GREEN}${title}${NC}"
    
    # Try different terminal emulators
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="${title}" -- bash -c "${command}; read -p 'Press Enter to close...'" &
        sleep 1
    elif command -v xterm &> /dev/null; then
        xterm -title "${title}" -e bash -c "${command}; read -p 'Press Enter to close...'" &
        sleep 1
    elif command -v konsole &> /dev/null; then
        konsole --title="${title}" -e bash -c "${command}; read -p 'Press Enter to close...'" &
        sleep 1
    else
        echo -e "${RED}[ERROR]${NC} No compatible terminal found."
        echo "Please install gnome-terminal, xterm, or konsole"
        exit 1
    fi
}

# Step 1: RIC Stack
echo -e "${BLUE}[1/4]${NC} Starting RIC Stack..."
open_terminal "RIC Stack" "cd ${RIC_PATH} && docker compose up"
sleep 5

# Step 2: Open 5GS Core
echo -e "${BLUE}[2/4]${NC} Starting Open 5GS Core..."
open_terminal "5GS Core" "cd ${SRSRAN_PATH} && docker compose up 5gc"
sleep 5

# Step 3: srsRAN gNB
echo -e "${BLUE}[3/4]${NC} Starting srsRAN gNB..."
echo -e "${YELLOW}⏳ Waiting 5 seconds before starting gNB...${NC}"
sleep 5
open_terminal "srsRAN gNB" "cd ${CONFIGS_PATH} && gnb -c gnb_zmq.yaml"
echo -e "${YELLOW}💡 Watch for gNB connecting to AMF in the terminal${NC}"
sleep 5

# Step 4: srsUE
echo -e "${BLUE}[4/4]${NC} Starting srsUE..."
echo -e "${YELLOW}⏳ Waiting 5 seconds before starting UE...${NC}"
sleep 5
open_terminal "srsUE" "sudo ip netns add ue1 2>/dev/null || true; sudo ip netns list; cd ${CONFIGS_PATH} && sudo srsue ue_zmq.conf"

echo ""
echo "=========================================================================="
echo -e "${GREEN}✓ All components launched in separate terminals!${NC}"
echo "=========================================================================="
echo ""
echo -e "${YELLOW}Monitor each terminal window for startup progress.${NC}"
echo -e "${YELLOW}Press Ctrl+C in this terminal to stop monitoring.${NC}"
echo "=========================================================================="
echo ""

# Wait indefinitely
while true; do
    sleep 1
done
