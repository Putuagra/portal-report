import time
from fpdf import FPDF
import os
import dataframe_image as dfi
import shutil
from core.presentation import generate_vertical_bar
from core.data import check_type
from io import BytesIO


class PDF(FPDF):

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


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


def style_dataframe(df, format_rules):
    return (
        df.style.format(format_rules)
        .map(color_negative_red, subset=["Trx Pct Change"])
        .hide(axis="index")
    )


def export_to_image(styled_df, file_path):
    dfi.export(styled_df, file_path, dpi=300, table_conversion="matplotlib")


def generate_charts(df, max_tps_path, total_path, label_tps_rps, label_req_trx, type):
    generate_vertical_bar(df, max_tps_path, f"Max {label_tps_rps}", type)
    generate_vertical_bar(df, total_path, f"Total {label_req_trx} Per Day", type)


def handle_maverick(df_per_day, day_format_rules, label_tps_rps, label_req_trx, type):
    df_type_ext = df_per_day[df_per_day["Type"] == "external"]
    df_type_in = df_per_day[df_per_day["Type"] == "internal"]

    summary_ext = calculate_summary(df_type_ext, label_req_trx)
    summary_in = calculate_summary(df_type_in, label_req_trx)

    styled_df_ext = style_dataframe(df_type_ext, day_format_rules)
    styled_df_in = style_dataframe(df_type_in, day_format_rules)

    export_to_image(styled_df_ext, "resources/data_ex.png")
    export_to_image(styled_df_in, "resources/data_in.png")

    generate_charts(
        df_type_ext,
        "resources/verticalBarMaxEx.png",
        "resources/verticalBarTotalEx.png",
        label_tps_rps,
        label_req_trx,
        type,
    )
    generate_charts(
        df_type_in,
        "resources/verticalBarMaxIn.png",
        "resources/verticalBarTotalIn.png",
        label_tps_rps,
        label_req_trx,
        type,
    )
    return {
        "summary_ext": summary_ext,
        "summary_in": summary_in,
    }


def handle_non_maverick(df_per_day, day_format_rules, label_tps_rps, label_req_trx, type):
    styled_df_day = style_dataframe(df_per_day, day_format_rules)
    export_to_image(styled_df_day, "resources/data.png")
    generate_charts(
        df_per_day,
        "resources/verticalBarMax.png",
        "resources/verticalBarTotal.png",
        label_tps_rps,
        label_req_trx,
        type,
    )
    summary = calculate_summary(df_per_day, label_req_trx)
    return {"summary": summary}


def write_pdf_content(pdf, type, req_or_trx, REQ_or_TRX, TPS_or_RPS, summary):
    if type != "Maverick":
        write_to_pdf(
            pdf, f"1. The table below illustrates the monthly {REQ_or_TRX}s of {type}:"
        )
        pdf.image("./resources/data.png", w=170)
    else:
        write_to_pdf(
            pdf,
            f"1a. The table below illustrates the monthly {REQ_or_TRX}s of {type} external:",
        )
        pdf.image("./resources/data_ex.png", w=170)
        pdf.add_page()
        write_to_pdf(
            pdf,
            f"1b. The table below illustrates the monthly {REQ_or_TRX}s of {type} internal:",
        )
        pdf.image("./resources/data_in.png", w=170)

    pdf.add_page()
    write_to_pdf(
        pdf, f"2. The table below illustrates total amount monthly {REQ_or_TRX}s:"
    )
    pdf.image("./resources/data2.png", w=170)
    pdf.ln(10)

    if type != "Maverick":
        write_to_pdf(
            pdf,
            f"3. The visualisations below shows Max {TPS_or_RPS} and Total {REQ_or_TRX} per Day:",
        )
        pdf.image("./resources/verticalBarMax.png", h=75, w=199)
        pdf.ln(10)
        pdf.image("./resources/verticalBarTotal.png", h=75, w=199)
        pdf.ln(10)
        write_to_pdf(
            pdf,
            f"In conclusion, This month {req_or_trx}s show a total decrease in {req_or_trx}s by {summary['summary']['Negative Values Count']} and increase in {req_or_trx}s by {summary['summary']['Positive Values Count']}. The lowest decrease was {summary['summary']['Minimum']:.2f}%, while the highest increase reached {summary['summary']['Maximum']:.2f}%. The highest {req_or_trx} total occurred on {summary['summary']['Trx Date']}, with a value of {summary['summary']['Max Total Trx']} .",
        )
    else:
        write_to_pdf(
            pdf,
            f"3a. The visualisations below shows Max {TPS_or_RPS} and Total {REQ_or_TRX} external per Day:",
        )
        pdf.image("./resources/verticalBarMaxEx.png", h=75, w=199)
        pdf.ln(10)
        pdf.image("./resources/verticalBarTotalEx.png", h=75, w=199)
        pdf.add_page()
        write_to_pdf(
            pdf,
            f"3b. The visualisations below shows Max {TPS_or_RPS} and Total {REQ_or_TRX} internal per Day:",
        )
        pdf.image("./resources/verticalBarMaxIn.png", h=75, w=199)
        pdf.ln(10)
        pdf.image("./resources/verticalBarTotalIn.png", h=75, w=199)  
        pdf.ln(10)
        write_to_pdf(
            pdf,
            f"In conclusion, This month {req_or_trx}s show a total decrease in {req_or_trx}s by {summary['summary_ext']['Negative Values Count']} and increase in {req_or_trx}s by {summary['summary_ext']['Positive Values Count']} for external, and show a total decrease in {req_or_trx}s by {summary['summary_in']['Negative Values Count']} and increase in {req_or_trx}s by {summary['summary_in']['Positive Values Count']} for internal. The lowest decrease was {summary['summary_ext']['Minimum']:.2f}%, while the highest increase reached {summary['summary_ext']['Maximum']:.2f}%. The highest {req_or_trx} total occurred on {summary['summary_ext']['Trx Date']} with a value of {summary['summary_ext']['Max Total Trx']} for external, and the highest {req_or_trx} total occurred on {summary['summary_in']['Trx Date']} with a value of {summary['summary_in']['Max Total Trx']} for internal.",
        )


def calculate_summary(df, REQ_or_TRX):
    # Count for summary
    max_row_trx = df.loc[df[f"Total {REQ_or_TRX} Per Day"].idxmax()]
    return {
        "Minimum": df["Trx Pct Change"].min(),
        "Maximum": df["Trx Pct Change"].max(),
        "Negative Values Count": (df["Trx Pct Change"] < 0).sum(),
        "Positive Values Count": (df["Trx Pct Change"] > 0).sum(),
        "Max Total Trx": "{:,.0f}".format(max_row_trx[f"Total {REQ_or_TRX} Per Day"]).replace(",", "."),
        "Trx Date": max_row_trx[f"{REQ_or_TRX} Date"],
    }


def dataframe_to_pdf(df_per_day, df_per_month, type):
    # TPS_or_RPS, req_or_trx, REQ_or_TRX = check_type(type)
    variable = check_type(type)

    title = "Monthly Report"

    if not os.path.exists("resources"):
        os.makedirs("resources")

    styled_df_month = df_per_month.style.format()

    day_format_rules = {
        "Trx Pct Change": "{:.2f}%",
        f"Total {variable["REQ_TRX"]} Per Day": "{:,.0f}",
        f"Avg {variable["TPS_RPS"]}": "{:.0f}",
        f"Max {variable["TPS_RPS"]}": "{:.0f}",
        f"Max {variable["TPS_RPS"]} (95th Percentile)": "{:.0f}",
    }
    month_format_rules = {
        f"Total {variable["REQ_TRX"]} Per Month": "{:,.0f}",
    }

    if type == "BNI Direct":
        day_format_rules[f"Nominal {variable["REQ_TRX"]} Per Day"] = "{:,.0f}"
        month_format_rules[f"Nominal {variable["REQ_TRX"]} Per Month"] = "{:,.0f}"

    if type == "Maverick":
        summary = handle_maverick(
            df_per_day, day_format_rules, variable["TPS_RPS"], variable["REQ_TRX"], type
        )
    else:
        summary = handle_non_maverick(
            df_per_day, day_format_rules, variable["TPS_RPS"], variable["REQ_TRX"], type
        )

    styled_df_month = df_per_month.style.format(month_format_rules).hide(axis="index")
    dfi.export(
        styled_df_month, "resources/data2.png", dpi=300, table_conversion="matplotlib"
    )

    pdf = PDF()
    # First Page
    pdf.add_page()
    create_title(title, pdf)
    write_pdf_content(
        pdf,
        type,
        variable["req_trx"],
        variable["REQ_TRX"],
        variable["TPS_RPS"],
        summary,
    )

    if os.path.exists("resources"):
        shutil.rmtree("resources")

    buffer = BytesIO()
    pdf.output(dest="S").encode("latin1")
    buffer.write(pdf.output(dest="S").encode("latin1"))
    buffer.seek(0)

    return buffer
