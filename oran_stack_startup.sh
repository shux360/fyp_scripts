#!/bin/bash
# ORAN Stack Startup Script - tmux Version
# Starts each component in a separate tmux session for SSH/headless VM usage

set -e

# Configuration
BASE_PATH="/root/fyp"
SRSRAN_PATH="${BASE_PATH}/srsRAN_Project"
CORE5G_PATH="${BASE_PATH}/srsRAN_Project/docker"
RIC_PATH="${BASE_PATH}/oran-sc-ric"
CONFIGS_PATH="${SRSRAN_PATH}/configs"

# Config files
GNB_CONFIG="gnb_zmq.yaml"
UE_CONFIG="ue_zmq.conf"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================================================="
echo "                    ORAN Stack Startup Script - tmux"
echo "=========================================================================="
echo ""

# Check tmux
if ! command -v tmux &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} tmux is not installed."
    echo "Install it using:"
    echo "sudo apt update && sudo apt install -y tmux"
    exit 1
fi

# Check paths
if [ ! -d "$RIC_PATH" ]; then
    echo -e "${RED}[ERROR]${NC} RIC path not found: $RIC_PATH"
    exit 1
fi

if [ ! -d "$SRSRAN_PATH" ]; then
    echo -e "${RED}[ERROR]${NC} srsRAN path not found: $SRSRAN_PATH"
    exit 1
fi

if [ ! -d "$CONFIGS_PATH" ]; then
    echo -e "${RED}[ERROR]${NC} Configs path not found: $CONFIGS_PATH"
    exit 1
fi

if [ ! -d "$CORE5G_PATH" ]; then
    echo -e "${RED}[ERROR]${NC} Configs path not found: $CORE5G_PATH"
    exit 1
fi


# Function to start tmux session
start_tmux_session() {
    local session_name="$1"
    local title="$2"
    local command="$3"

    echo -e "${BLUE}[*]${NC} Starting ${GREEN}${title}${NC} in tmux session: ${YELLOW}${session_name}${NC}"

    if tmux has-session -t "$session_name" 2>/dev/null; then
        echo -e "${YELLOW}[WARN]${NC} Existing session '${session_name}' found. Killing it..."
        tmux kill-session -t "$session_name"
        sleep 1
    fi

    tmux new-session -d -s "$session_name" "bash -lc '${command}; echo; echo \"Process exited. Press Ctrl+b then d to detach.\"; exec bash'"
}

echo -e "${BLUE}[1/4]${NC} Starting RIC Stack..."
start_tmux_session "ric_stack" "RIC Stack" "cd ${RIC_PATH} && docker compose up"
sleep 5

echo -e "${BLUE}[2/4]${NC} Starting Open5GS Core..."
start_tmux_session "open5gs_core" "Open5GS Core" "cd ${CORE5G_PATH} && docker compose up 5gc"
sleep 5

echo -e "${BLUE}[3/4]${NC} Starting srsRAN gNB..."
echo -e "${YELLOW}⏳ Waiting 5 seconds before starting gNB...${NC}"
sleep 5
start_tmux_session "gnb" "srsRAN gNB" "cd ${CONFIGS_PATH} && gnb -c ${GNB_CONFIG}"
echo -e "${YELLOW}💡 Check gNB logs for AMF and E2 connection.${NC}"
sleep 5

echo -e "${BLUE}[4/4]${NC} Starting srsUE..."
echo -e "${YELLOW}⏳ Waiting 5 seconds before starting UE...${NC}"
sleep 5
start_tmux_session "ue" "srsUE" "sudo ip netns add ue1 2>/dev/null || true; sudo ip netns list; cd ${CONFIGS_PATH} && sudo srsue ${UE_CONFIG}"

echo ""
echo "=========================================================================="
echo -e "${GREEN}✓ All components started in tmux sessions.${NC}"
echo "=========================================================================="
echo ""
echo "View running sessions:"
echo "  tmux ls"
echo ""
echo "Attach to RIC Stack:"
echo "  tmux attach -t ric_stack"
echo ""
echo "Attach to Open5GS Core:"
echo "  tmux attach -t open5gs_core"
echo ""
echo "Attach to gNB:"
echo "  tmux attach -t gnb"
echo ""
echo "Attach to UE:"
echo "  tmux attach -t ue"
echo ""
echo "Detach from any tmux session without stopping it:"
echo "  Ctrl+b then d"
echo ""
echo "Stop all ORAN sessions:"
echo "  tmux kill-session -t ric_stack"
echo "  tmux kill-session -t open5gs_core"
echo "  tmux kill-session -t gnb"
echo "  tmux kill-session -t ue"
echo "=========================================================================="
