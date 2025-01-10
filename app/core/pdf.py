import time
from fpdf import FPDF
import os
import dataframe_image as dfi
import shutil
from core.presentation import generate_vertical_bar
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


def write_to_pdf(pdf, words):
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.set_font("Helvetica", "", 12)

    pdf.write(5, words)
    pdf.ln(10)


def color_negative_red(val):
    color = "red" if val < 0 else "green" if val > 0 else "black"
    return f"color: {color}"


def dataframe_to_pdf(df_per_day, df_per_month, summary, type):
    title = "Monthly Report"

    if not os.path.exists("resources"):
        os.makedirs("resources")

    styled_df_day = df_per_day.style.format()
    styled_df_month = df_per_month.style.format()

    day_format_rules = {
        "Trx Pct Change": "{:.2f}%",
        "Total Transaction Per Day": "{:,.0f}",
        "Avg TPS": "{:.0f}",
        "Max TPS (95th Percentile)": "{:.0f}",
    }
    month_format_rules = {
        "Total Transaction Per Month": "{:,.0f}",
    }

    if type == "BNI Direct":
        day_format_rules["Nominal Transaction Per Day"] = "{:,.0f}"
        month_format_rules["Nominal Transaction Per Month"] = "{:,.0f}"
    elif type == "Maverick":
        df_per_day = df_per_day.sort_values(by=["Type", "Transaction Date"])

    # Formatting table dataframe and add color
    styled_df_day = (
        df_per_day.style.format(day_format_rules)
        .bar(
            subset=["Total Transaction Per Day"]
            + (["Nominal Transaction Per Day"] if type == "BNI Direct" else []),
            color="lightgreen",
        )
        .map(color_negative_red, subset=["Trx Pct Change"]).hide(axis='index')
    )

    styled_df_month = df_per_month.style.format(month_format_rules).hide(axis='index')

    # Export dataframe to image
    dfi.export(styled_df_day, "resources/data.png", dpi=300)
    dfi.export(styled_df_month, "resources/data2.png", dpi=300)

    # Generate chart to image
    generate_vertical_bar(df_per_day, "resources/verticalBarMax.png", "Max TPS")
    generate_vertical_bar(
        df_per_day, "resources/verticalBarTotal.png", "Total Transaction Per Day"
    )

    pdf = PDF()
    # First Page
    pdf.add_page()
    create_title(title, pdf)
    write_to_pdf(
        pdf, f"1. The table below illustrates the monthly transactions of {type}:"
    )
    pdf.image("./resources/data.png", w=170)
    pdf.ln(10)

    # Second Page
    pdf.add_page()
    write_to_pdf(
        pdf, "2. The table below illustrates total amount monthly transactions:"
    )
    pdf.image("./resources/data2.png", w=170)
    pdf.ln(10)
    write_to_pdf(
        pdf, "3. The visualisations below shows Max TPS and Total Transaction per Day:"
    )
    pdf.image("./resources/verticalBarMax.png", h=75, w=199)
    pdf.ln(10)
    pdf.image("./resources/verticalBarTotal.png", h=75, w=199)
    pdf.ln(10)
    write_to_pdf(
        pdf,
        f"In conclusion, This month transactions show a total decrease in transactions by {summary['Negative Values Count']} and an increase in transactions by {summary['Positive Values Count']}. The lowest decrease was {summary['Minimum']:.2f}%, while the highest increase reached {summary['Maximum']:.2f}%. The highest transaction total occurred on {summary['Trx Date']}, with a value of {summary['Max Total Trx']}.",
    )

    if os.path.exists("resources"):
        shutil.rmtree("resources")

    buffer = BytesIO()
    pdf.output(dest="S").encode("latin1")
    buffer.write(pdf.output(dest="S").encode("latin1"))
    buffer.seek(0)

    return buffer
