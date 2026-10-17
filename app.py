from functools import wraps
import os
import sqlite3
from urllib.parse import quote_plus
from flask import Flask, request, redirect, url_for, session, flash, render_template_string, abort

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'replace-this-secret-key-before-deployment')
DB = os.path.join(os.path.dirname(__file__), 'healthcare.db')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
OFFICIAL_SOURCE = 'https://www.zpsatara.gov.in/en/satara-district-primary-health-centers-phcs-list/'

# Names and talukas below are taken from the Zilla Parishad Satara PHC directory.
# Resource counts, doctor names, departments, timings, and medicine information are DEMO DATA.
PHCS = [
 ('Bamnoli','Jawali'),('Kelghar','Jawali'),('Kudal','Jawali'),('Kusumbi','Jawali'),('Saigaon','Jawali'),
 ('Helgaon','Karad'),('Indoli','Karad'),('Kale','Karad'),('Kole','Karad'),('Maskarwadi','Karad'),('Masur','Karad'),('Mhasoli','Karad'),('Rethare Bk','Karad'),('Sadashivgad','Karad'),('Supane','Karad'),('Umbraj','Karad'),('Wadgaon Haweli','Karad'),('Yelgaon','Karad'),('Yewati','Karad'),
 ('Aahire','Khandala'),('Loham','Khandala'),('Lonand','Khandala'),('Shirwal','Khandala'),
 ('Diskal','Khatav'),('Gursale','Khatav'),('Katarkhatav','Khatav'),('Khatav','Khatav'),('Mayani','Khatav'),('Nimsode','Khatav'),('Padal','Khatav'),('Pusegaon','Khatav'),('Pusesavali','Khatav'),
 ('Kinhai','Koregaon'),('Rahimatpur','Koregaon'),('Satararoad','Koregaon'),('Palashi Koregaon','Koregaon'),('Tadwale','Koregaon'),('Wathar Kiroli','Koregaon'),('Wathar Station','Koregaon'),
 ('Pachagani','Mahabaleshwar'),('Taldev','Mahabaleshwar'),('Tapola','Mahabaleshwar'),
 ('Malawadi','Man'),('Mardi','Man'),('Mhaswad','Man'),('Palashi Man','Man'),('Pulkoti','Man'),('Shingnapur','Man'),
 ('Chafal','Patan'),('Helwak','Patan'),('Kalgaon','Patan'),('Keral','Patan'),('Malharpeth','Patan'),('Marali','Patan'),('Morgiri','Patan'),('Murud','Patan'),('Salave','Patan'),('Sanbur','Patan'),('Sonawade','Patan'),('Talmawale','Patan'),('Tarale','Patan'),
 ('Barad','Phaltan'),('Bibi','Phaltan'),('Giravi','Phaltan'),('Rajale','Phaltan'),('Sakharwadi','Phaltan'),('Taradgaon','Phaltan'),('Tathvada','Phaltan'),
 ('Angapur Vandan','Satara'),('Chinchaner Vandan','Satara'),('Kanher','Satara'),('Kshetramahuli','Satara'),('Kumthe','Satara'),('Limb','Satara'),('Nagthane','Satara'),('Nandgaon','Satara'),('Parali','Satara'),('Thoseghar','Satara'),('Vaduth','Satara'),('Venegaon','Satara'),
 ('Bavdhan','Wai'),('Bhuinj','Wai'),('Kavathe','Wai'),('Malatpur','Wai')
]

STYLE = '''
:root{--blue:#175b9c;--blue2:#eaf3fc;--ink:#18324b;--muted:#66788a;--line:#dce6ef;--bg:#f5f8fc;--green:#18794e;--amber:#fff4d6}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,Arial,sans-serif}a{color:var(--blue)}.top{background:#fff;border-bottom:1px solid var(--line);padding:15px max(16px,calc((100% - 1180px)/2));display:flex;align-items:center;justify-content:space-between;gap:15px}.brand{font-weight:850;font-size:18px;color:var(--ink);text-decoration:none}.brand b{color:var(--blue)}.nav{display:flex;gap:12px;align-items:center;flex-wrap:wrap}.nav a{text-decoration:none;font-weight:650;font-size:13px}.wrap{max-width:1180px;margin:auto;padding:26px 18px}.hero{background:linear-gradient(115deg,#123f70,#1e75b5);color:white;border-radius:20px;padding:34px;display:grid;grid-template-columns:1.5fr 1fr;gap:24px;align-items:center}.hero h1{font-size:clamp(28px,4vw,42px);line-height:1.15;margin:8px 0 12px}.hero p{max-width:680px;color:#e1efff;margin:0}.tag{font-size:11px;letter-spacing:1.2px;font-weight:800}.hero-note{background:#ffffff18;border:1px solid #ffffff35;border-radius:14px;padding:18px}.hero-note strong{font-size:27px;display:block}.searchbox,.panel,.card,.stat{background:white;border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 5px 20px #17324b08}.searchbox{margin:18px 0}.filters{display:grid;grid-template-columns:2fr 1fr auto;gap:10px}input,select{width:100%;min-width:0;border:1px solid #cedbe6;border-radius:9px;padding:11px 12px;font:inherit;background:white;color:var(--ink)}.btn{border:0;border-radius:9px;background:var(--blue);color:white;padding:11px 15px;font:inherit;font-weight:750;cursor:pointer;text-decoration:none;display:inline-block;text-align:center}.btn.light{background:#fff;color:var(--blue);border:1px solid var(--line)}.btn.small{font-size:12px;padding:8px 11px}.sectionhead{display:flex;justify-content:space-between;align-items:end;gap:12px;margin:26px 0 13px}.sectionhead h2{margin:0;font-size:23px}.muted,.hint{color:var(--muted)}.hint{font-size:12px}.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.card{display:flex;flex-direction:column;gap:8px}.card h3{font-size:18px;margin:0}.type{display:inline-block;width:max-content;max-width:100%;font-size:11px;font-weight:800;background:var(--blue2);color:var(--blue);padding:4px 8px;border-radius:6px}.card .loc{color:var(--muted);font-size:13px}.card .btn{margin-top:auto}.sample{background:var(--amber);color:#70520d;border:1px solid #f2e2ad;padding:10px 12px;border-radius:9px;font-size:12px}.detailhead{display:flex;justify-content:space-between;align-items:start;gap:15px;flex-wrap:wrap}.detailhead h1{margin:6px 0;font-size:clamp(26px,4vw,36px)}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0}.stat p{margin:0 0 4px;color:var(--muted);font-size:12px}.stat strong{font-size:27px}.detailgrid{display:grid;grid-template-columns:1fr 1fr;gap:15px}.panel h2{margin:0 0 13px;font-size:19px}.kv{display:grid;grid-template-columns:150px 1fr;gap:8px;padding:9px 0;border-bottom:1px solid #edf1f5}.kv:last-child{border-bottom:0}.kv span:first-child{color:var(--muted)}.pills{display:flex;gap:7px;flex-wrap:wrap}.pill{border:1px solid var(--line);border-radius:30px;padding:6px 10px;font-size:12px}.doctor{border:1px solid var(--line);border-radius:10px;padding:12px;margin:9px 0}.doctor strong{display:block}.footer{text-align:center;color:var(--muted);font-size:12px;padding:26px}.login{max-width:420px;margin:5vh auto}.login form{display:grid;gap:13px}.formgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.formgrid label{font-size:12px;font-weight:750;display:grid;gap:5px}.flash{padding:10px 12px;border-radius:8px;margin:12px 0;background:#e7f7ed;color:#17643b}.flash.error{background:#ffeded;color:#9d2727}.tablewrap{overflow-x:auto}table{border-collapse:collapse;width:100%;white-space:nowrap}td,th{padding:11px;border-bottom:1px solid var(--line);text-align:left;font-size:13px}th{font-size:11px;color:var(--muted);text-transform:uppercase}.actions{display:flex;gap:6px;align-items:center}.actions form{margin:0}.empty{padding:28px;text-align:center;color:var(--muted)}@media(max-width:850px){.cards{grid-template-columns:repeat(2,1fr)}.hero{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.detailgrid{grid-template-columns:1fr}.formgrid{grid-template-columns:repeat(2,1fr)}}@media(max-width:560px){.wrap{padding:18px 12px}.top{padding:13px;align-items:flex-start}.brand{font-size:15px}.cards{grid-template-columns:1fr}.filters{grid-template-columns:1fr}.hero{padding:23px}.stats{gap:8px}.stat{padding:12px}.stat strong{font-size:22px}.formgrid{grid-template-columns:1fr}.kv{grid-template-columns:120px 1fr}}
'''

BASE = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{ title }} | Satara District Healthcare Portal</title><style>''' + STYLE + '''</style></head><body><header class="top"><a class="brand" href="{{ url_for('home') }}"><b>✚</b> Satara District <span class="muted">Healthcare Portal</span></a><nav class="nav"><a href="{{ url_for('home') }}">Find a facility</a>{% if session.get('logged_in') %}<a href="{{ url_for('officials') }}">Officials dashboard</a><a href="{{ url_for('logout') }}">Log out</a>{% else %}<a href="{{ url_for('login') }}">Officials login</a>{% endif %}</nav></header><main class="wrap">{% with msgs=get_flashed_messages(with_categories=true) %}{% for category,message in msgs %}<div class="flash {{ category }}">{{ message }}</div>{% endfor %}{% endwith %}{{ content|safe }}</main><footer class="footer">District Healthcare Monitoring and Management System · Student PBL prototype<br>Facility directory source: <a href="''' + OFFICIAL_SOURCE + '''" target="_blank" rel="noopener">Zilla Parishad Satara PHC list</a>. Resource and doctor details are sample data unless marked verified.</footer></body></html>'''

HOME = '''<section class="hero"><div><div class="tag">PUBLIC HEALTHCARE DIRECTORY · SATARA, MAHARASHTRA</div><h1>Find government healthcare near you.</h1><p>Search public hospitals and Primary Health Centres by facility name, town or taluka. Open a facility to view its services and directory information.</p></div><div class="hero-note"><span class="tag">DIRECTORY COVERAGE</span><strong>{{ total }}</strong><span>government healthcare facilities listed</span><p class="hint" style="color:#e1efff">Facility names and talukas are based on the official PHC directory. Other details are labelled sample data.</p></div></section><section class="searchbox"><form class="filters" method="get"><input name="q" value="{{ q }}" placeholder="Search by facility, town or taluka"><select name="type"><option value="">All facility types</option>{% for t in types %}<option value="{{ t }}" {% if selected_type==t %}selected{% endif %}>{{ t }}</option>{% endfor %}</select><button class="btn">Search facilities</button></form></section><div class="sectionhead"><div><h2>Government facilities</h2><div class="muted">{{ facilities|length }} results shown</div></div><span class="type">SAMPLE DATA NOTICE</span></div><section class="cards">{% for h in facilities %}<article class="card"><span class="type">{{ h.facility_type }}</span><h3>{{ h.name }}</h3><div class="loc">📍 {{ h.taluka }} taluka, Satara district</div><p class="hint">Beds, doctors, departments and medicine information are sample entries for demonstration.</p><a class="btn" href="{{ url_for('facility_detail', hid=h.id) }}">View facility details →</a></article>{% else %}<div class="panel empty">No facilities match your search. Try another town or facility type.</div>{% endfor %}</section>'''

DETAIL = '''<div class="detailhead"><div><a href="{{ url_for('home') }}">← Back to directory</a><span class="type" style="display:block;margin-top:12px">{{ h.facility_type }}</span><h1>{{ h.name }}</h1><p class="muted">{{ h.taluka }} taluka · Satara district, Maharashtra</p></div><a class="btn" target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query={{ (h.name ~ ' ' ~ h.taluka ~ ' Satara Maharashtra')|urlencode }}">Map & directions ↗</a></div><div class="sample">DEMO / SAMPLE DATA: facility name and taluka are based on the official PHC directory where available. Beds, phone, address, opening hours, doctors, departments and medicine status below are illustrative and must be verified before public deployment.</div><section class="stats"><article class="stat"><p>Total beds</p><strong>{{ h.total_beds }}</strong></article><article class="stat"><p>Reported available beds</p><strong>{{ h.available_beds }}</strong></article><article class="stat"><p>Departments listed</p><strong>{{ departments|length }}</strong></article><article class="stat"><p>Doctors listed</p><strong>{{ doctors|length }}</strong></article></section><section class="detailgrid"><article class="panel"><h2>Facility information</h2><div class="kv"><span>Address</span><strong>{{ h.address }}</strong></div><div class="kv"><span>Contact number</span><strong>{{ h.phone }}</strong></div><div class="kv"><span>Opening hours</span><strong>{{ h.opening_hours }}</strong></div><div class="kv"><span>Emergency service</span><strong>{{ h.emergency }}</strong></div><div class="kv"><span>Last updated</span><strong>{{ h.last_updated }}</strong></div><div class="kv"><span>Medicine availability</span><strong>{{ h.medicine_status }}</strong></div></article><article class="panel"><h2>Departments and services</h2><div class="pills">{% for d in departments %}<span class="pill">{{ d.name }}</span>{% endfor %}</div><p class="hint">Department and service listings are examples only and are not confirmation that a service is currently available.</p><h2 style="margin-top:20px">Services</h2><div class="pills">{% for s in services %}<span class="pill">{{ s }}</span>{% endfor %}</div></article><article class="panel"><h2>Doctors</h2>{% for d in doctors %}<div class="doctor"><strong>{{ d.name }}</strong><span>{{ d.specialization }}</span><div class="hint">Department: {{ d.department }}</div><div class="hint">Consultation: {{ d.timings }}</div></div>{% endfor %}<p class="hint">Sample doctor profiles only. No doctor phone numbers are displayed.</p></article><article class="panel"><h2>Location and updates</h2><p>Use the map link above to search for this facility's location. Confirm the address and directions before travelling.</p><div class="sample">Resource information is not real-time. Please contact the facility to confirm beds, timings, services and medicine availability.</div><p class="hint">Official directory: <a href="''' + OFFICIAL_SOURCE + '''" target="_blank" rel="noopener">Zilla Parishad Satara PHC list</a></p></article></section>'''

LOGIN = '''<section class="panel login"><div class="tag">RESTRICTED ACCESS</div><h1>Government officials login</h1><p class="muted">Sign in to manage facility records in this demonstration.</p><form method="post"><label>Username<input name="username" required autocomplete="username"></label><label>Password<input type="password" name="password" required autocomplete="current-password"></label><button class="btn">Sign in</button></form><p class="hint">Demo credentials: <b>admin</b> / <b>admin123</b>. Change these before any deployment.</p></section>'''

OFFICIALS = '''<div class="detailhead"><div><div class="tag">OFFICIALS PORTAL</div><h1>Facility management</h1><p class="muted">Signed in as {{ username }}. Manage sample directory entries.</p></div><span class="type">DEMO DATA</span></div><section class="stats"><article class="stat"><p>Facilities listed</p><strong>{{ summary.count }}</strong></article><article class="stat"><p>Total beds (sample)</p><strong>{{ summary.total }}</strong></article><article class="stat"><p>Available beds (sample)</p><strong>{{ summary.available }}</strong></article><article class="stat"><p>Facilities by type</p><strong>{{ summary.phcs }} PHCs</strong></article></section><section class="panel"><h2>Add a facility</h2><form class="formgrid" method="post" action="{{ url_for('add_facility') }}"><label>Facility name<input name="name" required></label><label>Facility type<select name="facility_type"><option>PHC</option><option>District Hospital</option><option>Sub-District Hospital</option><option>Rural Hospital</option><option>Rural/Cottage Hospital</option></select></label><label>Taluka<input name="taluka" required></label><label>Total beds (sample)<input type="number" min="0" name="total_beds" value="0" required></label><label>Available beds (sample)<input type="number" min="0" name="available_beds" value="0" required></label><label>Contact (sample)<input name="phone" value="Not verified"></label><div><button class="btn">Add facility</button></div></form></section><section class="panel" style="margin-top:16px"><h2>Facility records</h2><div class="tablewrap"><table><thead><tr><th>Name</th><th>Type</th><th>Taluka</th><th>Beds (sample)</th><th>Actions</th></tr></thead><tbody>{% for h in facilities %}<tr><td><a href="{{ url_for('facility_detail',hid=h.id) }}">{{ h.name }}</a></td><td>{{ h.facility_type }}</td><td>{{ h.taluka }}</td><td>{{ h.available_beds }} / {{ h.total_beds }}</td><td class="actions"><a class="btn light small" href="{{ url_for('edit_facility',hid=h.id) }}">Edit</a><form method="post" action="{{ url_for('delete_facility',hid=h.id) }}" onsubmit="return confirm('Delete this facility?')"><button class="btn small" style="background:#a83232">Delete</button></form></td></tr>{% endfor %}</tbody></table></div></section>'''

EDIT = '''<section class="panel"><a href="{{ url_for('officials') }}">← Back to officials dashboard</a><h1>Edit facility</h1><form class="formgrid" method="post"><label>Facility name<input name="name" value="{{ h.name }}" required></label><label>Facility type<select name="facility_type">{% for t in types %}<option {% if t==h.facility_type %}selected{% endif %}>{{ t }}</option>{% endfor %}</select></label><label>Taluka<input name="taluka" value="{{ h.taluka }}" required></label><label>Total beds (sample)<input type="number" min="0" name="total_beds" value="{{ h.total_beds }}" required></label><label>Available beds (sample)<input type="number" min="0" name="available_beds" value="{{ h.available_beds }}" required></label><label>Contact (sample)<input name="phone" value="{{ h.phone }}"></label><div><button class="btn">Save changes</button></div></form><p class="hint">Doctor and department entries are demonstration content in this prototype.</p></section>'''


def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c


def init_db():
    with connect() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS facilities(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, facility_type TEXT NOT NULL,
            district TEXT NOT NULL DEFAULT 'Satara', taluka TEXT NOT NULL, total_beds INTEGER NOT NULL DEFAULT 0,
            available_beds INTEGER NOT NULL DEFAULT 0, staff_count INTEGER NOT NULL DEFAULT 0,
            medicine_stock INTEGER NOT NULL DEFAULT 0, case_count INTEGER NOT NULL DEFAULT 0,
            address TEXT NOT NULL DEFAULT 'Address not verified — sample listing',
            phone TEXT NOT NULL DEFAULT 'Not verified — sample listing',
            opening_hours TEXT NOT NULL DEFAULT 'Sample: 9:00 AM–5:00 PM',
            emergency TEXT NOT NULL DEFAULT 'Not verified — contact facility',
            medicine_status TEXT NOT NULL DEFAULT 'Sample: availability not verified',
            last_updated TEXT NOT NULL DEFAULT 'Sample data — not a live update',
            data_source TEXT NOT NULL DEFAULT 'Official PHC directory name; other details are sample data')''')
        c.execute('''CREATE TABLE IF NOT EXISTS departments(id INTEGER PRIMARY KEY AUTOINCREMENT, facility_id INTEGER NOT NULL, name TEXT NOT NULL, FOREIGN KEY(facility_id) REFERENCES facilities(id) ON DELETE CASCADE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS doctors(id INTEGER PRIMARY KEY AUTOINCREMENT, facility_id INTEGER NOT NULL, name TEXT NOT NULL, specialization TEXT NOT NULL, department TEXT NOT NULL, timings TEXT NOT NULL, FOREIGN KEY(facility_id) REFERENCES facilities(id) ON DELETE CASCADE)''')
        if c.execute('SELECT COUNT(*) FROM facilities').fetchone()[0] == 0:
            seed = [('Satara District Hospital','District Hospital','Satara',120,24),('Karad Rural Hospital','Rural Hospital','Karad',60,8),('Wai Rural Hospital','Rural Hospital','Wai',45,10),('Rural Hospital Koregaon','Rural Hospital','Koregaon',40,9),('Rural Hospital Phaltan','Rural Hospital','Phaltan',50,11),('Rural Hospital Dahiwadi','Rural Hospital','Man',35,7),('Rural Hospital Patan','Rural Hospital','Patan',40,8),('Rural Hospital Mahabaleshwar','Rural Hospital','Mahabaleshwar',30,6),('Rural Hospital Khandala','Rural Hospital','Khandala',30,5),('Rural Hospital Medha','Rural Hospital','Jawali',25,5)]
            for name,typ,taluka,total,avail in seed:
                c.execute('INSERT INTO facilities(name,facility_type,taluka,total_beds,available_beds,staff_count,medicine_stock,case_count) VALUES(?,?,?,?,?,?,?,?)',(name,typ,taluka,total,avail,20,50,10))
            for name,taluka in PHCS:
                c.execute('INSERT INTO facilities(name,facility_type,taluka,total_beds,available_beds,staff_count,medicine_stock,case_count) VALUES(?,?,?,?,?,?,?,?)',(name,'PHC',taluka,20,5,12,25,8))
        # Seed illustrative departments/doctors for every facility, clearly marked as sample in the UI.
        if c.execute('SELECT COUNT(*) FROM departments').fetchone()[0] == 0:
            for f in c.execute('SELECT id,facility_type FROM facilities').fetchall():
                dept_names = ['General Medicine','Maternal & Child Health','Immunization'] if f['facility_type']=='PHC' else ['General Medicine','Emergency','Maternity','Paediatrics']
                for d in dept_names:
                    c.execute('INSERT INTO departments(facility_id,name) VALUES(?,?)',(f['id'],d))
                c.execute('INSERT INTO doctors(facility_id,name,specialization,department,timings) VALUES(?,?,?,?,?)',(f['id'],'Sample Doctor A','General Physician','General Medicine','Sample: 9:00 AM–1:00 PM'))
                c.execute('INSERT INTO doctors(facility_id,name,specialization,department,timings) VALUES(?,?,?,?,?)',(f['id'],'Sample Doctor B','Medical Officer','Maternal & Child Health' if f['facility_type']=='PHC' else 'Emergency','Sample: 2:00 PM–5:00 PM'))


def page(title, content, **context):
    return render_template_string(BASE, title=title, content=render_template_string(content, **context))


def officials_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.path))
        return fn(*args, **kwargs)
    return wrapper


@app.route('/')
def home():
    q = request.args.get('q','').strip()
    typ = request.args.get('type','').strip()
    sql = 'SELECT * FROM facilities WHERE 1=1'
    args = []
    if q:
        sql += ' AND (name LIKE ? OR taluka LIKE ? OR district LIKE ?)'
        args += [f'%{q}%'] * 3
    if typ:
        sql += ' AND facility_type=?'; args.append(typ)
    sql += ' ORDER BY CASE facility_type WHEN "District Hospital" THEN 0 WHEN "Rural Hospital" THEN 1 ELSE 2 END, taluka, name'
    with connect() as c:
        facilities = c.execute(sql,args).fetchall()
        total = c.execute('SELECT COUNT(*) FROM facilities').fetchone()[0]
        types = [r[0] for r in c.execute('SELECT DISTINCT facility_type FROM facilities ORDER BY facility_type').fetchall()]
    return page('Find care', HOME, facilities=facilities, total=total, q=q, types=types, selected_type=typ)


@app.route('/facility/<int:hid>')
def facility_detail(hid):
    with connect() as c:
        h = c.execute('SELECT * FROM facilities WHERE id=?',(hid,)).fetchone()
        if not h: abort(404)
        departments = c.execute('SELECT name FROM departments WHERE facility_id=? ORDER BY name',(hid,)).fetchall()
        doctors = c.execute('SELECT * FROM doctors WHERE facility_id=? ORDER BY name',(hid,)).fetchall()
    services = ['OPD consultation','Basic health services','Preventive care'] if h['facility_type']=='PHC' else ['OPD consultation','Emergency care','Basic diagnostic services','Maternity care']
    return page(h['name'], DETAIL, h=h, departments=departments, doctors=doctors, services=services)


@app.route('/officials/login', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USERNAME and request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = ADMIN_USERNAME
            return redirect(url_for('officials'))
        flash('Incorrect username or password.', 'error')
    return page('Officials login', LOGIN)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/officials')
@officials_required
def officials():
    with connect() as c:
        facilities = c.execute('SELECT * FROM facilities ORDER BY taluka,name').fetchall()
        summary = c.execute('SELECT COUNT(*) count,COALESCE(SUM(total_beds),0) total,COALESCE(SUM(available_beds),0) available,SUM(CASE WHEN facility_type="PHC" THEN 1 ELSE 0 END) phcs FROM facilities').fetchone()
    return page('Officials dashboard', OFFICIALS, facilities=facilities, summary=summary, username=session.get('username','admin'))


def form_facility():
    name = request.form.get('name','').strip()
    typ = request.form.get('facility_type','PHC').strip()
    taluka = request.form.get('taluka','').strip()
    phone = request.form.get('phone','Not verified — sample listing').strip() or 'Not verified — sample listing'
    total = int(request.form.get('total_beds','0'))
    avail = int(request.form.get('available_beds','0'))
    if not name or not taluka or total < 0 or avail < 0 or avail > total:
        raise ValueError('Please enter valid details. Available beds must not exceed total beds.')
    return name, typ, taluka, total, avail, phone


@app.route('/officials/add', methods=['POST'])
@officials_required
def add_facility():
    try:
        values = form_facility()
        with connect() as c:
            c.execute('INSERT INTO facilities(name,facility_type,taluka,total_beds,available_beds,phone) VALUES(?,?,?,?,?,?)',values)
            hid = c.execute('SELECT last_insert_rowid()').fetchone()[0]
            for d in ['General Medicine','Maternal & Child Health','Immunization']:
                c.execute('INSERT INTO departments(facility_id,name) VALUES(?,?)',(hid,d))
            c.execute('INSERT INTO doctors(facility_id,name,specialization,department,timings) VALUES(?,?,?,?,?)',(hid,'Sample Doctor','General Physician','General Medicine','Sample timings — verify locally'))
        flash('Facility added. Its non-directory details are sample data until verified.')
    except (ValueError, TypeError):
        flash('Please enter valid details. Available beds must not exceed total beds.','error')
    return redirect(url_for('officials'))


@app.route('/officials/edit/<int:hid>', methods=['GET','POST'])
@officials_required
def edit_facility(hid):
    with connect() as c:
        h = c.execute('SELECT * FROM facilities WHERE id=?',(hid,)).fetchone()
        if not h: abort(404)
        if request.method == 'POST':
            try:
                values = form_facility()
                c.execute('UPDATE facilities SET name=?,facility_type=?,taluka=?,total_beds=?,available_beds=?,phone=? WHERE id=?',values+(hid,))
                flash('Facility updated.')
                return redirect(url_for('officials'))
            except (ValueError, TypeError):
                flash('Please enter valid details. Available beds must not exceed total beds.','error')
    types = ['PHC','District Hospital','Sub-District Hospital','Rural Hospital','Rural/Cottage Hospital']
    return page('Edit facility', EDIT, h=h, types=types)


@app.route('/officials/delete/<int:hid>', methods=['POST'])
@officials_required
def delete_facility(hid):
    with connect() as c:
        c.execute('DELETE FROM facilities WHERE id=?',(hid,))
    flash('Facility deleted.')
    return redirect(url_for('officials'))


@app.errorhandler(404)
def not_found(_):
    return page('Not found', '<section class="panel"><h1>Facility not found</h1><p>The requested facility may have been removed.</p><a class="btn" href="{{ url_for(\'home\') }}">Back to directory</a></section>'), 404


with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)
