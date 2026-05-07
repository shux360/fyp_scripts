#!/usr/bin/env python3
"""
ORAN Stack Startup Script - Advanced Version with Separate Terminal Windows
Starts each component in its own terminal window for easier monitoring
"""

import subprocess
import time
import sys
import os

# Configuration
SRSRAN_PATH = "/fyp/srsRAN_Project"
RIC_PATH = "/fyp/oran-sc-ric"
CONFIGS_PATH = f"{SRSRAN_PATH}/configs"

class ORANStackStarterAdvanced:
    def __init__(self):
        self.terminal_pids = []
        
    def open_terminal(self, title, command):
        """Open a new terminal window with the given command"""
        print(f"[*] Opening terminal for: {title}")
        
        if sys.platform == 'win32':
            # For Windows/WSL - use Windows Terminal
            try:
                # Try using Windows Terminal
                proc = subprocess.Popen([
                    'wt', '-w', '0', 'nt', 'wsl', 'bash', '-c', command
                ])
                self.terminal_pids.append((title, proc))
                print(f"    ✓ Started: {title} (PID: {proc.pid})")
            except FileNotFoundError:
                # Fallback to wsl bash
                proc = subprocess.Popen([
                    'wsl', 'bash', '-c', command
                ])
                self.terminal_pids.append((title, proc))
                print(f"    ✓ Started: {title} (PID: {proc.pid})")
        else:
            # For Linux - use gnome-terminal or xterm
            if os.system('which gnome-terminal > /dev/null 2>&1') == 0:
                proc = subprocess.Popen([
                    'gnome-terminal', '--',
                    'bash', '-c', f'{command}; read -p "Press Enter to close..."'
                ])
            elif os.system('which xterm > /dev/null 2>&1') == 0:
                proc = subprocess.Popen([
                    'xterm', '-title', title, '-e',
                    'bash', '-c', f'{command}; read -p "Press Enter to close..."'
                ])
            else:
                # Fallback
                proc = subprocess.Popen([
                    'bash', '-c', command
                ])
            
            self.terminal_pids.append((title, proc))
            print(f"    ✓ Started: {title} (PID: {proc.pid})")
    
    def run(self):
        """Run all startup steps with separate terminals"""
        print("=" * 70)
        print(" " * 15 + "ORAN Stack Startup Script - Advanced")
        print("=" * 70)
        print()
        
        try:
            # Step 1: RIC Stack
            print("[1/4] Starting RIC Stack...")
            self.open_terminal(
                "RIC Stack",
                f"cd {RIC_PATH} && docker compose up"
            )
            time.sleep(2)
            
            # Step 2: Open 5GS Core
            print("\n[2/4] Starting Open 5GS Core...")
            self.open_terminal(
                "5GS Core",
                f"cd {SRSRAN_PATH} && docker compose up 5gc"
            )
            time.sleep(2)
            
            # Step 3: srsRAN gNB
            print("\n[3/4] Starting srsRAN gNB...")
            print("    ⏳ Waiting 5 seconds before starting gNB...")
            time.sleep(5)
            self.open_terminal(
                "srsRAN gNB",
                f"cd {CONFIGS_PATH} && gnb -c gnb_zmq.yaml"
            )
            print("    💡 Watch for gNB connecting to AMF in the terminal")
            time.sleep(3)
            
            # Step 4: srsUE
            print("\n[4/4] Starting srsUE...")
            print("    ⏳ Waiting 5 seconds before starting UE...")
            time.sleep(5)
            self.open_terminal(
                "srsUE",
                f"sudo ip netns add ue1 2>/dev/null || true; sudo ip netns list; cd {CONFIGS_PATH} && sudo srsue ue_zmq.conf"
            )
            
            print("\n" + "=" * 70)
            print("✓ All components launched in separate terminals!")
            print("=" * 70)
            print("\nRunning Components:")
            for title, proc in self.terminal_pids:
                print(f"  • {title}: PID {proc.pid}")
            print("\n" + "=" * 70)
            print("Monitor each terminal for startup progress.")
            print("Press Ctrl+C to attempt clean shutdown.")
            print("=" * 70)
            
            # Keep script running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n[!] Shutdown requested...")
                self.cleanup()
        
        except Exception as e:
            print(f"\n[ERROR] {e}")
            self.cleanup()
            sys.exit(1)
    
    def cleanup(self):
        """Attempt to terminate all processes"""
        print("Cleaning up processes...")
        for title, proc in self.terminal_pids:
            try:
                if proc.poll() is None:
                    proc.terminate()
                    print(f"  • Terminated: {title} (PID: {proc.pid})")
            except:
                pass

if __name__ == "__main__":
    starter = ORANStackStarterAdvanced()
    starter.run()
