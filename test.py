import json

# Step 1: Read the JSON file
with open('data.json', 'r') as f:
    data = json.load(f)

# Step 2: Convert to HTML
html = "<html><body><table border='1'>"

# Table headers
headers = data[0].keys()
html += "<tr>" + "".join(f"<th>{header}</th>" for header in headers) + "</tr>"

# Table rows
for row in data:
    html += "<tr>" + "".join(f"<td>{row[col]}</td>" for col in headers) + "</tr>"

html += "</table></body></html>"

# Step 3: Save to an HTML file
with open('output.html', 'w') as f:
    f.write(html)

print("HTML file has been generated: output.html")
