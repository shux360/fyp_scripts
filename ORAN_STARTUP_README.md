# ORAN Stack Startup Scripts

This directory contains automated scripts to start the ORAN stack components in separate tmux sessions. The scripts eliminate the need to manually open multiple terminals and run each command sequentially. Uses tmux for SSH/headless VM compatibility.

## Available Scripts

### 1. **oran_stack_startup.sh** (Recommended for Linux/WSL)

A bash script that starts components in separate tmux sessions.

**Usage:**

```bash
chmod +x oran_stack_startup.sh
./oran_stack_startup.sh
```

**Requirements:**

- tmux must be installed:
  ```bash
  sudo apt update && sudo apt install -y tmux
  ```

---

### 2. **oran_stack_startup_advanced.py** (Python Version with tmux)

Python script that starts components in separate tmux sessions.

**Usage:**

```bash
python3 oran_stack_startup_advanced.py
```

**Requirements:**

- Python 3.6+
- tmux installed

---

### 3. **oran_stack_startup.py** (Fallback Python Option)

Python script with tmux session management.

**Usage:**

```bash
python3 oran_stack_startup.py
```

**Requirements:**

- Python 3.6+
- tmux installed

---

## What Each Script Does

All scripts automate the following steps:

| Step | Command                                                                                           | Purpose             |
| ---- | ------------------------------------------------------------------------------------------------- | ------------------- |
| 1    | `cd /root/fyp/oran-sc-ric && docker compose up`                                                  | Start RIC Stack     |
| 2    | `cd /root/fyp/srsRAN_Project/docker && docker compose up 5gc`                                    | Start Open 5GS Core |
| 3    | `cd /root/fyp/srsRAN_Project/configs && gnb -c gnb_zmq.yaml`                                     | Start srsRAN gNB    |
| 4    | `sudo ip netns add ue1 && cd /root/fyp/srsRAN_Project/configs && sudo srsue ue_zmq.conf`         | Start srsUE         |

Each step runs in a separate tmux session with appropriate delays between startups.

---

## Script Execution Flow

```
1. RIC Stack starts in tmux session (5 second delay)
   ↓
2. 5GS Core starts in tmux session (5 second delay)
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

- Each component runs in its own tmux session
- View running sessions: `tmux ls`
- Attach to a session: `tmux attach -t <session_name>`
- Detach from a session: `Ctrl+b` then `d`
- The gNB session will show connection to AMF and E2 nodes
- The UE session will show connection establishment

### Stopping Services

To stop all services:

```bash
# Kill individual tmux sessions
tmux kill-session -t ric_stack
tmux kill-session -t open5gs_core
tmux kill-session -t gnb
tmux kill-session -t ue

# Or stop all ORAN-related sessions at once
tmux kill-session -t ric_stack; tmux kill-session -t open5gs_core; tmux kill-session -t gnb; tmux kill-session -t ue
```

---

## Troubleshooting

### tmux Not Installed

If you see "tmux is not installed":

```bash
sudo apt update && sudo apt install -y tmux
```

### Permission Denied

If you get permission errors:

```bash
# Make the bash script executable
chmod +x oran_stack_startup.sh
```

### Python Script Doesn't Find Commands

- Ensure Python 3 is installed: `python3 --version`
- Verify tmux is installed: `tmux --version`

### gNB Won't Connect to AMF

- Verify 5GS Core is fully started before gNB attempts connection
- Check Docker logs: `docker logs <container_id>`
- Ensure network connectivity between containers
- Attach to gNB session: `tmux attach -t gnb`

### UE Namespace Errors

- If `ip netns add ue1` fails with "File exists":
  - The namespace already exists; it will be reused
  - To clean up: `sudo ip netns delete ue1`
- Attach to UE session: `tmux attach -t ue`

---

## Configuration

To modify start paths or commands, edit the configuration section at the top of each script:

**Bash:**

```bash
BASE_PATH="/root/fyp"
SRSRAN_PATH="${BASE_PATH}/srsRAN_Project"
CORE5G_PATH="${BASE_PATH}/srsRAN_Project/docker"
RIC_PATH="${BASE_PATH}/oran-sc-ric"
CONFIGS_PATH="${SRSRAN_PATH}/configs"
```

**Python:**

```python
BASE_PATH = "/root/fyp"
SRSRAN_PATH = f"{BASE_PATH}/srsRAN_Project"
CORE5G_PATH = f"{BASE_PATH}/srsRAN_Project/docker"
RIC_PATH = f"{BASE_PATH}/oran-sc-ric"
CONFIGS_PATH = f"{SRSRAN_PATH}/configs"
```

---

## Recommended Script Selection

| Scenario        | Recommended Script      |
| --------------- | ----------------------- |
| Linux/WSL       | `oran_stack_startup.sh` |
| Python Fallback | `oran_stack_startup.py` |

All scripts use tmux for terminal session management, making them suitable for SSH and headless VM deployments.

---

## Version Information

- **Created:** May 2026
- **Updated:** May 2026 (tmux version)
- **Python Version Required:** 3.6+
- **Bash Version:** 4.0+
- **tmux Version Required:** 2.0+

---

## Support

For issues or feature requests, check:

1. Script output for error messages
2. Attached tmux sessions for component-specific errors: `tmux ls` and `tmux attach -t <session>`
3. Docker logs for container issues: `docker logs <container_id>`
