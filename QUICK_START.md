# ORAN Stack Quick Start Guide

## Quick Start (TL;DR)

### Option 1: Bash Script (Recommended)

```bash
chmod +x oran_stack_startup.sh
./oran_stack_startup.sh
```

### Option 2: Python Script

```bash
python3 oran_stack_startup_advanced.py
```

### Option 3: Alternative Python Script

```bash
python3 oran_stack_startup.py
```

---

## What Happens Next

| Time  | Action                           | Watch For                     |
| ----- | -------------------------------- | ----------------------------- |
| T+0s  | RIC Stack starts in tmux session | Docker containers launching   |
| T+5s  | 5GS Core starts in tmux session  | "Listening on..." messages    |
| T+10s | gNB starts in tmux session       | Connection to AMF established |
| T+15s | UE starts in tmux session        | Network connection successful |

---

## During Execution

### Monitor tmux Sessions

```bash
# List all tmux sessions
tmux ls

# Attach to RIC Stack session
tmux attach -t ric_stack

# Attach to 5GS Core session
tmux attach -t open5gs_core

# Attach to gNB session
tmux attach -t gnb

# Attach to UE session
tmux attach -t ue

# Detach from any session (without stopping it)
Ctrl+b then d
```

### Session 1: RIC Stack (ric_stack)

```
Starting ORAN-SC-RIC components...
[COMPONENT] Starting...
[COMPONENT] Ready
```

### Session 2: 5GS Core (open5gs_core)

```
Starting 5GC services...
[SERVICE] Initialized
[AMF] Listening on port 38412
```

### Session 3: gNB (gnb)

```
Loading configuration: gnb_zmq.yaml
GNU Radio Companion Starting...
[gNB] Connected to AMF at <IP>:<PORT>
[gNB] Connected to E2 node
```

### Session 4: UE (ue)

```
Network namespace created: ue1
Loading configuration: ue_zmq.conf
[UE] Connected to gNB
[UE] Connected to Core
```

---

## Health Check Commands

While services are running, check status:

```bash
# List all tmux sessions
tmux ls

# Check Docker containers
docker ps

# Check RIC stack containers
docker compose -f /root/fyp/oran-sc-ric/docker-compose.yml ps

# Check 5GS Core containers
docker compose -f /root/fyp/srsRAN_Project/docker/docker-compose.yml ps

# Check network namespaces
sudo ip netns list

# Check UE connection
sudo ip netns exec ue1 ip addr

# Monitor gNB process
ps aux | grep gnb

# Monitor srsue process
ps aux | grep srsue

# Attach to specific session for live output
tmux attach -t gnb     # For gNB logs
tmux attach -t ue      # For UE logs
```

---

## Stopping Services

```bash
# Method 1: Kill tmux sessions (Recommended)
tmux kill-session -t ric_stack
tmux kill-session -t open5gs_core
tmux kill-session -t gnb
tmux kill-session -t ue

# Method 2: Kill all at once
tmux kill-session -t ric_stack; tmux kill-session -t open5gs_core; tmux kill-session -t gnb; tmux kill-session -t ue

# Method 3: Use Docker to stop containers
# RIC Stack
docker compose -f /root/fyp/oran-sc-ric/docker-compose.yml down

# 5GS Core
docker compose -f /root/fyp/srsRAN_Project/docker/docker-compose.yml down

# Clean up network namespace
sudo ip netns delete ue1
```

---

## Common Issues & Fixes

### Issue: "tmux: command not found"

**Fix:** Install tmux

```bash
sudo apt update && sudo apt install -y tmux
```

### Issue: "Permission denied" on .sh script

**Fix:** Make it executable

```bash
chmod +x oran_stack_startup.sh
```

### Issue: "docker: command not found"

**Fix:** Ensure Docker is installed

```bash
# Check Docker
docker --version

# If not installed, follow docker documentation for your OS
```

### Issue: "5GC won't start" or "Port 38412 in use"

**Fix:** Clean up previous containers

```bash
# Stop all containers
docker stop $(docker ps -aq)

# Remove stopped containers
docker rm $(docker ps -aq)

# Or use compose to clean up
docker compose -f /root/fyp/srsRAN_Project/docker/docker-compose.yml down -v
```

### Issue: "gNB can't connect to AMF"

**Fix:** Ensure 5GS is fully started and check tmux session

```bash
# Wait 30-60 seconds after starting 5GS
# View gNB logs
tmux attach -t gnb

# Check Docker logs
docker logs <container_id>

# Verify network connectivity
docker exec <container> ping <amf_ip>
```

### Issue: "srsue fails to start"

**Fix:** Check network namespace and UE session

```bash
# Check if namespace exists
sudo ip netns list

# Delete and recreate if needed
sudo ip netns delete ue1 2>/dev/null || true
sudo ip netns add ue1

# View UE logs
tmux attach -t ue
```

---

## File Locations Reference

| Component | Config Path                             | Key Files            |
| --------- | --------------------------------------- | -------------------- |
| RIC Stack | `/root/fyp/oran-sc-ric/`                | `docker-compose.yml` |
| 5GS Core  | `/root/fyp/srsRAN_Project/docker/`      | `docker-compose.yml` |
| gNB       | `/root/fyp/srsRAN_Project/configs/`     | `gnb_zmq.yaml`       |
| UE        | `/root/fyp/srsRAN_Project/configs/`     | `ue_zmq.conf`        |

---

## Advanced: Manual Step-by-Step (If Scripts Fail)

Run these in separate tmux sessions:

**Session 1 (RIC Stack):**

```bash
tmux new-session -d -s ric_stack -c /root/fyp/oran-sc-ric 'docker compose up'
tmux attach -t ric_stack
```

**Session 2 (5GS Core) (wait ~5s):**

```bash
tmux new-session -d -s open5gs_core -c /root/fyp/srsRAN_Project/docker 'docker compose up 5gc'
tmux attach -t open5gs_core
```

**Session 3 (gNB) (wait ~5s):**

```bash
tmux new-session -d -s gnb -c /root/fyp/srsRAN_Project/configs 'gnb -c gnb_zmq.yaml'
tmux attach -t gnb
```

**Session 4 (UE) (wait ~5s):**

```bash
tmux new-session -d -s ue -c /root/fyp/srsRAN_Project/configs 'sudo ip netns add ue1 2>/dev/null || true; sudo ip netns list; sudo srsue ue_zmq.conf'
tmux attach -t ue
```

---

## Logs & Debugging

### View live logs from tmux session

```bash
# Attach to any tmux session to see live output
tmux attach -t ric_stack
tmux attach -t open5gs_core
tmux attach -t gnb
tmux attach -t ue

# Detach without stopping: Ctrl+b then d
```

### View container logs

```bash
docker logs -f <container_id>
# Example: docker logs -f oran-sc-ric-controller-1
```

### View all 5GC container logs

```bash
docker compose -f /root/fyp/srsRAN_Project/docker/docker-compose.yml logs -f
```

### Check system resources while running

```bash
# CPU and Memory usage
top

# Or use docker stats
docker stats
```

---

## Need Help?

1. Check output in tmux sessions: `tmux ls` and `tmux attach -t <session>`
2. Enable debug logging in config files (gnb_zmq.yaml, ue_zmq.conf)
3. Review Docker logs: `docker logs <container_id>`
4. Check if ports are already in use: `sudo netstat -tuln | grep LISTEN`
5. Verify paths are correct in your environment: `/root/fyp`

---

**Last Updated:** May 2026
**Script Version:** 2.0 (tmux version)
