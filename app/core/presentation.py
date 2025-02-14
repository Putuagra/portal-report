import matplotlib.pyplot as plt
import numpy as np
from core.data import check_type
from typing import Any


# def format_number(num):
#     if num >= 1000000:
#         return f"{num / 1000000:.1f}M"
#     elif num >= 1000:
#         return f"{num / 1000:.1f}K"
#     else:
#         return str(num)


def bar_chart(ax, x_axis, df_obj, width, color: str, label: dict[str, str], offset=0):
    bars = ax.bar(
        x_axis + offset,
        df_obj,
        width=width,
        color=color,
        label=label,
    )
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            "",
            ha="center",
            va="bottom",
            fontsize=8,
        )


def line_chart(ax, axis, df_obj, color: str, label: str):
    ax.plot(
        axis,
        df_obj,
        marker="o",
        linestyle="-",
        color=color,
        label=label,
    )


def add_annotation(ax, text, x, y, isBar=True):
    ax.annotate(
        text,
        (x, y),
        textcoords="offset points",
        xytext=(0, 2),
        ha="center",
        fontsize=10,
        fontweight="bold",
        color="red" if isBar else "black",
    ) # -> create annotation for chart
    # plt.scatter([x], [y], color="red", marker="*", s=100) # -> for star logo


def generate_vertical_bar(
    df: dict[str, Any], filename: str, label: dict[str, str], selected_type: str
):
    variable = check_type(selected_type)
    chart = {"fontsize": 12, "fontsize_title": 14, "fontweight": "bold", "pad": 10}
    df_this_month = df["this_month"].head(10).reset_index(drop=True) # -> get first 10 data
    max_index_thismonth = df_this_month[label].idxmax() # -> get index for line chart
    max_value_thismonth = df_this_month[label].max() # -> get max value for line chart
    fig, ax = plt.subplots(figsize=(15, 6))
    width = 0.2
    x = np.arange(len(df_this_month[f"{variable['REQ_TRX']} Date"]))
    if label == f"Max {variable['TPS_RPS']}":
        bar_chart(
            ax,
            x,
            df_this_month[f"Avg {variable['TPS_RPS']}"],
            width,
            "green",
            f"Avg {variable['TPS_RPS']}",
            offset=-width,
        )
        bar_chart(
            ax,
            x,
            df_this_month[label],
            width,
            "darkorange",
            label,
        )
        bar_chart(
            ax,
            x,
            df_this_month[f"Max {variable['TPS_RPS']} (95th Percentile)"],
            width,
            "brown",
            f"Max {variable['TPS_RPS']} (95th Percentile)",
            offset=width,
        )
        plt.title(
            f"{variable['TPS_RPS']} per Day",
            fontweight=chart["fontweight"],
            fontsize=chart["fontsize_title"],
            pad=chart["pad"],
        )
    else:
        bar_chart(
            ax,
            x,
            df_this_month[label],
            width,
            "darkorange",
            "Total Request This Month",
        )
        plt.title(
            label,
            fontweight=chart["fontweight"],
            fontsize=chart["fontsize_title"],
            pad=chart["pad"],
        )
    add_annotation(
        ax,
        f"{int(max_value_thismonth)}",
        max_index_thismonth,
        max_value_thismonth,
    )
    if not df["last_month"].empty:
        df_last_month = df["last_month"].head(10).reset_index(drop=True)
        x_mapped = np.arange(len(df_last_month[f"{variable['REQ_TRX']} Date"]))

        max_index_lastmonth = df_last_month[label].idxmax()
        max_value_lastmonth = df_last_month[label].max()
        line_chart(
            ax,
            x_mapped,
            df_last_month[label],
            "deepskyblue",
            "Total Request Last Month",
        )
        add_annotation(
            ax,
            f"{int(max_value_lastmonth)}",
            max_index_lastmonth,
            max_value_lastmonth,
            isBar=False,
        )
        # Add another label for last month data
        ax_top = ax.twiny()
        ax_top.set_xlim(ax.get_xlim()) # -> make sure both axes are in the same line
        ax_top.set_xticks(x_mapped) # -> how much ticks for date
        ax_top.set_xlabel(
            f"{variable['REQ_TRX']} Date (Last Month)",
            fontsize=chart["fontsize"],
            fontweight=chart["fontweight"],
        )
        ax_top.set_xticklabels(
            df_last_month[f"{variable['REQ_TRX']} Date"], rotation=45
        )

    # Add label
    ax.set_xlabel(
        f"{variable['REQ_TRX']} Date (This Month)",
        fontsize=12,
        color="red",
        fontweight=chart["fontweight"],
    )
    ax.set_xticks(x) # -> how much ticks for date
    ax.set_xticklabels(df_this_month[f"{variable['REQ_TRX']} Date"], rotation=45)
    ax.legend(bbox_to_anchor=(1, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight", pad_inches=0)
