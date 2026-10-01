import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results.csv")

plt.figure(figsize=(8,5))
plt.plot(df["lambda"],
         df["delay"],
         marker='o',
         linewidth=2)

plt.xlabel("Packet Arrival Rate (packets/s)")
plt.ylabel("Mean Delay (ms)")
plt.title("Mean Delay vs Packet Arrival Rate")
plt.grid(True)

plt.tight_layout()

plt.savefig(
    "part1_delay_vs_arrival.png",
    dpi=300,
    bbox_inches="tight"
)

print("Figure saved!")
