import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------------------------------------
# 1. Load per-seed results
# ------------------------------------------------------------
df = pd.read_csv("part4_results.csv")

# ------------------------------------------------------------
# 2. Compute mean, min, max for each p12 and each source
# ------------------------------------------------------------
stats = df.groupby("p12").agg(
    s1_mean=("source1_delay_ms", "mean"),
    s1_min=("source1_delay_ms", "min"),
    s1_max=("source1_delay_ms", "max"),
    s2_mean=("source2_delay_ms", "mean"),
    s2_min=("source2_delay_ms", "min"),
    s2_max=("source2_delay_ms", "max"),
    s3_mean=("source3_delay_ms", "mean"),
    s3_min=("source3_delay_ms", "min"),
    s3_max=("source3_delay_ms", "max"),
).reset_index()

# Save averaged data for convenience
stats.to_csv("part4_averaged.csv", index=False)

# ------------------------------------------------------------
# 3. Plot two-panel figure
# ------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# ---- Left panel: full p12 range, log scale ----
ax1.errorbar(stats["p12"], stats["s1_mean"],
             yerr=[stats["s1_mean"] - stats["s1_min"],
                   stats["s1_max"] - stats["s1_mean"]],
             marker='o', linestyle='-', capsize=3, label='Source 1')
ax1.errorbar(stats["p12"], stats["s2_mean"],
             yerr=[stats["s2_mean"] - stats["s2_min"],
                   stats["s2_max"] - stats["s2_mean"]],
             marker='s', linestyle='-', capsize=3, label='Source 2')
ax1.errorbar(stats["p12"], stats["s3_mean"],
             yerr=[stats["s3_mean"] - stats["s3_min"],
                   stats["s3_max"] - stats["s3_mean"]],
             marker='D', linestyle='-', capsize=3, label='Source 3')

ax1.set_yscale('log')
ax1.set_xlabel('Routing probability p12')
ax1.set_ylabel('Mean end-to-end delay (ms)')
ax1.set_title('Full range (log scale)')
ax1.axvline(1/3, color='gray', linestyle='--', linewidth=1, label='Stability bounds')
ax1.axvline(2/3, color='gray', linestyle='--', linewidth=1)
ax1.grid(True, alpha=0.3)
ax1.legend()

# ---- Right panel: balanced region (0.4 to 0.6) ----
mask = (stats["p12"] >= 0.4) & (stats["p12"] <= 0.6)
sub = stats[mask]

ax2.errorbar(sub["p12"], sub["s1_mean"],
             yerr=[sub["s1_mean"] - sub["s1_min"],
                   sub["s1_max"] - sub["s1_mean"]],
             marker='o', linestyle='-', capsize=3, label='Source 1')
ax2.errorbar(sub["p12"], sub["s2_mean"],
             yerr=[sub["s2_mean"] - sub["s2_min"],
                   sub["s2_max"] - sub["s2_mean"]],
             marker='s', linestyle='-', capsize=3, label='Source 2')
ax2.errorbar(sub["p12"], sub["s3_mean"],
             yerr=[sub["s3_mean"] - sub["s3_min"],
                   sub["s3_max"] - sub["s3_mean"]],
             marker='D', linestyle='-', capsize=3, label='Source 3')

ax2.set_xlabel('Routing probability p12')
ax2.set_ylabel('Mean end-to-end delay (ms)')
ax2.set_title('Balanced routing region')
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.savefig("part4_delay_vs_p12.png", dpi=300)
plt.show()
