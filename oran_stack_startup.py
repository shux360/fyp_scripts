#!/usr/bin/env python3
"""
ORAN Stack Startup Script with Cyber Probes
Starts the RIC stack, 5GS core, srsRAN gNB, srsUE, and cyber probes in separate tmux sessions
"""

import subprocess
import time
import sys
import os
from pathlib import Path

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

class ORANStackStarter:
    def __init__(self):
        self.processes = []
        self._validate_paths()
        
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
                print(f"[ERROR] {name} path not found: {path}")
                sys.exit(1)
    
    def _get_terminal_command(self, command_str):
        """Get the appropriate terminal command based on OS"""
        if sys.platform == 'win32':
            # Use Windows terminal or WSL
            return f'wsl bash -c "{command_str}"'
        else:
            # Use tmux for Linux
            return command_str
    
    def start_tmux_session(self, session_name, title, command):
        """Start a tmux session with the given command"""
        print(f"[*] Starting {title} in tmux session: {session_name}")
        
        # Check if session exists
        check_cmd = f"tmux has-session -t {session_name} 2>/dev/null && tmux kill-session -t {session_name}; sleep 1"
        os.system(check_cmd)
        
        # Create new tmux session
        tmux_cmd = f"tmux new-session -d -s {session_name} \"bash -lc '{command}; echo; echo \\\"Process exited. Press Ctrl+b then d to detach.\\\"; exec bash'\""
        result = os.system(tmux_cmd)
        
        if result == 0:
            print(f"   ✓ {title} started in session: {session_name}")
        else:
            print(f"   [ERROR] Failed to start {title}")
            sys.exit(1)
    
    def start_ric_stack(self):
        """Step 1: Start the RIC stack"""
        print("[1/4] Starting RIC Stack...")
        cmd = f'cd {RIC_PATH} && docker compose up'
        self.start_tmux_session("ric_stack", "RIC Stack", cmd)
        time.sleep(5)
    
    def start_5gc(self):
        """Step 2: Start the Open 5GS core"""
        print("[2/4] Starting Open5GS Core...")
        cmd = f'cd {CORE5G_PATH} && docker compose up 5gc'
        self.start_tmux_session("open5gs_core", "Open5GS Core", cmd)
        time.sleep(5)
    
    def start_gnb(self):
        """Step 3: Start the srsRAN gNB"""
        print("[3/4] Starting srsRAN gNB...")
        print("   ⏳ Waiting 5 seconds before starting gNB...")
        time.sleep(5)
        cmd = f'cd {CONFIGS_PATH} && gnb -c {GNB_CONFIG}'
        self.start_tmux_session("gnb", "srsRAN gNB", cmd)
        print("   💡 Check gNB logs for AMF and E2 connection.")
        time.sleep(5)
    
    def start_ue(self):
        """Step 4: Start the srsUE"""
        print("[4/8] Starting srsUE...")
        print("   ⏳ Waiting 5 seconds before starting UE...")
        time.sleep(5)
        cmd = f'sudo ip netns add ue1 2>/dev/null || true; sudo ip netns list; cd {CONFIGS_PATH} && sudo srsue {UE_CONFIG}'
        self.start_tmux_session("ue", "srsUE", cmd)
    
    def start_cyber_probe_manager(self):
        """Step 5: Start Cyber Probe Manager"""
        print("\n[5/8] Starting Cyber Probe Manager...")
        print("   ⏳ Waiting 5 seconds before starting cyber probe manager...")
        time.sleep(5)
        cmd = f'cd {XAPPS_PATH} && python3 -m uvicorn cyber_probe_manager_xapp2:app --host 0.0.0.0 --port 5050'
        self.start_tmux_session("cyber_probe_manager", "Cyber Probe Manager", cmd)
    
    def start_probes(self):
        """Step 6-8: Start cyber probes (O-DU, O-CU, O-RU)"""
        probe_start_time = 6
        for probe_key, probe_config in PROBES.items():
            print(f"\n[{probe_start_time}/8] Starting {probe_config['title']}...")
            print(f"   ⏳ Waiting 3 seconds before starting {probe_config['title']}...")
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
        """Run all startup steps"""
        print("=" * 70)
        print(" " * 15 + "ORAN Stack Startup Script - tmux Version with Cyber Probes")
        print("=" * 70)
        print()
        
        try:
            self.start_ric_stack()
            self.start_5gc()
            self.start_gnb()
            self.start_ue()
            self.start_cyber_probe_manager()
            self.start_probes()
            
            print()
            print("=" * 70)
            print("✓ All components started in tmux sessions.")
            print("=" * 70)
            print()
            print("View running sessions:")
            print("  tmux ls")
            print()
            print("Attach to RIC Stack:")
            print("  tmux attach -t ric_stack")
            print()
            print("Attach to Open5GS Core:")
            print("  tmux attach -t open5gs_core")
            print()
            print("Attach to gNB:")
            print("  tmux attach -t gnb")
            print()
            print("Attach to UE:")
            print("  tmux attach -t ue")
            print()
            print("Attach to Cyber Probe Manager:")
            print("  tmux attach -t cyber_probe_manager")
            print()
            print("Attach to O-DU Probe:")
            print("  tmux attach -t probe_odu")
            print()
            print("Attach to O-CU Probe:")
            print("  tmux attach -t probe_ocu")
            print()
            print("Attach to O-RU Probe:")
            print("  tmux attach -t probe_oru")
            print()
            print("Detach from any tmux session without stopping it:")
            print("  Ctrl+b then d")
            print()
            print("Stop all ORAN sessions:")
            print("  tmux kill-session -t ric_stack")
            print("  tmux kill-session -t open5gs_core")
            print("  tmux kill-session -t gnb")
            print("  tmux kill-session -t ue")
            print("  tmux kill-session -t cyber_probe_manager")
            print("  tmux kill-session -t probe_odu")
            print("  tmux kill-session -t probe_ocu")
            print("  tmux kill-session -t probe_oru")
            print("=" * 70)
            
            # Keep the script running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nShutting down all services...")
                self.cleanup()
        
        except Exception as e:
            print(f"Error: {e}")
            self.cleanup()
            sys.exit(1)
    
    def cleanup(self):
        """Terminate all tmux sessions"""
        sessions = ["ric_stack", "open5gs_core", "gnb", "ue", "cyber_probe_manager", "probe_odu", "probe_ocu", "probe_oru"]
        for session in sessions:
            os.system(f"tmux kill-session -t {session} 2>/dev/null || true")
            print(f"  • Terminated tmux session: {session}")

if __name__ == "__main__":
    starter = ORANStackStarter()
    starter.run()
