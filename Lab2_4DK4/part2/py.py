import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("part2_results.csv")

summary = (
    df.groupby("lambda")
      .agg({
          "violations":"sum",
          "processed":"sum"
      })
)

summary["prob"] = (
    summary["violations"]
    /
    summary["processed"]
)

plt.figure(figsize=(8,5))

plt.plot(
    summary.index,
    summary["prob"],
    'o-',
    linewidth=2
)

plt.axhline(
    y=0.02,
    color='red',
    linestyle='--',
    label='2% Threshold'
)

plt.xlabel("Arrival Rate (packets/s)")
plt.ylabel("P(delay > 20 ms)")
plt.title("Part 2 Delay Violation Probability")

plt.grid(True)
plt.legend()

plt.savefig(
    "part2_probability.png",
    dpi=300
)

plt.show()
