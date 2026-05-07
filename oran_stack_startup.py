#!/usr/bin/env python3
"""
ORAN Stack Startup Script
Starts the RIC stack, 5GS core, srsRAN gNB, and srsUE in separate terminals
"""

import subprocess
import time
import sys
import os
from pathlib import Path

# Configuration
SRSRAN_PATH = "/fyp/srsRAN_Project"
RIC_PATH = "/fyp/oran-sc-ric"
CONFIGS_PATH = f"{SRSRAN_PATH}/configs"

class ORANStackStarter:
    def __init__(self):
        self.processes = []
        self.is_wsl = self._detect_wsl()
        
    def _detect_wsl(self):
        """Detect if running in WSL"""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except:
            return False
    
    def _get_terminal_command(self, command_str):
        """Get the appropriate terminal command based on OS"""
        if sys.platform == 'win32':
            # Use Windows terminal or WSL
            return f'wsl bash -c "{command_str}"'
        else:
            # Use gnome-terminal or xterm for Linux
            if os.system('which gnome-terminal > /dev/null 2>&1') == 0:
                return f'gnome-terminal -- bash -c "{command_str}"'
            elif os.system('which xterm > /dev/null 2>&1') == 0:
                return f'xterm -e bash -c "{command_str}"'
            else:
                # Fallback to bash -c
                return f'bash -c "{command_str}"'
    
    def start_ric_stack(self):
        """Step 1: Start the RIC stack"""
        print("[1/4] Starting RIC stack...")
        cmd = f'cd {RIC_PATH} && docker compose up'
        
        if sys.platform == 'win32':
            # Use Windows terminal for WSL
            proc = subprocess.Popen(
                ['wsl', 'bash', '-c', cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            proc = subprocess.Popen(
                ['bash', '-c', cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        self.processes.append(('RIC Stack', proc))
        print(f"   ✓ RIC stack started (PID: {proc.pid})")
        time.sleep(3)
    
    def start_5gc(self):
        """Step 2: Start the Open 5GS core"""
        print("[2/4] Starting Open 5GS core...")
        cmd = f'cd {SRSRAN_PATH} && docker compose up 5gc'
        
        if sys.platform == 'win32':
            proc = subprocess.Popen(
                ['wsl', 'bash', '-c', cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            proc = subprocess.Popen(
                ['bash', '-c', cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        self.processes.append(('5GS Core', proc))
        print(f"   ✓ 5GS core started (PID: {proc.pid})")
        time.sleep(3)
    
    def start_gnb(self):
        """Step 3: Start the srsRAN gNB"""
        print("[3/4] Starting srsRAN gNB...")
        cmd = f'cd {CONFIGS_PATH} && gnb -c gnb_zmq.yaml'
        
        if sys.platform == 'win32':
            proc = subprocess.Popen(
                ['wsl', 'bash', '-c', cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            proc = subprocess.Popen(
                ['bash', '-c', cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        self.processes.append(('srsRAN gNB', proc))
        print(f"   ✓ srsRAN gNB started (PID: {proc.pid})")
        print("   ⏳ Waiting for gNB to connect to AMF...")
        time.sleep(5)
    
    def start_ue(self):
        """Step 4: Start the srsUE"""
        print("[4/4] Starting srsUE...")
        
        # Create network namespace and start UE
        setup_cmd = f'sudo ip netns add ue1; cd {CONFIGS_PATH} && sudo srsue ue_zmq.conf'
        
        if sys.platform == 'win32':
            proc = subprocess.Popen(
                ['wsl', 'bash', '-c', setup_cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            proc = subprocess.Popen(
                ['bash', '-c', setup_cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        self.processes.append(('srsUE', proc))
        print(f"   ✓ srsUE started (PID: {proc.pid})")
    
    def run(self):
        """Run all startup steps"""
        print("=" * 60)
        print("ORAN Stack Startup Script")
        print("=" * 60)
        print()
        
        try:
            self.start_ric_stack()
            self.start_5gc()
            self.start_gnb()
            self.start_ue()
            
            print()
            print("=" * 60)
            print("All components started successfully!")
            print("=" * 60)
            print()
            print("Running processes:")
            for name, proc in self.processes:
                print(f"  • {name}: PID {proc.pid}")
            print()
            print("To stop all services, press Ctrl+C")
            print("=" * 60)
            
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
        """Terminate all processes"""
        for name, proc in self.processes:
            if proc.poll() is None:  # Process is still running
                try:
                    proc.terminate()
                    print(f"  • Terminated {name} (PID: {proc.pid})")
                except:
                    pass
        
        # Wait for all processes to terminate
        for name, proc in self.processes:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                print(f"  • Force killed {name} (PID: {proc.pid})")

if __name__ == "__main__":
    starter = ORANStackStarter()
    starter.run()
