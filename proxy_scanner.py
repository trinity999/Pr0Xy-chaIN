#!/usr/bin/env python3
"""
Proxy-enabled Scanner Wrapper
Integrates proxy chains with popular security scanning tools
"""

import json
import random
import subprocess
import os
import sys
import argparse
import time
import requests
from pathlib import Path

class ProxyScanner:
    def __init__(self, config_file="proxy_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.current_proxy = None
        
    def load_config(self):
        """Load proxy configuration"""
        if not os.path.exists(self.config_file):
            print(f"[ERROR] Config file {self.config_file} not found. Run proxy_chain_setup.py first.")
            sys.exit(1)
            
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def get_random_proxy(self):
        """Get a random working proxy"""
        if not self.config.get('working_proxies'):
            print("[ERROR] No working proxies available")
            return None
        return random.choice(self.config['working_proxies'])
    
    def validate_proxy(self, proxy):
        """Validate a single proxy quickly"""
        try:
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxy_dict,
                timeout=5  # Quick validation
            )
            return response.status_code == 200
        except:
            return False
    
    def rotate_proxy(self, max_retries=3):
        """Rotate to a new proxy with validation"""
        for attempt in range(max_retries):
            candidate_proxy = self.get_random_proxy()
            if not candidate_proxy:
                return None
                
            # Quick validation before using
            if self.validate_proxy(candidate_proxy):
                self.current_proxy = candidate_proxy
                print(f"[+] Using proxy: {self.current_proxy}")
                return self.current_proxy
            else:
                print(f"[!] Proxy {candidate_proxy} failed validation, trying another...")
                
        # If all attempts failed, try without validation as fallback
        self.current_proxy = self.get_random_proxy()
        if self.current_proxy:
            print(f"[~] Using proxy (unvalidated): {self.current_proxy}")
        return self.current_proxy
    
    def get_proxy_env(self):
        """Get proxy environment variables"""
        if not self.current_proxy:
            self.rotate_proxy()
            
        if not self.current_proxy:
            return {}
            
        proxy_url = f"http://{self.current_proxy}"
        return {
            'HTTP_PROXY': proxy_url,
            'HTTPS_PROXY': proxy_url,
            'http_proxy': proxy_url,
            'https_proxy': proxy_url
        }
    
    def run_nmap(self, target, options="", use_proxy=True):
        """Run nmap with proxy support"""
        if use_proxy:
            self.rotate_proxy()
            # Nmap doesn't support HTTP proxies directly, use proxychains
            cmd = f"proxychains4 -f proxychains.conf nmap {options} {target}"
        else:
            cmd = f"nmap {options} {target}"
            
        print(f"🎯 Running: {cmd}")
        return self.run_command(cmd)
    
    def run_gobuster(self, target, wordlist, options="", use_proxy=True):
        """Run gobuster with proxy support"""
        if use_proxy:
            proxy = self.rotate_proxy()
            if proxy:
                cmd = f"gobuster dir -u {target} -w {wordlist} --proxy http://{proxy} {options}"
            else:
                cmd = f"gobuster dir -u {target} -w {wordlist} {options}"
        else:
            cmd = f"gobuster dir -u {target} -w {wordlist} {options}"
            
        print(f"🎯 Running: {cmd}")
        return self.run_command(cmd)
    
    def run_ffuf(self, target, wordlist, options="", use_proxy=True):
        """Run ffuf with proxy support"""
        if use_proxy:
            proxy = self.rotate_proxy()
            if proxy:
                cmd = f"ffuf -u {target} -w {wordlist} -x http://{proxy} {options}"
            else:
                cmd = f"ffuf -u {target} -w {wordlist} {options}"
        else:
            cmd = f"ffuf -u {target} -w {wordlist} {options}"
            
        print(f"🎯 Running: {cmd}")
        return self.run_command(cmd)
    
    def run_nuclei(self, target, options="", use_proxy=True):
        """Run nuclei with proxy support"""
        if use_proxy:
            proxy = self.rotate_proxy()
            if proxy:
                cmd = f"nuclei -u {target} -proxy-url http://{proxy} {options}"
            else:
                cmd = f"nuclei -u {target} {options}"
        else:
            cmd = f"nuclei -u {target} {options}"
            
        print(f"🎯 Running: {cmd}")
        return self.run_command(cmd)
    
    def run_masscan(self, target, options="", use_proxy=True):
        """Run masscan (note: doesn't support proxies directly)"""
        if use_proxy:
            print("⚠️  Warning: masscan doesn't support proxies. Consider using nmap instead.")
            
        cmd = f"masscan {options} {target}"
        print(f"🎯 Running: {cmd}")
        return self.run_command(cmd)
    
    def run_curl(self, url, options="", use_proxy=True):
        """Run curl with proxy support"""
        if use_proxy:
            proxy = self.rotate_proxy()
            if proxy:
                # Add silent flag and ensure we get clean JSON output
                if 'httpbin.org/ip' in url and '-s' not in options:
                    cmd = f"curl --proxy http://{proxy} -s {options} {url}"
                else:
                    cmd = f"curl --proxy http://{proxy} {options} {url}"
            else:
                cmd = f"curl {options} {url}"
        else:
            cmd = f"curl {options} {url}"
            
        print(f"🎯 Running: {cmd}")
        result = self.run_command(cmd)
        
        # If this is an IP check, also output the result cleanly
        if result and result.returncode == 0 and 'httpbin.org/ip' in url:
            if result.stdout.strip():
                print(f"🔍 IP Result: {result.stdout.strip()}")
        
        return result
    
    def run_command(self, cmd):
        """Execute command with proper environment"""
        env = os.environ.copy()
        env.update(self.get_proxy_env())
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                env=env,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print("✅ Command completed successfully")
                if result.stdout:
                    print("Output:", result.stdout[:500])
            else:
                print(f"❌ Command failed with code {result.returncode}")
                if result.stderr:
                    print("Error:", result.stderr[:500])
                    
            return result
            
        except subprocess.TimeoutExpired:
            print("⏰ Command timed out")
        except Exception as e:
            print(f"❌ Error running command: {e}")
        
        return None
    
    def test_proxy_connectivity(self):
        """Test current proxy connectivity and return IP"""
        # Always rotate to get a fresh proxy
        self.rotate_proxy()
            
        if not self.current_proxy:
            print("❌ No proxy available for testing")
            return False
            
        try:
            proxy_dict = {
                'http': f'http://{self.current_proxy}',
                'https': f'http://{self.current_proxy}'
            }
            
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxy_dict,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                current_ip = data.get('origin')
                print(f"✅ Proxy {self.current_proxy} working. Current IP: {current_ip}")
                # Output JSON for easy parsing
                print(f'{{"origin": "{current_ip}"}}')
                return True
            else:
                print(f"❌ Proxy {self.current_proxy} returned status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Proxy {self.current_proxy} failed: {e}")
            # Try fallback without proxy to check connectivity
            try:
                fallback_response = requests.get('http://httpbin.org/ip', timeout=10)
                if fallback_response.status_code == 200:
                    fallback_data = fallback_response.json()
                    print(f"⚠️ Fallback direct connection. IP: {fallback_data.get('origin')}")
                    print(f'{{"origin": "{fallback_data.get("origin")}"}}')
            except:
                pass
            
        return False

def main():
    parser = argparse.ArgumentParser(description="Proxy-enabled Security Scanner")
    parser.add_argument('tool', choices=['nmap', 'gobuster', 'ffuf', 'nuclei', 'curl', 'test'], 
                       help='Scanning tool to run')
    parser.add_argument('target', help='Target URL or IP')
    parser.add_argument('--wordlist', '-w', help='Wordlist file (for gobuster/ffuf)')
    parser.add_argument('--options', '-o', default='', help='Additional tool options')
    parser.add_argument('--no-proxy', action='store_true', help='Disable proxy usage')
    parser.add_argument('--config', default='proxy_config.json', help='Proxy config file')
    
    args = parser.parse_args()
    
    scanner = ProxyScanner(args.config)
    use_proxy = not args.no_proxy
    
    if args.tool == 'test':
        scanner.test_proxy_connectivity()
        return
    
    # Tool-specific execution
    if args.tool == 'nmap':
        scanner.run_nmap(args.target, args.options, use_proxy)
    elif args.tool == 'gobuster':
        if not args.wordlist:
            print("❌ Wordlist required for gobuster")
            sys.exit(1)
        scanner.run_gobuster(args.target, args.wordlist, args.options, use_proxy)
    elif args.tool == 'ffuf':
        if not args.wordlist:
            print("❌ Wordlist required for ffuf")
            sys.exit(1)
        scanner.run_ffuf(args.target, args.wordlist, args.options, use_proxy)
    elif args.tool == 'nuclei':
        scanner.run_nuclei(args.target, args.options, use_proxy)
    elif args.tool == 'curl':
        scanner.run_curl(args.target, args.options, use_proxy)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("🔧 Proxy Scanner - Usage Examples:")
        print("=" * 40)
        print("python proxy_scanner.py test httpbin.org")
        print("python proxy_scanner.py nmap 192.168.1.1 -o '-sS -p 80,443'")
        print("python proxy_scanner.py gobuster https://example.com -w /path/to/wordlist")
        print("python proxy_scanner.py nuclei https://example.com")
        print("python proxy_scanner.py curl https://httpbin.org/ip")
        print("\nFirst run proxy_chain_setup.py to initialize proxies!")
        sys.exit(1)
        
    main()
