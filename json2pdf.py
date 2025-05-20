import json
import sys
from fpdf import FPDF
from fpdf.enums import XPos, YPos
 
def wrap_hard(text, interval=80):
    return '\n'.join(text[i:i+interval] for i in range(0, len(text), interval))
 
if len(sys.argv) != 3:
    print("Usage: python3 json_to_pdf.py <input.json> <output.pdf>")
    sys.exit(1)
 
input_json = sys.argv[1]
output_pdf = sys.argv[2]
 
with open(input_json, "r", encoding="utf-8") as f:
    data = json.load(f)
 
artifact_name = data.get("ArtifactName", "N/A")
vulns = []
secrets = []
 
for result in data.get("Results", []):
    target = result.get("Target", "N/A")
   
    for v in result.get("Vulnerabilities", []):
        vulns.append({
            "Artifact Name": artifact_name,
            "Target": target,
            "Vulnerability ID": v.get("VulnerabilityID"),
            "Package": v.get("PkgName"),
            "Package ID": v.get("PkgID", "N/A"),
            "Title": v.get("Title", "N/A"),
            "Installed Version": v.get("InstalledVersion"),
            "Fixed Version": v.get("FixedVersion", "N/A"),
            "Source": v.get("SeveritySource", ""),
            "Severity": v.get("Severity"),
            "CVSS Score": str(v.get("CVSS", {}).get("ghsa", {}).get("V3Score", "N/A")),
            "CWE": ", ".join(v.get("CweIDs", [])) or "N/A",
            "Primary URL": v.get("PrimaryURL", "N/A"),
            "Description": v.get("Description", "No description provided."),
            "References": "\n".join(v.get("References", [])) or "No references provided."
        })
 
    for s in result.get("Secrets", []):
        secrets.append({
            "Artifact Name": artifact_name,
            "Target": target,
            "Rule ID": s.get("RuleID"),
            "Category": s.get("Category"),
            "Severity": s.get("Severity"),
            "Title": s.get("Title"),
            "Code Match": s.get("Match"),
            "Start Line": s.get("StartLine"),
            "End Line": s.get("EndLine")
        })
 
# --- SORT VULNS BY SEVERITY ---
 
severity_order = {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 4,
    "UNKNOWN": 5
}
 
vulns.sort(key=lambda v: severity_order.get(v.get("Severity", "UNKNOWN").upper(), 5))
 
# ---------------------------
 
class PDF(FPDF):
    def header(self):
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255)
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 10, "Vulnerability Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
        self.ln(2)
 
    def multi_cell_nb_lines(self, w, h, txt):
        # Computes number of lines a MultiCell of width w will take
        cw = self.get_string_width
        if not txt:
            return 1
        lines = 0
        for line in txt.split('\n'):
            lines += max(1, int(cw(line) / w) + 1)
        return lines
 
    def label_value(self, label, value, highlight=False, multiline=False):
        self.set_font("Helvetica", "B", 9)
        label_width = 45
        value_width = 145
        line_height = 7
 
        if not multiline:
            self.cell(label_width, line_height, f"{label}:", border=1)
            self.set_font("Helvetica", "", 9)
            if highlight:
                color = (255, 204, 0) if value.upper() == "MEDIUM" else (255, 102, 102) if value.upper() == "HIGH" else (144, 238, 144)
                self.set_fill_color(*color)
                self.cell(value_width, line_height, value, border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                self.cell(value_width, line_height, value, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            value = wrap_hard(value)
            self.set_font("Helvetica", "", 9)
 
            nb_lines = self.multi_cell_nb_lines(value_width, line_height, value)
            cell_height = nb_lines * line_height
 
            x = self.get_x()
            y = self.get_y()
 
            # Draw label cell with same height as value cell
            self.set_xy(x, y)
            self.cell(label_width, cell_height, f"{label}:", border=1, align="L")
 
            # Draw value cell next to label
            self.set_xy(x + label_width, y)
            if highlight:
                color = (255, 204, 0) if value.upper() == "MEDIUM" else (255, 102, 102) if value.upper() == "HIGH" else (144, 238, 144)
                self.set_fill_color(*color)
                self.multi_cell(value_width, line_height, value, border=1, fill=True)
            else:
                self.multi_cell(value_width, line_height, value, border=1)
 
            self.ln(0)
 
pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=12)
pdf.set_margins(10, 10, 10)
pdf.core_fonts_encoding = "utf-8"
 
for vuln in vulns:
    pdf.add_page()
 
    pdf.label_value("Artifact Name", vuln["Artifact Name"])
    pdf.label_value("Target", vuln["Target"])
    pdf.label_value("Vulnerability ID", vuln["Vulnerability ID"])
    pdf.label_value("Title", vuln["Title"], multiline=True)
    pdf.label_value("Package", vuln["Package"])
    pdf.label_value("Package ID", vuln["Package ID"])
    pdf.label_value("Installed Version", vuln["Installed Version"])
    pdf.label_value("Fixed Version", vuln["Fixed Version"])
    pdf.label_value("Source", vuln["Source"])
    pdf.label_value("Severity", vuln["Severity"], highlight=True)
    pdf.label_value("CVSS Score", vuln["CVSS Score"])
    pdf.label_value("CWE", vuln["CWE"])
    pdf.label_value("Primary URL", vuln["Primary URL"], multiline=True)
    pdf.label_value("Description", vuln["Description"], multiline=True)
    pdf.label_value("References", vuln["References"], multiline=True)
 
# Secrets (if any)
if secrets:
    for secret in secrets:
        pdf.add_page()
        pdf.label_value("Artifact Name", secret["Artifact Name"])
        pdf.label_value("Target", secret["Target"])
        pdf.label_value("Rule ID", secret["Rule ID"])
        pdf.label_value("Category", secret["Category"])
        pdf.label_value("Severity", secret["Severity"], highlight=True)
        pdf.label_value("Title", secret["Title"])
        pdf.label_value("Start Line", str(secret["Start Line"]))
        pdf.label_value("End Line", str(secret["End Line"]))
        pdf.label_value("Matched Code", secret["Code Match"], multiline=True)
 
pdf.output(output_pdf)
print(f"\n✅ PDF ready: {output_pdf}")
