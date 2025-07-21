#!/usr/bin/env python3
"""Quick test of improved features"""

from improved_test_suite import ImprovedProxyChainTester

def test_enhanced_features():
    """Test the enhanced parsing and validation features"""
    tester = ImprovedProxyChainTester()

    print('🧪 Testing Enhanced Features')
    print('=' * 40)

    # Test IP validation
    test_ips = ['192.168.1.1', 'invalid', '999.999.999.999', '125.107.207.225']
    print('\n📍 IP Validation Tests:')
    for ip in test_ips:
        valid = tester.validate_ip_address(ip)
        print(f'   {ip}: {"✅ Valid" if valid else "❌ Invalid"}')

    print('\n📤 IP Extraction Tests:')
    # Test IP extraction
    test_outputs = [
        'Current IP: 192.168.1.1',
        '{"origin": "125.107.207.225"}',
        '✅ Proxy working. Current IP: 8.8.8.8',
        'No IP found here',
        'Output: {\n  "origin": "183.145.247.215"\n}'
    ]
    for output in test_outputs:
        ip = tester.extract_ip_from_output(output)
        print(f'   "{output[:35]}" → {ip or "None"}')

    print('\n🔧 Command Execution Test:')
    # Test command execution with validation
    result = tester.run_command_with_validation(['python', 'proxy_scanner.py', '--help'], timeout=15)
    success = "✅" if result.get('success') else "❌"
    print(f'   Help command: {success} (return code: {result.get("returncode")})')
    
    print('\n✅ Enhanced features test completed!')

if __name__ == "__main__":
    test_enhanced_features()
