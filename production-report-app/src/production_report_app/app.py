from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

DATA = [
    {"line": "Line A", "shift": "Day", "target": 520, "actual": 488, "scrap": 18, "downtime": 32, "hours": 8},
    {"line": "Line B", "shift": "Day", "target": 610, "actual": 592, "scrap": 16, "downtime": 24, "hours": 8},
    {"line": "Line C", "shift": "Night", "target": 580, "actual": 505, "scrap": 22, "downtime": 44, "hours": 8},
    {"line": "Line D", "shift": "Night", "target": 480, "actual": 474, "scrap": 9, "downtime": 18, "hours": 8},
]


def safe_number(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(default)
    return number


def calculate_efficiency(actual: float, target: float) -> float:
    if target <= 0:
        return 0.0
    return min(100.0, max(0.0, (actual / target) * 100.0))


def compute_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    target = sum(safe_number(entry.get("target")) for entry in entries)
    actual = sum(safe_number(entry.get("actual")) for entry in entries)
    scrap = sum(safe_number(entry.get("scrap")) for entry in entries)
    downtime = sum(safe_number(entry.get("downtime")) for entry in entries)
    hours = sum(safe_number(entry.get("hours")) for entry in entries)

    efficiency = calculate_efficiency(actual, target)
    losses = target - actual
    quality_rate = 0.0 if actual == 0 else ((actual - scrap) / actual) * 100.0

    return {
        "target": target,
        "actual": actual,
        "scrap": scrap,
        "downtime": downtime,
        "hours": hours,
        "efficiency": round(efficiency, 1),
        "losses": round(losses, 1),
        "quality_rate": round(min(100.0, max(0.0, quality_rate)), 1),
    }


def compute_line_rows(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in entries:
        target = safe_number(item.get("target"))
        actual = safe_number(item.get("actual"))
        scrap = safe_number(item.get("scrap"))
        downtime = safe_number(item.get("downtime"))
        efficiency = calculate_efficiency(actual, target)
        quality_rate = 0.0 if actual == 0 else ((actual - scrap) / actual) * 100.0
        rows.append(
            {
                "line": item.get("line", "Unknown"),
                "shift": item.get("shift", "Unknown"),
                "target": int(target),
                "actual": int(actual),
                "scrap": int(scrap),
                "downtime": int(downtime),
                "efficiency": round(efficiency, 1),
                "quality_rate": round(min(100.0, max(0.0, quality_rate)), 1),
                "variance": int(actual - target),
            }
        )
    return rows


def build_dashboard_html() -> str:
    summary = compute_summary(DATA)
    rows = compute_line_rows(DATA)
    max_output = max((row["actual"] for row in rows), default=1)

    cards = [
        ("Output", f"{summary['actual']} units", f"{summary['efficiency']}% efficiency"),
        ("Target", f"{summary['target']} units", f"{summary['losses']} units behind"),
        ("Downtime", f"{summary['downtime']} min", f"{summary['hours']} hours tracked"),
        ("Quality", f"{summary['quality_rate']}%", f"{summary['scrap']} scrap units"),
    ]

    card_html = "\n".join(
        f"<article class=\"card\"><div class=\"card-label\">{label}</div><div class=\"card-value\">{value}</div><div class=\"card-meta\">{trend}</div><span class=\"card-status\">{('OK' if label != 'Facturación' else 'ALERTA')}</span></article>"
        for label, value, trend in cards
    )

    table_rows = "\n".join(
        f"<tr><td>{row['line']}</td><td>{row['target']}</td><td>{row['actual']}</td><td>{row['efficiency']}%</td><td><span class=\"status {'green' if row['efficiency'] >= 90 else 'yellow' if row['efficiency'] >= 80 else 'red'}\"></span></td></tr>"
        for row in rows
    )

    bars = "\n".join(
        f"<div class=\"bar-col\"><div class=\"bar\" style=\"height: {(row['actual'] / max_output) * 100}%\"></div><div class=\"bar-label\">{row['line']}</div></div>"
        for row in rows
    )

    alerts = "\n".join(
        (
            f"<li><span class=\"dot red\"></span><span>{row['line']} is below target efficiency ({row['efficiency']}%)</span></li>"
            if row["efficiency"] < 85
            else f"<li><span class=\"dot yellow\"></span><span>{row['line']} had elevated downtime ({row['downtime']} min)</span></li>"
            if row["downtime"] > 25
            else f"<li><span class=\"dot green\"></span><span>{row['line']} is operating within expected thresholds</span></li>"
        )
        for row in rows
    )

    status = "excellent" if summary["efficiency"] >= 95 else "acceptable" if summary["efficiency"] >= 85 else "needs attention"
    status_color = "#2c9a5d" if summary["efficiency"] >= 90 else "#ec9a1f"

    return f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Wireframe - Producción</title>
    <style>
      :root {{
        --bg: #f3f3f3;
        --panel: #f8f8f8;
        --panel-strong: #ededed;
        --line: #c9c9c9;
        --line-dark: #8d8d8d;
        --text: #2f2f2f;
        --muted: #6b6b6b;
        --label: #9b9b9b;
        --shadow: 0 0 0 1px rgba(0,0,0,0.08);
      }}

      * {{ box-sizing: border-box; }}
      body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: var(--bg); color: var(--text); }}
      .app {{ display: flex; min-height: 100vh; }}
      .sidebar {{ width: 260px; background: #efefef; border-right: 1px solid var(--line); padding: 22px 12px; }}
      .brand {{ border: 1px solid var(--line-dark); padding: 14px 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; text-align: center; background: #e7e7e7; margin-bottom: 20px; }}
      .nav {{ display: grid; gap: 8px; }}
      .nav-item {{ display: flex; align-items: center; gap: 10px; padding: 12px 10px; border: 1px solid transparent; color: var(--text); font-size: 14px; }}
      .nav-item.active {{ background: #e8e8e8; border-color: var(--line-dark); font-weight: 700; }}
      .nav-icon {{ width: 18px; height: 18px; border: 1px solid var(--line-dark); display: inline-block; background: #dddddd; }}

      .main {{ flex: 1; padding: 20px 24px 28px; }}
      .topbar {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; border: 1px solid var(--line-dark); background: #f7f7f7; padding: 16px 18px; margin-bottom: 20px; }}
      .title {{ font-size: 16px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }}
      .toolbar {{ display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }}
      .field {{ display: flex; align-items: center; gap: 8px; font-size: 12px; text-transform: uppercase; color: var(--muted); }}
      .box {{ border: 1px solid var(--line-dark); background: #f2f2f2; min-width: 120px; height: 30px; display: inline-flex; align-items: center; justify-content: center; padding: 0 10px; }}
      .btn {{ border: 1px solid var(--line-dark); background: #eeeeee; padding: 8px 14px; font-size: 12px; text-transform: uppercase; font-weight: 700; cursor: default; }}

      .kpis {{ display: grid; grid-template-columns: repeat(4, minmax(150px, 1fr)); gap: 14px; margin-bottom: 20px; }}
      .card {{ border: 1px solid var(--line-dark); background: var(--panel); padding: 14px 12px; min-height: 130px; }}
      .card-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 12px; }}
      .card-value {{ font-size: 32px; font-weight: 700; line-height: 1; margin-bottom: 18px; }}
      .card-meta {{ font-size: 12px; color: var(--muted); }}
      .card-status {{ display: inline-block; margin-top: 10px; font-size: 12px; font-weight: 700; border: 1px solid var(--line-dark); padding: 2px 6px; }}

      .panel-grid {{ display: grid; grid-template-columns: 1.7fr 0.9fr; gap: 20px; margin-bottom: 20px; }}
      .panel {{ border: 1px solid var(--line-dark); background: var(--panel); }}
      .panel-header {{ border-bottom: 1px solid var(--line); padding: 12px 16px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; }}
      .table-wrap {{ overflow-x: auto; }}
      table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
      th, td {{ border-bottom: 1px solid var(--line); padding: 10px 12px; text-align: left; }}
      th {{ background: #f1f1f1; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }}
      .status {{ display: inline-block; width: 12px; height: 12px; border: 1px solid var(--line-dark); background: #dcdcdc; vertical-align: middle; }}
      .status.green {{ background: #dfe8d8; }}
      .status.red {{ background: #e8d5d5; }}
      .status.yellow {{ background: #ece0c9; }}

      .alerts {{ list-style: none; margin: 0; padding: 0; }}
      .alerts li {{ border-bottom: 1px solid var(--line); padding: 12px 16px; display: flex; align-items: flex-start; gap: 10px; font-size: 12px; }}
      .dot {{ width: 10px; height: 10px; border-radius: 50%; border: 1px solid var(--line-dark); margin-top: 3px; }}
      .dot.red {{ background: #d7b4b4; }}
      .dot.yellow {{ background: #e2d39d; }}
      .dot.green {{ background: #c9d9ba; }}

      .chart {{ display: flex; align-items: end; gap: 12px; height: 180px; padding: 20px 16px 10px; }}
      .bar-col {{ flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8px; }}
      .bar {{ width: 100%; max-width: 32px; background: #d4d4d4; border: 1px solid var(--line-dark); }}
      .bar-label {{ font-size: 10px; color: var(--muted); text-transform: uppercase; }}

      @media (max-width: 900px) {{
        .app {{ flex-direction: column; }}
        .sidebar {{ width: 100%; border-right: none; border-bottom: 1px solid var(--line); }}
        .kpis {{ grid-template-columns: repeat(2, minmax(150px, 1fr)); }}
        .panel-grid {{ grid-template-columns: 1fr; }}
      }}
    </style>
  </head>
  <body>
    <div class="app">
      <aside class="sidebar">
        <div class="brand">Corbel Producción</div>
        <nav class="nav">
          <div class="nav-item active"><span class="nav-icon"></span>Dashboard</div>
          <div class="nav-item"><span class="nav-icon"></span>Producción</div>
          <div class="nav-item"><span class="nav-icon"></span>Máquinas</div>
          <div class="nav-item"><span class="nav-icon"></span>Pedidos</div>
          <div class="nav-item"><span class="nav-icon"></span>Despachos</div>
          <div class="nav-item"><span class="nav-icon"></span>Facturación</div>
          <div class="nav-item"><span class="nav-icon"></span>Tiempos</div>
          <div class="nav-item"><span class="nav-icon"></span>Análisis</div>
          <div class="nav-item"><span class="nav-icon"></span>Reportes</div>
          <div class="nav-item"><span class="nav-icon"></span>Configuración</div>
        </nav>
      </aside>

      <main class="main">
        <header class="topbar">
          <div class="title">Dashboard de Producción</div>
          <div class="toolbar">
            <div class="field"><span>Fecha</span><span class="box">14/08/2026</span></div>
            <div class="field"><span>Turno</span><span class="box">Todos</span></div>
            <button class="btn">Actualizar</button>
          </div>
        </header>

        <section class="kpis">
          {card_html}
        </section>

        <section class="panel-grid">
          <div class="panel">
            <div class="panel-header">Estado de producción</div>
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Área</th>
                    <th>Meta</th>
                    <th>Actual</th>
                    <th>Cumplimiento</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {table_rows}
                </tbody>
              </table>
            </div>
          </div>

          <div class="panel">
            <div class="panel-header">Alertas</div>
            <ul class="alerts">{alerts}</ul>
          </div>
        </section>

        <section class="panel">
          <div class="panel-header">Producción</div>
          <div class="chart">{bars}</div>
        </section>
      </main>
    </div>
  </body>
</html>
"""


class ProductionReportHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(build_dashboard_html().encode("utf-8"))
            return

        if self.path == "/api/report":
            response = {
                "summary": compute_summary(DATA),
                "lines": compute_line_rows(DATA),
            }
            payload = json.dumps(response).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Not found")

    def log_message(self, format: str, *args: Any) -> None:
        return


def main(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), ProductionReportHandler)
    print(f"Production Report App running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
