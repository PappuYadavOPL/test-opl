const fs = require('fs');

const input = process.argv[2];
const output = process.argv[3];

if (!input || !output) {
  console.error("Usage: node json2html.js <input.json> <output.html>");
  process.exit(1);
}

const data = JSON.parse(fs.readFileSync(input, 'utf8'));
const vulnerabilities = data.vulnerabilities || [];
const components = data.components || [];

function getComponent(ref) {
  return components.find(c => c['bom-ref'] === ref);
}

function getSeverityBadge(sev) {
  const s = (sev || '').toLowerCase();
  if (s === 'critical') return '<span class="badge bg-danger">Critical'</span>;
  if (s === 'high') return '<span class="badge bg-warning text-dark">High'</span>;
  if (s === 'medium') return '<span class="badge bg-info text-dark">Medium'</span>;
  if (s === 'low') return '<span class="badge bg-success">Low'</span>;
  return '<span class="badge bg-secondary">Unknown'</span>;
}

const severityCount = {
  Critical: 0,
  High: 0,
  Medium: 0,
  Low: 0,
  Unknown: 0
};

const rows = vulnerabilities.flatMap((vuln, index) => {
  const id = vuln.id || 'N/A';
  const severityRaw = vuln.ratings?.[0]?.severity || 'Unknown';
  const severity = severityRaw.charAt(0).toUpperCase() + severityRaw.slice(1).toLowerCase();
  const score = vuln.ratings?.[0]?.score ?? 'N/A';
  const desc = vuln.description || 'N/A';
  const sourceUrl = vuln.source?.url || 'N/A';
  const affects = vuln.affects || [];

  if (severityCount[severity] !== undefined) severityCount[severity]++;
  else severityCount.Unknown++;

  return affects.map((aff, subIndex) => {
    const component = getComponent(aff.ref);
    const compName = component ? `${component.name}@${component.version}` : aff.ref;
    const filePath = component?.properties?.find(p => p.name.includes("location") && p.value)?.value || 'N/A';

    return `
      <tr>
        <td>${index + 1}${affects.length > 1 ? `.${subIndex + 1}` : ''}</td>
        <td>${id}</td>
        <td>${severity}</td>
        <td>${score}</td>
        <td>${compName}</td>
        <td>${filePath}</td>
        <td><a href="${sourceUrl}" target="_blank">${sourceUrl}</a></td>
        <td>${desc}</td>
      </tr>
    `;
  });
}).join('\n');

const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>SBOM Vulnerability Report</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap5.min.css" rel="stylesheet">
  <style>
    body { padding: 20px; background-color: #f8f9fa; }
    .badge { font-size: 0.9em; }
    .filter-container { margin-bottom: 20px; }
    .filter-container label { margin-right: 10px; }
    .summary-badges span { margin-right: 10px; }
  </style>
</head>
<body>
  <div class="container-fluid">
    <h2 class="mb-4">SBOM Vulnerability Report</h2>

    <div class="summary-badges mb-2">
      <strong>Total Vulnerabilities:</strong> ${vulnerabilities.length}
      <span class="badge bg-danger">Critical: ${severityCount.Critical}</span>
      <span class="badge bg-warning text-dark">High: ${severityCount.High}</span>
      <span class="badge bg-info text-dark">Medium: ${severityCount.Medium}</span>
      <span class="badge bg-success">Low: ${severityCount.Low}</span>
      <span class="badge bg-secondary">Unknown: ${severityCount.Unknown}</span>
    </div>

    <div class="filter-container mb-3">
      <label for="severityFilter"><strong>Filter by Severity:</strong></label>
      <select id="severityFilter" class="form-select w-auto d-inline-block">
        <option value="">All</option>
        <option value="Critical">Critical</option>
        <option value="High">High</option>
        <option value="Medium">Medium</option>
        <option value="Low">Low</option>
        <option value="Unknown">Unknown</option>
      </select>
    </div>

    <div class="table-responsive">
      <table id="vulnTable" class="table table-striped table-bordered">
        <thead class="table-dark">
          <tr>
            <th>#</th>
            <th>Vuln ID</th>
            <th>Severity</th>
            <th>CVSS Score</th>
            <th>Affected Component</th>
            <th>File Path</th>
            <th>Source URL</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          ${rows || `<tr><td colspan="8" class="text-center">No vulnerabilities found.</td></tr>`}
        </tbody>
      </table>
    </div>
  </div>

  <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
  <script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap5.min.js"></script>
  <script>
    $(document).ready(function() {
      const table = $('#vulnTable').DataTable({
        responsive: true,
        pageLength: 10,
        lengthMenu: [10, 25, 50, 100],
        language: { search: "Search:" },
        columnDefs: [
          {
            targets: 2,
            render: function(data, type, row) {
              const s = data.toLowerCase();
              if (s === 'critical') return '<span class="badge bg-danger">Critical';</span>
              if (s === 'high') return '<span class="badge bg-warning text-dark">High';</span>
              if (s === 'medium') return '<span class="badge bg-info text-dark">Medium';</span>
              if (s === 'low') return '<span class="badge bg-success">Low';</span>
              return '<span class="badge bg-secondary">Unknown';</span>
            }
          }
        ]
      });

      // Custom severity filter
      $('#severityFilter').on('change', function() {
        const selected = $(this).val();
        if (selected) {
          table.column(2).search('^' + selected + '$', true, false).draw();
        } else {
          table.column(2).search('').draw();
        }
      });
    });
  </script>
</body>
</html>
`;

fs.writeFileSync(output, html, 'utf8');
console.log(`✅ Filterable report generated at ${output}`);
 
