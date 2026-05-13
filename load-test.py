#!/usr/bin/env python3
"""
StrataWerks Ignition Load Tester v2
Simulates 5 concurrent AI requests via OpenRouter — same as what
each seat agent does when processing a user message.

Run: python3 /tmp/load-test.py
"""
import time
import json
import threading
import urllib.request

API_KEY = open("/home/oliver/.openclaw/.env").read()
# Parse OPENROUTER_API_KEY from .env
for line in API_KEY.splitlines():
    if "OPENROUTER_API_KEY" in line:
        API_KEY = line.split("=", 1)[1].strip().strip('"')
        break

SEATS = ["seat1", "seat2", "seat3", "seat4", "seat5"]
PROMPTS = [
    "Count from 1 to 20, one number per line.",
    "List the planets in order from the sun.",
    "Write a haiku about mountains.",
    "Name 10 countries that start with the letter C.",
    "Explain what RAM is in 3 sentences.",
]

results = {}
lock = threading.Lock()


def call_llm(seat_id, prompt, round_num):
    start = time.time()
    try:
        payload = json.dumps({
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
        }).encode()

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
                "HTTP-Referer": "https://stratawerks.ai",
                "X-Title": f"StrataWerks-LoadTest-{seat_id}",
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode())
            elapsed = time.time() - start
            tokens = body.get("usage", {}).get("total_tokens", 0)
            preview = body["choices"][0]["message"]["content"][:60].replace("\n", " ")
            with lock:
                results.setdefault(seat_id, []).append(
                    {"round": round_num, "elapsed": round(elapsed, 2), "tokens": tokens, "status": "ok"}
                )
            print(f"  ✓ {seat_id} [{round_num}] {elapsed:.1f}s / {tokens}tok — \"{preview}…\"")

    except Exception as e:
        elapsed = time.time() - start
        print(f"  ✗ {seat_id} [{round_num}] ERROR: {e} ({elapsed:.1f}s)")
        with lock:
            results.setdefault(seat_id, []).append(
                {"round": round_num, "elapsed": round(elapsed, 2), "tokens": 0, "status": "error"}
            )


def run_round(round_num):
    prompt = PROMPTS[round_num % len(PROMPTS)]
    print(f"\nRound {round_num + 1} — 5 concurrent requests")
    print(f"  Prompt: \"{prompt[:60]}\"")

    threads = [
        threading.Thread(target=call_llm, args=(seat, prompt, round_num + 1))
        for seat in SEATS
    ]
    t0 = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=90)
    print(f"  All done in {time.time() - t0:.1f}s wall time")


def print_summary():
    print("\n" + "=" * 52)
    print("SUMMARY")
    print("=" * 52)
    total_tokens = 0
    for seat in SEATS:
        runs = results.get(seat, [])
        ok = [r for r in runs if r["status"] == "ok"]
        avg = sum(r["elapsed"] for r in ok) / len(ok) if ok else 0
        toks = sum(r["tokens"] for r in ok)
        total_tokens += toks
        print(f"  {seat:6}  {len(ok)}/{len(runs)} ok  avg {avg:.1f}s  {toks} tokens")
    print(f"\n  Total tokens used: {total_tokens}")
    print("=" * 52)


if __name__ == "__main__":
    print("=" * 52)
    print("StrataWerks Ignition Load Tester v2")
    print(f"Model: openai/gpt-4o-mini (via OpenRouter)")
    print(f"Seats: {len(SEATS)}  |  Rounds: 3")
    print("=" * 52)

    for i in range(3):
        run_round(i)
        if i < 2:
            print(f"\n  Cooling down 5s...")
            time.sleep(5)

    print_summary()
