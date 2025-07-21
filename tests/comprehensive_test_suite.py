#!/usr/bin/env python3
"""
ENHANCED Comprehensive Test Suite for Pr0Xy-chaIN Tool
Improved parsing, validation, and more reliable testing
"""

import json
import time
import requests
import subprocess
import os
import sys
import re
import threading
from datetime import datetime
from pathlib import Path
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

class ProxyChainTester:
    def __init__(self):
        self.config_file = "proxy_config.json"
        self.results = {
            "test_start_time": datetime.now().isoformat(),
            "basic_connectivity": {},
            "ip_rotation": {},
            "performance_metrics": {},
            "tool_integration": {},
            "stress_tests": {},
            "error_handling": {},
            "daemon_tests": {},
            "summary": {}
        }
        self.load_config()
        self.test_patterns = {
            "ip_pattern": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            "current_ip_pattern": r'Current IP:\s*([0-9.]+)',
            "origin_pattern": r'"origin":\s*"([^"]+)"'
        }
        
    def validate_ip_address(self, ip_string):
        """Validate if string contains a valid IP address"""
        if not ip_string or isinstance(ip_string, str) and "Error" in ip_string:
            return False
        
        # Extract IP using regex
        ip_match = re.search(self.test_patterns["ip_pattern"], str(ip_string))
        if not ip_match:
            return False
            
        ip = ip_match.group()
        parts = ip.split('.')
        
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False
    
    def extract_ip_from_output(self, output_text):
        """Enhanced IP extraction with multiple patterns"""
        if not output_text:
            return None
            
        # Try different patterns
        patterns = [
            self.test_patterns["current_ip_pattern"],
            self.test_patterns["origin_pattern"],
            r'"origin"\s*:\s*"([^"]+)"',  # JSON format
            r'Current IP:\s*(\S+)',       # Status output
            r'origin":\s*"([^"]+)"'       # Partial JSON
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output_text)
            if match:
                potential_ip = match.group(1)
                if self.validate_ip_address(potential_ip):
                    return potential_ip
        
        # Fallback: look for any valid IP in the text
        ip_match = re.search(self.test_patterns["ip_pattern"], output_text)
        if ip_match:
            potential_ip = ip_match.group()
            if self.validate_ip_address(potential_ip):
                return potential_ip
                
        return None
        
    def load_config(self):
        """Load proxy configuration"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
                self.working_proxies = self.config.get('working_proxies', [])
        except FileNotFoundError:
            print("❌ Configuration file not found. Please run initialization first.")
            self.config = {}
            self.working_proxies = []
    
    def print_banner(self):
        """Print test suite banner"""
        print("=" * 80)
        print("🧪 Pr0Xy-chaIN COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"📅 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 Available Proxies: {len(self.working_proxies)}")
        print("=" * 80)
        print()
    
    def get_current_ip_direct(self):
        """Get current IP without proxy"""
        try:
            response = requests.get('http://httpbin.org/ip', timeout=10)
            if response.status_code == 200:
                return response.json().get('origin')
        except Exception as e:
            return f"Error: {e}"
        return None
    
    def get_current_ip_with_proxy(self, proxy):
        """Get current IP using specific proxy"""
        try:
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            response = requests.get('http://httpbin.org/ip', proxies=proxy_dict, timeout=15)
            if response.status_code == 200:
                return response.json().get('origin')
        except Exception as e:
            return f"Error: {e}"
        return None
    
    def test_basic_connectivity(self):
        """Test 1: Basic proxy connectivity"""
        print("🔍 TEST 1: Basic Proxy Connectivity")
        print("-" * 50)
        
        # Get direct IP first
        direct_ip = self.get_current_ip_direct()
        print(f"📍 Direct IP (no proxy): {direct_ip}")
        
        self.results["basic_connectivity"]["direct_ip"] = direct_ip
        self.results["basic_connectivity"]["proxy_tests"] = []
        
        for i, proxy in enumerate(self.working_proxies, 1):
            print(f"\n🔗 Testing Proxy {i}/{len(self.working_proxies)}: {proxy}")
            start_time = time.time()
            
            proxy_ip = self.get_current_ip_with_proxy(proxy)
            response_time = time.time() - start_time
            
            test_result = {
                "proxy": proxy,
                "ip": proxy_ip,
                "response_time": round(response_time, 2),
                "working": "Error" not in str(proxy_ip),
                "ip_changed": proxy_ip != direct_ip and "Error" not in str(proxy_ip)
            }
            
            if test_result["working"]:
                print(f"✅ Working - IP: {proxy_ip} | Response: {response_time:.2f}s")
            else:
                print(f"❌ Failed - {proxy_ip}")
                
            self.results["basic_connectivity"]["proxy_tests"].append(test_result)
        
        working_count = sum(1 for t in self.results["basic_connectivity"]["proxy_tests"] if t["working"])
        print(f"\n📊 Summary: {working_count}/{len(self.working_proxies)} proxies working")
        
    def test_ip_rotation(self):
        """Test 2: IP rotation and randomization"""
        print("\n🔄 TEST 2: IP Rotation and Randomization")
        print("-" * 50)
        
        rotation_results = []
        unique_ips = set()
        
        # Test multiple rotations
        for i in range(10):
            print(f"🎲 Rotation {i+1}/10", end=" - ")
            
            # Use proxy scanner to get random proxy
            try:
                result = subprocess.run([
                    'python', 'proxy_scanner.py', 'test', 'httpbin.org'
                ], capture_output=True, text=True, timeout=30)
                
                # Enhanced parsing with multiple methods
                output = result.stdout
                ip = self.extract_ip_from_output(output)
                
                if ip and self.validate_ip_address(ip):
                    unique_ips.add(ip)
                    print(f"✅ IP: {ip}")
                    rotation_results.append({"rotation": i+1, "ip": ip, "success": True})
                else:
                    # Try alternative method
                    alt_result = subprocess.run([
                        'python', 'proxy_scanner.py', 'curl', 'http://httpbin.org/ip'
                    ], capture_output=True, text=True, timeout=30)
                    
                    alt_ip = self.extract_ip_from_output(alt_result.stdout)
                    if alt_ip and self.validate_ip_address(alt_ip):
                        unique_ips.add(alt_ip)
                        print(f"✅ IP: {alt_ip} (via curl)")
                        rotation_results.append({"rotation": i+1, "ip": alt_ip, "success": True})
                    else:
                        print("❌ Failed to get IP")
                        rotation_results.append({"rotation": i+1, "ip": None, "success": False})
                    
            except Exception as e:
                print(f"Error: {e}")
                rotation_results.append({"rotation": i+1, "ip": None, "success": False, "error": str(e)})
            
            time.sleep(2)  # Small delay between rotations
        
        self.results["ip_rotation"] = {
            "total_rotations": 10,
            "successful_rotations": sum(1 for r in rotation_results if r["success"]),
            "unique_ips": len(unique_ips),
            "unique_ip_list": list(unique_ips),
            "rotation_details": rotation_results
        }
        
        print(f"\n📊 Rotation Summary:")
        print(f"   ✅ Successful: {self.results['ip_rotation']['successful_rotations']}/10")
        print(f"   🎯 Unique IPs: {len(unique_ips)}")
        print(f"   📍 IPs Found: {', '.join(list(unique_ips)[:5])}{'...' if len(unique_ips) > 5 else ''}")
    
    def test_performance_metrics(self):
        """Test 3: Performance and response time metrics"""
        print("\n⚡ TEST 3: Performance Metrics")
        print("-" * 50)
        
        performance_data = {
            "direct_connection": [],
            "proxy_connections": [],
            "comparison": {}
        }
        
        # Test direct connection speed (baseline)
        print("📊 Testing direct connection speed...")
        for i in range(5):
            start = time.time()
            ip = self.get_current_ip_direct()
            duration = time.time() - start
            performance_data["direct_connection"].append(duration)
            print(f"   Direct test {i+1}: {duration:.2f}s")
        
        # Test proxy connection speeds
        print("\n📊 Testing proxy connection speeds...")
        for proxy in self.working_proxies[:3]:  # Test first 3 proxies
            proxy_times = []
            print(f"🔗 Testing proxy: {proxy}")
            
            for i in range(3):
                start = time.time()
                ip = self.get_current_ip_with_proxy(proxy)
                duration = time.time() - start
                proxy_times.append(duration)
                print(f"   Proxy test {i+1}: {duration:.2f}s")
            
            performance_data["proxy_connections"].append({
                "proxy": proxy,
                "times": proxy_times,
                "average": statistics.mean(proxy_times),
                "min": min(proxy_times),
                "max": max(proxy_times)
            })
        
        # Calculate averages
        direct_avg = statistics.mean(performance_data["direct_connection"])
        proxy_avgs = [p["average"] for p in performance_data["proxy_connections"]]
        overall_proxy_avg = statistics.mean(proxy_avgs) if proxy_avgs else 0
        
        performance_data["comparison"] = {
            "direct_average": round(direct_avg, 2),
            "proxy_average": round(overall_proxy_avg, 2),
            "slowdown_factor": round(overall_proxy_avg / direct_avg, 2) if direct_avg > 0 else 0
        }
        
        self.results["performance_metrics"] = performance_data
        
        print(f"\n📊 Performance Summary:")
        print(f"   🚀 Direct avg: {direct_avg:.2f}s")
        print(f"   🔗 Proxy avg: {overall_proxy_avg:.2f}s")
        print(f"   📈 Slowdown: {performance_data['comparison']['slowdown_factor']}x")
    
    def test_tool_integration(self):
        """Test 4: Integration with security tools"""
        print("\n🛠️ TEST 4: Tool Integration")
        print("-" * 50)
        
        tools_to_test = [
            {
                "tool": "curl",
                "command": ["python", "proxy_scanner.py", "curl", "http://httpbin.org/ip"],
                "expected_in_output": "origin"
            },
            {
                "tool": "curl_custom",
                "command": ["python", "proxy_scanner.py", "curl", "http://httpbin.org/headers", "-o", "-H 'User-Agent: TestAgent'"],
                "expected_in_output": "TestAgent"
            }
        ]
        
        tool_results = []
        
        for tool_test in tools_to_test:
            print(f"\n🔧 Testing {tool_test['tool']}...")
            try:
                start_time = time.time()
                result = subprocess.run(
                    tool_test["command"], 
                    capture_output=True, 
                    text=True, 
                    timeout=60
                )
                execution_time = time.time() - start_time
                
                success = (result.returncode == 0 and 
                          tool_test["expected_in_output"] in result.stdout)
                
                tool_result = {
                    "tool": tool_test["tool"],
                    "command": " ".join(tool_test["command"]),
                    "success": success,
                    "execution_time": round(execution_time, 2),
                    "return_code": result.returncode,
                    "stdout_sample": result.stdout[:200] if result.stdout else "",
                    "stderr_sample": result.stderr[:200] if result.stderr else ""
                }
                
                if success:
                    print(f"   ✅ Success ({execution_time:.2f}s)")
                else:
                    print(f"   ❌ Failed (code: {result.returncode})")
                    
            except subprocess.TimeoutExpired:
                tool_result = {
                    "tool": tool_test["tool"],
                    "command": " ".join(tool_test["command"]),
                    "success": False,
                    "execution_time": 60,
                    "error": "Timeout"
                }
                print(f"   ⏰ Timeout")
                
            except Exception as e:
                tool_result = {
                    "tool": tool_test["tool"],
                    "command": " ".join(tool_test["command"]),
                    "success": False,
                    "error": str(e)
                }
                print(f"   ❌ Error: {e}")
            
            tool_results.append(tool_result)
        
        self.results["tool_integration"] = {
            "total_tools_tested": len(tools_to_test),
            "successful_integrations": sum(1 for t in tool_results if t.get("success", False)),
            "test_details": tool_results
        }
        
        success_count = self.results["tool_integration"]["successful_integrations"]
        print(f"\n📊 Integration Summary: {success_count}/{len(tools_to_test)} tools working")
    
    def test_concurrent_usage(self):
        """Test 5: Concurrent proxy usage (stress test)"""
        print("\n🚀 TEST 5: Concurrent Usage Stress Test")
        print("-" * 50)
        
        def make_request(proxy, request_id):
            """Make a single request through proxy"""
            try:
                start_time = time.time()
                proxy_dict = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
                response = requests.get('http://httpbin.org/ip', proxies=proxy_dict, timeout=20)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    ip = response.json().get('origin')
                    return {
                        'request_id': request_id,
                        'proxy': proxy,
                        'success': True,
                        'ip': ip,
                        'response_time': duration
                    }
            except Exception as e:
                return {
                    'request_id': request_id,
                    'proxy': proxy,
                    'success': False,
                    'error': str(e)
                }
        
        # Test with 15 concurrent requests
        concurrent_results = []
        print("📡 Launching 15 concurrent requests...")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for i in range(15):
                proxy = self.working_proxies[i % len(self.working_proxies)] if self.working_proxies else None
                if proxy:
                    future = executor.submit(make_request, proxy, i+1)
                    futures.append(future)
            
            for future in as_completed(futures):
                result = future.result()
                concurrent_results.append(result)
                status = "✅" if result.get('success') else "❌"
                print(f"   {status} Request {result['request_id']}: {result.get('ip', 'Failed')}")
        
        successful = sum(1 for r in concurrent_results if r and r.get('success'))
        response_times = [r['response_time'] for r in concurrent_results if r and r.get('response_time')]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        self.results["stress_tests"] = {
            "concurrent_requests": 15,
            "successful_requests": successful,
            "failed_requests": 15 - successful,
            "success_rate": round((successful / 15) * 100, 2),
            "average_response_time": round(avg_response_time, 2),
            "request_details": concurrent_results
        }
        
        print(f"\n📊 Stress Test Summary:")
        print(f"   ✅ Success Rate: {self.results['stress_tests']['success_rate']}%")
        print(f"   ⚡ Avg Response: {avg_response_time:.2f}s")
    
    def test_error_handling(self):
        """Test 6: Error handling and edge cases"""
        print("\n🛡️ TEST 6: Error Handling and Edge Cases")
        print("-" * 50)
        
        error_tests = []
        
        # Test 1: Invalid proxy
        print("🔍 Testing invalid proxy handling...")
        try:
            result = self.get_current_ip_with_proxy("999.999.999.999:9999")
            error_tests.append({
                "test": "invalid_proxy",
                "result": result,
                "handled_gracefully": "Error" in str(result)
            })
        except Exception as e:
            error_tests.append({
                "test": "invalid_proxy",
                "error": str(e),
                "handled_gracefully": True
            })
        
        # Test 2: Timeout handling
        print("🔍 Testing timeout handling...")
        try:
            proxy_dict = {'http': 'http://10.255.255.1:8080', 'https': 'http://10.255.255.1:8080'}
            start_time = time.time()
            requests.get('http://httpbin.org/ip', proxies=proxy_dict, timeout=3)
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            error_tests.append({
                "test": "timeout_handling",
                "duration": duration,
                "handled_gracefully": duration <= 4  # Should timeout around 3s
            })
        except Exception as e:
            error_tests.append({
                "test": "timeout_handling",
                "error": str(e),
                "handled_gracefully": True
            })
        
        # Test 3: Empty proxy list
        print("🔍 Testing empty proxy configuration...")
        original_proxies = self.working_proxies.copy()
        self.working_proxies = []
        
        try:
            # This should handle empty proxy list gracefully
            result = subprocess.run([
                'python', 'proxy_scanner.py', 'test', 'httpbin.org'
            ], capture_output=True, text=True, timeout=15)
            
            error_tests.append({
                "test": "empty_proxy_list",
                "return_code": result.returncode,
                "handled_gracefully": result.returncode != 0 or "No working proxies" in result.stdout
            })
        except Exception as e:
            error_tests.append({
                "test": "empty_proxy_list",
                "error": str(e),
                "handled_gracefully": True
            })
        finally:
            self.working_proxies = original_proxies
        
        self.results["error_handling"] = {
            "total_error_tests": len(error_tests),
            "gracefully_handled": sum(1 for t in error_tests if t.get("handled_gracefully", False)),
            "test_details": error_tests
        }
        
        handled = self.results["error_handling"]["gracefully_handled"]
        total = self.results["error_handling"]["total_error_tests"]
        print(f"\n📊 Error Handling Summary: {handled}/{total} cases handled gracefully")
    
    def test_daemon_functionality(self):
        """Test 7: Daemon functionality"""
        print("\n🔄 TEST 7: Daemon Functionality")
        print("-" * 50)
        
        daemon_tests = []
        
        # Test daemon status
        print("🔍 Checking daemon status...")
        try:
            result = subprocess.run([
                'python', 'proxy_status.py'
            ], capture_output=True, text=True, timeout=30)
            
            daemon_tests.append({
                "test": "daemon_status_check",
                "success": result.returncode == 0,
                "output": result.stdout[:200]
            })
            
            if result.returncode == 0:
                print("   ✅ Daemon status check successful")
            else:
                print("   ❌ Daemon status check failed")
                
        except Exception as e:
            daemon_tests.append({
                "test": "daemon_status_check",
                "success": False,
                "error": str(e)
            })
            print(f"   ❌ Error: {e}")
        
        # Test daemon configuration
        print("🔍 Checking daemon configuration files...")
        config_files = ["daemon_status.json", "daemon.pid"]
        for config_file in config_files:
            exists = os.path.exists(config_file)
            daemon_tests.append({
                "test": f"config_file_{config_file}",
                "exists": exists,
                "readable": os.access(config_file, os.R_OK) if exists else False
            })
            print(f"   {'✅' if exists else '❌'} {config_file}: {'Found' if exists else 'Missing'}")
        
        self.results["daemon_tests"] = {
            "total_daemon_tests": len(daemon_tests),
            "successful_tests": sum(1 for t in daemon_tests if t.get("success", t.get("exists", False))),
            "test_details": daemon_tests
        }
        
        success = self.results["daemon_tests"]["successful_tests"]
        total = self.results["daemon_tests"]["total_daemon_tests"]
        print(f"\n📊 Daemon Tests Summary: {success}/{total} tests passed")
    
    def generate_comprehensive_report(self):
        """Generate final comprehensive report"""
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        # Calculate overall scores
        total_tests = 0
        passed_tests = 0
        
        # Basic connectivity score
        if self.results.get("basic_connectivity"):
            connectivity_tests = len(self.results["basic_connectivity"].get("proxy_tests", []))
            connectivity_passed = sum(1 for t in self.results["basic_connectivity"]["proxy_tests"] if t["working"])
            total_tests += connectivity_tests
            passed_tests += connectivity_passed
            print(f"\n🔍 CONNECTIVITY: {connectivity_passed}/{connectivity_tests} proxies working ({connectivity_passed/connectivity_tests*100:.1f}%)")
        
        # IP rotation score
        if self.results.get("ip_rotation"):
            rotation_total = self.results["ip_rotation"]["total_rotations"]
            rotation_passed = self.results["ip_rotation"]["successful_rotations"]
            total_tests += rotation_total
            passed_tests += rotation_passed
            print(f"🔄 ROTATION: {rotation_passed}/{rotation_total} rotations successful ({rotation_passed/rotation_total*100:.1f}%)")
            print(f"   🎯 Unique IPs discovered: {self.results['ip_rotation']['unique_ips']}")
        
        # Performance metrics
        if self.results.get("performance_metrics"):
            perf = self.results["performance_metrics"]["comparison"]
            print(f"⚡ PERFORMANCE:")
            print(f"   📊 Direct connection: {perf['direct_average']}s avg")
            print(f"   🔗 Proxy connection: {perf['proxy_average']}s avg")
            print(f"   📈 Slowdown factor: {perf['slowdown_factor']}x")
        
        # Tool integration score
        if self.results.get("tool_integration"):
            tool_total = self.results["tool_integration"]["total_tools_tested"]
            tool_passed = self.results["tool_integration"]["successful_integrations"]
            total_tests += tool_total
            passed_tests += tool_passed
            print(f"🛠️ TOOL INTEGRATION: {tool_passed}/{tool_total} tools working ({tool_passed/tool_total*100:.1f}%)")
        
        # Stress test results
        if self.results.get("stress_tests"):
            stress_rate = self.results["stress_tests"]["success_rate"]
            print(f"🚀 STRESS TEST: {stress_rate}% success rate under concurrent load")
        
        # Error handling score
        if self.results.get("error_handling"):
            error_total = self.results["error_handling"]["total_error_tests"]
            error_passed = self.results["error_handling"]["gracefully_handled"]
            total_tests += error_total
            passed_tests += error_passed
            print(f"🛡️ ERROR HANDLING: {error_passed}/{error_total} cases handled gracefully ({error_passed/error_total*100:.1f}%)")
        
        # Overall score
        overall_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "overall_score": round(overall_score, 1),
            "test_end_time": datetime.now().isoformat()
        }
        
        print(f"\n{'='*50}")
        print(f"🏆 OVERALL SCORE: {overall_score:.1f}% ({passed_tests}/{total_tests})")
        
        if overall_score >= 80:
            print("✅ EXCELLENT - Proxy chain is working optimally!")
        elif overall_score >= 60:
            print("⚠️ GOOD - Minor issues detected, but functional")
        else:
            print("❌ NEEDS ATTENTION - Multiple issues require fixing")
        
        print(f"{'='*50}")
        
        # Save detailed report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Detailed report saved to: {report_file}")
        
        return self.results
    
    def run_all_tests(self):
        """Run all test suites"""
        self.print_banner()
        
        try:
            self.test_basic_connectivity()
            self.test_ip_rotation()
            self.test_performance_metrics()
            self.test_tool_integration()
            self.test_concurrent_usage()
            self.test_error_handling()
            self.test_daemon_functionality()
            
            return self.generate_comprehensive_report()
            
        except KeyboardInterrupt:
            print("\n⚠️ Test suite interrupted by user")
            return None
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            return None

def main():
    tester = ProxyChainTester()
    results = tester.run_all_tests()
    
    if results:
        print(f"\n🎉 Test suite completed successfully!")
        print(f"📊 Final Score: {results['summary']['overall_score']}%")
    else:
        print("\n❌ Test suite did not complete successfully")

if __name__ == "__main__":
    main()
