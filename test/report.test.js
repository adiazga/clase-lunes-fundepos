const test = require('node:test');
const assert = require('node:assert/strict');

const {
  calculateEfficiency,
  calculateProductionSummary,
  getLinePerformance,
  generateSummaryText
} = require('../report.js');

test('calculateEfficiency handles targets accurately', () => {
  assert.equal(calculateEfficiency(120, 100), 120);
  assert.equal(calculateEfficiency(80, 100), 80);
  assert.equal(calculateEfficiency(10, 0), 0);
});

test('calculateProductionSummary aggregates output and quality', () => {
  const summary = calculateProductionSummary([
    { target: 100, actual: 95, scrap: 3, downtime: 10, hours: 8 },
    { target: 80, actual: 76, scrap: 2, downtime: 5, hours: 8 }
  ]);

  assert.equal(summary.target, 180);
  assert.equal(summary.actual, 171);
  assert.equal(summary.scrap, 5);
  assert.equal(summary.losses, 9);
  assert.equal(summary.efficiency, 95);
  assert.equal(summary.qualityRate, 97.1);
});

test('getLinePerformance includes variance and quality metrics', () => {
  const rows = getLinePerformance([
    { line: 'Line A', shift: 'Day', target: 100, actual: 90, scrap: 4, downtime: 10, hours: 8 }
  ]);

  assert.equal(rows[0].efficiency, 90);
  assert.equal(rows[0].variance, -10);
  assert.equal(rows[0].qualityRate, 95.6);
});

test('generateSummaryText describes output status', () => {
  const text = generateSummaryText({
    efficiency: 94.5,
    actual: 470,
    target: 500,
    losses: 30,
    scrap: 12
  });

  assert.match(text, /excellent|acceptable|needs attention/);
  assert.match(text, /470/);
});
