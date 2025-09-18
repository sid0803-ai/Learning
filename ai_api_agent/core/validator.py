import re

def validate_business_rules(request_body, response, business_rules):
    """Validate rules on request + response."""

    errors = []
    status_code = getattr(response, "status_code", None)

    for rule in business_rules:
        if "email must be in valid format" in rule:
            email = request_body.get("email", "")
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                errors.append("Invalid email format")

        if "mobile must be exactly 10 digits" in rule:
            mobile = request_body.get("mobile", "")
            if not (mobile.isdigit() and len(mobile) == 10):
                errors.append("Invalid mobile length")

        if "name must not be empty" in rule:
            if not request_body.get("name"):
                errors.append("Name is empty")

        if "status must be 200" in rule:
            if status_code != 200:
                errors.append(f"Expected 200, got {status_code}")

        if "response must include" in rule:
            key = rule.split("include")[-1].strip()
            try:
                if key not in response.json():
                    errors.append(f"Response missing: {key}")
            except:
                errors.append("Response not JSON")

    return errors
