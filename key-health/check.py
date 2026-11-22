import json
import os
import time
import urllib.error
import urllib.request


def http_status(req, timeout=30):
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return None, type(e).__name__


def check_alchemy():
    key = os.environ.get("ALCHEMY_KEY", "")
    if not key:
        print("ALCHEMY: MISSING (secret not injected)", flush=True)
        return
    req = urllib.request.Request(
        "https://eth-mainnet.g.alchemy.com/v2/" + key,
        data=json.dumps(
            {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}
        ).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    status, body = http_status(req)
    if status == 200:
        try:
            ok = "result" in json.loads(body)
        except Exception:
            ok = False
        print(
            "ALCHEMY: %s (http 200, eth_blockNumber %s)"
            % ("PASS" if ok else "FAIL", "ok" if ok else "no result"),
            flush=True,
        )
    elif status is None:
        print("ALCHEMY: ERROR (network: %s)" % body, flush=True)
    else:
        print("ALCHEMY: FAIL (http %s)" % status, flush=True)


def check_chainstack():
    key = os.environ.get("CHAINSTACK_KEY", "")
    if not key:
        print("CHAINSTACK: MISSING (secret not injected)", flush=True)
        return
    req = urllib.request.Request(
        "https://api.chainstack.com/v1/organization/",
        headers={"Authorization": "Bearer " + key},
        method="GET",
    )
    status, body = http_status(req)
    if status == 200:
        print("CHAINSTACK: PASS (http 200, organization ok)", flush=True)
    elif status is None:
        print("CHAINSTACK: ERROR (network: %s)" % body, flush=True)
    else:
        print("CHAINSTACK: FAIL (http %s)" % status, flush=True)


def main():
    print("key health check starting", flush=True)
    check_alchemy()
    check_chainstack()
    print("HEALTH-CHECK DONE", flush=True)
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
