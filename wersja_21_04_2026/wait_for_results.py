import os, time, sys
target = 'gridsearch_results_full_50k_50y.json'
start = time.time()
while not os.path.exists(target):
    elapsed = time.time() - start
    if elapsed > 600:  # 10 min timeout
        print(f"⏰ Timeout after {elapsed/60:.1f} min")
        sys.exit(1)
    print(f"[{int(elapsed):3d}s] Waiting..." , flush=True, end='\r')
    time.sleep(5)
print(f"\n✅ File created after {elapsed/60:.1f} minutes")
with open(target) as f:
    lines = len(f.readlines())
print(f"📊 Results file: {lines} lines")
