# ORAN Stack Quick Start Guide

## Quick Start (TL;DR)

### Option 1: Linux/WSL with Terminal Emulator (Recommended)
```bash
chmod +x oran_stack_startup.sh
./oran_stack_startup.sh
```

### Option 2: Windows/WSL with Python
```bash
python3 oran_stack_startup_advanced.py
```

### Option 3: Pure Python (Most Compatible)
```bash
python3 oran_stack_startup.py
```

---

## What Happens Next

| Time | Action | Watch For |
|------|--------|-----------|
| T+0s | RIC Stack starts in Terminal 1 | Docker containers launching |
| T+3s | 5GS Core starts in Terminal 2 | "Listening on..." messages |
| T+8s | gNB starts in Terminal 3 | Connection to AMF established |
| T+13s | UE starts in Terminal 4 | Network connection successful |

---

## During Execution

### Terminal 1 (RIC Stack)
```
Starting ORAN-SC-RIC components...
[COMPONENT] Starting...
[COMPONENT] Ready
```

### Terminal 2 (5GS Core)
```
Starting 5GC services...
[SERVICE] Initialized
[AMF] Listening on port 38412
```

### Terminal 3 (gNB)
```
Loading configuration: gnb_zmq.yaml
GNU Radio Companion Starting...
[gNB] Connected to AMF at <IP>:<PORT>
```

### Terminal 4 (UE)
```
Network namespace created: ue1
Loading configuration: ue_zmq.conf
[UE] Connected to gNB
[UE] Connected to Core
```

---

## Health Check Commands

While services are running, check status in a new terminal:

```bash
# Check Docker containers
docker ps

# Check RIC stack
docker compose -f /fyp/oran-sc-ric/docker-compose.yml ps

# Check 5GS Core
docker compose -f /fyp/srsRAN_Project/docker-compose.yml ps

# Check network namespaces
sudo ip netns list

# Check UE connection
sudo ip netns exec ue1 ip addr

# Check if gnb is running
ps aux | grep gnb

# Check if srsue is running
ps aux | grep srsue
```

---

## Stopping Services

```bash
# Method 1: Stop from each terminal (Recommended)
# Go to each terminal window and press Ctrl+C
# (They will stop gracefully)

# Method 2: Force stop from command line
# RIC Stack
docker compose -f /fyp/oran-sc-ric/docker-compose.yml down

# 5GS Core
docker compose -f /fyp/srsRAN_Project/docker-compose.yml down

# Kill srsRAN processes
pkill -f gnb
pkill -f srsue

# Clean up network namespace
sudo ip netns delete ue1
```

---

## Common Issues & Fixes

### Issue: "No terminal emulator found"
**Fix:** Install a terminal emulator
```bash
# Ubuntu/Debian
sudo apt-get install gnome-terminal

# Or use xterm
sudo apt-get install xterm
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
docker compose -f /fyp/srsRAN_Project/docker-compose.yml down -v
```

### Issue: "gNB can't connect to AMF"
**Fix:** Ensure 5GS is fully started
- Wait 30-60 seconds after starting 5GS
- Check Docker logs: `docker logs <container>`
- Verify network connectivity: `docker exec <container> ping <amf_ip>`

### Issue: "srsue fails to start"
**Fix:** Check network namespace
```bash
# Check if namespace exists
sudo ip netns list

# Delete and recreate if needed
sudo ip netns delete ue1 2>/dev/null || true
sudo ip netns add ue1
```

---

## File Locations Reference

| Component | Config Path | Key Files |
|-----------|-------------|-----------|
| RIC Stack | `/fyp/oran-sc-ric/` | `docker-compose.yml` |
| 5GS Core | `/fyp/srsRAN_Project/` | `docker-compose.yml` |
| gNB | `/fyp/srsRAN_Project/configs/` | `gnb_zmq.yaml` |
| UE | `/fyp/srsRAN_Project/configs/` | `ue_zmq.conf` |

---

## Advanced: Manual Step-by-Step (If Scripts Fail)

Run these in separate terminals:

**Terminal 1:**
```bash
cd /fyp/oran-sc-ric
docker compose up
```

**Terminal 2 (wait ~3s):**
```bash
cd /fyp/srsRAN_Project
docker compose up 5gc
```

**Terminal 3 (wait ~8s):**
```bash
cd /fyp/srsRAN_Project/configs
gnb -c gnb_zmq.yaml
```

**Terminal 4 (wait ~13s):**
```bash
sudo ip netns add ue1 2>/dev/null || true
ip netns list
cd /fyp/srsRAN_Project/configs
sudo srsue ue_zmq.conf
```

---

## Logs & Debugging

### View live logs for a container
```bash
docker logs -f <container_id>
# Example: docker logs -f oran-sc-ric-controller-1
```

### View all container logs
```bash
docker compose -f /fyp/srsRAN_Project/docker-compose.yml logs -f
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

1. Check output in each terminal for error messages
2. Enable debug logging in config files (gnb_zmq.yaml, ue_zmq.conf)
3. Review Docker logs: `docker logs <container_id>`
4. Check if ports are already in use: `sudo netstat -tuln | grep LISTEN`
5. Verify paths are correct in your environment

---

**Last Updated:** May 2026
**Script Version:** 1.0
