import requests

def call_api(endpoint, context=None):
    method = endpoint["method"].upper()
    url = endpoint["url"]
    headers = endpoint.get("headers", {})
    body = endpoint.get("body", {})

    # Inject context variables (e.g. replace {lead_id})
    if context:
        for key, val in context.items():
            url = url.replace("{" + key + "}", str(val))

    try:
        if method == "POST":
            res = requests.post(url, json=body, headers=headers, timeout=10)
        elif method == "GET":
            res = requests.get(url, headers=headers, timeout=10)
        else:
            return {"status": "error", "message": f"Unsupported method {method}"}

        json_data = res.json() if res.content else {}
        context_out = {}

        if "extract_id" in endpoint and isinstance(json_data, dict):
            if endpoint["extract_id"] in json_data:
                context_out[endpoint["extract_id"]] = json_data[endpoint["extract_id"]]

        return {"status": res.status_code, "data": json_data, "context": context_out}

    except Exception as e:
        return {"status": "error", "message": str(e)}
