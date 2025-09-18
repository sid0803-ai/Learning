import requests, json, time
from openai import OpenAI

client = OpenAI()

def run_api_tests(file_path="endpoints.json"):
    with open(file_path) as f:
        endpoints = json.load(f)

    context = {}  # store extracted values
    results = []

    for ep in endpoints:
        method = ep.get("method", "GET").upper()
        url = ep["url"]
        body = ep.get("body", {})
        headers = ep.get("headers", {"Content-Type": "application/json"})

        # If this API depends on another, replace placeholder
        if ep.get("depends_on"):
            dep_name = ep["depends_on"]
            if dep_name in context:
                key = ep["replace_in_url"]
                val = context[dep_name]
                url = url.replace(key, str(val))

        start = time.time()
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                resp = requests.post(url, json=body, headers=headers, timeout=10)
            else:
                resp = requests.request(method, url, json=body, headers=headers, timeout=10)

            elapsed = round(time.time() - start, 2)
            data = {}
            try:
                data = resp.json()
            except:
                pass

            # Extract ID if defined
            if ep.get("extract") and data.get(ep["extract"]):
                context[ep["name"]] = data[ep["extract"]]

            results.append({
                "name": ep["name"],
                "url": url,
                "status": resp.status_code,
                "time": elapsed,
                "success": 200 <= resp.status_code < 300,
                "response": data
            })
        except Exception as e:
            results.append({
                "name": ep["name"],
                "url": url,
                "status": "ERROR",
                "time": None,
                "success": False,
                "error": str(e)
            })

    return results

if __name__ == "__main__":
    results = run_api_tests()
    for r in results:
        print(f"{'✅' if r['success'] else '❌'} {r['name']} → {r['status']} in {r['time']}s")
