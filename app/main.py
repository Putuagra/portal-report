import streamlit as st
import calendar
from core.generate import generate_excel_file, generate_pdf_file
from datetime import datetime, timedelta, timezone
from util.enums import Months, Types


def get_dropdown_options():
    month_options = [month.value for month in Months]
    type_options = [type.value for type in Types]

    current_year = datetime.now().year
    year_options = list(range(2024, current_year + 1))
    return month_options, type_options, year_options


def get_time_range(selected_year: str, selected_month: str):
    month_number = list(Months).index(selected_month) + 1
    days_in_month = calendar.monthrange(selected_year, month_number)[1]
    wib_zone = timezone(timedelta(hours=7))
    start_time = datetime(
        selected_year, month_number, 1, 0, 0, 0, tzinfo=wib_zone
    ).isoformat()
    end_time = datetime(
        selected_year, month_number, days_in_month, 23, 59, 59, tzinfo=wib_zone
    ).isoformat()

    return start_time, end_time


def main():
    # Configure the main page
    
    st.set_page_config(
        page_title="Self-Service Portal",
        page_icon="📊",
        layout="wide",
    )

    # Set title
    st.title("Client Self-Service Portal")

    month_options, type_options, year_options = get_dropdown_options()
    selected_month = st.selectbox("Select a month", month_options)
    selected_year = st.selectbox("Select a year", year_options)
    selected_type = st.selectbox("Select a type", type_options)

    selected_month_enum = Months(selected_month)

    # Get time range
    start_time, end_time = get_time_range(selected_year, selected_month_enum)

    st.subheader("Instructions:")

    # Set text
    st.write(
        "Welcome to the self-service portal! Use the dropdown menus below to select a month and year, and then click the button to generate a PDF file or Excel file."
    )

    generate_excel_file(
        start_time, end_time, selected_type, selected_month, selected_year
    )
    generate_pdf_file(
        start_time, end_time, selected_type, selected_month, selected_year
    )


if __name__ == "__main__":
    main()
