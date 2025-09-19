import os
from datetime import datetime

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>AI API Agent Report - {ts}</title>
  <style>
    body {{
      font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
      padding: 20px;
      background: #f7f9fb;
      color: #222;
    }}
    h1 {{ color: #111; margin-bottom: 0; }}
    .meta {{ margin-top: 4px; color: #555; font-size: 14px; }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin-top: 20px;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }}
    th, td {{
      border: 1px solid #eee;
      padding: 10px;
      text-align: left;
      font-size: 14px;
    }}
    th {{
      background: #0b5fff;
      color: #fff;
    }}
    tr.pass td {{ background: #e6ffed; }}
    tr.fail td {{ background: #ffe6e6; }}
    pre {{
      background: #fff;
      padding: 8px;
      border: 1px solid #eee;
      overflow-x: auto;
      font-size: 13px;
      white-space: pre-wrap;
    }}
    .badge-pass {{
      background: #28a745;
      color: white;
      padding: 2px 6px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
    }}
    .badge-fail {{
      background: #dc3545;
      color: white;
      padding: 2px 6px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
    }}
    .reason {{
      margin-top: 6px;
      color: #b71c1c;
      font-size: 13px;
      font-weight: 500;
    }}
    ul.summary {{
      margin-top: 12px;
      line-height: 1.6;
    }}
  </style>
</head>
<body>
  <h1>AI API Agent Report</h1>
  <div class="meta">Run Timestamp: {ts} &nbsp;|&nbsp; Agent: {agent_name}</div>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Endpoint</th>
        <th>Method</th>
        <th>URL</th>
        <th>Status</th>
        <th>Result</th>
        <th>Details</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>

  <h2>Summary</h2>
  <ul class="summary">
    <li>Total endpoints: {total}</li>
    <li>✅ Passed: {passed}</li>
    <li>❌ Failed: {failed}</li>
  </ul>

  <h2>Raw Data</h2>
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
  <td>{badge}</td>
  <td>
    <pre>{details}</pre>
    {reason_block}
  </td>
</tr>
"""


def make_report(run_results, agent_name="APIAgent", output_dir="reports"):
    """
    Generate an HTML report for API Agent test results.
    """
    os.makedirs(output_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows_html = ""
    passed, failed = 0, 0

    for idx, result in enumerate(run_results, start=1):
        success = result.get("success", False)

        if success:
            row_class = "pass"
            badge = '<span class="badge-pass">PASS</span>'
            reason_block = ""
            passed += 1
        else:
            row_class = "fail"
            badge = '<span class="badge-fail">FAIL</span>'
            failure_reason = result.get("reason", "Unknown error")
            reason_block = f'<div class="reason">Reason: {failure_reason}</div>'
            failed += 1

        rows_html += ROW_TEMPLATE.format(
            idx=idx,
            name=result.get("name", "Unnamed"),
            method=result.get("method", "GET"),
            url=result.get("url", "#"),
            url_short=result.get("url", "#").replace("https://", "").replace("http://", ""),
            status=result.get("status", "N/A"),
            details=result.get("details", ""),
            row_class=row_class,
            badge=badge,
            reason_block=reason_block
        )

    total = passed + failed

    html_content = HTML_TEMPLATE.format(
        ts=ts,
        agent_name=agent_name,
        rows=rows_html,
        total=total,
        passed=passed,
        failed=failed,
        raw=run_results
    )

    report_path = os.path.join(output_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return report_path
