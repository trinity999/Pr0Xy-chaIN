#!/usr/bin/env python3
"""
Update proxy configuration by filtering out non-working proxies
Based on comprehensive test results
"""

import json
import requests
import concurrent.futures
import time
from pathlib import Path

def test_proxy_quick(proxy):
    """Quick test for proxy functionality"""
    try:
        proxy_dict = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        response = requests.get(
            'http://httpbin.org/ip',
            proxies=proxy_dict,
            timeout=8
        )
        if response.status_code == 200:
            data = response.json()
            return proxy, True, data.get('origin')
    except Exception as e:
        pass
    return proxy, False, None

def update_proxy_config():
    """Update the proxy configuration with only working proxies"""
    config_file = "proxy_config.json"
    
    # Load current configuration
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    current_proxies = config.get('working_proxies', [])
    print(f"🔍 Testing {len(current_proxies)} proxies...")
    
    working_proxies = []
    proxy_ips = {}
    
    # Test proxies concurrently for speed
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(test_proxy_quick, proxy) for proxy in current_proxies]
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            proxy, is_working, ip = future.result()
            if is_working:
                working_proxies.append(proxy)
                proxy_ips[proxy] = ip
                print(f"✅ {proxy} -> {ip}")
            else:
                print(f"❌ {proxy} -> Failed")
    
    # Update configuration
    config['working_proxies'] = working_proxies
    
    # Save updated configuration
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n📊 Summary:")
    print(f"   Original proxies: {len(current_proxies)}")
    print(f"   Working proxies: {len(working_proxies)}")
    print(f"   Removed: {len(current_proxies) - len(working_proxies)}")
    print(f"   Success rate: {len(working_proxies)/len(current_proxies)*100:.1f}%")
    
    return working_proxies, proxy_ips

if __name__ == "__main__":
    working_proxies, proxy_ips = update_proxy_config()
    
    print("\n🎯 Working Proxy IPs:")
    for proxy, ip in proxy_ips.items():
        print(f"   {proxy} -> {ip}")
