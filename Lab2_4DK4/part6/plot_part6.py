import pandas as pd
import matplotlib.pyplot as plt

raw = pd.read_csv("part6_results.csv")
summary = (
    raw.groupby("data_lambda", as_index=False)
       .agg(
           voice_delay_ms=("voice_delay_ms", "mean"),
           data_delay_ms=("data_delay_ms", "mean"),
       )
)

print(summary.to_string(index=False))
summary.to_csv("part6_summary.csv", index=False)

plt.figure(figsize=(9, 6))
plt.plot(summary["data_lambda"], summary["voice_delay_ms"],
         marker="o", linewidth=2, label="Voice packets")
plt.plot(summary["data_lambda"], summary["data_delay_ms"],
         marker="s", linewidth=2, label="Data packets")
plt.xlabel("Data Packet Arrival Rate (packets/s)")
plt.ylabel("Mean Delay (ms)")
plt.title("Part 6: Non-Preemptive Voice Priority")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("part6_priority_delay.png", dpi=300, bbox_inches="tight")
plt.show()
