import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("part3_results.csv")
df.columns = df.columns.str.strip()

average = (
    df.groupby("lambda", as_index=False)["mean_delay_ms"]
      .mean()
)

plt.plot(
    average["lambda"],
    average["mean_delay_ms"],
    marker="o",
    linestyle="-",
    label="M/D/2: Two 500 Kbps Links"
)

plt.xlabel("Packet Arrival Rate, λ (packets/s)")
plt.ylabel("Mean Packet Delay (ms)")
plt.title("Mean Packet Delay vs. Arrival Rate")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("part3_mean_delay.png", dpi=300)
plt.show()
