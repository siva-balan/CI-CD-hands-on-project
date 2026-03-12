from flask import Flask, request, render_template_string
import re

app = Flask(__name__)

# --- HTML TEMPLATE (layout + strips + separate quote search) ---
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>FIX 4.4 Log Analyzer</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
        :root{
            --bg: #f5f7fb;
            --card: #ffffff;
            --muted: #6b7280;
            --accent: #2563eb;
            --accent-2: #0ea5a4;
            --danger: #ef4444;
            --success: #10b981;
            --border: #e6e9ee;
            --shadow: 0 6px 18px rgba(15,23,42,0.06);
            --chip-bg: #eef2ff;
        }
        html,body { height:100%; margin:0; font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; background:var(--bg); color:#0f172a; }
        .container { max-width:1100px; margin:28px auto; padding:20px; }
        header { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:18px; }
        h1 { font-size:20px; margin:0; }
        .subtitle { color:var(--muted); font-size:13px; margin-top:4px; }

        .card { background:var(--card); border-radius:12px; padding:18px; box-shadow:var(--shadow); border:1px solid var(--border); }
        .grid { display:grid; grid-template-columns: 1fr 360px; gap:18px; align-items:start; }
        .full { grid-column: 1 / -1; }

        label { display:block; font-weight:600; margin-bottom:8px; font-size:13px; }
        textarea, input[type=file] { box-sizing: border-box; width:100%; }
        textarea { min-height:140px; resize:vertical; padding:12px; border-radius:8px; border:1px solid var(--border); font-family: monospace; font-size:13px; color:#0f172a; background:#fbfdff; }
        input[type=file] { padding:6px 0; }

        .controls { display:flex; gap:10px; align-items:center; margin-top:12px; flex-wrap:wrap; }

        button.primary {
            background: linear-gradient(90deg,var(--accent), #1e40af);
            color:white; border:none; padding:10px 14px; border-radius:8px; cursor:pointer; font-weight:600;
            box-shadow: 0 6px 14px rgba(37,99,235,0.18);
        }
        button.ghost {
            background:transparent; border:1px solid var(--border); padding:10px 14px; border-radius:8px; cursor:pointer; color:var(--muted);
        }
        button.clear {
            background:transparent; border:1px dashed #cbd5e1; padding:8px 12px; border-radius:8px; cursor:pointer; color:var(--danger);
        }

        .summary { display:flex; gap:12px; flex-wrap:wrap; margin-top:12px; }
        .stat { background:#f8fafc; border-radius:8px; padding:10px 12px; border:1px solid var(--border); min-width:140px; }
        .stat strong { display:block; font-size:18px; }
        .small { color:var(--muted); font-size:13px; }

        table { width:100%; border-collapse:collapse; margin-top:10px; font-size:13px; }
        th, td { text-align:left; padding:10px 12px; border-bottom:1px solid #eef2f7; vertical-align:top; }
        th { background:#fbfdff; font-size:13px; color:#0f172a; }
        .badge { display:inline-block; padding:6px 8px; border-radius:8px; font-size:12px; color:white; }
        .badge-logon { background:var(--success); }
        .badge-logout { background:var(--danger); }
        .badge-sub { background:var(--accent-2); }

        .strip {
            display:flex;
            gap:8px;
            align-items:center;
            overflow-x:auto;
            padding:10px;
            margin-top:12px;
            border-radius:8px;
            background: linear-gradient(90deg, rgba(14,165,164,0.04), rgba(37,99,235,0.02));
            border:1px solid var(--border);
        }
        .chip {
            background:var(--chip-bg);
            padding:8px 12px;
            border-radius:999px;
            white-space:nowrap;
            font-size:13px;
            color:#0f172a;
            border:1px solid rgba(14,165,164,0.08);
            position:relative;
        }
        .chip small { display:block; color:var(--muted); font-size:11px; margin-top:4px; }

        @media (max-width:900px) {
            .grid { grid-template-columns: 1fr; }
            .container { padding:12px; }
        }
    </style>
</head>
<body>
<div class="container">
    <header>
        <div>
            <h1>FIX 4.4 Log Analyzer</h1>
            <div class="subtitle">Upload a log file or paste FIX messages. Supports SOH (&lt;0x01&gt;), <code>|</code>, and <code>^A</code> delimiters.</div>
        </div>
        <div class="small">No storage • Runs locally</div>
    </header>

    <div class="grid">
        <!-- Left: uploader + textarea -->
        <div class="card">
            <form id="logform" method="post" enctype="multipart/form-data">
                <input type="hidden" id="raw_text_cache" name="raw_text_cache" value="{{ raw_text_cache|default('', true)|e }}">
                <div>
                    <label>Upload log file</label>
                    <input id="fileinput" type="file" name="logfile" accept=".log,.txt">
                </div>

                <div style="margin:12px 0; text-align:center; color:var(--muted); font-weight:600">— OR —</div>

                <div>
                    <label>Paste logs</label>
                    <textarea id="logtext" name="logtext" placeholder="Paste FIX logs here...">{{ logtext if logtext }}</textarea>
                </div>

                <div class="controls">
                    <button type="submit" class="primary" name="action" value="analyze">Analyze</button>
                    <button id="clearBtn" class="ghost" type="button">Clear</button>
                    <button id="resetAndReload" class="clear" type="button" title="Clear and reload page">Clear & Reload</button>
                </div>
            </form>

            <div class="small" style="margin-top:12px">Flow: upload logs → Analyze → then search QuoteID using the box below.</div>
        </div>

        <!-- Right: summary -->
        <div>
            <div class="card">
                <div style="display:flex; align-items:center; justify-content:space-between;">
                    <div>
                        <div style="font-weight:700">Summary</div>
                        <div class="small" style="margin-top:6px">Parsed message overview</div>
                    </div>
                </div>

                {% if summary %}
                <div class="summary">
                    <div class="stat">
                        <div class="small">Total messages</div>
                        <strong>{{ summary.total }}</strong>
                    </div>
                    <div class="stat">
                        <div class="small">Logon (35=A)</div>
                        <strong>{{ summary.logon }}</strong>
                    </div>
                    <div class="stat">
                        <div class="small">Logout (35=5)</div>
                        <strong>{{ summary.logout }}</strong>
                    </div>
                    <div class="stat">
                        <div class="small">MD/Quote Req (35=V/R)</div>
                        <strong>{{ summary.mdreq }}</strong>
                    </div>
                    <div class="stat">
                        <div class="small">Unique subscribed pairs</div>
                        <strong>{{ summary.ccpairs }}</strong>
                    </div>
                </div>
                {% else %}
                <div class="small" style="margin-top:12px">No analysis yet — upload a log or paste messages and click <strong>Analyze</strong>.</div>
                {% endif %}
            </div>
        </div>

        <!-- Full-width strips -->
        <div class="full">
            {% if ccpairs %}
                <div class="strip card">
                    <div style="font-weight:700; margin-right:8px; white-space:nowrap;">Subscribed pairs:</div>
                    {% for s in ccpairs %}
                        <div class="chip">{{ s }}</div>
                    {% endfor %}
                </div>
            {% endif %}

            {% if streaming_pairs %}
                <div class="strip card" style="margin-top:8px;">
                    <div style="font-weight:700; margin-right:8px; white-space:nowrap;">Streaming Indicative Quotes (last 537=0):</div>
                    {% for s in streaming_pairs %}
                        <div class="chip" title="{{ last_quote_details.get(s,'') }}">{{ s }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        </div>

        <!-- Quote search card (separate) -->
        <div class="full">
            <div class="card" style="margin-top:8px;">
                <h3 style="margin:0 0 8px 0;">Search by QuoteID (117)</h3>
                <div style="display:flex; gap:8px; align-items:center; margin-bottom:8px; flex-wrap:wrap;">
                    <input
                        type="text"
                        id="quoteSearchInput"
                        name="quote_search"
                        form="logform"
                        placeholder="Enter QuoteID"
                        value="{{ quote_search or '' }}"
                        style="padding:6px 8px; border-radius:6px; border:1px solid var(--border); font-size:12px; min-width:160px;">
                    <button
                        type="submit"
                        id="quoteSearchBtn"
                        form="logform"
                        name="action"
                        value="search_quote"
                        class="ghost"
                        style="padding:6px 10px; font-size:12px;">
                        Search
                    </button>
                    <button
                        type="button"
                        id="quoteClearBtn"
                        class="ghost"
                        style="padding:6px 10px; font-size:12px;">
                        Clear QuoteID
                    </button>
                </div>

                {% if quote_search %}
                    {% if quote_results %}
                        <table>
                            <thead>
                                <tr>
                                    <th>No</th>
                                    <th>SendingTime (52)</th>
                                    <th>MsgType (35)</th>
                                    <th>QuoteID (117)</th>
                                    <th>Symbol (55)</th>
                                    <th>Key tags</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for m in quote_results %}
                                <tr>
                                    <td>{{ loop.index }}</td>
                                    <td>{{ m.get('52','') }}</td>
                                    <td>{{ m.get('35','') }}</td>
                                    <td>{{ m.get('117','') }}</td>
                                    <td>{{ m.get('55','') }}</td>
                                    <td>
                                        49={{ m.get('49','') }},
                                        56={{ m.get('56','') }},
                                        537={{ m.get('537','') }}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% else %}
                        <div class="small">No messages found with QuoteID {{ quote_search }} (including related 35=V/R by 262/131).</div>
                    {% endif %}
                {% endif %}
            </div>
        </div>

        <!-- Full width results -->
        <div class="full">
            {% if summary %}
            <div class="card">
                <h3 style="margin:0 0 8px 0">Login / Logout (first/last, ordered by time)</h3>

                {% if log_highlights %}
                <table>
                    <thead>
                        <tr>
                            <th>No</th>
                            <th>SendingTime (52)</th>
                            <th>Type (35)</th>
                            <th>SenderCompID (49)</th>
                            <th>TargetCompID (56)</th>
                            <th>Text (58)</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for h in log_highlights %}
                        {% set m = h['msg'] %}
                        <tr>
                            <td>{{ loop.index }}</td>
                            <td>{{ m.get('52','') }}</td>
                            <td>
                                {% if m.get('35') == 'A' %}
                                    <span class="badge badge-logon">{{ m.get('35','') }}</span>
                                {% else %}
                                    <span class="badge badge-logout">{{ m.get('35','') }}</span>
                                {% endif %}
                            </td>
                            <td>{{ m.get('49','') }}</td>
                            <td>{{ m.get('56','') }}</td>
                            <td>{{ m.get('58','') }}</td>
                            <td>{{ h['note'] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="small">No login/logout messages found.</div>
                {% endif %}
            </div>

            <!-- MD / Quote Requests (only 35=V or 35=R) -->
            {% if mdreqs %}
            <div style="margin-top:12px;" class="card">
                <h3 style="margin:0 0 8px 0">Market Data / Quote Requests (35=V / 35=R)</h3>
                <table>
                    <thead>
                        <tr>
                            <th>No</th>
                            <th>SendingTime</th>
                            <th>MsgType</th>
                            <th>MDReqID / QuoteReqID</th>
                            <th>Subscription (263)</th>
                            <th>Symbols (55)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for m in mdreqs %}
                        <tr>
                            <td>{{ loop.index }}</td>
                            <td>{{ m.get('52','') }}</td>
                            <td><span class="badge badge-sub">{{ m.get('35','') }}</span></td>
                            <td>{{ m.get('262', m.get('131','')) }}</td>
                            <td>{{ m.get('263','') }}</td>
                            <td>{{ m.get('_symbols','') }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endif %}

            {% endif %}
        </div>
    </div>
</div>

<script>
document.getElementById('clearBtn').addEventListener('click', function(){
    var form = document.getElementById('logform');
    form.reset();
    var ta = document.getElementById('logtext');
    if (ta) ta.value = '';
    var fi = document.getElementById('fileinput');
    if (fi) fi.value = '';
    var qc = document.getElementById('quoteSearchInput');
    if (qc) qc.value = '';
});

document.getElementById('resetAndReload').addEventListener('click', function(){
    var form = document.getElementById('logform');
    form.reset();
    var ta = document.getElementById('logtext');
    if (ta) ta.value = '';
    var fi = document.getElementById('fileinput');
    if (fi) fi.value = '';
    var qc = document.getElementById('quoteSearchInput');
    if (qc) qc.value = '';
    window.location.href = window.location.pathname;
});

// Prevent quote search submit if QuoteID is empty
document.getElementById('quoteSearchBtn').addEventListener('click', function(e){
    var qc = document.getElementById('quoteSearchInput');
    if (!qc || qc.value.trim() === '') {
        e.preventDefault();
    }
});

// Clear QuoteID and clear search results (but keep analysis)
document.getElementById('quoteClearBtn').addEventListener('click', function(){
    var qc = document.getElementById('quoteSearchInput');
    if (qc) qc.value = '';
    // submit form so backend clears quote_results but keeps analysis via raw_text_cache
    var form = document.getElementById('logform');
    if (form) form.submit();
});
</script>
</body>
</html>
"""

# --- FIX PARSING HELPERS ---


def detect_delimiter(line: str) -> str:
    """
    Detect delimiter used in FIX message.
    Supported: SOH (\x01), |,  | , ^A
    """
    if '\x01' in line:
        return '\x01'
    if '^A' in line:
        return '^A'
    if ' | ' in line:
        return ' | '
    if '|' in line:
        return '|'
    return '\x01'  # fallback


def parse_fix_message(line: str) -> dict:
    """
    Parse a single chunk that is expected to contain one FIX message.
    Strips whitespace and returns dict of tag->value.
    """
    if not isinstance(line, str):
        line = str(line)
    line = line.strip()
    if not line:
        return {}

    # trim any leading non-8=FIX text and keep rest
    idx = line.find("8=FIX")
    if idx != -1:
        line = line[idx:]

    delim = detect_delimiter(line)
    parts = line.split(delim)

    msg = {}
    for part in parts:
        part = part.strip()
        if '=' not in part:
            continue
        tag, value = part.split('=', 1)
        tag = tag.strip()
        value = value.strip()
        msg[tag] = value

    return msg


def find_fix_message_chunks(raw_text: str):
    """
    Robustly split the raw text into message chunks by locating all occurrences of '8=FIX'.
    Handles blank lines, leading spaces, and messages that span lines.
    """
    if not raw_text:
        return []

    text = raw_text.replace('\r\n', '\n').replace('\r', '\n')
    starts = [m.start() for m in re.finditer(r'8=FIX', text)]
    chunks = []
    if not starts:
        for line in text.splitlines():
            if line.strip():
                chunks.append(line.strip())
        return chunks

    for i, s in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        chunk = text[s:end].strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def extract_messages(raw_text: str):
    """
    Parse the raw input into FIX message dicts, skipping empty lines and robustly handling spacing.
    Messages are then sorted by tag 52 (SendingTime).
    """
    messages = []
    chunks = find_fix_message_chunks(raw_text)
    for chunk in chunks:
        if not chunk or not chunk.strip():
            continue
        msg = parse_fix_message(chunk)
        if msg.get("8", "").startswith("FIX"):
            messages.append(msg)

    def get_ts(m):
        return m.get("52", "")

    messages.sort(key=get_ts)
    return messages


def classify_messages(messages):
    """
    From messages extract:
      - logons (35=A)
      - logouts (35=5)
      - mdreqs (35=V or 35=R)
      - quotes (35=S) only for streaming indicative (537=0) last-per-symbol
    Also build:
      - per-message _symbols (comma-separated)
      - global unique subscribed symbols list (ccpairs)
      - streaming last-quote summary (symbols where last 35=S had 537==0)
    """
    logons = []
    logouts = []
    mdreqs = []
    unique_symbols = set()
    last_quote_for_symbol = {}

    for m in messages:
        msg_type = m.get("35")
        symbols_in_msg = [val for tag, val in m.items() if tag == "55"]

        if msg_type == "A":
            logons.append(m)

        elif msg_type == "5":
            logouts.append(m)

        elif msg_type in ("V", "R"):
            for s in symbols_in_msg:
                unique_symbols.add(s)
            m["_symbols"] = ", ".join(symbols_in_msg) if symbols_in_msg else ""
            mdreqs.append(m)

        elif msg_type == "S":
            qstatus = m.get("537")
            if qstatus == "0":
                for s in symbols_in_msg:
                    last_quote_for_symbol[s] = m

    symbols_list = sorted(unique_symbols)
    streaming_pairs = sorted(last_quote_for_symbol.keys())

    last_quote_details = {}
    for sym, msg in last_quote_for_symbol.items():
        qid = msg.get("117", "")
        ts = msg.get("52", "")
        last_quote_details[sym] = f"QuoteID={qid} | {ts}"

    summary = {
        "total": len(messages),
        "logon": len(logons),
        "logout": len(logouts),
        "mdreq": len(mdreqs),
        "ccpairs": len(symbols_list)
    }

    return summary, logons, logouts, mdreqs, symbols_list, streaming_pairs, last_quote_details


# --- WEB ROUTE ---


@app.route("/", methods=["GET", "POST"])
def index():
    logtext = ""
    raw_text_cache = ""
    summary = None
    logons = []
    logouts = []
    mdreqs = []
    symbols = []
    streaming_pairs = []
    last_quote_details = {}
    quote_search = ""
    quote_results = []
    log_highlights = []

    if request.method == "POST":
        uploaded_file = request.files.get("logfile")
        text_area = request.form.get("logtext", "")
        quote_search = request.form.get("quote_search", "").strip()
        raw_text_cache = request.form.get("raw_text_cache", "")

        raw_text = ""

        # Priority: new file > new textarea > cached raw_text
        if uploaded_file and uploaded_file.filename:
            content = uploaded_file.read()
            try:
                raw_text = content.decode("utf-8", errors="ignore")
            except AttributeError:
                raw_text = content
            logtext = ""
        elif text_area.strip():
            raw_text = text_area
            logtext = text_area
        elif raw_text_cache.strip():
            raw_text = raw_text_cache
            # keep existing logtext as-is (whatever was last rendered)

        if raw_text.strip():
            # update cache so subsequent quote searches reuse same logs
            raw_text_cache = raw_text

            messages = extract_messages(raw_text)
            (summary, logons, logouts, mdreqs,
             symbols, streaming_pairs, last_quote_details) = classify_messages(messages)

            # 1) build login/logout highlights: first/last login & logout, ordered by timestamp
            def ts(m): return m.get("52", "")

            hl = []
            if logons:
                hl.append({"msg": logons[0], "note": "First Login"})
                if len(logons) > 1:
                    hl.append({"msg": logons[-1], "note": "Last Login"})
            if logouts:
                hl.append({"msg": logouts[0], "note": "First Logout"})
                if len(logouts) > 1:
                    hl.append({"msg": logouts[-1], "note": "Last Logout"})

            # Deduplicate messages (same object)
            seen = set()
            cleaned = []
            for h in hl:
                msg = h["msg"]
                ident = id(msg)
                if ident in seen:
                    continue
                seen.add(ident)
                cleaned.append(h)

            cleaned.sort(key=lambda h: ts(h["msg"]))
            log_highlights = cleaned

            # 2) quote search: if QuoteID is provided, search:
            #    - any message with 117 == QuoteID
            #    - any 35=V/R where 262 == QuoteID or 131 == QuoteID
            if quote_search:
                tmp = []
                for m in messages:
                    if m.get("117") == quote_search:
                        tmp.append(m)
                    elif m.get("35") in ("V", "R") and (
                        m.get("262") == quote_search or m.get("131") == quote_search
                    ):
                        tmp.append(m)

                # de-duplicate by object id (basic, but enough)
                seen2 = set()
                for m in tmp:
                    ident = id(m)
                    if ident in seen2:
                        continue
                    seen2.add(ident)
                    quote_results.append(m)

    return render_template_string(
        HTML_TEMPLATE,
        logtext=logtext,
        raw_text_cache=raw_text_cache,
        summary=summary,
        logons=logons,
        logouts=logouts,
        log_highlights=log_highlights,
        mdreqs=mdreqs,
        ccpairs=symbols,
        streaming_pairs=streaming_pairs,
        last_quote_details=last_quote_details,
        quote_search=quote_search,
        quote_results=quote_results
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FIX 4.4 Log Analyzer")
    parser.add_argument("--port", type=int, default=5000, help="Port to run on (default: 5000)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    app.run(host="0.0.0.0", port=args.port, debug=args.debug)