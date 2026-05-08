# Cyber Probes Integration Guide

## Overview

The ORAN stack startup scripts have been enhanced to include automatic deployment of cyber probe components alongside the core ORAN infrastructure. This guide explains the new functionality.

## New Components (Steps 5-8)

### Step 5: Cyber Probe Manager

- **Port**: 5050
- **Command**: `python3 -m uvicorn cyber_probe_manager_xapp2:app --host 0.0.0.0 --port 5050`
- **Location**: `/root/fyp/oran-sc-ric/xApps/python`
- **Purpose**: Central manager for all cyber probes
- **tmux Session**: `cyber_probe_manager`

### Step 6: O-DU Probe

- **Probe ID**: probe-odu-001
- **Component Type**: O-DU
- **Component Name**: simulated-o-du-1
- **IP Address**: 10.0.0.12
- **Interface**: E2
- **Location**: `/root/fyp/oran-sc-ric/xApps/python`
- **tmux Session**: `probe_odu`

### Step 7: O-CU Probe

- **Probe ID**: probe-ocu-001
- **Component Type**: O-CU
- **Component Name**: simulated-o-cu-1
- **IP Address**: 10.0.0.13
- **Interface**: F1/E1/NG
- **Location**: `/root/fyp/oran-sc-ric/xApps/python`
- **tmux Session**: `probe_ocu`

### Step 8: O-RU Probe

- **Probe ID**: probe-oru-001
- **Component Type**: O-RU
- **Component Name**: simulated-o-ru-1
- **IP Address**: 10.0.0.11
- **Interface**: OPEN-FRONTHAUL
- **Location**: `/root/fyp/oran-sc-ric/xApps/python`
- **tmux Session**: `probe_oru`

## Total Timeline

| Time  | Component           | Session Name        |
| ----- | ------------------- | ------------------- |
| T+0s  | RIC Stack           | ric_stack           |
| T+5s  | Open5GS Core (5GC)  | open5gs_core        |
| T+10s | srsRAN gNB          | gnb                 |
| T+15s | srsUE               | ue                  |
| T+20s | Cyber Probe Manager | cyber_probe_manager |
| T+23s | O-DU Probe          | probe_odu           |
| T+26s | O-CU Probe          | probe_ocu           |
| T+29s | O-RU Probe          | probe_oru           |

**Total Setup Time**: ~30 seconds

## Usage

### Start All Components

```bash
# Using bash script (recommended)
chmod +x oran_stack_startup.sh
./oran_stack_startup.sh

# Using Python
python3 oran_stack_startup.py
python3 oran_stack_startup_advanced.py
```

### Monitor Individual Components

```bash
# List all sessions
tmux ls

# Attach to a specific session
tmux attach -t cyber_probe_manager
tmux attach -t probe_odu
tmux attach -t probe_ocu
tmux attach -t probe_oru
```

### Stop All Components at Once

```bash
# Kill all ORAN sessions
tmux kill-session -t ric_stack; \
tmux kill-session -t open5gs_core; \
tmux kill-session -t gnb; \
tmux kill-session -t ue; \
tmux kill-session -t cyber_probe_manager; \
tmux kill-session -t probe_odu; \
tmux kill-session -t probe_ocu; \
tmux kill-session -t probe_oru
```

## Environment Variables Used

### O-DU Probe

```bash
PROBE_ID=probe-odu-001
COMPONENT_TYPE=O-DU
COMPONENT_NAME=simulated-o-du-1
IP_ADDRESS=10.0.0.12
INTERFACE=E2
```

### O-CU Probe

```bash
PROBE_ID=probe-ocu-001
COMPONENT_TYPE=O-CU
COMPONENT_NAME=simulated-o-cu-1
IP_ADDRESS=10.0.0.13
INTERFACE=F1/E1/NG
```

### O-RU Probe

```bash
PROBE_ID=probe-oru-001
COMPONENT_TYPE=O-RU
COMPONENT_NAME=simulated-o-ru-1
IP_ADDRESS=10.0.0.11
INTERFACE=OPEN-FRONTHAUL
```

## Expected Output

### Cyber Probe Manager (Port 5050)

```
Uvicorn running on http://0.0.0.0:5050
Application startup complete
Waiting for probe connections...
```

### O-DU/O-CU/O-RU Probes

```
Starting cyber probe...
[Probe Name] Connecting to manager at localhost:5050
[Probe Name] Connected successfully
[Probe Name] Monitoring [COMPONENT_TYPE] activity
```

## Troubleshooting

### Port 5050 Already in Use

```bash
# Kill process on port 5050
lsof -i :5050
kill -9 <PID>

# Or change port in scripts (XAPPS_PATH/cyber_probe_manager_xapp2:app settings)
```

### Probes Can't Connect to Manager

- Ensure cyber_probe_manager started first (check with `tmux attach -t cyber_probe_manager`)
- Verify network connectivity: `ping 127.0.0.1:5050`
- Check firewall rules

### Script Fails to Start Probes

- Ensure Python dependencies are installed:
  ```bash
  pip install uvicorn fastapi
  ```
- Verify xApps directory exists: `ls -la /root/fyp/oran-sc-ric/xApps/python/`

## Configuration

To modify probe settings, edit the script configuration section:

### Bash Script

```bash
# Edit oran_stack_startup.sh
XAPPS_PATH="${RIC_PATH}/xApps/python"
PROBE_ODU_ID="probe-odu-001"
PROBE_ODU_COMPONENT="O-DU"
# ... etc
```

### Python Scripts

```python
# Edit oran_stack_startup.py or oran_stack_startup_advanced.py
XAPPS_PATH = f"{RIC_PATH}/xApps/python"
PROBES = {
    "probe_odu": {
        "title": "O-DU Probe",
        "env": {
            "PROBE_ID": "probe-odu-001",
            # ... etc
        }
    }
}
```

## Version History

- **v2.0 (Current)**: Added cyber probe support (4 new components: Probe Manager + 3 Probes)
- **v1.0**: Initial release with 4 core ORAN components (RIC, 5GC, gNB, UE)

---

**Last Updated**: May 2026
**Tested With**: Ubuntu 20.04+, Python 3.8+, tmux 2.0+, Docker 20.10+
