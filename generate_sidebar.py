import json, os

# ── CSV parser ────────────────────────────────────────────────────────────────
def parse_csv_line(line):
    fields = []
    i = 0
    line = line.rstrip('\r\n')
    while i < len(line):
        if line[i] == '"':
            i += 1
            field = ''
            while i < len(line):
                if line[i] == '"':
                    if i + 1 < len(line) and line[i+1] == '"':
                        field += '"'; i += 2
                    else:
                        i += 1; break
                else:
                    field += line[i]; i += 1
            fields.append(field)
        else:
            j = i
            while j < len(line) and line[j] != ',':
                j += 1
            fields.append(line[i:j].strip())
            i = j
        if i < len(line) and line[i] == ',':
            i += 1
            while i < len(line) and line[i] == ' ':
                i += 1
    return fields

# ── Pill class by value / position ───────────────────────────────────────────
def pill_cls(value, pos):
    v = value.strip()
    if v.upper() == 'TOFU':       return 'p-tofu'
    if v.upper() == 'BOFU':       return 'p-bofu'
    if v.lower() == 'branded':    return 'p-branded'
    if v.lower() == 'competitor': return 'p-competitor'
    if pos == 0: return 'p-product'
    if pos == 1: return 'p-audience'
    if pos == 2: return 'p-feature'
    return 'p-other'

TAG_ORDER = {'p-product': 0, 'p-other': 0,
             'p-tofu': 1, 'p-bofu': 1, 'p-branded': 1, 'p-competitor': 1,
             'p-audience': 2, 'p-feature': 3}

# ── Process one CSV file ──────────────────────────────────────────────────────
def process(path, label):
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    rows = []
    for line in lines:
        if not line.strip():
            continue
        fields = parse_csv_line(line)
        if len(fields) < 4:
            continue
        prompt   = fields[0]
        topic    = fields[1]
        tags_raw = fields[3]
        tag_vals = [t.strip() for t in tags_raw.split(';')]
        tags = sorted([{'v': v, 'c': pill_cls(v, i)}
                       for i, v in enumerate(tag_vals) if v],
                      key=lambda t: TAG_ORDER.get(t['c'], 99))
        rows.append({'prompt': prompt, 'topic': topic, 'tags': tags})
    return {'label': label, 'rows': rows}

base = r'C:\Projects\Omnia\dimensional-prompt-ui-prototype'
files = [
    process(os.path.join(base, 'unbranded.csv'),   'Unbranded'),
    process(os.path.join(base, 'branded.csv'),      'Branded'),
    process(os.path.join(base, 'competitors.csv'),  'Competitors'),
]
all_rows = []
for f in files:
    print(f"  {f['label']}: {len(f['rows'])} rows")
    all_rows.extend(f['rows'])
print(f"  Total: {len(all_rows)} rows")

DATA_JSON = json.dumps(all_rows, ensure_ascii=False)

TMPL = open(os.path.join(base, '_sidebar_tmpl.html'), encoding='utf-8').read()
HTML = TMPL.replace('/*DATA_PLACEHOLDER*/', DATA_JSON)

out = os.path.join(base, 'prompt-sidebar.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(HTML)
print(f'Written: {out}')
