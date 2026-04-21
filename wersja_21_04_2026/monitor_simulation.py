"""
Monitor full simulation progress and auto-generate heatmaps when ready
"""
import os
import json
import time
import subprocess
from pathlib import Path

results_file = 'gridsearch_results_full_50k_50y.json'
max_wait = 120 * 60  # 120 minutes max wait
check_interval = 30  # Check every 30 seconds
start_time = time.time()

print("\n" + "="*80)
print("📊 MONITORING FULL SIMULATION PROGRESS")
print("="*80)
print(f"Looking for: {results_file}")
print(f"Max wait time: {max_wait//60} minutes")
print(f"Check interval: {check_interval} seconds")
print("="*80 + "\n")

while time.time() - start_time < max_wait:
    if os.path.exists(results_file):
        print(f"\n✅ Results file found! Loading: {results_file}")
        
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            if len(results) == 25:
                print(f"✅ All 25 combinations completed successfully!")
                print("\n" + "="*80)
                print("RESULTS SUMMARY:")
                print("="*80)
                
                scores = [r['score'] for r in results]
                print(f"Min score:  {min(scores):+7.2f}%")
                print(f"Max score:  {max(scores):+7.2f}%")
                print(f"Mean score: {sum(scores)/len(scores):+7.2f}%")
                
                print("\n🏆 TOP 5 CONFIGURATIONS:")
                for i, r in enumerate(sorted(results, key=lambda x: -x['score'])[:5]):
                    print(f"  {i+1}. BR={r['birth_rate']:.4f}, MR={r['mortality_rate']:.6f} → " +
                          f"{r['score']:+7.2f}% (Pop: {r['initial_population']} → {r['final_population']})")
                
                print("\n" + "="*80)
                print("⏳ Generating visualizations from full simulation data...")
                print("="*80 + "\n")
                
                # Auto-generate heatmaps
                try:
                    print("1️⃣  Generating basic heatmap...")
                    result = subprocess.run([
                        '.venv/bin/python', 
                        'generate_heatmap_realistic.py',
                        '--input-file', results_file,
                        '--output-file', 'heatmap_full_50k_50y_realistic.html'
                    ], capture_output=True, timeout=30)
                    if result.returncode == 0:
                        print("   ✅ Basic heatmap created: heatmap_full_50k_50y_realistic.html")
                    else:
                        print(f"   ⚠️  Error: {result.stderr.decode()[:200]}")
                except Exception as e:
                    print(f"   ⚠️  Could not generate basic heatmap: {e}")
                
                try:
                    print("2️⃣  Generating detailed heatmap...")
                    result = subprocess.run([
                        '.venv/bin/python',
                        'generate_heatmap_detailed.py',
                        '--input-file', results_file,
                        '--output-file', 'heatmap_full_50k_50y_detailed.html'
                    ], capture_output=True, timeout=30)
                    if result.returncode == 0:
                        print("   ✅ Detailed heatmap created: heatmap_full_50k_50y_detailed.html")
                    else:
                        print(f"   ⚠️  Error: {result.stderr.decode()[:200]}")
                except Exception as e:
                    print(f"   ⚠️  Could not generate detailed heatmap: {e}")
                
                print("\n" + "="*80)
                print("✅ FULL SIMULATION AND VISUALIZATION COMPLETE!")
                print("="*80 + "\n")
                break
            else:
                print(f"⏳ Found partial results: {len(results)}/25 combinations")
                remaining = 25 - len(results)
                elapsed = time.time() - start_time
                print(f"   Elapsed: {elapsed//60:.0f}min {elapsed%60:.0f}s")
                print(f"   Remaining combos: {remaining}")
        
        except Exception as e:
            print(f"⚠️  Error reading results file: {e}")
    
    else:
        elapsed = time.time() - start_time
        mins, secs = int(elapsed // 60), int(elapsed % 60)
        print(f"[{mins:02d}:{secs:02d}] ⏳ Waiting for results... still running", flush=True)
    
    time.sleep(check_interval)

if time.time() - start_time >= max_wait:
    print(f"\n⏰ Timeout! Script did not complete within {max_wait//60} minutes")
