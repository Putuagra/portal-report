import time
from fpdf import FPDF
import os
import dataframe_image as dfi
import shutil
import pandas as pd
from core.presentation import generate_vertical_bar
from core.data import check_type
from io import BytesIO
from typing import Any


class PDF(FPDF):

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


RESOURCES_DIR = "resources"
IMAGE_DPI = 150


def create_title(title, pdf):

    # Add main title
    pdf.set_font("Helvetica", "b", 20)
    pdf.ln(20)
    pdf.write(5, title)
    pdf.ln(10)

    # Add date of report
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(r=128, g=128, b=128)
    today = time.strftime("%d/%m/%Y")
    pdf.write(4, f"{today}")

    # Add line break
    pdf.ln(10)


def write_to_pdf(pdf, text):
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.set_font("Helvetica", "", 12)
    pdf.write(5, text)
    pdf.ln(10)


def color_negative_red(value):
    return f"color: {'red' if value < 0 else 'green' if value > 0 else 'black'}"


def style_dataframe(df: dict[str, Any], format_rules: dict[str, str]):
    return (
        df.style.format(format_rules)
        .map(color_negative_red, subset=["Trx Pct Change"])
        .hide(axis="index")
    )


def export_to_image(styled_df, file_path: str):
    dfi.export(styled_df, file_path, dpi=IMAGE_DPI, table_conversion="matplotlib")


def generate_charts(
    df_obj: dict[str, Any],
    max_tps_path: str,
    total_path: str,
    label_tps_rps: dict[str, str],
    label_req_trx: dict[str, str],
    selected_type: str,
):
    generate_vertical_bar(df_obj, max_tps_path, f"Max {label_tps_rps}", selected_type)
    generate_vertical_bar(
        df_obj, total_path, f"Total {label_req_trx} Per Day", selected_type
    )


def process_dataframe(
    df_obj: dict[str, Any],
    format_rules: dict[str, str],
    output_prefix: str,
    variable: dict[str, str],
    selected_type: str,
):
    styled_df = style_dataframe(df_obj["this_month"], format_rules)
    data_image_path = f"{RESOURCES_DIR}/{output_prefix}.png"
    export_to_image(styled_df, data_image_path)

    max_tps_path = f"{RESOURCES_DIR}/{output_prefix}_verticalBarMax.png"
    total_path = f"{RESOURCES_DIR}/{output_prefix}_verticalBarTotal.png"
    generate_charts(
        df_obj,
        max_tps_path,
        total_path,
        variable["TPS_RPS"],
        variable["REQ_TRX"],
        selected_type,
    )

    return calculate_summary(df_obj["this_month"], variable["REQ_TRX"])


def handle_data(
    df_obj: dict[str, Any],
    day_format_rules: dict[str, str],
    variable: dict[str, str],
    selected_type: str,
    is_wondr=False,
):
    if is_wondr:
        df_ext = {
            "this_month": df_obj["this_month"][
                df_obj["this_month"]["Type"] == "external"
            ],
            "last_month": (
                df_obj["last_month"][df_obj["last_month"]["Type"] == "external"]
                if not df_obj["last_month"].empty
                else pd.DataFrame()
            ),
        }

        df_in = {
            "this_month": df_obj["this_month"][
                df_obj["this_month"]["Type"] == "internal"
            ],
            "last_month": (
                df_obj["last_month"][df_obj["last_month"]["Type"] == "internal"]
                if not df_obj["last_month"].empty
                else pd.DataFrame()
            ),
        }

        summary_ext = process_dataframe(
            df_ext, day_format_rules, "data_ex", variable, selected_type
        )
        summary_in = process_dataframe(
            df_in, day_format_rules, "data_in", variable, selected_type
        )

        return {
            "summary_ext": summary_ext,
            "summary_in": summary_in,
        }
    else:
        summary = process_dataframe(
            df_obj, day_format_rules, "data", variable, selected_type
        )
        return {"summary": summary}


def write_section(pdf, title, image_path, height=0, width=185):
    write_to_pdf(pdf, title)
    pdf.image(image_path, h=height, w=width)


def write_conclusion(pdf, req_or_trx, summary=None, summary_ext=None, summary_in=None):
    if summary_ext and summary_in:
        conclusion_text = (
            f"In conclusion, This month {req_or_trx}s show a total decrease in {req_or_trx}s by {summary_ext['Negative Values Count']} "
            f"and increase in {req_or_trx}s by {summary_ext['Positive Values Count']} for external, and show a total decrease in {req_or_trx}s "
            f"by {summary_in['Negative Values Count']} and increase in {req_or_trx}s by {summary_in['Positive Values Count']} for internal. "
            f"The lowest decrease was {summary_ext['Minimum']:.2f}%, while the highest increase reached {summary_ext['Maximum']:.2f}% for external. "
            f"The lowest decrease was {summary_in['Minimum']:.2f}%, while the highest increase reached {summary_in['Maximum']:.2f}% for internal. "
            f"The highest {req_or_trx} total occurred on {summary_ext['Trx Date']} with a value of {summary_ext['Max Total Trx']} for external, "
            f"and the highest {req_or_trx} total occurred on {summary_in['Trx Date']} with a value of {summary_in['Max Total Trx']} for internal."
        )
    elif summary:
        conclusion_text = (
            f"In conclusion, This month {req_or_trx}s show a total decrease in {req_or_trx}s by {summary['summary']['Negative Values Count']} "
            f"and increase in {req_or_trx}s by {summary['summary']['Positive Values Count']}. The lowest decrease was {summary['summary']['Minimum']:.2f}%, "
            f"while the highest increase reached {summary['summary']['Maximum']:.2f}%. The highest {req_or_trx} total occurred on {summary['summary']['Trx Date']}, "
            f"with a value of {summary['summary']['Max Total Trx']}."
        )
    else:
        conclusion_text = "No summary data available"
    write_to_pdf(pdf, conclusion_text)


def write_pdf_content(pdf, type, variable, summary):

    pdf.add_page()
    create_title("Monthly Report", pdf)

    if type != "WONDR":
        write_section(
            pdf,
            f"1. The table below illustrates the monthly {variable["REQ_TRX"]}s of {type}:",
            f"./{RESOURCES_DIR}/data.png",
        )
    else:
        write_section(
            pdf,
            f"1a. The table below illustrates the monthly {variable["REQ_TRX"]}s of {type} external:",
            f"./{RESOURCES_DIR}/data_ex.png",
        )
        pdf.add_page()
        write_section(
            pdf,
            f"1b. The table below illustrates the monthly {variable["REQ_TRX"]}s of {type} internal:",
            f"./{RESOURCES_DIR}/data_in.png",
        )

    pdf.add_page()
    write_section(
        pdf,
        f"2. The table below illustrates total amount monthly {variable["REQ_TRX"]}s:",
        f"./{RESOURCES_DIR}/data_month.png",
    )
    pdf.ln(10)

    if type != "WONDR":
        write_section(
            pdf,
            f"3. The visualisations below shows Max {variable["TPS_RPS"]} and Total {variable["REQ_TRX"]} per Day:",
            f"./{RESOURCES_DIR}/data_verticalBarMax.png",
            75,
            199,
        )
        pdf.ln(10)
        pdf.image(f"./{RESOURCES_DIR}/data_verticalBarTotal.png", h=75, w=199)
        pdf.ln(10)
        write_conclusion(pdf, variable["req_trx"], summary=summary)
    else:
        write_section(
            pdf,
            f"3a. The visualisations below shows Max {variable["TPS_RPS"]} and Total {variable["REQ_TRX"]} external per Day:",
            f"./{RESOURCES_DIR}/data_ex_verticalBarMax.png",
            75,
            199,
        )
        pdf.ln(10)
        pdf.image(f"./{RESOURCES_DIR}/data_ex_verticalBarTotal.png", h=75, w=199)
        pdf.add_page()
        write_section(
            pdf,
            f"3b. The visualisations below shows Max {variable["TPS_RPS"]} and Total {variable["REQ_TRX"]} internal per Day:",
            f"./{RESOURCES_DIR}/data_in_verticalBarMax.png",
            75,
            199,
        )
        pdf.ln(10)
        pdf.image(f"./{RESOURCES_DIR}/data_in_verticalBarTotal.png", h=75, w=199)
        pdf.ln(10)
        write_conclusion(
            pdf,
            variable["req_trx"],
            summary_ext=summary["summary_ext"],
            summary_in=summary["summary_in"],
        )


def calculate_summary(df, REQ_or_TRX):
    # Count for summary
    max_row_trx = df.loc[df[f"Total {REQ_or_TRX} Per Day"].idxmax()]
    return {
        "Minimum": df["Trx Pct Change"].min(),
        "Maximum": df["Trx Pct Change"].max(),
        "Negative Values Count": (df["Trx Pct Change"] < 0).sum(),
        "Positive Values Count": (df["Trx Pct Change"] > 0).sum(),
        "Max Total Trx": "{:,.0f}".format(
            max_row_trx[f"Total {REQ_or_TRX} Per Day"]
        ).replace(",", "."),
        "Trx Date": max_row_trx[f"{REQ_or_TRX} Date"],
    }


def dataframe_to_pdf(
    df_param: dict[str, pd.DataFrame | dict[str, Any] | dict | None], selected_type: str
):
    variable = check_type(selected_type)

    df_obj = {
        "this_month": df_param["this_month"]["data_pdf_day"],
        "last_month": (
            df_param["last_month"]["data_pdf_day"]
            if bool(df_param["last_month"]) is True
            else pd.DataFrame()
        ),
    }

    if not os.path.exists("resources"):
        os.makedirs("resources")

    day_format_rules = {
        "Trx Pct Change": "{:.2f}%",
        f"Total {variable['REQ_TRX']} Per Day": "{:,.0f}",
        f"Avg {variable['TPS_RPS']}": "{:.0f}",
        f"Max {variable['TPS_RPS']}": "{:.0f}",
        f"Max {variable['TPS_RPS']} (95th Percentile)": "{:.0f}",
    }
    month_format_rules = {
        f"Total {variable['REQ_TRX']} Per Month": "{:,.0f}",
    }

    if selected_type == "BNI Direct":
        day_format_rules[f"Nominal {variable['REQ_TRX']} Per Day"] = "{:,.0f}"
        month_format_rules[f"Nominal {variable['REQ_TRX']} Per Month"] = "{:,.0f}"

    if selected_type == "WONDR":
        summary = handle_data(
            df_obj,
            day_format_rules,
            variable,
            selected_type,
            is_wondr=True,
        )
    else:
        summary = handle_data(
            df_obj,
            day_format_rules,
            variable,
            selected_type,
            is_wondr=False,
        )

    styled_df_month = (
        df_param["this_month"]["data_pdf_month"]
        .style.format(month_format_rules)
        .hide(axis="index")
    )
    export_to_image(styled_df_month, f"./{RESOURCES_DIR}/data_month.png")

    pdf = PDF()

    write_pdf_content(
        pdf,
        selected_type,
        variable,
        summary,
    )

    if os.path.exists(f"{RESOURCES_DIR}"):
        shutil.rmtree(f"{RESOURCES_DIR}")

    buffer = BytesIO()
    buffer.write(pdf.output(dest="S"))
    buffer.seek(0)

    return buffer
