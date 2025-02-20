import pandas as pd
from io import BytesIO


def run_excel_test(data: pd.DataFrame) -> pd.DataFrame:
    filtered_data_day = data["data_pdf_day"]
    filtered_data_month = data["data_pdf_month"]
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        filtered_data_day.to_excel(writer, index=False, sheet_name="Day")
        filtered_data_month.to_excel(writer, index=False, sheet_name="Month")
        
        workbook = writer.book
        worksheet = writer.sheets["Day"]
        
        format_positive = workbook.add_format({"font_color": "#006100"})
        format_negative = workbook.add_format({"font_color": "#9C0006"})
        
        trx_col = pct_col = None
        for col_idx, col_name in enumerate(filtered_data_day.columns):
            col_name_lower = col_name.lower()
            if "total" in col_name_lower:
                trx_col = col_idx
            elif "pct" in col_name_lower:
                pct_col = col_idx
            elif "type" in col_name_lower:
                max_row, max_col = filtered_data_day.shape
                worksheet.autofilter(0, 0, max_row, 1)
            if trx_col is not None and pct_col is not None:
                break
        
        worksheet.conditional_format(
            2,
            trx_col,
            len(filtered_data_day),
            trx_col,
            {
                "type": "data_bar",
                "bar_color": "#00FF00",
                'bar_solid': True
            }
        )
        worksheet.conditional_format(
            2,
            pct_col,
            len(filtered_data_day),
            pct_col,
            {
                "type": "cell",
                "criteria": ">",
                "value": 0,
                "format": format_positive,
            }
        )
        worksheet.conditional_format(
            2,
            pct_col,
            len(filtered_data_day),
            pct_col,
            {
                "type": "cell",
                "criteria": "<",
                "value": 0,
                "format": format_negative,
            }
        )
    output.seek(0)

    return output
