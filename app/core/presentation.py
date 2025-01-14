import matplotlib.pyplot as plt
import numpy as np



def generate_vertical_bar(df, filename, label):
    df = df.head(20)
    plt.figure(figsize=(10, 6))
    width = 0.2
    x = np.arange(len(df["Transaction Date"]))
    if label == "Max TPS":
        bar1 = plt.bar(x - width, df[label], width=width, color="skyblue", label=label)
        bar2 = plt.bar(x, df["Avg TPS"], width=width, color="yellow", label="Avg TPS")
        bar3 = plt.bar(
            x + width,
            df["Max TPS (95th Percentile)"],
            width=width,
            color="red",
            label="Max TPS (95th Percentile)",
        )
        plt.title("TPS per Day")
        for bars in [bar1, bar2, bar3]:
            for bar in bars:
                height = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    f"{height:.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                )
    else:
        bar = plt.bar(x, df[label], width=width, color="skyblue", label=label)
        plt.title(label)
        for bar in bar:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{height:.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    # Add labels and title
    plt.xlabel("Transaction Date")
    plt.legend(bbox_to_anchor=(1, 1), loc="upper left")
    plt.xticks(x, df["Transaction Date"], rotation=45)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight", pad_inches=0)

    # Show the plot
    # plt.show()