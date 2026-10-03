import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("part4_results.csv")

summary = (
    df.groupby("p12", as_index=False)
      .agg(
          source1_delay_ms=("source1_delay_ms", "mean"),
          source2_delay_ms=("source2_delay_ms", "mean"),
          source3_delay_ms=("source3_delay_ms", "mean")
      )
)

print(summary.to_string(index=False))

summary.to_csv(
    "part4_summary.csv",
    index=False
)

plt.figure(figsize=(9, 6))

plt.plot(
    summary["p12"],
    summary["source1_delay_ms"],
    marker="o",
    linewidth=2,
    label="Source 1"
)

plt.plot(
    summary["p12"],
    summary["source2_delay_ms"],
    marker="s",
    linewidth=2,
    label="Source 2"
)

plt.plot(
    summary["p12"],
    summary["source3_delay_ms"],
    marker="^",
    linewidth=2,
    label="Source 3"
)

plt.axvline(
    x=0.5,
    color="gray",
    linestyle="--",
    linewidth=1,
    label="Balanced routing: p12 = 0.5"
)

plt.xlabel("Routing Probability p12")
plt.ylabel("Mean End-to-End Delay (ms)")
plt.title("Part 4: Mean Packet Delay vs Routing Probability")

plt.xticks(summary["p12"])
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(
    "part4_delay_vs_p12.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
