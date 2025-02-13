from elasticsearch import Elasticsearch
import yaml
import json
from typing import Any


# Function to load YAML config
# Change with your path and name file .yaml
def load_config_elk():
    try:
        with open("app/connection_config.yaml", "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise Exception(f"Failed to load config file: {e}")


elk_config = load_config_elk()


def index_source(selected_index: str):
    index_source = elk_config["elkhub"]["index-source"]
    if selected_index not in index_source:
        raise ValueError(
            f"Selected index '{selected_index}' not found in configuration."
        )
    return index_source[selected_index]


def elasticsearch_client():
    try:
        es = Elasticsearch(
            [elk_config["elkhub"]["url"]],
            verify_certs=False,
            ssl_show_warn=False,
            request_timeout=30,  # Request timeout (seconds)
            max_retries=10,  # Number of retries for failed requests
            retry_on_timeout=True,  # Retry on timeout error
            http_compress=True,
        )
        return es
    except Exception as e:
        raise Exception(f"Failed to create Elasticsearch client: {e}")


def load_json(file_path="app/query/queries.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        raise Exception(f"Failed to load JSON file: {e}")


def modify_query(
    query,
    query_size,
    start_timestamp: dict[Any, Any],
    end_time: dict[str, str],
    gt_type="gte",
):
    query["size"] = query_size
    range_filter = query["query"]["bool"]["filter"][0]["range"]["@timestamp"]

    range_filter.pop("gt", None)

    range_filter[gt_type] = start_timestamp
    range_filter["lt"] = end_time
    return query
