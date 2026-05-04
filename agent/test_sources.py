"""
SHEtoken Agent — Source Connectivity Test
Run this to see which RSS sources are reachable on your network.

Usage: python test_sources.py

This helps diagnose DNS/firewall issues before running the full agent.
"""
import requests, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, ".")
from config import NEWS_SOURCES

TIMEOUT = 8

def test_source(name, url, language, region, *args):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SHEtoken/1.0)"}
        resp = requests.get(url, headers=headers,
                           timeout=TIMEOUT, allow_redirects=True)
        return name, resp.status_code, "OK" if resp.ok else "HTTP error"
    except requests.exceptions.ConnectionError as e:
        if "getaddrinfo" in str(e) or "NameResolution" in str(e):
            return name, 0, "DNS FAIL - blocked by network/firewall"
        return name, 0, f"Connection error"
    except requests.exceptions.Timeout:
        return name, 0, "Timeout"
    except Exception as e:
        return name, 0, str(e)[:60]

print("Testing all RSS sources...\n")
print(f"{'Source':<25} {'Status':<8} {'Result'}")
print("-" * 65)

ok = fail = dns = 0
with ThreadPoolExecutor(max_workers=8) as ex:
    futures = {ex.submit(test_source, *src): src[0] for src in NEWS_SOURCES}
    for future in as_completed(futures):
        name, code, msg = future.result()
        if code and code < 400:
            status = f"[OK {code}]"
            ok += 1
        elif "DNS FAIL" in msg:
            status = "[DNS  ]"
            dns += 1
        else:
            status = f"[FAIL ]"
            fail += 1
        print(f"  {name:<23} {status:<8} {msg}")

print(f"\nSummary: {ok} reachable | {fail} errors | {dns} DNS blocked")
if dns > 0:
    print(f"\nNote: {dns} sources blocked by DNS/network.")
    print("This is a local network issue (corporate proxy, VPN, or firewall).")
    print("Try opening one of the blocked URLs in your browser to confirm.")
    print(f"The agent will still work with the {ok} reachable sources.")
