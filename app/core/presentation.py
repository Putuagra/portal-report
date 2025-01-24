import matplotlib.pyplot as plt
import numpy as np
from core.data import check_type



def generate_vertical_bar(df, filename, label, type):
    # TPS_or_RPS, req_or_trx, REQ_or_TRX = check_type(type)
    variable = check_type(type)
    df = df.head(20)
    plt.figure(figsize=(10, 6))
    width = 0.2
    x = np.arange(len(df[f"{variable["REQ_TRX"]} Date"]))
    if label == f"Max {variable["TPS_RPS"]}":
        bar1 = plt.bar(x - width, df[label], width=width, color="skyblue", label=label)
        bar2 = plt.bar(x, df[f"Avg {variable["TPS_RPS"]}"], width=width, color="yellow", label=f"Avg {variable["TPS_RPS"]}")
        if f"Max {variable["TPS_RPS"]} (95th Percentile)" in df.columns:
            bar3 = plt.bar(
                x + width,
                df[f"Max {variable["TPS_RPS"]} (95th Percentile)"],
                width=width,
                color="red",
                label=f"Max {variable["TPS_RPS"]} (95th Percentile)",
            )
        else:
            bar3 = None
        plt.title(f"{variable["TPS_RPS"]} per Day")
        for bars in [bar1, bar2, bar3]:
            if bars is not None:
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
    plt.xlabel(f"{variable["REQ_TRX"]} Date")
    plt.legend(bbox_to_anchor=(1, 1), loc="upper left")
    plt.xticks(x, df[f"{variable["REQ_TRX"]} Date"], rotation=45)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight", pad_inches=0)

    # Show the plot
    # plt.show()