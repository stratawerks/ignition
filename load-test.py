#!/usr/bin/env python3
"""
Ignition Load Tester — sends concurrent prompts to all 5 seat agents
via the OpenClaw gateway API and measures response times.

Run on beta unit: python3 load-test.py
"""

import time
import json
import threading
import urllib.request
import urllib.error
from datetime import datetime

GATEWAY_URL = "http://localhost:18789"
SEATS = ["seat1", "seat2", "seat3", "seat4", "seat5"]

PROMPTS = [
    "What is 2 + 2? Answer in one word.",
    "Name one planet in our solar system.",
    "What color is the sky? One word.",
    "Complete this: The capital of France is ___.",
    "What year did World War 2 end? Numbers only.",
]

results = {}
lock = threading.Lock()


def send_to_agent(seat_id, prompt, prompt_num):
    """Send a message to an agent and measure response time."""
    start = time.time()
    try:
        payload = json.dumps({
            "message": prompt,
            "agentId": seat_id,
        }).encode()

        req = urllib.request.Request(
            f"{GATEWAY_URL}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode()
            elapsed = time.time() - start
            with lock:
                results[seat_id] = results.get(seat_id, [])
                results[seat_id].append({
                    "prompt_num": prompt_num,
                    "elapsed": round(elapsed, 2),
                    "status": "ok",
                    "response_len": len(body),
                })
            print(f"  ✓ {seat_id} [{prompt_num}] — {elapsed:.1f}s")

    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        print(f"  ✗ {seat_id} [{prompt_num}] — HTTP {e.code} ({elapsed:.1f}s)")
        with lock:
            results[seat_id] = results.get(seat_id, [])
            results[seat_id].append({"prompt_num": prompt_num, "elapsed": round(elapsed, 2), "status": f"http_{e.code}"})
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ✗ {seat_id} [{prompt_num}] — {type(e).__name__}: {e} ({elapsed:.1f}s)")
        with lock:
            results[seat_id] = results.get(seat_id, [])
            results[seat_id].append({"prompt_num": prompt_num, "elapsed": round(elapsed, 2), "status": "error"})


def run_round(round_num):
    """Fire all 5 seats simultaneously with a prompt."""
    prompt = PROMPTS[round_num % len(PROMPTS)]
    print(f"\nRound {round_num + 1} — firing all 5 seats concurrently")
    print(f"  Prompt: \"{prompt}\"")

    threads = []
    for seat in SEATS:
        t = threading.Thread(target=send_to_agent, args=(seat, prompt, round_num + 1))
        threads.append(t)

    # Launch all simultaneously
    for t in threads:
        t.start()

    # Wait for all to complete
    for t in threads:
        t.join(timeout=90)


def print_summary():
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for seat in SEATS:
        runs = results.get(seat, [])
        if not runs:
            print(f"  {seat}: no data")
            continue
        ok = [r for r in runs if r["status"] == "ok"]
        avg = sum(r["elapsed"] for r in ok) / len(ok) if ok else 0
        print(f"  {seat}: {len(ok)}/{len(runs)} ok, avg {avg:.1f}s")


if __name__ == "__main__":
    print("=" * 50)
    print("StrataWerks Ignition Load Tester")
    print(f"Target: {GATEWAY_URL}")
    print(f"Seats:  {', '.join(SEATS)}")
    print("=" * 50)

    ROUNDS = 3  # Change to run more rounds

    for i in range(ROUNDS):
        run_round(i)
        if i < ROUNDS - 1:
            print(f"\n  Waiting 5s before next round...")
            time.sleep(5)

    print_summary()
    print("\nDone. Check btop for resource usage during the test.")
