import json
from core.api_handler import call_api
from core.validator import validate_business_rules
from config.settings import API_KEY
from core.reporter import make_report
import traceback

class APIAgent:
    def __init__(self, endpoints_file):
        with open(endpoints_file, "r") as f:
            self.endpoints = json.load(f)
        self.context = {}  # for chaining IDs
        self.run_results = []

    def run(self):
        for ep in self.endpoints:
            print(f"\n🔍 Running {ep['name']}")
            try:
                url = ep["url"].format(**self.context)
            except Exception:
                # if formatting fails because placeholder missing, keep raw url
                url = ep["url"]

            headers = ep.get("headers", {}).copy()
            # ensure x-api-key from config is always present
            headers["x-api-key"] = API_KEY

            body = ep.get("body", None)
            resp = call_api(ep["method"], url, headers, body)

            # normalize response for reporting and validation
            response_status = None
            response_body = None
            try:
                response_status = resp.status_code
                response_body = resp.json()
            except Exception:
                # if resp is an error dict (from call_api) or text
                if isinstance(resp, dict) and resp.get("error"):
                    response_body = {"error": resp.get("error")}
                else:
                    try:
                        response_body = resp.text
                        response_status = resp.status_code if hasattr(resp, "status_code") else None
                    except:
                        response_body = str(resp)

            # Validate business rules
            validation_errors = validate_business_rules(body or {}, resp, ep.get("business_rules", []))

            ok = (len(validation_errors) == 0) and (response_status == 200 or response_status is None and not isinstance(response_body, dict) or response_status == 200)

            # Extract ID for chaining (safe)
            chain_context = {}
            if "extract_id" in ep:
                try:
                    if isinstance(response_body, dict) and response_body.get(ep["extract_id"]) is not None:
                        self.context[ep["extract_id"]] = response_body.get(ep["extract_id"])
                        chain_context = {ep["extract_id"]: self.context[ep["extract_id"]]}
                        print(f"🔗 Extracted {ep['extract_id']} → {self.context[ep['extract_id']]}")
                    else:
                        print(f"⚠ No {ep['extract_id']} found in response")
                except Exception as e:
                    print("⚠ Error extracting id:", e)

            # Save run result
            self.run_results.append({
                "name": ep.get("name"),
                "method": ep.get("method"),
                "url": url,
                "request_body": body,
                "response_status": response_status,
                "response_body": response_body,
                "validation_errors": validation_errors,
                "chain_context": chain_context,
                "ok": ok
                # "ai_notes": None  # placeholder for future AI analysis
            })

            # Handle chain_to immediately if defined
            if "chain_to" in ep:
                # find endpoint by name and run it right away using updated context
                next_ep = next((x for x in self.endpoints if x.get("name") == ep["chain_to"]), None)
                if next_ep:
                    print(f"🔁 Running chained endpoint: {next_ep['name']}")
                    # simple immediate call: format url with context and call
                    try:
                        next_url = next_ep["url"].format(**self.context)
                    except Exception:
                        next_url = next_ep["url"]
                    n_headers = next_ep.get("headers", {}).copy()
                    n_headers["x-api-key"] = API_KEY
                    n_resp = call_api(next_ep["method"], next_url, n_headers, next_ep.get("body"))
                    # extract and validate similarly (quick)
                    try:
                        n_status = n_resp.status_code
                        n_body = n_resp.json()
                    except:
                        n_status = getattr(n_resp, "status_code", None)
                        n_body = n_resp.text if hasattr(n_resp, "text") else str(n_resp)
                    n_validation_errors = validate_business_rules(next_ep.get("body", {}) or {}, n_resp, next_ep.get("business_rules", []))
                    n_ok = (len(n_validation_errors) == 0 and n_status == 200)
                    self.run_results.append({
                        "name": next_ep.get("name"),
                        "method": next_ep.get("method"),
                        "url": next_url,
                        "request_body": next_ep.get("body"),
                        "response_status": n_status,
                        "response_body": n_body,
                        "validation_errors": n_validation_errors,
                        "chain_context": {},
                        "ok": n_ok
                    })

        # After run, write HTML report
        try:
            report_path = make_report(self.run_results, agent_name="APIAgent")
            print(f"\n📄 HTML report generated: {report_path}")
        except Exception as e:
            print("❌ Failed to generate report:", e, traceback.format_exc())
