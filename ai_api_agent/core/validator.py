import re

def validate_request(endpoint):
    body = endpoint.get("body", {})
    errors = []

    for rule in endpoint.get("business_rules", []):
        r = rule.lower()

        if "email" in r and "valid format" in r:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", body.get("email", "")):
                errors.append("Invalid email format")

        if "mobile" in r and "10 digits" in r:
            if not re.match(r"^\d{10}$", str(body.get("mobile", ""))):
                errors.append("Invalid mobile number")

        if "name" in r and "not be empty" in r:
            if not body.get("name"):
                errors.append("Name must not be empty")

    return errors


def validate_response(endpoint, response):
    errors = []
    rules = endpoint.get("business_rules", [])
    data = response.get("data", {})
    status = response.get("status")

    for rule in rules:
        r = rule.lower()

        if "status must be 200" in r and status != 200:
            errors.append(f"Expected status 200 but got {status}")

        if "response must include name" in r:
            if not isinstance(data, dict) or "name" not in data:
                errors.append("Missing 'name' in response")

        if "response must include email" in r:
            if not isinstance(data, dict) or "email" not in data:
                errors.append("Missing 'email' in response")

    return errors
