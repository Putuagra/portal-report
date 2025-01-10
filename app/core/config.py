from elasticsearch import Elasticsearch
import yaml
import json


# Function to load YAML config
def load_config_elk():
    with open("app/connection_config.yaml", "r") as file:
        elk_config = yaml.safe_load(file)
    return elk_config


elk_config = load_config_elk()


def index_source(selected_index):
    index_source = elk_config["elkhub"]["index-source"]
    source = index_source[selected_index]
    return source


def elasticsearch_client():
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

def load_queries(file_path="app/query/queries.json"):
    with open(file_path, "r") as file:
        return json.load(file)
    
def modify_query(query, query_size, start_timestamp, end_time, gt_type="gte"):
    query["size"] = query_size
    range_filter = query["query"]["bool"]["filter"][0]["range"]["@timestamp"]
    
    range_filter[gt_type] = start_timestamp
    range_filter["lt"] = end_time
    return query