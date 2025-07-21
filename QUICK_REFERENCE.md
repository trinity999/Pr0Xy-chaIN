# 🚀 Proxy Chain Tool - Quick Reference

## ⚡ Quick Start Commands

```bash
# Start the system
init-proxy-chain-now

# Check status
proxy-status

# Test connectivity
proxy-scan test httpbin.org

# Stop the system
proxy-stop
```

## 🔧 Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init-proxy-chain-now` | Initialize and start daemon | `init-proxy-chain-now` |
| `proxy-status` | Show daemon status | `proxy-status` |
| `proxy-stop` | Stop daemon | `proxy-stop` |
| `proxy-scan` | Run tools through proxies | `proxy-scan curl httpbin.org/ip` |

## 🎯 Tool Integration

### Web Scanning
```bash
# Directory enumeration
proxy-scan gobuster https://target.com -w wordlists/common.txt

# Parameter fuzzing
proxy-scan ffuf https://target.com/FUZZ -w params.txt

# Vulnerability scanning
proxy-scan nuclei https://target.com
```

### Network Scanning
```bash
# Port scanning (requires proxychains)
proxy-scan nmap target.com -o "-sS -p 80,443"

# Service enumeration
proxy-scan nmap target.com -o "-sV -sC -p 22,80,443"
```

### API Testing
```bash
# GET request
proxy-scan curl https://api.target.com/users

# POST request
proxy-scan curl https://api.target.com -o "-X POST -d 'data=test'"

# With headers
proxy-scan curl https://api.target.com -o "-H 'Authorization: Bearer TOKEN'"
```

## 📊 Status and Monitoring

### Check System Health
```bash
proxy-status                    # Full status report
python proxy_status.py status   # Detailed status
Get-Content logs\proxy_daemon.log -Wait  # Real-time logs
```

### Configuration Files
- `working_proxies.txt` - Current proxy list
- `proxy_config.json` - System configuration  
- `proxychains.conf` - Proxychains configuration
- `daemon_status.json` - Runtime status

## 🔄 Common Workflows

### Bug Bounty Reconnaissance
```bash
init-proxy-chain-now
proxy-status
proxy-scan gobuster https://target.com -w subdomains.txt
proxy-scan nuclei https://target.com
```

### Penetration Testing
```bash
init-proxy-chain-now
proxy-scan nmap 192.168.1.0/24 -o "-sS -T4"
proxy-scan gobuster http://192.168.1.100 -w directories.txt
```

### API Security Testing
```bash
init-proxy-chain-now
proxy-scan curl https://api.target.com/health
proxy-scan ffuf https://api.target.com/FUZZ -w endpoints.txt
```

## ⚡ Advanced Usage

### Custom Refresh Interval
```bash
python proxy_status.py start --refresh-interval 1800  # 30 minutes
```

### Manual Proxy Management
```python
# In Python scripts
from proxy_scanner import ProxyScanner
scanner = ProxyScanner()
proxy = scanner.get_random_proxy()
```

### Batch Operations
```bash
# Multiple targets
for target in target1.com target2.com target3.com; do
    proxy-scan gobuster https://$target -w wordlist.txt
done
```

## 🛠️ Troubleshooting

### Common Issues
```bash
# No proxies found
python proxy_chain_setup.py

# Command not found  
$env:PATH += ";/path/to/Pr0Xy-chaIN"

# Daemon won't start
python proxy_status.py stop
python proxy_status.py start

# Check logs
type logs\proxy_daemon.log
```

### Performance Tuning
```python
# In proxy_chain_setup.py
max_workers = 20        # Reduce concurrent threads
timeout = 15           # Increase timeout
refresh_interval = 7200 # 2-hour refresh
```

## 📋 File Locations

```
Pr0Xy-chaIN/
├── init-proxy-chain-now.bat    # Main command
├── proxy-status.bat            # Status checker  
├── proxy-stop.bat              # Stop daemon
├── proxy-scan.bat              # Tool wrapper
├── working_proxies.txt         # Active proxy list
├── proxy_config.json           # Configuration
├── proxychains.conf            # Proxychains config
├── daemon_status.json          # Runtime status
└── logs/
    └── proxy_daemon.log        # Activity logs
```

## ⚠️ Important Notes

- **Authorization**: Only scan authorized targets
- **Rate Limiting**: Implement delays between requests  
- **Legal Compliance**: Follow local laws and regulations
- **Proxy Trust**: Free proxies may not be secure
- **Regular Updates**: Restart daemon weekly for fresh proxies

## 📖 Full Documentation

For detailed documentation, see: `DOCUMENTATION.md`

---
**Quick Reference v1.0** | Last Updated: January 2024
