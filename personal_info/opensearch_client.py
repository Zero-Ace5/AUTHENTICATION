from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "OmniMan@129"),
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
)
