import os
from main import solve_turnstile, parse_proxy
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Proxy provided by the user
RAW_PROXY = "5.175.215.9:6969:260423171zzjyea-country-us:qe0swevki65u"

def run_test():
    print("=== Testing Turnstile Solver Locally ===")
    
    proxy_str = parse_proxy(RAW_PROXY)
    print(f"Parsed Proxy String: {proxy_str}")
    
    # Test WITH proxy to confirm full production flow
    print("\nStarting solver WITH proxy (production mode)...")
    token = solve_turnstile(proxy_str, headless=False)
    
    if token:
        print("\n[SUCCESS] Token obtained!")
        print(f"Token (first 50 chars): {token[:50]}...")
        print(f"Token length: {len(token)}")
    else:
        print("\n[FAILED] Could not get token.")

if __name__ == "__main__":
    run_test()
