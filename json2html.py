#!/usr/bin/env python3
"""
Script to convert a vulnerability JSON file to a structured HTML report
"""

import json
import sys
from collections import Counter

def parse_vuln_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        sys.exit(1)

    results = []
    artifact_name = data.get('ArtifactName', '')
    created_at = data.get('CreatedAt', '')

    for result in data.get('Results', []):
        target = result.get('Target', '')
        for vuln in result.get('Vulnerabilities', []):
            results.append({
                'Artifact Name': artifact_name,
                'Target': target,
                'Vulnerability ID': vuln.get('VulnerabilityID', ''),
                'CWE IDs': ', '.join(vuln.get('CweIDs', [])),
                'Severity': vuln.get('Severity', '').upper(),
                'Severity Source': vuln.get('SeveritySource', ''),
                'Package ID': vuln.get('PkgID', ''),
                'Package Name': vuln.get('PkgName', ''),
                'Title': vuln.get('Title', ''),
                'Description': vuln.get('Description', ''),
                'Installed Version': vuln.get('InstalledVersion', ''),
                'Fixed Version': vuln.get('FixedVersion', ''),
                'Primary URL': vuln.get('PrimaryURL', ''),
                'Published Date': vuln.get('PublishedDate', ''),
                'Last Modified Date': vuln.get('LastModifiedDate', '')
            })

    return results

def generate_html(vulnerabilities, output_file):
    if not vulnerabilities:
        print("No data to write to HTML.")
        return

    severity_counts = Counter(v['Severity'] for v in vulnerabilities)
    total = len(vulnerabilities)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Vulnerability Report</title>
<style>
    body {{ font-family: Arial, sans-serif; padding: 20px; }}
    h1, h2 {{ color: #333; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background-color: #f2f2f2; }}
    tr:nth-child(even) {{ background-color: #fafafa; }}
    .critical {{ background-color: #ff9999; }}
    .high {{ background-color: #ffc7ce; }}
    .medium {{ background-color: #ffeb9c; }}
    .low {{ background-color: #c6efce; }}

    .button-bar button {{
        margin-right: 10px;
        padding: 8px 12px;
        border: none;
        cursor: pointer;
        font-weight: bold;
    }}
    .filter-active {{ background-color: #007bff; color: white; }}
</style>
<script>
function filterSeverity(level) {{
    const rows = document.querySelectorAll('table#vulnTable tbody tr');
    rows.forEach(row => {{
        const severity = row.getAttribute('data-severity');
        row.style.display = (level === 'ALL' || severity === level) ? '' : 'none';
    }});

    document.querySelectorAll('.button-bar button').forEach(btn => btn.classList.remove('filter-active'));
    document.getElementById('btn-' + level).classList.add('filter-active');
}}
</script>
</head>
<body>
<h1>Vulnerability Report</h1>
<p><strong>Total Vulnerabilities:</strong> {total}</p>

<h2>Severity Summary</h2>
<table>
<tr>
  <th>CRITICAL</th><th>HIGH</th><th>MEDIUM</th><th>LOW</th>
</tr>
<tr>
  <td>{severity_counts.get('CRITICAL', 0)}</td>
  <td>{severity_counts.get('HIGH', 0)}</td>
  <td>{severity_counts.get('MEDIUM', 0)}</td>
  <td>{severity_counts.get('LOW', 0)}</td>
</tr>
</table>

<div class="button-bar" style="margin-top: 20px;">
  <button id="btn-ALL" class="filter-active" onclick="filterSeverity('ALL')">Show All</button>
  <button id="btn-CRITICAL" onclick="filterSeverity('CRITICAL')">Critical</button>
  <button id="btn-HIGH" onclick="filterSeverity('HIGH')">High</button>
  <button id="btn-MEDIUM" onclick="filterSeverity('MEDIUM')">Medium</button>
  <button id="btn-LOW" onclick="filterSeverity('LOW')">Low</button>
</div>

<h2>Detailed Vulnerabilities</h2>
<table id="vulnTable">
<thead><tr>
<th>Sr. No.</th>"""

    headers = list(vulnerabilities[0].keys())
    for header in headers:
        html += f"<th>{header}</th>"
    html += "</tr></thead><tbody>\n"

    for i, vuln in enumerate(vulnerabilities, start=1):
        severity_class = vuln.get("Severity", "").lower()
        html += f'<tr class="{severity_class}" data-severity="{vuln.get("Severity", "")}">'
        html += f"<td>{i}</td>"
        for header in headers:
            value = vuln.get(header, "")
            if header == "Primary URL" and value:
                value = f'<a href="{value}" target="_blank">{value}</a>'
            html += f"<td>{value}</td>"
        html += "</tr>\n"

    html += """
</tbody></table>
</body>
</html>"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"HTML report created successfully: {output_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 json2html.py input.json output.html")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    vulnerabilities = parse_vuln_json(input_file)
    generate_html(vulnerabilities, output_file)

if __name__ == "__main__":
    main()

