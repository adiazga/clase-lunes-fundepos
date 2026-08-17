function toNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function clampPercent(value) {
  return Math.min(100, Math.max(0, value));
}

function calculateEfficiency(actual, target) {
  if (!target || target <= 0) {
    return 0;
  }

  return clampPercent((actual / target) * 100);
}

function calculateProductionSummary(entries = []) {
  const summary = entries.reduce(
    (acc, entry) => {
      const target = toNumber(entry.target);
      const actual = toNumber(entry.actual);
      const downtime = toNumber(entry.downtime);
      const scrap = toNumber(entry.scrap);
      const hours = toNumber(entry.hours);

      acc.target += target;
      acc.actual += actual;
      acc.downtime += downtime;
      acc.scrap += scrap;
      acc.hours += hours;

      return acc;
    },
    { target: 0, actual: 0, downtime: 0, scrap: 0, hours: 0 }
  );

  const efficiency = calculateEfficiency(summary.actual, summary.target);
  const losses = summary.target - summary.actual;
  const qualityRate = summary.actual === 0 ? 0 : ((summary.actual - summary.scrap) / summary.actual) * 100;

  return {
    target: summary.target,
    actual: summary.actual,
    downtime: summary.downtime,
    scrap: summary.scrap,
    hours: summary.hours,
    losses,
    efficiency,
    qualityRate: clampPercent(qualityRate)
  };
}

function getLinePerformance(entries = []) {
  return entries.map((entry) => {
    const target = toNumber(entry.target);
    const actual = toNumber(entry.actual);
    const scrap = toNumber(entry.scrap);
    const downtime = toNumber(entry.downtime);
    const efficiency = calculateEfficiency(actual, target);
    const qualityRate = actual === 0 ? 0 : ((actual - scrap) / actual) * 100;

    return {
      ...entry,
      target,
      actual,
      scrap,
      downtime,
      efficiency: Number(efficiency.toFixed(1)),
      qualityRate: Number(clampPercent(qualityRate).toFixed(1)),
      variance: actual - target
    };
  });
}

function generateSummaryText(summary) {
  const efficiency = toNumber(summary.efficiency);
  const status = efficiency >= 95 ? 'excellent' : efficiency >= 85 ? 'acceptable' : 'needs attention';

  return `Production is ${status} with ${efficiency.toFixed(1)}% efficiency. ${summary.actual} units were produced against a target of ${summary.target}, with ${summary.losses} units short and ${summary.scrap} scrap units recorded.`;
}

const ProductionReport = {
  calculateEfficiency,
  calculateProductionSummary,
  getLinePerformance,
  generateSummaryText,
  toNumber
};

if (typeof module !== 'undefined') {
  module.exports = ProductionReport;
}

if (typeof window !== 'undefined') {
  window.ProductionReport = ProductionReport;
}
