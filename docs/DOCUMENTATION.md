# 🔗 Proxy Chain Tool - Comprehensive Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Core Components](#core-components)
6. [Command Reference](#command-reference)
7. [Usage Scenarios](#usage-scenarios)
8. [Configuration](#configuration)
9. [Tool Integration](#tool-integration)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)
12. [Security Considerations](#security-considerations)
13. [API Reference](#api-reference)
14. [Contributing](#contributing)

---

## Overview

The **Proxy Chain Tool** is a comprehensive, enterprise-grade proxy management system designed for security researchers, penetration testers, and bug bounty hunters. It provides automated proxy discovery, validation, rotation, and integration with popular security scanning tools.

### Key Features
- 🔄 **Automatic Proxy Discovery**: Fetches proxies from multiple free sources
- ✅ **Real-time Validation**: Tests proxy connectivity and performance
- 🔁 **Intelligent Rotation**: Smart proxy switching for scanning activities  
- 🛠️ **Tool Integration**: Native support for Nmap, Gobuster, FFUF, Nuclei, cURL
- 📊 **Background Daemon**: Runs continuously maintaining proxy pools
- 🎯 **One-Command Setup**: Simple initialization with `init-proxy-chain-now`
- 📝 **Comprehensive Logging**: Detailed activity logs and monitoring
- 🌐 **Multi-Source**: GitHub repos, APIs, and public proxy databases

### Use Cases
- **Bug Bounty Hunting**: Distribute scanning traffic across multiple IPs
- **Penetration Testing**: Avoid IP-based rate limiting and detection
- **Research Activities**: Anonymous reconnaissance and data gathering
- **Load Distribution**: Spread heavy scanning across proxy networks
- **Geo-location Testing**: Access services from different locations

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Proxy Chain System                       │
├─────────────────────────────────────────────────────────────┤
│  User Commands                                              │
│  ├── init-proxy-chain-now (Main initializer)               │
│  ├── proxy-status (Status checker)                         │
│  ├── proxy-stop (Daemon controller)                        │
│  └── proxy-scan (Tool wrapper)                             │
├─────────────────────────────────────────────────────────────┤
│  Core Engine                                               │
│  ├── ProxyChainManager (Discovery & validation)            │
│  ├── ProxyChainDaemon (Background service)                 │
│  ├── ProxyScanner (Tool integration)                       │
│  └── ProxyDaemonManager (Process management)               │
├─────────────────────────────────────────────────────────────┤
│  Data Sources                                              │
│  ├── GitHub Proxy Lists                                    │
│  ├── Public APIs (GeoNode, ProxyList)                      │
│  ├── Community Databases                                   │
│  └── Fallback Proxies                                      │
├─────────────────────────────────────────────────────────────┤
│  Output Formats                                            │
│  ├── working_proxies.txt (Plain text list)                │
│  ├── proxychains.conf (Proxychains config)                │
│  ├── proxy_config.json (JSON configuration)               │
│  └── daemon_status.json (Status file)                     │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
[Proxy Sources] → [Fetcher] → [Validator] → [Storage] → [Rotation] → [Tools]
       ↓              ↓           ↓           ↓          ↓         ↓
   GitHub APIs    HTTP Requests  Concurrent   Files    Random    Scanner
   Public Lists   Rate Limited   Testing    JSON/TXT  Selection  Integration
```

---

## Installation

### Prerequisites
- **Python 3.7+** (Tested on 3.8-3.13)
- **Windows 10/11** (Primary platform)
- **PowerShell 5.1+** (For installation scripts)
- **Internet Connection** (For proxy discovery)

### System Requirements
- **RAM**: Minimum 512MB available
- **Storage**: 50MB for system files + logs
- **Network**: Outbound HTTP/HTTPS access
- **Permissions**: User-level (Admin for system PATH)

### Installation Methods

#### Method 1: Automatic Setup
```powershell
# Download and run setup script
powershell -ExecutionPolicy Bypass -File setup_proxy_chain.ps1
```

#### Method 2: Manual Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system commands (optional)
powershell -ExecutionPolicy Bypass -File install_commands.ps1 -User
```

#### Method 3: Development Setup
```bash
# Clone or download files to desired directory
# Ensure all Python files are in the same directory
# Run initialization
python init_proxy_chain.py
```

---

## Quick Start

### Basic Usage
```bash
# 1. Initialize the system (one-time setup)
init-proxy-chain-now

# 2. Check system status
proxy-status

# 3. Test proxy connectivity  
proxy-scan test httpbin.org

# 4. Start scanning with proxies
proxy-scan curl https://httpbin.org/ip
```

### First-Time Setup
```bash
# Step 1: Run the initializer
init-proxy-chain-now
# This will:
# - Install dependencies
# - Create directories
# - Start the daemon
# - Fetch initial proxies

# Step 2: Wait for proxy discovery (2-5 minutes)
proxy-status

# Step 3: Verify proxy functionality
proxy-scan curl https://httpbin.org/ip
```

---

## Core Components

### 1. ProxyChainManager (`proxy_chain_setup.py`)
**Purpose**: Core proxy discovery and validation engine

#### Key Methods:
```python
class ProxyChainManager:
    def fetch_all_proxies()        # Discover proxies from all sources
    def validate_proxies()         # Test proxy connectivity 
    def create_proxy_chain()       # Generate proxy chains
    def get_random_proxy()         # Select random working proxy
    def save_proxies()            # Persist proxy list
```

#### Proxy Sources:
- **GitHub Repository**: `github.com/clarketm/proxy-list`
- **GeoNode API**: `proxylist.geonode.com/api/proxy-list`
- **TheSpeedX List**: `github.com/TheSpeedX/PROXY-List`
- **Proxy Download API**: `proxy-list.download/api/v1/get`

### 2. ProxyChainDaemon (`proxy_chain_daemon.py`)
**Purpose**: Background service for continuous proxy management

#### Features:
- **Auto-refresh**: Updates proxy list every hour (configurable)
- **Health Checks**: Tests random proxies every 5 minutes
- **Graceful Shutdown**: Handles SIGINT/SIGTERM signals
- **Status Reporting**: Maintains daemon_status.json
- **Error Recovery**: Continues operation despite failures

#### Configuration:
```python
refresh_interval = 3600    # Proxy refresh interval (seconds)
health_check_interval = 300 # Health check frequency (seconds)
max_workers = 50           # Concurrent validation threads
```

### 3. ProxyScanner (`proxy_scanner.py`)
**Purpose**: Tool integration wrapper for proxy-enabled scanning

#### Supported Tools:
| Tool | Proxy Support | Command Example |
|------|---------------|-----------------|
| **Nmap** | Via Proxychains | `proxy-scan nmap target.com -o "-sS -p 80,443"` |
| **Gobuster** | Native HTTP | `proxy-scan gobuster https://example.com -w wordlist.txt` |
| **FFUF** | Native HTTP | `proxy-scan ffuf https://example.com/FUZZ -w wordlist.txt` |
| **Nuclei** | Native HTTP | `proxy-scan nuclei https://example.com` |
| **cURL** | Native HTTP | `proxy-scan curl https://httpbin.org/ip` |

### 4. ProxyDaemonManager (`proxy_status.py`)
**Purpose**: Daemon lifecycle management and monitoring

#### Operations:
```bash
proxy-status start     # Start the daemon
proxy-status stop      # Stop the daemon  
proxy-status restart   # Restart the daemon
proxy-status status    # Show detailed status
```

---

## Command Reference

### Primary Commands

#### `init-proxy-chain-now`
**Description**: One-command initialization and startup

**Usage**:
```bash
init-proxy-chain-now
```

**What it does**:
1. Checks system dependencies
2. Installs missing Python packages
3. Creates necessary directories
4. Starts the background daemon
5. Initiates proxy discovery
6. Shows system status and usage guide

**Output Example**:
```
🔗 PROXY CHAIN INITIALIZER
==================================================
🔍 Checking dependencies...
✅ All dependencies found
✅ Directory ready: logs
✅ Directory ready: output  
✅ Directory ready: wordlists
🚀 Starting proxy chain daemon...
✅ Daemon started with PID 12345
```

#### `proxy-status`
**Description**: System status and monitoring

**Usage**:
```bash
proxy-status
```

**Output Example**:
```
🔗 Proxy Chain Daemon Status
========================================
🟢 Status: RUNNING
📅 Started: 2024-01-15T10:30:00.123456
🔄 Last Refresh: 2024-01-15T11:30:00.789012
🎯 Working Proxies: 47
🔢 Total Refreshes: 3
📊 Current Status: active
💾 Proxy File: 47 proxies available
📋 Sample proxies:
   • 1.2.3.4:8080
   • 5.6.7.8:3128
   • 9.10.11.12:80
   ... and 44 more
📝 Log File: 2.5 KB
```

#### `proxy-stop`
**Description**: Stop the background daemon

**Usage**:
```bash
proxy-stop
```

**Output**:
```
✅ Daemon (PID 12345) stopped gracefully
```

#### `proxy-scan`
**Description**: Proxy-enabled tool execution

**Syntax**:
```bash
proxy-scan <tool> <target> [options]
```

**Parameters**:
- `tool`: Scanner tool (nmap, gobuster, ffuf, nuclei, curl, test)
- `target`: Target URL or IP address
- `options`: Tool-specific options

---

## Usage Scenarios

### Scenario 1: Bug Bounty Reconnaissance

**Objective**: Perform subdomain enumeration without IP detection

```bash
# 1. Start the proxy system
init-proxy-chain-now

# 2. Wait for proxies to be discovered
proxy-status

# 3. Run subdomain enumeration through proxies
proxy-scan gobuster https://target.com -w wordlists/subdomains.txt -o "-t 10 -q"

# 4. Follow up with directory enumeration on found subdomains  
proxy-scan gobuster https://api.target.com -w wordlists/directory-list-2.3-medium.txt

# 5. Run nuclei templates through proxies
proxy-scan nuclei https://target.com -o "-t nuclei-templates/"
```

### Scenario 2: Penetration Testing - Network Scanning

**Objective**: Scan target network while avoiding rate limiting

```bash
# 1. Initialize system
init-proxy-chain-now

# 2. Perform port scanning through proxy chains
proxy-scan nmap 192.168.1.0/24 -o "-sS -T4 -p 1-1000"

# 3. Service enumeration on discovered ports
proxy-scan nmap 192.168.1.100 -o "-sV -sC -p 22,80,443"

# 4. HTTP service discovery
proxy-scan gobuster http://192.168.1.100 -w wordlists/common.txt
```

### Scenario 3: API Testing and Fuzzing

**Objective**: Test API endpoints with different source IPs

```bash
# 1. Start proxy system
init-proxy-chain-now

# 2. Test API endpoint connectivity
proxy-scan curl https://api.target.com/v1/users -o "-H 'Authorization: Bearer TOKEN'"

# 3. Fuzz API parameters
proxy-scan ffuf https://api.target.com/v1/FUZZ -w wordlists/api-endpoints.txt -o "-H 'Authorization: Bearer TOKEN'"

# 4. Test different HTTP methods
proxy-scan curl https://api.target.com/v1/users -o "-X POST -d '{\"test\":\"data\"}' -H 'Content-Type: application/json'"
```

### Scenario 4: Continuous Monitoring

**Objective**: Set up automated scanning with proxy rotation

```bash
# 1. Initialize with custom refresh interval (30 minutes)
python proxy_status.py start --refresh-interval 1800

# 2. Create monitoring script
#!/bin/bash
while true; do
    proxy-scan curl https://target.com/health -o "-s"
    sleep 300  # Check every 5 minutes
done

# 3. Monitor proxy health
watch -n 60 proxy-status
```

### Scenario 5: Geolocation Testing

**Objective**: Test service availability from different geographic locations

```bash
# 1. Start proxy system
init-proxy-chain-now

# 2. Test service from multiple proxy locations
for i in {1..10}; do
    echo "Test #$i:"
    proxy-scan curl https://geo-restricted-service.com -o "-s -I"
    sleep 10
done

# 3. Analyze response headers for geo-blocking
proxy-scan curl https://target.com -o "-v" | grep -E "(Location|Country|Region)"
```

### Scenario 6: Load Testing with Proxies

**Objective**: Distribute load testing traffic across multiple IPs

```bash
# 1. Initialize system
init-proxy-chain-now

# 2. Concurrent requests through different proxies
for i in {1..50}; do
    proxy-scan curl https://target.com/api/endpoint -o "-s -w '%{http_code}\n'" &
done
wait

# 3. Monitor proxy performance
proxy-status
```

---

## Configuration

### System Configuration Files

#### `proxy_config.json`
**Purpose**: Main system configuration
```json
{
  "working_proxies": [
    "1.2.3.4:8080",
    "5.6.7.8:3128"
  ],
  "rotation_enabled": true,
  "chain_length": 3,
  "timeout": 10,
  "user_agents": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
  ]
}
```

#### `proxychains.conf`
**Purpose**: Proxychains4 configuration
```ini
# Proxychains config for scanning
strict_chain
proxy_dns
remote_dns_subnet 224
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
http 1.2.3.4 8080
http 5.6.7.8 3128
http 9.10.11.12 80
```

#### `daemon_status.json`
**Purpose**: Daemon runtime status
```json
{
  "started": "2024-01-15T10:30:00.123456",
  "last_refresh": "2024-01-15T11:30:00.789012", 
  "working_proxies": 47,
  "total_refreshes": 3,
  "status": "active"
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HTTP_PROXY` | System HTTP proxy | Set by daemon |
| `HTTPS_PROXY` | System HTTPS proxy | Set by daemon |
| `PROXY_REFRESH_INTERVAL` | Refresh frequency (seconds) | 3600 |
| `PROXY_TIMEOUT` | Connection timeout | 10 |
| `PROXY_MAX_WORKERS` | Validation threads | 50 |

### Customization Options

#### Custom Proxy Sources
Add custom proxy sources by modifying `proxy_chain_setup.py`:
```python
self.proxy_sources = {
    'custom-source': 'https://your-proxy-api.com/list',
    # ... existing sources
}
```

#### Timeout Settings
Adjust validation timeouts:
```python
def validate_proxies(self, proxy_list, max_workers=50, timeout=15):
    # Custom timeout for slow proxies
```

#### Refresh Intervals
Customize daemon refresh frequency:
```bash
python proxy_status.py start --refresh-interval 7200  # 2 hours
```

---

## Tool Integration

### Nmap Integration
**Method**: Via Proxychains4

**Setup**:
```bash
# Install proxychains4 (Windows Subsystem for Linux)
wsl sudo apt update && wsl sudo apt install proxychains4

# Usage through proxy-scan
proxy-scan nmap target.com -o "-sS -p 80,443,8080"
```

**Direct Usage**:
```bash
# Using generated proxychains.conf
proxychains4 -f proxychains.conf nmap -sS target.com
```

### Gobuster Integration
**Method**: Native HTTP proxy support

**Usage**:
```bash
# Directory enumeration
proxy-scan gobuster https://target.com -w wordlists/common.txt -o "-t 20 -q"

# Subdomain enumeration  
proxy-scan gobuster https://target.com -w wordlists/subdomains.txt -o "-m dns"
```

**Direct Usage**:
```bash
# Using current proxy from config
gobuster dir -u https://target.com -w wordlist.txt --proxy http://1.2.3.4:8080
```

### FFUF Integration
**Method**: Native HTTP proxy support

**Usage**:
```bash
# Parameter fuzzing
proxy-scan ffuf https://target.com/page?FUZZ=value -w params.txt

# Directory fuzzing  
proxy-scan ffuf https://target.com/FUZZ -w directories.txt -o "-mc 200,301,302"
```

### Nuclei Integration
**Method**: Native proxy support

**Usage**:
```bash
# Run all templates
proxy-scan nuclei https://target.com

# Specific template categories
proxy-scan nuclei https://target.com -o "-tags cve,xss -severity medium,high"
```

### cURL Integration
**Method**: Native proxy support

**Usage**:
```bash
# Basic request
proxy-scan curl https://httpbin.org/ip

# POST request with data
proxy-scan curl https://api.target.com -o "-X POST -d 'data=test' -H 'Content-Type: application/x-www-form-urlencoded'"

# Custom headers
proxy-scan curl https://target.com -o "-H 'User-Agent: Custom-Agent' -H 'Authorization: Bearer token'"
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "No working proxies found"
**Symptoms**: System reports 0 working proxies after initialization

**Solutions**:
1. Check internet connectivity
2. Verify firewall settings allow outbound HTTP/HTTPS
3. Try manual proxy validation:
   ```bash
   python proxy_chain_setup.py
   ```
4. Check proxy source availability:
   ```bash
   curl -I https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt
   ```

#### Issue: "Daemon fails to start"
**Symptoms**: `init-proxy-chain-now` reports daemon startup failure

**Solutions**:
1. Check Python installation:
   ```bash
   python --version
   pip list | grep psutil
   ```
2. Verify file permissions
3. Check for port conflicts
4. Review daemon logs:
   ```bash
   type logs\proxy_daemon.log
   ```

#### Issue: "Command not found"
**Symptoms**: `init-proxy-chain-now` command not recognized

**Solutions**:
1. Add to PATH manually:
   ```powershell
   $env:PATH += ";/path/to/Pr0Xy-chaIN"
   ```
2. Use full paths:
   ```bash
   python /path/to/Pr0Xy-chaIN/init_proxy_chain.py
   ```
3. Run installation script:
   ```powershell
   powershell -ExecutionPolicy Bypass -File install_commands.ps1 -User
   ```

#### Issue: "Proxies working slowly"
**Symptoms**: Scanning takes much longer than expected

**Solutions**:
1. Increase timeout values:
   ```python
   # In proxy_chain_setup.py
   timeout = 20  # Increase from 10
   ```
2. Reduce concurrent workers:
   ```python
   max_workers = 20  # Reduce from 50
   ```
3. Filter by response time during validation

#### Issue: "Tool-specific errors"
**Symptoms**: Specific scanner tools fail through proxies

**Solutions**:
1. **Nmap**: Ensure proxychains4 is installed
2. **Gobuster**: Check target URL format (include protocol)
3. **FFUF**: Verify wordlist file exists and is readable
4. **Nuclei**: Update to latest version for proxy support

### Debug Mode
Enable detailed logging:
```python
# In any Python file, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Analysis
Check daemon activity:
```bash
# View real-time logs
Get-Content logs\proxy_daemon.log -Wait

# Search for errors
Select-String "ERROR" logs\proxy_daemon.log

# View last 50 lines
Get-Content logs\proxy_daemon.log | Select-Object -Last 50
```

---

## Best Practices

### Security Best Practices

#### 1. Proxy Validation
- Always validate proxies before use
- Set appropriate timeouts to avoid hanging
- Regularly refresh proxy lists to remove dead proxies

#### 2. Rate Limiting
```bash
# Implement delays between requests
proxy-scan curl https://target.com
sleep 5
proxy-scan curl https://target.com/api
```

#### 3. User Agent Rotation
Customize user agents to avoid detection:
```json
{
  "user_agents": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
  ]
}
```

### Performance Best Practices

#### 1. Proxy Pool Management
- Maintain minimum 20-30 working proxies
- Set refresh intervals based on proxy stability
- Monitor proxy response times

#### 2. Concurrent Operations
```bash
# Limit concurrent connections
proxy-scan gobuster https://target.com -o "-t 10"  # 10 threads max
```

#### 3. Resource Management
- Monitor system memory usage during large scans
- Clean up log files periodically
- Restart daemon weekly for fresh proxy pools

### Operational Best Practices

#### 1. Target Authorization
```bash
# Always verify authorization before scanning
echo "Scanning target: $TARGET"
echo "Authorization: [Confirm Y/N]"
read confirmation
```

#### 2. Output Management
```bash
# Organize scan results
mkdir results/$(date +%Y-%m-%d)
proxy-scan gobuster https://target.com > results/$(date +%Y-%m-%d)/gobuster.txt
```

#### 3. Backup and Recovery
```bash
# Backup working proxy list
copy working_proxies.txt backups\working_proxies_$(date +%Y%m%d).txt

# Backup configuration
copy proxy_config.json backups\
```

---

## Security Considerations

### Legal and Ethical Guidelines

#### ⚠️ **IMPORTANT DISCLAIMERS**
- **Authorization Required**: Only use on systems you own or have explicit written permission to test
- **Respect Rate Limits**: Don't overwhelm target services
- **Follow Disclosure**: Report findings through appropriate channels
- **Legal Compliance**: Ensure compliance with local laws and regulations

### Proxy Security Risks

#### 1. Traffic Interception
- **Risk**: Free proxies may log or intercept traffic
- **Mitigation**: Use HTTPS for sensitive requests
- **Best Practice**: Avoid sending credentials through proxies

#### 2. Proxy Reliability
- **Risk**: Proxies may be operated by malicious actors  
- **Mitigation**: Validate proxy sources and behavior
- **Best Practice**: Rotate proxies frequently

#### 3. IP Attribution
- **Risk**: Proxy activities may still be traced back
- **Mitigation**: Use legitimate proxy services for critical work
- **Best Practice**: Understand proxy logging policies

### Network Security

#### 1. Firewall Configuration
```powershell
# Allow outbound HTTP/HTTPS for proxy validation
New-NetFirewallRule -DisplayName "Proxy Chain Tool" -Direction Outbound -Protocol TCP -LocalPort 80,443,8080,3128 -Action Allow
```

#### 2. DNS Considerations
```bash
# Use proxy DNS resolution when possible
proxy-scan curl https://target.com --resolve target.com:443:127.0.0.1
```

### Data Protection

#### 1. Log Security
- Store logs in secure locations
- Rotate logs to prevent excessive disk usage
- Consider log encryption for sensitive environments

#### 2. Configuration Security
- Protect configuration files from unauthorized access
- Use environment variables for sensitive settings
- Regularly audit proxy sources

---

## API Reference

### Core Classes

#### ProxyChainManager
```python
class ProxyChainManager:
    def __init__(self):
        """Initialize proxy manager with default sources"""
        
    def fetch_all_proxies(self) -> List[str]:
        """Fetch proxies from all configured sources
        
        Returns:
            List of proxy strings in format 'ip:port'
        """
        
    def validate_proxies(self, proxy_list: List[str], max_workers: int = 50) -> List[str]:
        """Validate proxy connectivity
        
        Args:
            proxy_list: List of proxy strings to validate
            max_workers: Number of concurrent validation threads
            
        Returns:
            List of working proxy strings
        """
        
    def test_proxy(self, proxy: str, timeout: int = 10) -> bool:
        """Test individual proxy connectivity
        
        Args:
            proxy: Proxy string in format 'ip:port'
            timeout: Connection timeout in seconds
            
        Returns:
            True if proxy is working, False otherwise
        """
        
    def get_random_proxy(self) -> str:
        """Get random working proxy
        
        Returns:
            Random proxy string or None if no proxies available
        """
        
    def create_proxy_chain(self, chain_length: int = 3) -> List[str]:
        """Create proxy chain for advanced routing
        
        Args:
            chain_length: Number of proxies in chain
            
        Returns:
            List of proxy strings forming a chain
        """
```

#### ProxyScanner
```python
class ProxyScanner:
    def __init__(self, config_file: str = "proxy_config.json"):
        """Initialize scanner with configuration
        
        Args:
            config_file: Path to JSON configuration file
        """
        
    def rotate_proxy(self) -> str:
        """Rotate to new random proxy
        
        Returns:
            New proxy string or None
        """
        
    def run_nmap(self, target: str, options: str = "", use_proxy: bool = True):
        """Run Nmap through proxy chain
        
        Args:
            target: Target IP or hostname
            options: Nmap command line options
            use_proxy: Whether to use proxy routing
        """
        
    def run_gobuster(self, target: str, wordlist: str, options: str = "", use_proxy: bool = True):
        """Run Gobuster through proxy
        
        Args:
            target: Target URL
            wordlist: Path to wordlist file
            options: Gobuster options
            use_proxy: Whether to use proxy routing
        """
        
    def test_proxy_connectivity(self) -> bool:
        """Test current proxy connectivity
        
        Returns:
            True if current proxy is working
        """
```

### Configuration Schema

#### proxy_config.json
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "working_proxies": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}:\\d{1,5}$"
      }
    },
    "rotation_enabled": {
      "type": "boolean",
      "default": true
    },
    "chain_length": {
      "type": "integer", 
      "minimum": 1,
      "maximum": 10,
      "default": 3
    },
    "timeout": {
      "type": "integer",
      "minimum": 5,
      "maximum": 60,
      "default": 10
    },
    "user_agents": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": ["working_proxies"]
}
```

### REST API Endpoints (Future Enhancement)
```python
# Planned API endpoints for remote management
GET    /api/v1/status          # Get daemon status
GET    /api/v1/proxies         # List working proxies  
POST   /api/v1/proxies/refresh # Trigger proxy refresh
DELETE /api/v1/proxies/{id}    # Remove specific proxy
POST   /api/v1/scan            # Submit scan job
GET    /api/v1/scan/{id}       # Get scan results
```

---

## Contributing

### Development Setup
```bash
# Clone development environment
git clone <repository-url>
cd proxy-chain-tool

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black *.py
flake8 *.py
```

### Feature Requests
- **Enhanced Geo-targeting**: Add proxy location detection
- **Performance Metrics**: Add response time tracking
- **Proxy Scoring**: Implement proxy reliability scoring
- **GUI Interface**: Web-based management interface
- **Docker Support**: Containerized deployment option

### Bug Reports
Please include:
1. System information (OS, Python version)
2. Complete error messages and stack traces
3. Steps to reproduce the issue
4. Expected vs actual behavior
5. Log file excerpts (logs/proxy_daemon.log)

### Code Style
- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Include docstrings for all public methods
- Add unit tests for new functionality

---

## License and Legal

### Software License
This tool is provided for educational and authorized security testing purposes only.

### Liability Disclaimer
- Users are solely responsible for compliance with applicable laws
- The authors assume no liability for misuse of this software
- Use only on systems you own or have explicit permission to test

### Third-Party Components
- **Requests**: HTTP library (Apache 2.0 License)
- **PSUtil**: System utilities (BSD 3-Clause License)  
- **Proxy Sources**: Various public sources with their own terms

### Support and Contact
For issues, questions, or contributions:
- Create GitHub issues for bugs and feature requests
- Follow responsible disclosure for security issues
- Check documentation before asking questions

---

**Last Updated**: January 2024
**Version**: 1.0.0
**Compatibility**: Windows 10/11, Python 3.7+
