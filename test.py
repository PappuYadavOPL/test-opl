import json

# Load the JSON SBOM file
with open('sbom.json', 'r') as f:
    sbom = json.load(f)

# Start the HTML content
html = """
<html>
<head>
    <title>SBOM Components Report</title>
    <style>
        table { border-collapse: collapse; width: 100%; font-family: Arial; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
<h2>SBOM Components Report</h2>
<table>
    <tr>
        <th>Name</th>
        <th>Version</th>
        <th>Type</th>
        <th>Licenses</th>
        <th>CPE</th>
        <th>PURL</th>
        <th>Language</th>
    </tr>
"""

# Iterate over components
for component in sbom.get("components", []):
    name = component.get("name", "")
    version = component.get("version", "")
    ctype = component.get("type", "")
    cpe = component.get("cpe", "")
    purl = component.get("purl", "")

    # Extract licenses
    licenses = ", ".join([lic.get("license", {}).get("id", "") for lic in component.get("licenses", [])])

    # Extract language from properties
    language = ""
    for prop in component.get("properties", []):
        if prop.get("name") == "syft:package:language":
            language = prop.get("value")
            break

    # Add a row to the HTML table
    html += f"""
    <tr>
        <td>{name}</td>
        <td>{version}</td>
        <td>{ctype}</td>
        <td>{licenses}</td>
        <td>{cpe}</td>
        <td>{purl}</td>
        <td>{language}</td>
    </tr>
    """

# Finish HTML
html += """
</table>
</body>
</html>
"""

# Write the output HTML
with open('sbom_report.html', 'w') as f:
    f.write(html)

print("✅ SBOM HTML report generated: sbom_report.html")
