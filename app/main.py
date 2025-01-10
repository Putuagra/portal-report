import streamlit as st
import calendar
import glob
import os
from core.excel import run_excel_test
from core.data import main, create_lock_file, remove_lock_file
from core.pdf import dataframe_to_pdf
from core.loading import loading_animation
from datetime import datetime, timedelta, timezone


# Configure the main page
st.set_page_config(
    page_title="Self-Service Portal",
    page_icon="📊",
    layout="wide",
)

# Set title
st.title("Client Self-Service Portal")

months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

types = ["BNI Direct", "Maverick"]

current_year = datetime.now().year
years = list(range(2024, current_year + 1))

selected_month = st.selectbox("Select a month", months)
selected_years = st.selectbox("Select a year", years)
selected_types = st.selectbox("Select a type", types)
month_number = months.index(selected_month) + 1
days_in_month = calendar.monthrange(current_year, month_number)[1]

subheader = st.subheader("Instructions:")

# Set text
st.write(
    "Welcome to the self-service portal! Use the dropdown menus below to select a month and year, and then click the button to generate a PDF file or Excel file."
)

wib_zone = timezone(timedelta(hours=7))
start_time = datetime(
    selected_years, month_number, 1, 0, 0, 0, tzinfo=wib_zone
).isoformat()
end_time = datetime(
    selected_years, month_number, days_in_month, 23, 59, 59, tzinfo=wib_zone
).isoformat()

placeholder = st.empty()



if st.button("Generate Excel"):
    if os.path.exists("generate_excel.lock"):
        st.write("Excel generate is in progress. Please wait until it completes.")
    else:
        try:
            create_lock_file("generate_excel.lock")
            loading_animation(placeholder, 0)
            data_df = main(start_time, end_time, selected_types)
            loading_animation(placeholder, 80)
            if data_df:
                buffer = run_excel_test(data_df)
                loading_animation(placeholder, 90)
                st.download_button(
                    label="Download Excel",
                    data=buffer,
                    file_name=f"Report-{selected_month}-{selected_years}-{selected_types}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            else:
                st.warning("Data is empty")
            loading_animation(placeholder, 100)
        except Exception as e:
            print(e)
            lock_files = glob.glob("*.lock")
            for lock_file in lock_files:
                os.remove(lock_file)
        finally:
            remove_lock_file("generate_excel.lock")
            placeholder.empty()


if st.button("Generate PDF"):
    if os.path.exists("generate_pdf.lock"):
        st.write("PDF generate is in progress. Please wait until it completes.")
    else:
        try:
            create_lock_file("generate_pdf.lock")
            loading_animation(placeholder, 0)
            data_df = main(start_time, end_time, selected_types)
            loading_animation(placeholder, 80)
            if data_df:
                buffer = dataframe_to_pdf(
                    data_df["data_pdf_day"],
                    data_df["data_pdf_month"],
                    data_df["summary"],
                    selected_types,
                )
                loading_animation(placeholder, 90)
                st.download_button(
                    label="Download PDF",
                    data=buffer,
                    file_name=f"Report-{selected_month}-{selected_years}-{selected_types}.pdf",
                    mime="application/pdf",
                )
            else:
                st.warning("Data is empty")
            loading_animation(placeholder, 100)
        except Exception as e:
            print(e)
            lock_files = glob.glob("*.lock")
            for lock_file in lock_files:
                os.remove(lock_file)
        finally:
            remove_lock_file("generate_pdf.lock")
            placeholder.empty()

# # insert image
# st.image("assets/picture.jpg")
