# ORAN Stack Startup Scripts

This directory contains automated scripts to start the ORAN stack components in separate terminals. The scripts eliminate the need to manually open multiple terminals and run each command sequentially.

## Available Scripts

### 1. **oran_stack_startup.sh** (Recommended for Linux/WSL)

A bash script that opens separate terminal windows for each component.

**Usage:**

```bash
chmod +x oran_stack_startup.sh
./oran_stack_startup.sh
```

**Requirements:**

- One of these terminal emulators must be installed:
  - `gnome-terminal` (GNOME Desktop)
  - `xterm` (X11)
  - `konsole` (KDE)

---

### 2. **oran_stack_startup_advanced.py** (For Windows/WSL with Windows Terminal)

Python script that opens separate terminal windows using Windows Terminal if available.

**Usage:**

```bash
python3 oran_stack_startup_advanced.py
```

**Requirements:**

- Python 3.6+
- Windows Terminal (recommended) or WSL with bash

---

### 3. **oran_stack_startup.py** (Fallback Option)

Python script that runs all components with built-in subprocess management.

**Usage:**

```bash
python3 oran_stack_startup.py
```

**Requirements:**

- Python 3.6+

---

## What Each Script Does

All scripts automate the following steps:

| Step | Command                                                                             | Purpose             |
| ---- | ----------------------------------------------------------------------------------- | ------------------- |
| 1    | `cd /fyp/oran-sc-ric && docker compose up`                                          | Start RIC Stack     |
| 2    | `cd /fyp/srsRAN_Project && docker compose up 5gc`                                   | Start Open 5GS Core |
| 3    | `cd /fyp/srsRAN_Project/configs && gnb -c gnb_zmq.yaml`                             | Start srsRAN gNB    |
| 4    | `sudo ip netns add ue1 && cd /fyp/srsRAN_Project/configs && sudo srsue ue_zmq.conf` | Start srsUE         |

Each step runs in a separate terminal with appropriate delays between startups.

---

## Script Execution Flow

```
1. RIC Stack starts (3 second delay)
   ↓
2. 5GS Core starts (3 second delay)
   ↓
3. srsRAN gNB starts (5 second delay before starting)
   ↓
4. srsUE starts (5 second delay before starting)
```

---

## Important Notes

### Permissions

The srsUE step requires `sudo` privileges. You may need to:

- Enter your password when prompted
- Or configure sudo to work without a password for the specific commands

### Network Namespace

The script automatically attempts to create a network namespace for the UE:

```bash
sudo ip netns add ue1
```

If it already exists, the error is suppressed and execution continues.

### Monitoring

- Each component runs in its own terminal window
- Watch the terminal windows to see startup progress
- The gNB terminal will show connection to AMF
- The UE terminal will show connection establishment

### Stopping Services

To stop all services:

1. Go to each terminal window
2. Press `Ctrl+C` to stop that component
3. Or use Docker commands to stop containers:

```bash
# Stop RIC Stack
docker compose -f /fyp/oran-sc-ric/docker-compose.yml down

# Stop 5GS Core
docker compose -f /fyp/srsRAN_Project/docker-compose.yml down 5gc
```

---

## Troubleshooting

### No Terminal Manager Found

If you see "No compatible terminal found":

- Install one of: `gnome-terminal`, `xterm`, or `konsole`
- Or edit the script to use a different terminal emulator

### Permission Denied

If you get permission errors:

```bash
# Make the bash script executable
chmod +x oran_stack_startup.sh
```

### Python Script Doesn't Find Commands

- Ensure Python 3 is installed: `python3 --version`
- Check that WSL bash is available: `wsl bash --version`

### gNB Won't Connect to AMF

- Verify 5GS Core is fully started before gNB attempts connection
- Check Docker logs: `docker logs <container_id>`
- Ensure network connectivity between containers

### UE Namespace Errors

- If `ip netns add ue1` fails with "File exists":
  - The namespace already exists; it will be reused
  - To clean up: `sudo ip netns delete ue1`

---

## Configuration

To modify start paths or commands, edit the configuration section at the top of each script:

**Bash:**

```bash
SRSRAN_PATH="/fyp/srsRAN_Project"
RIC_PATH="/fyp/oran-sc-ric"
CONFIGS_PATH="${SRSRAN_PATH}/configs"
```

**Python:**

```python
SRSRAN_PATH = "/fyp/srsRAN_Project"
RIC_PATH = "/fyp/oran-sc-ric"
CONFIGS_PATH = f"{SRSRAN_PATH}/configs"
```

---

## Recommended Script Selection

| Scenario                     | Recommended Script               |
| ---------------------------- | -------------------------------- |
| Linux with GNOME/KDE         | `oran_stack_startup.sh`          |
| WSL with Windows Terminal    | `oran_stack_startup_advanced.py` |
| WSL without Windows Terminal | `oran_stack_startup.py`          |
| Minimal Linux (no GUI)       | `oran_stack_startup.py`          |

---

## Version Information

- **Created:** May 2026
- **Python Version Required:** 3.6+
- **Bash Version:** 4.0+
- **Tested On:** Linux, WSL

---

## Support

For issues or feature requests, check:

1. Script output for error messages
2. Individual terminal windows for component-specific errors
3. Docker logs for container issues
