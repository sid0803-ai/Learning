import os
import datetime
import html
from typing import List, Dict, Any

REPORT_DIR = "storage/results"

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>AI API Agent Report - {ts}</title>
  <style>
    body{{font-family:Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; padding:20px; background:#f7f9fb}}
    h1{{color:#111;}}
    table{{border-collapse:collapse; width:100%; margin-top:12px;}}
    th,td{{border:1px solid #ddd; padding:8px; text-align:left;}}
    th{{background:#0b5fff; color:#fff;}}
    tr.pass td{{background:#e6ffed}}
    tr.fail td{{background:#ffe6e6}}
    pre{{background:#fff; padding:8px; border:1px solid #eee; overflow:auto}}
    .meta{{margin-top:8px; color:#555}}
  </style>
</head>
<body>
  <h1>AI API Agent Report</h1>
  <div class="meta">Run Timestamp: {ts} &nbsp;|&nbsp; Agent: {agent_name}</div>
  <table>
    <thead>
      <tr>
        <th>#</th><th>Endpoint</th><th>Method</th><th>URL</th><th>Status</th><th>Result</th><th>Details</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>

  <h2>Summary</h2>
  <ul>
    <li>Total endpoints: {total}</li>
    <li>Passed: {passed}</li>
    <li>Failed: {failed}</li>
  </ul>

  <h2>Raw Data (JSON-ish)</h2>
  <pre>{raw}</pre>
</body>
</html>
"""

ROW_TEMPLATE = """
<tr class="{row_class}">
  <td>{idx}</td>
  <td>{name}</td>
  <td>{method}</td>
  <td><a href="{url}" target="_blank">{url_short}</a></td>
  <td>{status}</td>
  <td>{result}</td>
  <td><pre>{details}</pre></td>
</tr>
"""

def safe_str(x):
    try:
        return html.escape(str(x))
    except:
        return ""

def make_report(run_results: List[Dict[str, Any]], agent_name="APIAgent") -> str:
    os.makedirs(REPORT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    rows_html = ""
    passed = 0
    failed = 0
    for i, r in enumerate(run_results, start=1):
        ok = r.get("ok", False)
        row_class = "pass" if ok else "fail"
        if ok: passed += 1
        else: failed += 1

        details = {
            "request_body": r.get("request_body"),
            "response_status": r.get("response_status"),
            "response_body": r.get("response_body"),
            "validation_errors": r.get("validation_errors"),
            "chain_context": r.get("chain_context"),
            # placeholder for AI notes (commented integration)
            # "ai_notes": r.get("ai_notes")
        }

        rows_html += ROW_TEMPLATE.format(
            row_class=row_class,
            idx=i,
            name=safe_str(r.get("name")),
            method=safe_str(r.get("method")),
            url=safe_str(r.get("url")),
            url_short=safe_str((r.get("url")[:80] + "...") if len(r.get("url",""))>85 else r.get("url")),
            status=safe_str(r.get("response_status")),
            result="PASS" if ok else "FAIL",
            details=safe_str(details)
        )

    raw = html.escape(str(run_results))
    html_content = HTML_TEMPLATE.format(
        ts=ts,
        agent_name=agent_name,
        rows=rows_html,
        total=len(run_results),
        passed=passed,
        failed=failed,
        raw=raw
    )

    filename = os.path.join(REPORT_DIR, f"ai_api_report_{ts}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    return filename
