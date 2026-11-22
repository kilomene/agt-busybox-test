import json
import os
import time
import urllib.error
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36"}


def http(req, timeout=30):
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read().decode("utf-8", "replace")
        except Exception:
            return e.code, ""
    except Exception as e:
        return None, type(e).__name__


def brief(body, limit=220):
    body = " ".join((body or "").split())
    return body[:limit]


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
        headers={"Content-Type": "application/json", **UA},
        method="POST",
    )
    status, body = http(req)
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
        print(
            "ALCHEMY: FAIL (http %s) body: %s" % (status, brief(body)), flush=True
        )


def check_chainstack():
    key = os.environ.get("CHAINSTACK_KEY", "")
    if not key:
        print("CHAINSTACK: MISSING (secret not injected)", flush=True)
        return
    for path in ("organization/", "projects/"):
        req = urllib.request.Request(
            "https://api.chainstack.com/v1/" + path,
            headers={"Authorization": "Bearer " + key, **UA},
            method="GET",
        )
        status, body = http(req)
        if status == 200:
            print(
                "CHAINSTACK: PASS (http 200 on /v1/%s)" % path, flush=True
            )
            return
        if status is None:
            print(
                "CHAINSTACK: ERROR (network: %s on /v1/%s)" % (body, path),
                flush=True,
            )
            return
        print(
            "CHAINSTACK: http %s on /v1/%s body: %s"
            % (status, path, brief(body)),
            flush=True,
        )
    print("CHAINSTACK: FAIL (no 200 on either endpoint)", flush=True)


def main():
    print("key health check v2 starting", flush=True)
    check_alchemy()
    check_chainstack()
    print("HEALTH-CHECK DONE", flush=True)
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
