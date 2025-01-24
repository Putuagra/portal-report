import pandas as pd
import glob
import sys
import os
from datetime import timedelta, timezone
from core.config import (
    elasticsearch_client,
    index_source,
    load_queries,
    modify_query,
    load_fields,
)


# def check_type(type):
#     if type in ["QRIS"]:
#         return ("RPS", "request", "Request")
#     else:
#         return ("TPS", "transaction", "Transaction")

def check_type(type):
    if type in ["QRIS"]:
        # return ("RPS", "request", "Request")
        return {"TPS_RPS": "RPS", "req_trx": "request", "REQ_TRX": "Request"}
    else:
        # return ("TPS", "transaction", "Transaction")
        return {"TPS_RPS": "TPS", "req_trx": "transaction", "REQ_TRX": "Transaction"}


def calculate_tps(df_clear, selected_types):
    day_group = (
        ["TRX_DATE"]
        if selected_types in ["BNI Direct", "BIFAST", "QRIS"]
        else ["TRX_DATE", "type"]
    )
    month_group = (
        ["per_month"]
        if selected_types in ["BNI Direct", "BIFAST", "QRIS"]
        else ["per_month", "type"]
    )

    fields = load_fields()
    base_fields = fields.get(selected_types)

    # Define aggregation logic for per-day calculations
    day_aggregations = {
        "max_tps": (base_fields["max"], "max"),
        "avg_tps": (base_fields["avg"], "mean"),
        "total_transaction_per_day": (base_fields["total"], "sum"),
        "max_percentile_95": (base_fields["max"], lambda x: x.quantile(0.95)),
    }

    if selected_types == "BNI Direct":
        day_aggregations["nominal_transaction_per_day"] = (
            base_fields["total_debit"],
            "sum",
        )

    day_aggregations = dict(sorted(day_aggregations.items()))
    tps_per_day = df_clear.groupby(day_group).agg(**day_aggregations).reset_index()

    month_aggregations = {
        "total_transaction_per_month": (base_fields["total"], "sum"),
    }
    if selected_types == "BNI Direct":
        month_aggregations["nominal_transaction_per_month"] = (
            base_fields["total_debit"],
            "sum",
        )

    # Calculate total and nominal transaction per month
    tps_per_month = (
        df_clear.groupby(month_group).agg(**month_aggregations).reset_index()
    )

    # Calculate transaction percent change
    if selected_types in ["BNI Direct", "BIFAST", "QRIS"]:
        tps_per_day["transaction_percent_change"] = (
            tps_per_day["total_transaction_per_day"].pct_change() * 100
        ).fillna(0)
    else:
        tps_per_day["transaction_percent_change"] = (
            tps_per_day.groupby("type")["total_transaction_per_day"].pct_change() * 100
        ).fillna(0)

    return tps_per_day, tps_per_month


def summary_tps(df_clear, selected_types):
    if df_clear is not None and not df_clear.empty:
        tps_per_day, tps_per_month = calculate_tps(df_clear, selected_types)
        # TPS_or_RPS, req_or_trx, REQ_or_TRX = check_type(selected_types)
        variable = check_type(selected_types)

        # tps_per_day["doc_id"] = tps_per_day["TRX_DATE"] + "_" + selected_types
        tps_per_day.rename(columns={"TRX_DATE": "@timestamp"}, inplace=True)
        tps_per_day["@timestamp"] = pd.to_datetime(
            tps_per_day["@timestamp"], format="%Y%m%d"
        )

        tps_per_day = tps_per_day.sort_values(by="@timestamp")
        tps_per_day["@timestamp"] = tps_per_day["@timestamp"].dt.strftime("%Y-%m-%d")

        rename_tps_per_day = {
            "@timestamp": f"{variable["REQ_TRX"]} Date",
            "max_tps": f"Max {variable["TPS_RPS"]}",
            "avg_tps": f"Avg {variable["TPS_RPS"]}",
            "max_percentile_95": f"Max {variable["TPS_RPS"]} (95th Percentile)",
            "total_transaction_per_day": f"Total {variable["REQ_TRX"]} Per Day",
            "transaction_percent_change": "Trx Pct Change",
        }

        rename_tps_per_month = {
            "total_transaction_per_month": f"Total {variable["REQ_TRX"]} Per Month",
            "per_month": "Month",
        }

        tps_per_day = tps_per_day.rename(columns=rename_tps_per_day)
        tps_per_month = tps_per_month.rename(columns=rename_tps_per_month)

        if selected_types == "BNI Direct":
            tps_per_day["nominal_transaction_per_day"] = tps_per_day[
                "nominal_transaction_per_day"
            ].apply(lambda x: int(x))
            tps_per_day = tps_per_day.rename(
                columns={
                    "nominal_transaction_per_day": f"Nominal {variable["REQ_TRX"]} Per Day"
                }
            )

            tps_per_month["nominal_transaction_per_month"] = tps_per_month[
                "nominal_transaction_per_month"
            ].apply(lambda x: int(x))
            tps_per_month = tps_per_month.rename(
                columns={
                    "nominal_transaction_per_month": f"Nominal {variable["REQ_TRX"]} Per Month"
                }
            )
        elif selected_types == "Maverick":
            tps_per_day = tps_per_day.rename(columns={"type": "Type"})
            tps_per_month = tps_per_month.rename(columns={"type": "Type"})

        tps_per_day.index = tps_per_day.index + 1
        tps_per_month.index = tps_per_month.index + 1

        return {
            "data_pdf_day": tps_per_day,
            "data_pdf_month": tps_per_month,
        }
    else:
        return None


def process_and_save_dataframe(all_results, selected_types):
    try:
        create_lock_file("process_and_save_dataframe")
        if all_results:

            df = pd.DataFrame(all_results)

            df["@timestamp"] = pd.to_datetime(df["@timestamp"]).dt.tz_convert("UTC")
            wib_zone = timezone(timedelta(hours=7))
            df["TRX_DATE"] = (
                df["@timestamp"].dt.tz_convert(wib_zone).dt.strftime("%Y%m%d")
            )
            df["per_month"] = df["TRX_DATE"].str[:6].apply(lambda x: f"{x[:4]}-{x[4:]}")

            # df.to_csv("dataframe.csv")

            tps = summary_tps(df, selected_types)
            return tps
        else:
            return None
    except Exception as e:
        print(e)
        lock_files = glob.glob("*.lock")
        for lock_file in lock_files:
            os.remove(lock_file)
    finally:
        remove_lock_file("process_and_save_dataframe")


def create_lock_file(lock_file_path):
    """Create a lock file to prevent multiple instances."""
    if os.path.exists(lock_file_path):
        sys.exit(1)
    else:
        with open(lock_file_path, "w") as lock_file:
            lock_file.write(str(os.getpid()))  # Store the process ID in the lock file


def remove_lock_file(lock_file_path):
    """Remove the lock file."""
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)


def main(start_time, end_time, selected_types):
    query_size = 10000
    rows_list = []
    queries = load_queries()
    base_query = queries.get(selected_types)

    query = modify_query(base_query, query_size, start_time, end_time)

    try:
        # Initial search request
        client = elasticsearch_client()
        index_source_elastic = index_source(selected_types)
        page = client.search(index=index_source_elastic, body=query)

        hits = page["hits"]["hits"]

        rows_list = [
            {
                "_id": hit["_id"],
                **{field: hit["_source"].get(field) for field in hit["_source"]},
            }
            for hit in hits
        ]

        if len(rows_list) >= query_size:

            while hits:
                # query = custom_query(rows_list[-1]["@timestamp"], gt_type="gt")
                query = modify_query(
                    base_query,
                    query_size,
                    rows_list[-1]["@timestamp"],
                    end_time,
                    gt_type="gt",
                )

                response = client.search(index=index_source_elastic, body=query)
                hits = response["hits"]["hits"]
                if not hits:
                    print("not hits")
                    break

                rows_list.extend(
                    {
                        "_id": hit["_id"],
                        **{
                            field: hit["_source"].get(field) for field in hit["_source"]
                        },
                    }
                    for hit in hits
                )

    except Exception as e:
        print(f"Error during initial search: {e}")

    if len(rows_list) > 0:
        dataframe = process_and_save_dataframe(rows_list, selected_types)
        return dataframe
    else:
        return None
