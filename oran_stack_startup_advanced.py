#!/usr/bin/env python3
"""
ORAN Stack Startup Script - Advanced Version with tmux and Cyber Probes
Starts each component in a separate tmux session with cyber probe support
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
XAPPS_PATH = f"{RIC_PATH}/xApps/python"

# Config files
GNB_CONFIG = "gnb_zmq.yaml"
UE_CONFIG = "ue_zmq.conf"

# Cyber Probe Configuration
PROBES = {
    "probe_odu": {
        "title": "O-DU Probe",
        "session": "probe_odu",
        "env": {
            "PROBE_ID": "probe-odu-001",
            "COMPONENT_TYPE": "O-DU",
            "COMPONENT_NAME": "simulated-o-du-1",
            "IP_ADDRESS": "10.0.0.12",
            "INTERFACE": "E2"
        }
    },
    "probe_ocu": {
        "title": "O-CU Probe",
        "session": "probe_ocu",
        "env": {
            "PROBE_ID": "probe-ocu-001",
            "COMPONENT_TYPE": "O-CU",
            "COMPONENT_NAME": "simulated-o-cu-1",
            "IP_ADDRESS": "10.0.0.13",
            "INTERFACE": "F1/E1/NG"
        }
    },
    "probe_oru": {
        "title": "O-RU Probe",
        "session": "probe_oru",
        "env": {
            "PROBE_ID": "probe-oru-001",
            "COMPONENT_TYPE": "O-RU",
            "COMPONENT_NAME": "simulated-o-ru-1",
            "IP_ADDRESS": "10.0.0.11",
            "INTERFACE": "OPEN-FRONTHAUL"
        }
    }
}

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
            "5GC": CORE5G_PATH,
            "xApps": XAPPS_PATH
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
    
    def start_probes(self):
        """Step 6-8: Start cyber probes (O-DU, O-CU, O-RU)"""
        probe_start_time = 6
        for probe_key, probe_config in PROBES.items():
            print(f"\n\033[94m[{probe_start_time}/8]\033[0m Starting {probe_config['title']}...")
            print(f" \033[93m⏳ Waiting 3 seconds before starting {probe_config['title']}...\033[0m")
            time.sleep(3)
            
            # Build environment variables
            env_vars = " ".join([f"{k}={v}" for k, v in probe_config['env'].items()])
            cmd = f'cd {XAPPS_PATH} && {env_vars} python3 cyber_probe.py'
            
            self.start_tmux_session(
                probe_config['session'],
                probe_config['title'],
                cmd
            )
            probe_start_time += 1
    
    def run(self):
        """Run all startup steps with separate tmux sessions"""
        print("=" * 70)
        print(" " * 15 + "ORAN Stack Startup Script - tmux Version with Cyber Probes")
        print("=" * 70)
        print()
        
        try:
            # Step 1: RIC Stack
            print("\033[94m[1/8]\033[0m Starting RIC Stack...")
            self.start_tmux_session(
                "ric_stack",
                "RIC Stack",
                f"cd {RIC_PATH} && docker compose up"
            )
            time.sleep(5)
            
            # Step 2: Open 5GS Core
            print("\n\033[94m[2/8]\033[0m Starting Open5GS Core...")
            self.start_tmux_session(
                "open5gs_core",
                "Open5GS Core",
                f"cd {CORE5G_PATH} && docker compose up 5gc"
            )
            time.sleep(5)
            
            # Step 3: srsRAN gNB
            print("\n\033[94m[3/8]\033[0m Starting srsRAN gNB...")
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
            print("\n\033[94m[4/8]\033[0m Starting srsUE...")
            print(" \033[93m⏳ Waiting 5 seconds before starting UE...\033[0m")
            time.sleep(5)
            self.start_tmux_session(
                "ue",
                "srsUE",
                f"sudo ip netns add ue1 2>/dev/null || true; sudo ip netns list; cd {CONFIGS_PATH} && sudo srsue {UE_CONFIG}"
            )
            
            # Step 5: Cyber Probe Manager
            print("\n\033[94m[5/8]\033[0m Starting Cyber Probe Manager...")
            print(" \033[93m⏳ Waiting 5 seconds before starting cyber probe manager...\033[0m")
            time.sleep(5)
            self.start_tmux_session(
                "cyber_probe_manager",
                "Cyber Probe Manager",
                f"cd {XAPPS_PATH} && python3 -m uvicorn cyber_probe_manager_xapp2:app --host 0.0.0.0 --port 5050"
            )
            
            # Steps 6-8: Cyber Probes
            self.start_probes()
            
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
            print("\nAttach to Cyber Probe Manager:")
            print("  tmux attach -t cyber_probe_manager")
            print("\nAttach to O-DU Probe:")
            print("  tmux attach -t probe_odu")
            print("\nAttach to O-CU Probe:")
            print("  tmux attach -t probe_ocu")
            print("\nAttach to O-RU Probe:")
            print("  tmux attach -t probe_oru")
            print("\nDetach from any tmux session without stopping it:")
            print("  Ctrl+b then d")
            print("\nStop all ORAN sessions:")
            print("  tmux kill-session -t ric_stack")
            print("  tmux kill-session -t open5gs_core")
            print("  tmux kill-session -t gnb")
            print("  tmux kill-session -t ue")
            print("  tmux kill-session -t cyber_probe_manager")
            print("  tmux kill-session -t probe_odu")
            print("  tmux kill-session -t probe_ocu")
            print("  tmux kill-session -t probe_oru")
            print("=" * 70)
        
        except Exception as e:
            print(f"\n\033[91m[ERROR]\033[0m {e}")
            sys.exit(1)

if __name__ == "__main__":
    starter = ORANStackStarterAdvanced()
    starter.run()
