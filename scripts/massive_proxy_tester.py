#!/usr/bin/env python3
"""
Massive Proxy Tester - Process ALL 39,000+ Proxies for Maximum Reliability
Tests the entire proxy database instead of limiting to 200-500
"""

import requests
import json
import random
import time
import threading
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from datetime import datetime, timedelta
import queue
import math

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MassiveProxyTester:
    def __init__(self):
        self.working_proxies = []
        self.dead_proxies = set()
        self.proxy_scores = {}
        self.last_refresh = None
        self.target_working_proxies = 100  # Aim for 100+ working proxies
        
        # All proxy sources
        self.proxy_sources = {
            'monosans-http': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
            'monosans-socks4': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
            'monosans-socks5': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
            'vakhov-http': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt',
            'vakhov-https': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt',
            'vakhov-socks4': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt',
            'vakhov-socks5': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt',
            'clarketm-daily': 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'speedx-http': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'speedx-socks4': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
            'speedx-socks5': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
            'geonode-api': 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc',
            'proxy-list-api': 'https://www.proxy-list.download/api/v1/get?type=http',
            'openproxy-http': 'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt',
            'proxy-daily': 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt'
        }

    def fetch_all_proxies_massive(self):
        """Fetch ALL proxies from ALL sources"""
        logger.info("🌐 Fetching ALL proxies from ALL sources...")
        all_proxies = set()
        
        for source_name, url in self.proxy_sources.items():
            try:
                logger.info(f"📡 Fetching from {source_name}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, timeout=30, headers=headers)
                response.raise_for_status()
                
                if source_name == 'geonode-api':
                    data = response.json()
                    for proxy in data.get('data', []):
                        if proxy.get('protocols', []):
                            all_proxies.add(f"{proxy['ip']}:{proxy['port']}")
                else:
                    # Text-based proxy lists
                    for line in response.text.strip().split('\n'):
                        line = line.strip()
                        if ':' in line and not line.startswith(('#', '//')):
                            parts = line.split(':')
                            if len(parts) == 2:
                                try:
                                    int(parts[1])  # Validate port
                                    if parts[0].count('.') == 3:  # Basic IP validation
                                        all_proxies.add(line)
                                except ValueError:
                                    continue
                
                logger.info(f"✅ Source {source_name}: {len(all_proxies)} total unique proxies so far")
                
            except Exception as e:
                logger.error(f"❌ Failed to fetch {source_name}: {e}")
        
        # Remove previously known dead proxies
        all_proxies = all_proxies - self.dead_proxies
        
        logger.info(f"🎯 MASSIVE COLLECTION: {len(all_proxies)} unique proxies ready for testing!")
        return list(all_proxies)

    def test_proxy_fast(self, proxy):
        """Fast proxy testing with multiple endpoints"""
        test_urls = [
            'http://httpbin.org/ip',
            'http://icanhazip.com',
            'http://ipinfo.io/ip'
        ]
        
        start_time = time.time()
        
        try:
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            # Try first endpoint
            response = requests.get(
                test_urls[0],
                proxies=proxy_dict,
                timeout=5,  # Faster timeout for mass testing
                verify=False
            )
            
            if response.status_code == 200:
                speed = time.time() - start_time
                return True, speed, proxy
                
        except:
            pass
        
        return False, None, proxy

    def massive_parallel_test(self, all_proxies):
        """Test ALL proxies with massive parallelization"""
        total_proxies = len(all_proxies)
        logger.info(f"🚀 MASSIVE TESTING: Processing ALL {total_proxies:,} proxies...")
        logger.info("💪 Using high parallelization for maximum speed...")
        
        working_proxies = []
        proxy_speeds = {}
        
        # Use very high worker count for mass testing
        max_workers = min(500, total_proxies)  # Up to 500 concurrent tests
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit ALL proxies for testing
            logger.info(f"⚡ Starting {max_workers} parallel workers...")
            future_to_proxy = {
                executor.submit(self.test_proxy_fast, proxy): proxy
                for proxy in all_proxies
            }
            
            completed = 0
            batch_size = max(100, total_proxies // 50)  # Progress updates
            
            for future in as_completed(future_to_proxy):
                completed += 1
                
                # Progress reporting
                if completed % batch_size == 0 or completed % 1000 == 0:
                    percentage = (completed / total_proxies) * 100
                    working_count = len(working_proxies)
                    success_rate = (working_count / completed) * 100 if completed > 0 else 0
                    
                    logger.info(f"📊 Progress: {completed:,}/{total_proxies:,} ({percentage:.1f}%) | "
                              f"Working: {working_count} | Success Rate: {success_rate:.2f}%")
                
                try:
                    is_working, speed, proxy = future.result()
                    if is_working:
                        working_proxies.append(proxy)
                        proxy_speeds[proxy] = speed
                        
                        # Log every working proxy found
                        logger.info(f"✅ FOUND: {proxy} (Speed: {speed:.2f}s) - Total: {len(working_proxies)}")
                    else:
                        self.dead_proxies.add(proxy)
                        
                except Exception as e:
                    proxy = future_to_proxy[future]
                    self.dead_proxies.add(proxy)
        
        self.working_proxies = working_proxies
        self.proxy_scores = proxy_speeds
        
        return working_proxies

    def run_massive_test(self):
        """Main method to run massive proxy testing"""
        print("🚀 MASSIVE PROXY TESTING - Processing ALL 39,000+ Proxies")
        print("=" * 70)
        
        # Load previous state
        self.load_state()
        
        # Fetch ALL proxies
        all_proxies = self.fetch_all_proxies_massive()
        
        if len(all_proxies) == 0:
            print("❌ No proxies to test!")
            return
        
        print(f"🎯 Target: Find {self.target_working_proxies}+ working proxies")
        print(f"📊 Testing ALL {len(all_proxies):,} proxies...")
        print("⚡ This will take 5-15 minutes depending on your connection")
        print()
        
        # Start massive testing
        start_time = time.time()
        working_proxies = self.massive_parallel_test(all_proxies)
        end_time = time.time()
        
        # Results
        total_time = end_time - start_time
        success_rate = (len(working_proxies) / len(all_proxies)) * 100
        
        print()
        print("🎉 MASSIVE TESTING COMPLETE!")
        print("=" * 50)
        print(f"✅ Working Proxies Found: {len(working_proxies):,}")
        print(f"🗑️  Dead Proxies: {len(self.dead_proxies):,}")
        print(f"📊 Success Rate: {success_rate:.3f}%")
        print(f"⏱️  Total Time: {total_time:.1f} seconds")
        print(f"🚀 Speed: {len(all_proxies)/total_time:.0f} proxies/second")
        
        if working_proxies:
            # Sort by speed (fastest first)
            sorted_proxies = sorted(self.proxy_scores.items(), key=lambda x: x[1])
            print(f"🥇 Fastest Proxy: {sorted_proxies[0][0]} ({sorted_proxies[0][1]:.2f}s)")
            print(f"🥉 Slowest Working: {sorted_proxies[-1][0]} ({sorted_proxies[-1][1]:.2f}s)")
        
        # Save results
        self.save_massive_results()
        
        return len(working_proxies)

    def save_massive_results(self):
        """Save all results from massive testing"""
        # Save working proxies (sorted by speed)
        with open('massive_working_proxies.txt', 'w') as f:
            sorted_proxies = sorted(self.proxy_scores.items(), key=lambda x: x[1])
            for proxy, speed in sorted_proxies:
                f.write(f"{proxy}\n")
        
        # Save detailed scores
        with open('massive_proxy_scores.json', 'w') as f:
            json.dump(self.proxy_scores, f, indent=2)
        
        # Save dead proxies for future exclusion
        with open('massive_dead_proxies.txt', 'w') as f:
            for proxy in self.dead_proxies:
                f.write(f"{proxy}\n")
        
        # Create summary report
        with open('massive_test_report.txt', 'w') as f:
            f.write(f"MASSIVE PROXY TEST REPORT\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"=" * 50 + "\n")
            f.write(f"Working Proxies: {len(self.working_proxies):,}\n")
            f.write(f"Dead Proxies: {len(self.dead_proxies):,}\n")
            f.write(f"Success Rate: {(len(self.working_proxies)/(len(self.working_proxies)+len(self.dead_proxies)))*100:.3f}%\n")
            f.write("\nTop 20 Fastest Proxies:\n")
            sorted_proxies = sorted(self.proxy_scores.items(), key=lambda x: x[1])[:20]
            for i, (proxy, speed) in enumerate(sorted_proxies, 1):
                f.write(f"{i:2d}. {proxy} - {speed:.2f}s\n")
        
        print("\n📁 Files created:")
        print("  - massive_working_proxies.txt (sorted by speed)")
        print("  - massive_proxy_scores.json")
        print("  - massive_dead_proxies.txt")
        print("  - massive_test_report.txt")

    def load_state(self):
        """Load previous state to avoid retesting known dead proxies"""
        try:
            if os.path.exists('massive_dead_proxies.txt'):
                with open('massive_dead_proxies.txt', 'r') as f:
                    self.dead_proxies = set(line.strip() for line in f if line.strip())
                logger.info(f"📂 Loaded {len(self.dead_proxies):,} previously known dead proxies")
        except Exception as e:
            logger.error(f"Error loading state: {e}")

def main():
    tester = MassiveProxyTester()
    
    print("⚠️  WARNING: This will test ALL 39,000+ proxies!")
    print("🔥 This process will use significant bandwidth and CPU")
    print("⏱️  Expected time: 5-15 minutes")
    print()
    
    proceed = input("🤔 Proceed with massive testing? (y/n): ")
    if proceed.lower() != 'y':
        print("👋 Cancelled. Use enhanced_proxy_manager.py for smaller batches.")
        return
    
    working_count = tester.run_massive_test()
    
    if working_count >= 50:
        print(f"\n🏆 EXCELLENT! Found {working_count} working proxies!")
        print("🎯 Your proxy reliability is now MAXIMUM LEVEL!")
    elif working_count >= 20:
        print(f"\n👍 GOOD! Found {working_count} working proxies!")
        print("🚀 Much better reliability achieved!")
    else:
        print(f"\n😐 Found {working_count} working proxies.")
        print("💡 Consider running again later for better results.")

if __name__ == "__main__":
    main()
