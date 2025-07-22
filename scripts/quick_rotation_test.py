#!/usr/bin/env python3
"""
Quick test for IP rotation functionality
"""

import subprocess
import re
import time

def extract_ip_from_output(output_text):
    """Extract IP from various output formats"""
    if not output_text:
        return None
        
    patterns = [
        r'\{"origin":\s*"([^"]+)"\}',  # Clean JSON format
        r'Current IP:\s*([0-9.]+)',
        r'"origin":\s*"([^"]+)"',
        r'IP Result:\s*\{"origin":\s*"([^"]+)"\}',
        r'IP:\s*([0-9.]+)',
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b'  # Any IP pattern as fallback
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, output_text)
        if match:
            if i == len(patterns) - 1:  # Last pattern (fallback) doesn't have groups
                potential_ip = match.group(0).strip()
            else:
                potential_ip = match.group(1).strip()
            # Validate IP format
            parts = potential_ip.split('.')
            if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
                # Skip common local/private ranges
                if not potential_ip.startswith(('127.', '169.254.', '0.', '255.')):
                    return potential_ip
                
    return None

def test_rotation_quick():
    """Test IP rotation 5 times"""
    print("🔄 Testing IP Rotation (5 attempts)")
    print("-" * 40)
    
    unique_ips = set()
    successful_rotations = 0
    
    for i in range(5):
        print(f"Rotation {i+1}/5: ", end="")
        
        try:
            # Test using the test command
            result = subprocess.run([
                'python', 'proxy_scanner.py', 'test', 'httpbin.org'
            ], capture_output=True, text=True, timeout=30)
            
            ip = extract_ip_from_output(result.stdout)
            
            if ip:
                unique_ips.add(ip)
                successful_rotations += 1
                print(f"✅ {ip}")
            else:
                # Debug: show what we got
                print(f"DEBUG: stdout='{result.stdout}', stderr='{result.stderr}', returncode={result.returncode}")
                # Try curl as backup
                curl_result = subprocess.run([
                    'python', 'proxy_scanner.py', 'curl', 'http://httpbin.org/ip'
                ], capture_output=True, text=True, timeout=30)
                
                curl_ip = extract_ip_from_output(curl_result.stdout)
                if curl_ip:
                    unique_ips.add(curl_ip)
                    successful_rotations += 1
                    print(f"✅ {curl_ip} (via curl)")
                else:
                    print(f"DEBUG curl: stdout='{curl_result.stdout}', stderr='{curl_result.stderr}'")
                    print("❌ Failed to extract IP")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        
        if i < 4:  # Don't wait after the last iteration
            time.sleep(1)
    
    print(f"\n📊 Rotation Results:")
    print(f"   ✅ Successful: {successful_rotations}/5")
    print(f"   🎯 Unique IPs: {len(unique_ips)}")
    print(f"   📍 IPs Found: {', '.join(unique_ips)}")
    
    return successful_rotations, unique_ips

if __name__ == "__main__":
    successful, ips = test_rotation_quick()
    if successful >= 3:
        print("\n🎉 IP Rotation is working well!")
    elif successful >= 1:
        print("\n⚠️ IP Rotation is partially working")
    else:
        print("\n❌ IP Rotation needs attention")
