const sampleEntries = [
  { line: 'Line A', shift: 'Day', target: 520, actual: 488, scrap: 18, downtime: 32, hours: 8 },
  { line: 'Line B', shift: 'Day', target: 610, actual: 592, scrap: 16, downtime: 24, hours: 8 },
  { line: 'Line C', shift: 'Night', target: 580, actual: 505, scrap: 22, downtime: 44, hours: 8 },
  { line: 'Line D', shift: 'Night', target: 480, actual: 474, scrap: 9, downtime: 18, hours: 8 }
];

const { calculateProductionSummary, getLinePerformance } = window.ProductionReport;

const summaryGrid = document.getElementById('summaryGrid');
const summaryText = document.getElementById('summaryText');
const tableBody = document.getElementById('lineTableBody');
const trendChart = document.getElementById('trendChart');
const alertList = document.getElementById('alertList');
const refreshButton = document.getElementById('refreshButton');

function buildSummaryCards(summary) {
  const cards = [
    { label: 'Output', value: `${summary.actual} units`, trend: `${summary.efficiency.toFixed(1)}% efficiency` },
    { label: 'Target', value: `${summary.target} units`, trend: `${summary.losses} units behind` },
    { label: 'Downtime', value: `${summary.downtime} min`, trend: `${summary.hours} hours tracked` },
    { label: 'Quality', value: `${summary.qualityRate.toFixed(1)}%`, trend: `${summary.scrap} scrap units` }
  ];

  summaryGrid.innerHTML = cards
    .map(
      (card) => `
        <article class="summary-card">
          <p class="label">${card.label}</p>
          <div class="value">${card.value}</div>
          <div class="trend">${card.trend}</div>
        </article>
      `
    )
    .join('');
}

function buildTable(rows) {
  tableBody.innerHTML = rows
    .map(
      (row) => `
        <tr>
          <td>${row.line}</td>
          <td>${row.shift}</td>
          <td>${row.target}</td>
          <td>${row.actual}</td>
          <td>${row.efficiency}%</td>
          <td>${row.qualityRate}%</td>
          <td>${row.downtime} min</td>
        </tr>
      `
    )
    .join('');
}

function buildTrendChart(rows) {
  const maxValue = Math.max(...rows.map((row) => row.actual), 1);

  trendChart.innerHTML = rows
    .map(
      (row) => `
        <div class="bar-column">
          <div class="bar" style="height: ${(row.actual / maxValue) * 100}%"></div>
          <span class="bar-label">${row.line}</span>
        </div>
      `
    )
    .join('');
}

function buildAlerts(rows) {
  const alertItems = rows.map((row) => {
    if (row.efficiency < 85) {
      return { text: `${row.line} is below target efficiency (${row.efficiency}%)`, type: 'danger' };
    }

    if (row.downtime > 25) {
      return { text: `${row.line} had elevated downtime (${row.downtime} min)`, type: 'warning' };
    }

    return { text: `${row.line} is operating within expected thresholds`, type: 'success' };
  });

  alertList.innerHTML = alertItems
    .map(
      (alert) => `
        <li>
          <span class="alert-dot ${alert.type}"></span>
          <span>${alert.text}</span>
        </li>
      `
    )
    .join('');
}

function renderDashboard(entries) {
  const rows = getLinePerformance(entries);
  const summary = calculateProductionSummary(entries);

  buildSummaryCards(summary);
  buildTable(rows);
  buildTrendChart(rows);
  buildAlerts(rows);

  summaryText.textContent = `${summary.efficiency.toFixed(1)}% overall efficiency`;
  summaryText.style.background = summary.efficiency >= 90 ? 'rgba(44, 154, 93, 0.1)' : 'rgba(236, 154, 31, 0.12)';
  summaryText.style.color = summary.efficiency >= 90 ? '#2c9a5d' : '#ec9a1f';
}

refreshButton.addEventListener('click', () => {
  renderDashboard(sampleEntries);
});

renderDashboard(sampleEntries);
