import json
import re
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import serial
import serial.tools.list_ports

# ================= KONFIGURACJA =================
# Na Macu port Arduino zaczyna się zwykle od '/dev/cu.usbmodem...' lub '/dev/cu.usbserial...'
# Zostaw None, a program sam go znajdzie!
SERIAL_PORT = None
BAUD_RATE = 115200
THRESHOLD = 200
PORT_HTTP = 8000
# ================================================

state = {
    "status": "Szukanie portu Arduino...",
    "connected": False,
    "fields": {}
}

HTML_PAGE = """<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<title>Elektroniczna Szachownica - Live</title>
<style>
  body { background: #1e1e1e; color: #eee; font-family: -apple-system, BlinkMacSystemFont, sans-serif; display: flex; flex-direction: column; align-items: center; margin: 0; padding: 20px; }
  #status { font-size: 16px; font-weight: 600; margin-bottom: 16px; padding: 8px 16px; border-radius: 8px; background: #2d2d2d; }
  .ok { color: #69f0ae; }
  .err { color: #ff5252; }
  .board-wrap { display: grid; grid-template-columns: 28px repeat(8, 72px); grid-template-rows: repeat(8, 72px) 28px; gap: 2px; background: #111; padding: 10px; border-radius: 10px; box-shadow: 0 8px 25px rgba(0,0,0,0.5); }
  .coord { display: flex; align-items: center; justify-content: center; font-weight: bold; color: #888; font-size: 14px; }
  .cell { display: flex; flex-direction: column; justify-content: space-between; padding: 5px; border-radius: 4px; box-sizing: border-box; transition: background 0.08s; }
  .light { background: #ebecd0; color: #222; }
  .dark { background: #779556; color: #222; }
  .inactive.light { background: #4a4a4a; color: #888; }
  .inactive.dark { background: #333333; color: #777; }
  .detected { background: #ffeb3b !important; color: #d32f2f !important; box-shadow: inset 0 0 0 3px #d32f2f; }
  .fname { font-size: 11px; font-weight: 700; opacity: 0.75; }
  .fval { font-family: monospace; font-size: 15px; font-weight: bold; text-align: center; margin-bottom: 14px; }
</style>
</head>
<body>
  <div id="status" class="err">Łączenie...</div>
  <div class="board-wrap" id="board"></div>

<script>
const files = ['a','b','c','d','e','f','g','h'];
const ranks = ['8','7','6','5','4','3','2','1'];
const threshold = """ + str(THRESHOLD) + """;
const board = document.getElementById('board');
const cells = {};

ranks.forEach((r, rIdx) => {
  const lbl = document.createElement('div');
  lbl.className = 'coord';
  lbl.textContent = r;
  board.appendChild(lbl);

  files.forEach((f, fIdx) => {
    const name = f + r;
    const isLight = (rIdx + fIdx) % 2 === 0;
    const cell = document.createElement('div');
    cell.className = 'cell inactive ' + (isLight ? 'light' : 'dark');
    cell.innerHTML = `<div class="fname">${name}</div><div class="fval">brak</div>`;
    board.appendChild(cell);
    cells[name] = { el: cell, isLight };
  });
});

board.appendChild(document.createElement('div'));
files.forEach(f => {
  const lbl = document.createElement('div');
  lbl.className = 'coord';
  lbl.textContent = f;
  board.appendChild(lbl);
});

async function refresh() {
  try {
    const res = await fetch('/state');
    const data = await res.json();
    const st = document.getElementById('status');
    st.textContent = data.status;
    st.className = data.connected ? 'ok' : 'err';

    for (const [name, obj] of Object.entries(cells)) {
      const val = data.fields[name];
      const base = obj.isLight ? 'light' : 'dark';
      if (val === undefined) {
        obj.el.className = 'cell inactive ' + base;
        obj.el.querySelector('.fval').textContent = 'brak';
      } else if (val < threshold) {
        obj.el.className = 'cell detected';
        obj.el.querySelector('.fval').textContent = '● ' + val;
      } else {
        obj.el.className = 'cell ' + base;
        obj.el.querySelector('.fval').textContent = val;
      }
    }
  } catch (e) {}
}
setInterval(refresh, 60);
</script>
</body>
</html>
"""

def find_arduino_port():
    if SERIAL_PORT:
        return SERIAL_PORT
    for p in serial.tools.list_ports.comports():
        dev = (p.device or "").lower()
        desc = (p.description or "").lower()
        if any(k in dev or k in desc for k in ["usbmodem", "usbserial", "ch340", "arduino"]):
            return p.device
    return None

def serial_worker():
    pattern = re.compile(r"([a-h][1-8])=(\d+)")
    while True:
        port = find_arduino_port()
        if not port:
            state["connected"] = False
            state["status"] = "Nie znaleziono Arduino! Podłącz płytkę USB..."
            time.sleep(1.5)
            continue
        try:
            with serial.Serial(port, BAUD_RATE, timeout=1) as ser:
                state["connected"] = True
                state["status"] = f"Połączono z {port} ({BAUD_RATE} baud)"
                while True:
                    line = ser.readline().decode("utf-8", errors="ignore").strip()
                    if line:
                        for field, val_str in pattern.findall(line):
                            state["fields"][field] = int(val_str)
        except Exception as e:
            state["connected"] = False
            state["status"] = f"Błąd portu {port}: {e} (zamknij Serial Monitor w Arduino IDE!)"
            time.sleep(1.5)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(state).encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))

    def log_message(self, format, *args):
        pass  # wyciszenie logów w konsoli PyCharma

if __name__ == "__main__":
    threading.Thread(target=serial_worker, daemon=True).start()
    url = f"http://127.0.0.1:{PORT_HTTP}"
    print(f"Szachownica działa! Otwieram w przeglądarce: {url}")
    webbrowser.open(url)
    HTTPServer(("127.0.0.1", PORT_HTTP), Handler).serve_forever()