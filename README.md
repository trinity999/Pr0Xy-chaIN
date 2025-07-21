# 🔗 Pr0Xy-chaIN - Advanced Proxy Chain Management Tool

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)](https://github.com/trinity999/Pr0Xy-chaIN)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Contributions](https://img.shields.io/badge/contributions-welcome-orange.svg)](CONTRIBUTING.md)

> **Enterprise-grade proxy chain management system for security researchers, penetration testers, and bug bounty hunters.**

## 🚀 Features

- 🔄 **Automatic Proxy Discovery** - Fetches proxies from multiple free sources
- ✅ **Real-time Validation** - Tests proxy connectivity and performance
- 🔁 **Intelligent Rotation** - Smart proxy switching for scanning activities
- 🛠️ **Tool Integration** - Native support for Nmap, Gobuster, FFUF, Nuclei, cURL
- 📊 **Enhanced Daemon Management** - Advanced status monitoring with health checks
- 🧪 **Comprehensive Testing** - Automated test suite with detailed reporting
- 🎯 **One-Command Setup** - Simple initialization with `init-proxy-chain-now`
- 📝 **Advanced Monitoring** - Resource usage, uptime, and proxy health tracking
- 🌐 **Multi-Source** - GitHub repos, APIs, and public proxy databases
- 🔧 **Auto-Repair** - Automatic detection and fixing of common issues

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/trinity999/Pr0Xy-chaIN.git
cd Pr0Xy-chaIN

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize the system (one-time setup)
init-proxy-chain-now

# 4. Start scanning with proxies
proxy-scan curl https://httpbin.org/ip
```

## 🎯 Use Cases

- **Bug Bounty Hunting** - Distribute scanning traffic across multiple IPs
- **Penetration Testing** - Avoid IP-based rate limiting and detection
- **Research Activities** - Anonymous reconnaissance and data gathering
- **Load Distribution** - Spread heavy scanning across proxy networks
- **Geo-location Testing** - Access services from different locations

## 🔧 Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init-proxy-chain-now` | Initialize and start daemon | `init-proxy-chain-now` |
| `proxy-status` | Enhanced daemon status with health checks | `proxy-status` |
| `proxy-stop` | Stop daemon | `proxy-stop` |
| `proxy-scan` | Run tools through proxies | `proxy-scan curl httpbin.org/ip` |
| `python tests/comprehensive_test_suite.py` | Run comprehensive test suite | `python tests/comprehensive_test_suite.py` |
| `proxy-status-enhanced` | Show detailed status with monitoring | `proxy-status-enhanced` |

## 🎮 Tool Integration

### Web Application Testing
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

# POST request with data
proxy-scan curl https://api.target.com -o "-X POST -d 'data=test'"

# Custom headers
proxy-scan curl https://api.target.com -o "-H 'Authorization: Bearer TOKEN'"
```

## 📊 Architecture

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
│  ├── ProxyScanner (Tool integration)                       │
│  ├── ProxyChainDaemon (Background service)                 │
│  └── ProxyDaemonManager (Process management)               │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Installation

### Prerequisites
- **Python 3.7+** (Tested on 3.8-3.13)
- **Windows 10/11** (Primary platform)
- **Internet Connection** (For proxy discovery)

### Method 1: Automatic Setup
```powershell
# Download and run setup script
powershell -ExecutionPolicy Bypass -File setup_proxy_chain.ps1
```

### Method 2: Manual Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system commands (optional)
powershell -ExecutionPolicy Bypass -File install_commands.ps1 -User
```

## 📖 Documentation

- **[Complete Documentation](docs/DOCUMENTATION.md)** - Detailed guide with all features
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Command cheat sheet and examples
- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute to the project
- **[Directory Structure](DIRECTORY_STRUCTURE.md)** - Organized project layout
- **[Performance Report](benchmarks/FINAL_PERFORMANCE_REPORT.md)** - Latest benchmarks

## ⚠️ Legal & Ethical Use

**IMPORTANT DISCLAIMERS:**
- **Authorization Required**: Only use on systems you own or have explicit written permission to test
- **Respect Rate Limits**: Don't overwhelm target services
- **Legal Compliance**: Ensure compliance with local laws and regulations
- **Responsible Disclosure**: Report findings through appropriate channels

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Feature Requests
- Enhanced geo-targeting with proxy location detection
- Performance metrics and response time tracking
- GUI interface for easier management
- Docker containerization support

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all proxy source providers
- Security community for feedback and suggestions
- Contributors who help improve the tool

## 🔗 Links

- **Repository**: [https://github.com/trinity999/Pr0Xy-chaIN](https://github.com/trinity999/Pr0Xy-chaIN)
- **Issues**: [Report bugs and request features](https://github.com/trinity999/Pr0Xy-chaIN/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/trinity999/Pr0Xy-chaIN/discussions)

---

**Pr0Xy-chaIN** - Making security testing more efficient, one proxy at a time! 🔗⚡

> **Created by**: [Abhijeet Panda](https://github.com/trinity999)
> 
> **Disclaimer**: This tool is for educational and authorized security testing purposes only. Users are responsible for compliance with applicable laws and regulations.
