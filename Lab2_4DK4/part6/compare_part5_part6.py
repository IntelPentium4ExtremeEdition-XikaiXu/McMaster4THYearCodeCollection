import pandas as pd
import matplotlib.pyplot as plt

p5 = pd.read_csv("../part5/part5_results.csv")
p6 = pd.read_csv("part6_results.csv")

p5s = p5.groupby("data_lambda", as_index=False).agg(
    voice_p5=("voice_delay_ms", "mean"),
    data_p5=("data_delay_ms", "mean"),
)
p6s = p6.groupby("data_lambda", as_index=False).agg(
    voice_p6=("voice_delay_ms", "mean"),
    data_p6=("data_delay_ms", "mean"),
)
summary = p5s.merge(p6s, on="data_lambda")
summary.to_csv("part5_part6_comparison.csv", index=False)
print(summary.to_string(index=False))

plt.figure(figsize=(10, 6))
plt.plot(summary["data_lambda"], summary["voice_p5"], "o-",
         linewidth=2, label="Voice, FCFS Part 5")
plt.plot(summary["data_lambda"], summary["voice_p6"], "o-",
         linewidth=2, label="Voice, Priority Part 6")
plt.plot(summary["data_lambda"], summary["data_p5"], "s--",
         linewidth=2, label="Data, FCFS Part 5")
plt.plot(summary["data_lambda"], summary["data_p6"], "s--",
         linewidth=2, label="Data, Priority Part 6")
plt.xlabel("Data Packet Arrival Rate (packets/s)")
plt.ylabel("Mean Delay (ms)")
plt.title("Part 5 versus Part 6: FCFS and Voice Priority")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("part5_vs_part6.png", dpi=300, bbox_inches="tight")
plt.show()
