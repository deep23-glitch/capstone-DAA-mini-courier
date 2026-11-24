"""Render saved console outputs as terminal-style PNG screenshots (for the report)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def shot(src, dst, max_lines=48):
    lines = open(src).read().rstrip().split("\n")[:max_lines]
    fig = plt.figure(figsize=(10, 0.158 * len(lines) + 0.5), facecolor="#1e1e2e")
    fig.text(0.02, 0.98, "\n".join(lines), va="top", family="monospace", fontsize=8.5, color="#d4d4d4")
    fig.savefig(dst, dpi=130, facecolor=fig.get_facecolor()); plt.close(fig)

for n in ("run_small", "run_medium_2opt", "test_results", "benchmark_summary"):
    shot(f"outputs/{n}.txt", f"outputs/screenshot_{n}.png", 40)
shot("outputs/run_large_all_trips.txt", "outputs/screenshot_run_large_all_trips.png", 30)
