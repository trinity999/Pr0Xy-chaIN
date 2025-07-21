#!/usr/bin/env python3
"""
IMPROVED Automated Test Suite for Pr0Xy-chaIN Tool
Enhanced with better parsing, validation, and more reliable testing
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

class ImprovedProxyChainTester:
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
        
    def load_config(self):
        """Load proxy configuration with validation"""
        try:
            if not os.path.exists(self.config_file):
                print(f"⚠️ Configuration file {self.config_file} not found")
                self.config = {}
                self.working_proxies = []
                return
                
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
                self.working_proxies = self.config.get('working_proxies', [])
                
            print(f"✅ Loaded configuration with {len(self.working_proxies)} proxies")
            
        except json.JSONDecodeError as e:
            print(f"❌ Configuration file corrupted: {e}")
            self.config = {}
            self.working_proxies = []
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            self.config = {}
            self.working_proxies = []
    
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
    
    def run_command_with_validation(self, command_list, timeout=30):
        """Run command with improved output parsing and validation"""
        try:
            print(f"🔧 Running: {' '.join(command_list)}")
            
            result = subprocess.run(
                command_list,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Enhanced result processing
            stdout_clean = result.stdout.strip() if result.stdout else ""
            stderr_clean = result.stderr.strip() if result.stderr else ""
            
            success = result.returncode == 0
            
            return {
                "success": success,
                "returncode": result.returncode,
                "stdout": stdout_clean,
                "stderr": stderr_clean,
                "command": " ".join(command_list)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "timeout",
                "command": " ".join(command_list),
                "timeout": timeout
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": " ".join(command_list)
            }
    
    def test_proxy_scanner_directly(self, tool, target, options=""):
        """Test proxy scanner with improved parsing"""
        command = ["python", "proxy_scanner.py", tool, target]
        if options:
            command.extend(["-o", options])
            
        result = self.run_command_with_validation(command)
        
        if result.get("success"):
            # Look for IP in output
            ip = self.extract_ip_from_output(result["stdout"])
            if ip:
                result["extracted_ip"] = ip
                result["ip_found"] = True
            else:
                result["ip_found"] = False
                
        return result
    
    def test_enhanced_ip_rotation(self):
        """Enhanced IP rotation testing with better parsing"""
        print("\n🔄 TEST 2: Enhanced IP Rotation and Randomization")
        print("-" * 50)
        
        rotation_results = []
        unique_ips = set()
        successful_rotations = 0
        
        for i in range(10):
            print(f"🎲 Rotation {i+1}/10 ", end="")
            
            # Test both the 'test' command and direct curl
            test_methods = [
                {"method": "test", "command": ["python", "proxy_scanner.py", "test", "httpbin.org"]},
                {"method": "curl", "command": ["python", "proxy_scanner.py", "curl", "http://httpbin.org/ip"]}
            ]
            
            rotation_successful = False
            found_ip = None
            method_used = None
            
            for test_method in test_methods:
                try:
                    result = self.run_command_with_validation(test_method["command"], timeout=30)
                    
                    if result.get("success"):
                        ip = self.extract_ip_from_output(result["stdout"])
                        if ip and self.validate_ip_address(ip):
                            unique_ips.add(ip)
                            found_ip = ip
                            method_used = test_method["method"]
                            rotation_successful = True
                            break
                            
                except Exception as e:
                    print(f"Method {test_method['method']} failed: {e}")
                    continue
            
            if rotation_successful:
                print(f"- ✅ IP: {found_ip} (via {method_used})")
                successful_rotations += 1
                rotation_results.append({
                    "rotation": i+1, 
                    "ip": found_ip, 
                    "success": True,
                    "method": method_used
                })
            else:
                print("- ❌ Failed to get IP")
                rotation_results.append({
                    "rotation": i+1, 
                    "ip": None, 
                    "success": False
                })
            
            time.sleep(1)  # Brief delay between rotations
        
        self.results["ip_rotation"] = {
            "total_rotations": 10,
            "successful_rotations": successful_rotations,
            "unique_ips": len(unique_ips),
            "unique_ip_list": list(unique_ips),
            "rotation_details": rotation_results
        }
        
        print(f"\n📊 Enhanced Rotation Summary:")
        print(f"   ✅ Successful: {successful_rotations}/10")
        print(f"   🎯 Unique IPs: {len(unique_ips)}")
        print(f"   📍 IPs Found: {', '.join(list(unique_ips)[:5])}{'...' if len(unique_ips) > 5 else ''}")
        
        return successful_rotations > 0
    
    def test_enhanced_tool_integration(self):
        """Enhanced tool integration testing with better validation"""
        print("\n🛠️ TEST 4: Enhanced Tool Integration")
        print("-" * 50)
        
        tools_to_test = [
            {
                "tool": "curl",
                "target": "http://httpbin.org/ip",
                "expected_patterns": ["origin", r'\d+\.\d+\.\d+\.\d+'],
                "description": "Basic IP check"
            },
            {
                "tool": "curl", 
                "target": "http://httpbin.org/headers",
                "options": "-H 'User-Agent: ProxyChainTest'",
                "expected_patterns": ["ProxyChainTest", "User-Agent"],
                "description": "Custom headers test"
            },
            {
                "tool": "test",
                "target": "httpbin.org", 
                "expected_patterns": ["Current IP", "working", r'\d+\.\d+\.\d+\.\d+'],
                "description": "Proxy connectivity test"
            }
        ]
        
        tool_results = []
        successful_integrations = 0
        
        for i, tool_test in enumerate(tools_to_test, 1):
            print(f"\n🔧 Test {i}/{len(tools_to_test)}: {tool_test['description']}")
            
            command = ["python", "proxy_scanner.py", tool_test["tool"], tool_test["target"]]
            if tool_test.get("options"):
                command.extend(["-o", tool_test["options"]])
            
            start_time = time.time()
            result = self.run_command_with_validation(command, timeout=60)
            execution_time = time.time() - start_time
            
            # Enhanced success criteria
            success = result.get("success", False)
            
            # Check for expected patterns
            patterns_found = 0
            if success and result.get("stdout"):
                for pattern in tool_test["expected_patterns"]:
                    if re.search(pattern, result["stdout"], re.IGNORECASE):
                        patterns_found += 1
            
            # Success if command ran and at least one pattern found
            enhanced_success = success and patterns_found > 0
            
            if enhanced_success:
                successful_integrations += 1
                print(f"   ✅ Success - {patterns_found}/{len(tool_test['expected_patterns'])} patterns found")
                
                # Try to extract IP for additional validation
                extracted_ip = self.extract_ip_from_output(result["stdout"])
                if extracted_ip:
                    print(f"   🎯 Extracted IP: {extracted_ip}")
            else:
                print(f"   ❌ Failed - Return code: {result.get('returncode', 'unknown')}")
                if result.get("stderr"):
                    print(f"   📝 Error: {result['stderr'][:100]}...")
            
            tool_result = {
                "tool": tool_test["tool"],
                "target": tool_test["target"],
                "description": tool_test["description"],
                "success": enhanced_success,
                "execution_time": round(execution_time, 2),
                "return_code": result.get("returncode"),
                "patterns_found": patterns_found,
                "patterns_total": len(tool_test["expected_patterns"]),
                "stdout_sample": result.get("stdout", "")[:200] if result.get("stdout") else "",
                "command": " ".join(command)
            }
            
            if extracted_ip:
                tool_result["extracted_ip"] = extracted_ip
                
            tool_results.append(tool_result)
        
        self.results["tool_integration"] = {
            "total_tools_tested": len(tools_to_test),
            "successful_integrations": successful_integrations,
            "success_rate": round((successful_integrations / len(tools_to_test)) * 100, 2),
            "test_details": tool_results
        }
        
        print(f"\n📊 Enhanced Integration Summary: {successful_integrations}/{len(tools_to_test)} tools working ({self.results['tool_integration']['success_rate']}%)")
        
        return successful_integrations > 0
    
    def test_daemon_functionality_enhanced(self):
        """Enhanced daemon functionality testing"""
        print("\n🔄 TEST 7: Enhanced Daemon Functionality")
        print("-" * 50)
        
        daemon_tests = []
        
        # Test 1: Enhanced status check
        print("🔍 Checking enhanced daemon status...")
        try:
            # Try the improved status checker first
            result = self.run_command_with_validation([
                "python", "improved_proxy_status.py", "status"
            ], timeout=30)
            
            status_success = result.get("success", False)
            if status_success:
                print("   ✅ Enhanced status check successful")
            else:
                # Fallback to original status
                result = self.run_command_with_validation([
                    "python", "proxy_status.py", "status"
                ], timeout=30)
                status_success = result.get("success", False)
                print(f"   {'✅' if status_success else '❌'} Fallback status check")
            
            daemon_tests.append({
                "test": "enhanced_status_check",
                "success": status_success,
                "output": result.get("stdout", "")[:200]
            })
            
        except Exception as e:
            daemon_tests.append({
                "test": "enhanced_status_check",
                "success": False,
                "error": str(e)
            })
            print(f"   ❌ Error: {e}")
        
        # Test 2: Health check
        print("🔍 Running health check...")
        try:
            result = self.run_command_with_validation([
                "python", "improved_proxy_status.py", "health"
            ], timeout=30)
            
            health_success = result.get("success", False)
            if health_success and result.get("stdout"):
                try:
                    health_data = json.loads(result["stdout"])
                    integrity_healthy = health_data.get("integrity", {}).get("healthy", False)
                    print(f"   {'✅' if integrity_healthy else '⚠️'} System integrity: {integrity_healthy}")
                except:
                    print("   ⚠️ Health data parsing failed")
            
            daemon_tests.append({
                "test": "health_check",
                "success": health_success,
                "output": result.get("stdout", "")[:200]
            })
            
        except Exception as e:
            daemon_tests.append({
                "test": "health_check", 
                "success": False,
                "error": str(e)
            })
            print(f"   ❌ Health check error: {e}")
        
        # Test 3: Configuration files validation
        print("🔍 Validating configuration files...")
        config_files = [
            {"file": "daemon_status.json", "required": False},
            {"file": "daemon.pid", "required": False}, 
            {"file": "proxy_config.json", "required": True},
            {"file": "working_proxies.txt", "required": True}
        ]
        
        for config_file in config_files:
            exists = os.path.exists(config_file["file"])
            readable = False
            size_ok = False
            
            if exists:
                readable = os.access(config_file["file"], os.R_OK)
                size_ok = os.path.getsize(config_file["file"]) > 0
            
            file_status = exists and readable and (size_ok or not config_file["required"])
            
            daemon_tests.append({
                "test": f"config_file_{config_file['file']}",
                "exists": exists,
                "readable": readable,
                "size_ok": size_ok,
                "success": file_status
            })
            
            status_icon = "✅" if file_status else ("⚠️" if not config_file["required"] else "❌")
            print(f"   {status_icon} {config_file['file']}: {'OK' if file_status else 'Issues'}")
        
        # Calculate success rate
        successful_tests = sum(1 for t in daemon_tests if t.get("success", False))
        total_tests = len(daemon_tests)
        
        self.results["daemon_tests"] = {
            "total_daemon_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": round((successful_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
            "test_details": daemon_tests
        }
        
        print(f"\n📊 Enhanced Daemon Tests Summary: {successful_tests}/{total_tests} tests passed ({self.results['daemon_tests']['success_rate']}%)")
        
        return successful_tests > (total_tests * 0.5)  # Pass if > 50% successful
    
    def run_all_enhanced_tests(self):
        """Run all enhanced test suites"""
        print("=" * 80)
        print("🧪 ENHANCED Pr0Xy-chaIN TEST SUITE")
        print("=" * 80)
        print(f"📅 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 Available Proxies: {len(self.working_proxies)}")
        print("=" * 80)
        print()
        
        try:
            # Run original tests that work well
            self.test_basic_connectivity()
            self.test_performance_metrics()
            self.test_error_handling()
            
            # Run enhanced tests 
            ip_rotation_ok = self.test_enhanced_ip_rotation()
            tool_integration_ok = self.test_enhanced_tool_integration()
            daemon_ok = self.test_daemon_functionality_enhanced()
            
            # Enhanced concurrent testing (simplified)
            self.test_concurrent_usage_enhanced()
            
            return self.generate_enhanced_report()
            
        except KeyboardInterrupt:
            print("\n⚠️ Enhanced test suite interrupted by user")
            return None
        except Exception as e:
            print(f"\n❌ Enhanced test suite failed with error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_concurrent_usage_enhanced(self):
        """Enhanced concurrent testing with better error handling"""
        print("\n🚀 TEST 5: Enhanced Concurrent Usage")
        print("-" * 50)
        
        if not self.working_proxies:
            print("⚠️ No proxies available for concurrent testing")
            self.results["stress_tests"] = {
                "concurrent_requests": 0,
                "successful_requests": 0,
                "success_rate": 0,
                "message": "No proxies available"
            }
            return
        
        def make_enhanced_request(proxy, request_id):
            """Make a single request through proxy with enhanced validation"""
            try:
                start_time = time.time()
                proxy_dict = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
                response = requests.get('http://httpbin.org/ip', proxies=proxy_dict, timeout=15)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    ip = data.get('origin', '')
                    
                    if self.validate_ip_address(ip):
                        return {
                            'request_id': request_id,
                            'proxy': proxy,
                            'success': True,
                            'ip': ip,
                            'response_time': duration
                        }
                
                return {
                    'request_id': request_id,
                    'proxy': proxy,
                    'success': False,
                    'error': f'Invalid response: {response.status_code}'
                }
                    
            except Exception as e:
                return {
                    'request_id': request_id,
                    'proxy': proxy,
                    'success': False,
                    'error': str(e)
                }
        
        # Test with fewer concurrent requests for better reliability
        concurrent_count = min(10, len(self.working_proxies) * 3)
        concurrent_results = []
        
        print(f"📡 Launching {concurrent_count} concurrent requests...")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            for i in range(concurrent_count):
                proxy = self.working_proxies[i % len(self.working_proxies)]
                future = executor.submit(make_enhanced_request, proxy, i+1)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        concurrent_results.append(result)
                        status = "✅" if result.get('success') else "❌"
                        print(f"   {status} Request {result['request_id']}: {result.get('ip', 'Failed')}")
                except Exception as e:
                    print(f"   ❌ Request failed: {e}")
        
        successful = sum(1 for r in concurrent_results if r and r.get('success'))
        response_times = [r['response_time'] for r in concurrent_results if r and r.get('response_time')]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        self.results["stress_tests"] = {
            "concurrent_requests": concurrent_count,
            "successful_requests": successful,
            "failed_requests": concurrent_count - successful,
            "success_rate": round((successful / concurrent_count) * 100, 2) if concurrent_count > 0 else 0,
            "average_response_time": round(avg_response_time, 2),
            "request_details": concurrent_results
        }
        
        print(f"\n📊 Enhanced Stress Test Summary:")
        print(f"   ✅ Success Rate: {self.results['stress_tests']['success_rate']}%")
        print(f"   ⚡ Avg Response: {avg_response_time:.2f}s")
    
    # Import the original methods that work well
    def test_basic_connectivity(self):
        """Use the original basic connectivity test (it works well)"""
        from comprehensive_test_suite import ProxyChainTester
        original_tester = ProxyChainTester()
        original_tester.working_proxies = self.working_proxies
        original_tester.results = {"basic_connectivity": {}}
        original_tester.test_basic_connectivity()
        self.results["basic_connectivity"] = original_tester.results["basic_connectivity"]
    
    def test_performance_metrics(self):
        """Use the original performance test (it works well)"""
        from comprehensive_test_suite import ProxyChainTester
        original_tester = ProxyChainTester()
        original_tester.working_proxies = self.working_proxies
        original_tester.results = {"performance_metrics": {}}
        original_tester.test_performance_metrics()
        self.results["performance_metrics"] = original_tester.results["performance_metrics"]
    
    def test_error_handling(self):
        """Use the original error handling test (it works well)"""
        from comprehensive_test_suite import ProxyChainTester
        original_tester = ProxyChainTester()
        original_tester.working_proxies = self.working_proxies
        original_tester.results = {"error_handling": {}}
        original_tester.test_error_handling()
        self.results["error_handling"] = original_tester.results["error_handling"]
    
    def generate_enhanced_report(self):
        """Generate enhanced comprehensive report"""
        print("\n" + "="*80)
        print("📋 ENHANCED COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        # Calculate enhanced scores
        total_tests = 0
        passed_tests = 0
        
        # Basic connectivity score
        if self.results.get("basic_connectivity"):
            connectivity_tests = len(self.results["basic_connectivity"].get("proxy_tests", []))
            connectivity_passed = sum(1 for t in self.results["basic_connectivity"]["proxy_tests"] if t["working"])
            total_tests += connectivity_tests
            passed_tests += connectivity_passed
            success_rate = (connectivity_passed/connectivity_tests*100) if connectivity_tests > 0 else 0
            print(f"\n🔍 CONNECTIVITY: {connectivity_passed}/{connectivity_tests} proxies working ({success_rate:.1f}%)")
        
        # Enhanced IP rotation score
        if self.results.get("ip_rotation"):
            rotation_total = self.results["ip_rotation"]["total_rotations"]
            rotation_passed = self.results["ip_rotation"]["successful_rotations"]
            total_tests += rotation_total
            passed_tests += rotation_passed
            success_rate = (rotation_passed/rotation_total*100) if rotation_total > 0 else 0
            print(f"🔄 IP ROTATION: {rotation_passed}/{rotation_total} rotations successful ({success_rate:.1f}%)")
            print(f"   🎯 Unique IPs discovered: {self.results['ip_rotation']['unique_ips']}")
        
        # Performance metrics
        if self.results.get("performance_metrics"):
            perf = self.results["performance_metrics"]["comparison"]
            print(f"⚡ PERFORMANCE:")
            print(f"   📊 Direct connection: {perf['direct_average']}s avg")
            print(f"   🔗 Proxy connection: {perf['proxy_average']}s avg")
            print(f"   📈 Slowdown factor: {perf['slowdown_factor']}x")
        
        # Enhanced tool integration score
        if self.results.get("tool_integration"):
            tool_total = self.results["tool_integration"]["total_tools_tested"]
            tool_passed = self.results["tool_integration"]["successful_integrations"]
            tool_rate = self.results["tool_integration"]["success_rate"]
            total_tests += tool_total
            passed_tests += tool_passed
            print(f"🛠️ TOOL INTEGRATION: {tool_passed}/{tool_total} tools working ({tool_rate}%)")
        
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
            error_rate = (error_passed/error_total*100) if error_total > 0 else 0
            print(f"🛡️ ERROR HANDLING: {error_passed}/{error_total} cases handled gracefully ({error_rate:.1f}%)")
        
        # Enhanced daemon tests
        if self.results.get("daemon_tests"):
            daemon_total = self.results["daemon_tests"]["total_daemon_tests"] 
            daemon_passed = self.results["daemon_tests"]["successful_tests"]
            daemon_rate = self.results["daemon_tests"]["success_rate"]
            total_tests += daemon_total
            passed_tests += daemon_passed
            print(f"🔄 DAEMON MANAGEMENT: {daemon_passed}/{daemon_total} tests passed ({daemon_rate:.1f}%)")
        
        # Overall score
        overall_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "overall_score": round(overall_score, 1),
            "test_end_time": datetime.now().isoformat(),
            "enhanced": True
        }
        
        print(f"\n{'='*50}")
        print(f"🏆 ENHANCED OVERALL SCORE: {overall_score:.1f}% ({passed_tests}/{total_tests})")
        
        if overall_score >= 85:
            print("✅ EXCELLENT - Enhanced proxy chain is working optimally!")
        elif overall_score >= 70:
            print("✅ GOOD - Minor issues detected, but functional")
        elif overall_score >= 50:
            print("⚠️ FAIR - Some issues need attention")
        else:
            print("❌ NEEDS ATTENTION - Multiple issues require fixing")
        
        print(f"{'='*50}")
        
        # Save detailed report
        report_file = f"enhanced_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Enhanced detailed report saved to: {report_file}")
        
        return self.results

def main():
    tester = ImprovedProxyChainTester()
    results = tester.run_all_enhanced_tests()
    
    if results:
        print(f"\n🎉 Enhanced test suite completed successfully!")
        print(f"📊 Final Enhanced Score: {results['summary']['overall_score']}%")
    else:
        print("\n❌ Enhanced test suite did not complete successfully")

if __name__ == "__main__":
    main()
