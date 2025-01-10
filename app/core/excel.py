import pandas as pd
from io import BytesIO


def run_excel_test(data: pd.DataFrame) -> pd.DataFrame:
    filtered_data_day = data["data_pdf_day"]
    filtered_data_month = data["data_pdf_month"]
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        filtered_data_day.to_excel(writer, index=False, sheet_name="Day")
        filtered_data_month.to_excel(writer, index=False, sheet_name="Month")
    output.seek(0)

    return output
