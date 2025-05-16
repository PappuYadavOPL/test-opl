#!/usr/bin/env python3
"""
Script to convert vulnerability JSON files to structured Excel format
Usage:
    python3 json2excel.py <input_json_or_directory> [output_excel_file]

Examples:
    python3 json2excel.py vuln_report.json vulnerability_report.xlsx
    python3 json2excel.py /path/to/json_dir/  # output file auto-named
"""

import json
import os
import sys
import pandas as pd
from datetime import datetime

def parse_vuln_json(file_path):
    """Parse the vulnerability JSON file and extract relevant information"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error opening or reading file {file_path}: {e}")
        return None

    results = []

    # Extract file metadata
    artifact_name = data.get('ArtifactName', '')
    created_at = data.get('CreatedAt', '')

    # Process each vulnerability
    for result in data.get('Results', []):
        target = result.get('Target', '')

        for vuln in result.get('Vulnerabilities', []):
            vuln_record = {
                'Source File': os.path.basename(file_path),
                'Artifact Name': artifact_name,
                'Created At': created_at,
                'Target': target,
                'Vulnerability ID': vuln.get('VulnerabilityID', ''),
                'Package ID': vuln.get('PkgID', ''),
                'Package Name': vuln.get('PkgName', ''),
                'Installed Version': vuln.get('InstalledVersion', ''),
                'Fixed Version': vuln.get('FixedVersion', ''),
                'Status': vuln.get('Status', ''),
                'Severity': vuln.get('Severity', ''),
                'Severity Source': vuln.get('SeveritySource', ''),
                'Title': vuln.get('Title', ''),
                'Description': vuln.get('Description', ''),
                'CWE IDs': ', '.join(vuln.get('CweIDs', [])),
                'Primary URL': vuln.get('PrimaryURL', ''),
                'Published Date': vuln.get('PublishedDate', ''),
                'Last Modified Date': vuln.get('LastModifiedDate', '')
            }
            results.append(vuln_record)

    return results

def process_directory(directory_path):
    """Process all JSON files in the directory"""
    all_vulns = []

    # Get all JSON files in the directory
    json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]

    if not json_files:
        print(f"No vulnerability JSON files found in {directory_path}")
        return None

    # Process each file
    for json_file in json_files:
        file_path = os.path.join(directory_path, json_file)
        print(f"Processing {file_path}...")
        vulns = parse_vuln_json(file_path)
        if vulns:
            all_vulns.extend(vulns)

    return all_vulns

def create_excel(vulnerabilities, output_file=None):
    """Create a structured Excel file from the vulnerability data"""
    if not vulnerabilities:
        print("No vulnerability data to export")
        return False

    # Create DataFrame
    df = pd.DataFrame(vulnerabilities)

    # Add Sr No column
    df.insert(0, 'Sr No', range(1, len(df) + 1))

    # Count severity levels for summary table
    severity_counts = {
        'CRITICAL': 0,
        'HIGH': 0,
        'MEDIUM': 0,
        'LOW': 0
    }

    for severity in df['Severity'].str.upper():
        if severity in severity_counts:
            severity_counts[severity] += 1

    total_findings = len(df)

    # Define desired column order
    columns_order = [
        'Sr No',
        'Artifact Name',
        'Target',
        'Vulnerability ID',
        'CWE IDs',
        'Severity',
        'Severity Source',
        'Package ID',
        'Package Name',
        'Title',
        'Description',
        'Installed Version',
        'Fixed Version',
        'Primary URL',
        'Published Date',
        'Last Modified Date'
    ]

    # Reorder DataFrame columns
    df = df[[col for col in columns_order if col in df.columns]]

    # Generate default output filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"vulnerability_report_{timestamp}.xlsx"

    # Ensure the output file has .xlsx extension
    if not output_file.endswith('.xlsx'):
        output_file += '.xlsx'

    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            workbook = writer.book

            # Write summary table at the top (starting at row 0, col 0)
            worksheet = workbook.add_worksheet('Vulnerabilities')

            # Define formats
            bold_center_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#BDD7EE',
                'border': 1
            })
            center_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })

            # Write total findings label and value (row 0)
            worksheet.write(0, 0, "Total Findings", bold_center_format)
            worksheet.write(0, 1, total_findings, center_format)

            # Leave a blank row (row 1)

            # Write severity headers (row 2)
            severities = ['Critical', 'High', 'Medium', 'Low']
            for col_num, severity in enumerate(severities):
                worksheet.write(2, col_num, severity, bold_center_format)

            # Write severity counts (row 3)
            for col_num, severity in enumerate(severities):
                worksheet.write(3, col_num, severity_counts[severity.upper()], center_format)

            # Write main dataframe below summary (start at row 5)
            df_start_row = 5
            df.to_excel(writer, sheet_name='Vulnerabilities', startrow=df_start_row, index=False)

            worksheet = writer.sheets['Vulnerabilities']

            # Header formatting for main table
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })

            for col_num, value in enumerate(df.columns.values):
                worksheet.write(df_start_row, col_num, value, header_format)

            for i, col in enumerate(df.columns):
                if col == 'Description':
                    worksheet.set_column(i, i, 50)
                elif 'URL' in col:
                    worksheet.set_column(i, i, 30)
                else:
                    worksheet.set_column(i, i, 20)

            worksheet.autofilter(df_start_row, 0, df_start_row + len(df), len(df.columns) - 1)
            worksheet.freeze_panes(df_start_row + 1, 0)

            severity_col = df.columns.get_loc('Severity')
            worksheet.conditional_format(df_start_row + 1, severity_col, df_start_row + len(df), severity_col, {
                'type': 'cell',
                'criteria': 'equal to',
                'value': '"HIGH"',
                'format': workbook.add_format({'bg_color': '#FFC7CE'})
            })
            worksheet.conditional_format(df_start_row + 1, severity_col, df_start_row + len(df), severity_col, {
                'type': 'cell',
                'criteria': 'equal to',
                'value': '"MEDIUM"',
                'format': workbook.add_format({'bg_color': '#FFEB9C'})
            })
            worksheet.conditional_format(df_start_row + 1, severity_col, df_start_row + len(df), severity_col, {
                'type': 'cell',
                'criteria': 'equal to',
                'value': '"LOW"',
                'format': workbook.add_format({'bg_color': '#C6EFCE'})
            })

        print(f"Excel report created successfully: {output_file}")
        return True

    except Exception as e:
        print(f"Error creating Excel file: {e}")
        return False

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Convert vulnerability JSON(s) to Excel report")
    parser.add_argument('input_path', help='Path to JSON file or directory containing JSON files')
    parser.add_argument('output_file', nargs='?', default=None, help='Output Excel file name (optional)')

    args = parser.parse_args()

    input_path = args.input_path
    output_file = args.output_file

    vulnerabilities = []

    if os.path.isdir(input_path):
        vulnerabilities = process_directory(input_path)
    elif os.path.isfile(input_path) and input_path.endswith('.json'):
        vulnerabilities = parse_vuln_json(input_path)
    else:
        print("Input path must be a JSON file or directory containing JSON files.")
        sys.exit(1)

    if vulnerabilities:
        create_excel(vulnerabilities, output_file)
    else:
        print("No vulnerabilities found to export")

if __name__ == "__main__":
    main()

