#!/usr/bin/env python3
"""
ORAN Stack Startup Script - Advanced Version with tmux
Starts each component in a separate tmux session
"""

import subprocess
import time
import sys
import os

# Configuration
BASE_PATH = "/root/fyp"
SRSRAN_PATH = f"{BASE_PATH}/srsRAN_Project"
CORE5G_PATH = f"{BASE_PATH}/srsRAN_Project/docker"
RIC_PATH = f"{BASE_PATH}/oran-sc-ric"
CONFIGS_PATH = f"{SRSRAN_PATH}/configs"

# Config files
GNB_CONFIG = "gnb_zmq.yaml"
UE_CONFIG = "ue_zmq.conf"

class ORANStackStarterAdvanced:
    def __init__(self):
        self.terminal_pids = []
        self._validate_paths()
        self._check_tmux()
    
    def _validate_paths(self):
        """Validate all required paths exist"""
        paths = {
            "RIC": RIC_PATH,
            "srsRAN": SRSRAN_PATH,
            "Configs": CONFIGS_PATH,
            "5GC": CORE5G_PATH
        }
        for name, path in paths.items():
            if not os.path.isdir(path):
                print(f"\033[91m[ERROR]\033[0m {name} path not found: {path}")
                sys.exit(1)
    
    def _check_tmux(self):
        """Check if tmux is installed"""
        if os.system("which tmux > /dev/null 2>&1") != 0:
            print("\033[91m[ERROR]\033[0m tmux is not installed.")
            print("Install it using: sudo apt update && sudo apt install -y tmux")
            sys.exit(1)
    
    def start_tmux_session(self, session_name, title, command):
        """Start a tmux session with the given command"""
        print(f"\033[94m[*]\033[0m Starting \033[92m{title}\033[0m in tmux session: \033[93m{session_name}\033[0m")
        
        # Check if session exists and kill it
        os.system(f"tmux has-session -t {session_name} 2>/dev/null && tmux kill-session -t {session_name}; sleep 1")
        
        # Create new tmux session
        tmux_cmd = f"tmux new-session -d -s {session_name} \"bash -lc '{command}; echo; echo \\\"Process exited. Press Ctrl+b then d to detach.\\\"; exec bash'\""
        result = os.system(tmux_cmd)
        
        if result == 0:
            print(f"    \033[92m✓\033[0m {title} started in session: {session_name}")
        else:
            print(f"    \033[91m[ERROR]\033[0m Failed to start {title}")
            sys.exit(1)
    
    def run(self):
        """Run all startup steps with separate tmux sessions"""
        print("=" * 70)
        print(" " * 15 + "ORAN Stack Startup Script - tmux Version")
        print("=" * 70)
        print()
        
        try:
            # Step 1: RIC Stack
            print("\033[94m[1/4]\033[0m Starting RIC Stack...")
            self.start_tmux_session(
                "ric_stack",
                "RIC Stack",
                f"cd {RIC_PATH} && docker compose up"
            )
            time.sleep(5)
            
            # Step 2: Open 5GS Core
            print("\n\033[94m[2/4]\033[0m Starting Open5GS Core...")
            self.start_tmux_session(
                "open5gs_core",
                "Open5GS Core",
                f"cd {CORE5G_PATH} && docker compose up 5gc"
            )
            time.sleep(5)
            
            # Step 3: srsRAN gNB
            print("\n\033[94m[3/4]\033[0m Starting srsRAN gNB...")
            print(" \033[93m⏳ Waiting 5 seconds before starting gNB...\033[0m")
            time.sleep(5)
            self.start_tmux_session(
                "gnb",
                "srsRAN gNB",
                f"cd {CONFIGS_PATH} && gnb -c {GNB_CONFIG}"
            )
            print(" \033[93m💡 Check gNB logs for AMF and E2 connection.\033[0m")
            time.sleep(5)
            
            # Step 4: srsUE
            print("\n\033[94m[4/4]\033[0m Starting srsUE...")
            print(" \033[93m⏳ Waiting 5 seconds before starting UE...\033[0m")
            time.sleep(5)
            self.start_tmux_session(
                "ue",
                "srsUE",
                f"sudo ip netns add ue1 2>/dev/null || true; sudo ip netns list; cd {CONFIGS_PATH} && sudo srsue {UE_CONFIG}"
            )
            
            print("\n" + "=" * 70)
            print("\033[92m✓ All components started in tmux sessions.\033[0m")
            print("=" * 70)
            print("\nView running sessions:")
            print("  tmux ls")
            print("\nAttach to RIC Stack:")
            print("  tmux attach -t ric_stack")
            print("\nAttach to Open5GS Core:")
            print("  tmux attach -t open5gs_core")
            print("\nAttach to gNB:")
            print("  tmux attach -t gnb")
            print("\nAttach to UE:")
            print("  tmux attach -t ue")
            print("\nDetach from any tmux session without stopping it:")
            print("  Ctrl+b then d")
            print("\nStop all ORAN sessions:")
            print("  tmux kill-session -t ric_stack")
            print("  tmux kill-session -t open5gs_core")
            print("  tmux kill-session -t gnb")
            print("  tmux kill-session -t ue")
            print("=" * 70)
        
        except Exception as e:
            print(f"\n\033[91m[ERROR]\033[0m {e}")
            sys.exit(1)

if __name__ == "__main__":
    starter = ORANStackStarterAdvanced()
    starter.run()
