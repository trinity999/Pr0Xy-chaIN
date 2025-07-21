#!/usr/bin/env python3
"""
ASCII Art Banner Module for Pr0Xy-chaIN
Displays unique banner with tool name and author info
"""

import random
import time
from datetime import datetime

def print_banner():
    """Print the unique ASCII art banner for Pr0Xy-chaIN"""
    
    # Color codes for terminal (ANSI escape sequences)
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m'
    }
    
    # Modern borderless ASCII art design
    banner = f"""
{colors['cyan']}{colors['bold']}

    ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗      ██████╗██╗  ██╗ █████╗ ██╗███╗   ██╗
    ██╔══██╗██╔══██╗██╔═████╗╚██╗██╔╝╚██╗ ██╔╝     ██╔════╝██║  ██║██╔══██╗██║████╗  ██║
    ██████╔╝██████╔╝██║██╔██║ ╚███╔╝  ╚████╔╝█████╗██║     ███████║███████║██║██╔██╗ ██║
    ██╔═══╝ ██╔══██╗████╔╝██║ ██╔██╗   ╚██╔╝ ╚════╝██║     ██╔══██║██╔══██║██║██║╚██╗██║
    ██║     ██║  ██║╚██████╔╝██╔╝ ██╗   ██║        ╚██████╗██║  ██║██║  ██║██║██║ ╚████║
    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝         ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝{colors['reset']}

{colors['yellow']}{colors['bold']}    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ▶▶▶  A D V A N C E D   P R O X Y   C H A I N   M A N A G E M E N T   S Y S T E M  ◀◀◀
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{colors['reset']}

{colors['green']}{colors['bold']}    🔗 Multi-Source Proxy Discovery     🔄 Intelligent Rotation System
    ⚡ Real-Time Validation Engine     🛠️  Seamless Tool Integration  
    📊 Background Daemon Service       🎯 One-Command Setup & Deploy{colors['reset']}

{colors['cyan']}{colors['bold']}    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {colors['magenta']}Created by: {colors['yellow']}Abhijeet Panda {colors['dim']}(@trinity999)
    {colors['magenta']}GitHub: {colors['blue']}https://github.com/trinity999/Pr0Xy-chaIN
    {colors['magenta']}Version: {colors['green']}v1.0.0 {colors['dim']}• Educational & Authorized Testing Only
    {colors['cyan']}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{colors['reset']}
"""
    
    print(banner)
    
    # Add animated dots loading effect
    print(f"{colors['yellow']}[{colors['white']}⚡{colors['yellow']}] Initializing Pr0Xy-chaIN", end="")
    for i in range(3):
        time.sleep(0.3)
        print(".", end="", flush=True)
    print(f" {colors['green']}Ready!{colors['reset']}")
    print()

def print_mini_banner():
    """Print a smaller version of the banner for quick commands"""
    colors = {
        'cyan': '\033[96m',
        'yellow': '\033[93m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m'
    }
    
    mini_banner = f"""
{colors['cyan']}{colors['bold']}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {colors['yellow']}Pr0Xy-chaIN {colors['white']}by Abhijeet Panda
    {colors['white']}Advanced Proxy Management Tool
    {colors['cyan']}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{colors['reset']}
"""
    print(mini_banner)

def print_success_banner():
    """Print success banner after initialization"""
    colors = {
        'green': '\033[92m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m'
    }
    
    success = f"""
{colors['green']}{colors['bold']}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✅ PROXY CHAIN INITIALIZED SUCCESSFULLY
    
    🚀 Ready for security testing!
    🔗 Proxy discovery in progress...
    
    Use: proxy-status to check progress
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{colors['reset']}
"""
    print(success)

def print_error_banner(message="Unknown Error"):
    """Print error banner"""
    colors = {
        'red': '\033[91m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m'
    }
    
    error = f"""
{colors['red']}{colors['bold']}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ❌ ERROR OCCURRED
    
    {message}
    
    Check logs for more details
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{colors['reset']}
"""
    print(error)

def print_status_header():
    """Print header for status display"""
    colors = {
        'blue': '\033[94m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m'
    }
    
    header = f"""
{colors['blue']}{colors['bold']}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🔗 PROXY CHAIN DAEMON STATUS 🔗
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{colors['reset']}"""
    print(header)

def print_status_footer():
    """Print footer for status display"""
    colors = {
        'blue': '\033[94m',
        'reset': '\033[0m',
        'bold': '\033[1m'
    }
    
    footer = f"""
{colors['blue']}{colors['bold']}    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{colors['reset']}
"""
    print(footer)

def get_random_proxy_art():
    """Get random proxy-themed ASCII art"""
    proxy_arts = [
        "🔗➤🌐➤🎯",
        "⚡🔄⚡🔄⚡",
        "🛡️➤🔗➤🎯",
        "📡➤🌍➤🎯",
        "🚀➤🔗➤💫"
    ]
    return random.choice(proxy_arts)

if __name__ == "__main__":
    print_banner()
    time.sleep(1)
    print_success_banner()
