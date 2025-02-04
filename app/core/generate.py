import streamlit as st
import os
import glob
from core.loading import loading_animation
from core.excel import run_excel_test
from core.data import main, create_lock_file, remove_lock_file
from core.pdf import dataframe_to_pdf

excel_file_lock = "generate_excel.lock"
pdf_file_lock = "generate_pdf.lock"


def clear_lock_files():
    lock_files = glob.glob("*.lock")
    for lock_file in lock_files:
        os.remove(lock_file)


def handle_excel_generate(
    start_time: str,
    end_time: str,
    selected_type: str,
    selected_month: str,
    selected_year: int,
    placeholder,
):
    try:
        create_lock_file(excel_file_lock)
        loading_animation(placeholder, 0)

        data_df = main(start_time, end_time, selected_type)
        loading_animation(placeholder, 80)

        if not data_df:
            st.warning("Data is empty")
            return

        buffer = run_excel_test(data_df)
        loading_animation(placeholder, 90)

        st.download_button(
            label="Download Excel",
            data=buffer,
            file_name=f"Report-{selected_month}-{selected_year}-{selected_type}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        loading_animation(placeholder, 100)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        print(f"Error: {e}")
        clear_lock_files()
    finally:
        remove_lock_file(excel_file_lock)
        placeholder.empty()


def generate_excel_file(
    start_time: str,
    end_time: str,
    selected_type: str,
    selected_month: str,
    selected_year: int,
):
    placeholder = st.empty()

    if st.button("Generate Excel"):
        if os.path.exists(excel_file_lock):
            st.write("Excel generate is in progress. Please wait until it completes.")
        else:
            handle_excel_generate(
                start_time,
                end_time,
                selected_type,
                selected_month,
                selected_year,
                placeholder,
            )


def handle_pdf_generate(
    start_time: str,
    end_time: str,
    selected_type: str,
    selected_month: str,
    selected_year: int,
    placeholder,
):
    try:
        create_lock_file(pdf_file_lock)
        loading_animation(placeholder, 0)

        data_df = main(start_time, end_time, selected_type)
        loading_animation(placeholder, 80)

        if not data_df:
            st.warning("Data is empty")
            return

        buffer = dataframe_to_pdf(
            data_df["data_pdf_day"],
            data_df["data_pdf_month"],
            selected_type,
        )

        loading_animation(placeholder, 100)
        st.download_button(
            label="Download PDF",
            data=buffer,
            file_name=f"Report-{selected_month}-{selected_year}-{selected_type}.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        clear_lock_files()
        st.error(f"An error occurred: {e}")
    finally:
        remove_lock_file(pdf_file_lock)
        placeholder.empty()


def generate_pdf_file(
    start_time: str,
    end_time: str,
    selected_type: str,
    selected_month: str,
    selected_year: int,
):
    placeholder = st.empty()

    if st.button("Generate PDF"):
        if os.path.exists(pdf_file_lock):
            st.write("PDF generate is in progress. Please wait until it completes.")
        else:
            handle_pdf_generate(
                start_time,
                end_time,
                selected_type,
                selected_month,
                selected_year,
                placeholder,
            )
