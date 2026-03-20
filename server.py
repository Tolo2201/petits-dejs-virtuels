#!/usr/bin/env python3
"""
Petits Déjs Virtuels TogeZer - Serveur de prise de rendez-vous
"""

import sqlite3
import json
import os
import uuid
import tornado.ioloop
import tornado.web
import tornado.httpserver

DB_PATH = os.path.join(os.path.dirname(__file__), 'rdv.db')
EVENT_DATE = "2026-03-25"
SLOTS = [
    "09:00", "09:20", "09:40",
    "10:00", "10:20", "10:40",
    "11:00", "11:20", "11:40",
    "12:00", "12:20", "12:40"
]

RECEPTIFS = [
    {"nom": "African Eagle", "pays": "Kenya", "continent": "Afrique", "contact_nom": "Legeais Cécile", "telephone": "+33624206523", "email": "cecile.legeais@orange.fr"},
    {"nom": "African Eagle", "pays": "Namibie", "continent": "Afrique", "contact_nom": "Christian Mutonji", "telephone": "+264813268386", "email": "cmutonji@tourvestdm.com"},
    {"nom": "All Dreams Cambodia", "pays": "Cambodge", "continent": "Asie - Océanie", "contact_nom": "Jacques Guichandut", "telephone": "+85512579555", "email": "jacques@alldreamscambodia.com"},
    {"nom": "AOV USA", "pays": "USA", "continent": "Amérique", "contact_nom": "Johan Miquel", "telephone": "+33669064338", "email": "aov.floride@gmail.com"},
    {"nom": "Archipel Contact", "pays": "Indonésie", "continent": "Asie - Océanie", "contact_nom": "Sylvie Ponte", "telephone": "+33659884894", "email": "sylvie@archipel.contact.com"},
    {"nom": "Aurora Travel & DMC", "pays": "Vietnam", "continent": "Asie - Océanie", "contact_nom": "Olivier Garessus", "telephone": "+84898154445", "email": "olivier@auroratravel.asia"},
    {"nom": "BB Voyage - IndeXperience", "pays": "Inde", "continent": "Asie - Océanie", "contact_nom": "Veronique Narayana Swamy", "telephone": "+919810623420", "email": "veroraghu@bbvoyageinde.com"},
    {"nom": "Brightside Travel", "pays": "Écosse, Irlande, Angleterre", "continent": "Europe", "contact_nom": "Loic Acosta", "telephone": "+447447013109", "email": "loic@brightside-travel.com"},
    {"nom": "Exact Tours", "pays": "Roumanie", "continent": "Europe", "contact_nom": "Moise Anda-Roxana", "telephone": "+40721332804", "email": "incoming@exact-tours.ro"},
    {"nom": "Feeling Guadeloupe", "pays": "Guadeloupe", "continent": "Amérique", "contact_nom": "Audrey Promeneur", "telephone": "+590690845840", "email": "audrey@feelingguadeloupe.fr"},
    {"nom": "Jean connaît un rayon", "pays": "France - Normandie", "continent": "Europe", "contact_nom": "Pierre Boyer", "telephone": "+33648351672", "email": "pierre.boyer@terra-group.com"},
    {"nom": "Mai Globe Travels", "pays": "Sri Lanka", "continent": "Asie - Océanie", "contact_nom": "Catherine Lebouille", "telephone": "+94773240190", "email": "catherine@maiglobe.com"},
    {"nom": "MekongTouch", "pays": "Vietnam", "continent": "Asie - Océanie", "contact_nom": "Catia Cristao", "telephone": "+33631279719", "email": "catia@mekongtouch.com"},
    {"nom": "Neosafar", "pays": "Liban", "continent": "Moyen Orient", "contact_nom": "Dior Sawaya", "telephone": "+33659237783", "email": "dior.sawaya@gmail.com"},
    {"nom": "Olalalanka", "pays": "Sri Lanka", "continent": "Asie - Océanie", "contact_nom": "Emmanuel Hugot", "telephone": "+94777888459", "email": "contact@olalalanka.com"},
    {"nom": "Outdoor Pyrénées Trekking", "pays": "France - Pyrénées", "continent": "Europe", "contact_nom": "Guillaume Martin", "telephone": "+33661086252", "email": "contact@agence-outdoor.fr"},
    {"nom": "Pura Vida Cabo Verde", "pays": "Cap Vert", "continent": "Afrique", "contact_nom": "Stan Brun", "telephone": "+33687852280", "email": "stan@puravidacaboverde.com"},
    {"nom": "Sense of Oceans", "pays": "Madagascar", "continent": "Afrique", "contact_nom": "Olivier Toboul", "telephone": "+261344962724", "email": "olivier@senseofoceans.com"},
    {"nom": "Sense of Oceans", "pays": "Mozambique", "continent": "Afrique", "contact_nom": "Martijn Mellaart", "telephone": "+27824906888", "email": "mmellaart@tourvestdm.com"},
    {"nom": "Senses of Siam", "pays": "Thaïlande", "continent": "Asie - Océanie", "contact_nom": "Rodolphe Godey", "telephone": "+66958088874", "email": "contact@senses-of-siam.co"},
    {"nom": "Shanti Travel", "pays": "Asie (multi-destinations)", "continent": "Asie - Océanie", "contact_nom": "Jérémy", "telephone": "", "email": "jeremy@shantitravel.com"},
    {"nom": "Soprasi", "pays": "Portugal", "continent": "Europe", "contact_nom": "Emeline Breant", "telephone": "+351962114763", "email": "info@soprasi.com"},
    {"nom": "Tanganyika Expeditions", "pays": "Tanzanie", "continent": "Afrique", "contact_nom": "Laurent Gavache", "telephone": "+33619398800", "email": "laurent@tanganyika.com"},
    {"nom": "Terra Africa", "pays": "Afrique du Sud", "continent": "Afrique", "contact_nom": "Thibault Jeannin", "telephone": "+33624969584", "email": "gm@terra.africa.com"},
    {"nom": "Terra Australia", "pays": "Australie", "continent": "Asie - Océanie", "contact_nom": "Christophe Napierai", "telephone": "+33659517258", "email": "manager@terra-australia.com.au"},
    {"nom": "Terra Balka", "pays": "Croatie, Slovénie & Monténégro", "continent": "Europe", "contact_nom": "Florian Servant", "telephone": "+33763219463", "email": "florian@terra-balka.com"},
    {"nom": "Terra Bolivia", "pays": "Bolivie", "continent": "Amérique", "contact_nom": "Lucie Gosnet", "telephone": "+59173209652", "email": "gerencia@terra-bolivia.com"},
    {"nom": "Terra Brazil", "pays": "Brésil", "continent": "Amérique", "contact_nom": "Samuel", "telephone": "", "email": "contact@terra-brazil.com"},
    {"nom": "Terra Caribea", "pays": "Costa Rica", "continent": "Amérique", "contact_nom": "Laura Grenouillet", "telephone": "+50688631070", "email": "gerencia@terra-caribea.com"},
    {"nom": "Terra Chile", "pays": "Chili", "continent": "Amérique", "contact_nom": "Eric Quillévéré", "telephone": "+34655812479", "email": "eric.quillevere@terra-group.com"},
    {"nom": "Terra Colombia & Panamerica", "pays": "Colombie, Canada, Nicaragua", "continent": "Amérique", "contact_nom": "Constance Faysse", "telephone": "+33768766783", "email": "constance.faysse@terra-group.com"},
    {"nom": "Terra Ecuador", "pays": "Équateur", "continent": "Amérique", "contact_nom": "Laura Mauro", "telephone": "+593986214186", "email": "laura@terra-ecuador.com"},
    {"nom": "Terra Guatemala", "pays": "Guatemala", "continent": "Amérique", "contact_nom": "Tristan Reger", "telephone": "+50235736082", "email": "tristan.reger@terra-group.com"},
    {"nom": "Terra Perou", "pays": "Pérou", "continent": "Amérique", "contact_nom": "Vicky Minaya", "telephone": "+51940203741", "email": "gerencia@terra-peru.com"},
    {"nom": "Tierra Latina", "pays": "Argentine", "continent": "Amérique", "contact_nom": "Chloé Proust", "telephone": "+33628229162", "email": "chloe@tierra-latina.com"},
    {"nom": "Viasuntours", "pays": "Grèce", "continent": "Europe", "contact_nom": "Charles", "telephone": "+306936021114", "email": "charles@viasuntours.gr"},
    {"nom": "Xplore Mexique", "pays": "Mexique", "continent": "Amérique", "contact_nom": "Benjamin Senoussi", "telephone": "+33683112966", "email": "benjamin@xplore-voyages.com"},
]

# Emoji flags for continents
CONTINENT_EMOJI = {
    "Afrique": "🌍",
    "Asie - Océanie": "🌏",
    "Amérique": "🌎",
    "Europe": "🇪🇺",
    "Moyen Orient": "🕌",
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS receptifs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        pays TEXT,
        continent TEXT,
        contact_nom TEXT,
        telephone TEXT,
        email TEXT,
        admin_token TEXT UNIQUE
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receptif_id INTEGER,
        heure TEXT,
        statut TEXT DEFAULT 'disponible',
        FOREIGN KEY (receptif_id) REFERENCES receptifs(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slot_id INTEGER UNIQUE,
        agence_nom TEXT,
        contact_nom TEXT,
        email TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (slot_id) REFERENCES slots(id)
    )''')
    conn.commit()

    # Seed receptifs if empty
    c.execute('SELECT COUNT(*) FROM receptifs')
    if c.fetchone()[0] == 0:
        print("\n=== INITIALISATION DE LA BASE DE DONNÉES ===")
        print(f"{'RÉCEPTIF':<40} {'PAYS':<35} {'TOKEN ADMIN'}")
        print("-" * 110)
        for r in RECEPTIFS:
            token = uuid.uuid4().hex[:12]
            c.execute('''INSERT INTO receptifs (nom, pays, continent, contact_nom, telephone, email, admin_token)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (r['nom'], r['pays'], r['continent'], r['contact_nom'], r['telephone'], r['email'], token))
            receptif_id = c.lastrowid
            # Create slots
            for heure in SLOTS:
                c.execute('INSERT INTO slots (receptif_id, heure, statut) VALUES (?, ?, ?)',
                         (receptif_id, heure, 'disponible'))
            label = f"{r['nom']} ({r['pays']})"
            print(f"{label:<40} {r['pays']:<35} http://localhost:5001/admin?token={token}")
        conn.commit()
        print("=" * 110)
        print()
    conn.close()


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")

    def options(self, *args):
        self.set_status(204)
        self.finish()

    def get_db(self):
        return get_db()

    def json_response(self, data, status=200):
        self.set_status(status)
        self.write(json.dumps(data, ensure_ascii=False))
        self.finish()

    def error(self, msg, status=400):
        self.json_response({"error": msg}, status)


class ReceptifsHandler(BaseHandler):
    def get(self):
        continent = self.get_argument("continent", None)
        pays = self.get_argument("pays", None)
        conn = self.get_db()
        c = conn.cursor()
        query = "SELECT * FROM receptifs"
        params = []
        conditions = []
        if continent:
            conditions.append("continent = ?")
            params.append(continent)
        if pays:
            conditions.append("pays LIKE ?")
            params.append(f"%{pays}%")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY continent, nom"
        c.execute(query, params)
        rows = [dict(r) for r in c.fetchall()]

        # Add slot counts
        for row in rows:
            c.execute("SELECT COUNT(*) FROM slots WHERE receptif_id=? AND statut='disponible'", (row['id'],))
            row['slots_disponibles'] = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM slots WHERE receptif_id=? AND statut='reserve'", (row['id'],))
            row['slots_reserves'] = c.fetchone()[0]
            row['total_slots'] = len(SLOTS)
            row['emoji'] = CONTINENT_EMOJI.get(row['continent'], '🌐')
        conn.close()
        self.json_response(rows)


class SlotsHandler(BaseHandler):
    def get(self, receptif_id):
        conn = self.get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM receptifs WHERE id=?", (receptif_id,))
        receptif = c.fetchone()
        if not receptif:
            conn.close()
            return self.error("Réceptif introuvable", 404)

        c.execute("""
            SELECT s.*, r.agence_nom, r.contact_nom as resa_contact, r.email as resa_email
            FROM slots s
            LEFT JOIN reservations r ON s.id = r.slot_id
            WHERE s.receptif_id = ?
            ORDER BY s.heure
        """, (receptif_id,))
        slots = [dict(s) for s in c.fetchall()]
        conn.close()
        self.json_response({
            "receptif": dict(receptif),
            "slots": slots,
            "event_date": EVENT_DATE
        })


class BookingHandler(BaseHandler):
    def post(self):
        try:
            data = json.loads(self.request.body)
        except:
            return self.error("JSON invalide")

        slot_id = data.get("slot_id")
        agence_nom = data.get("agence_nom", "").strip()
        contact_nom = data.get("contact_nom", "").strip()
        email = data.get("email", "").strip()

        if not all([slot_id, agence_nom, contact_nom, email]):
            return self.error("Tous les champs sont obligatoires")

        conn = self.get_db()
        c = conn.cursor()

        # Check slot exists and is available
        c.execute("SELECT * FROM slots WHERE id=? AND statut='disponible'", (slot_id,))
        slot = c.fetchone()
        if not slot:
            conn.close()
            return self.error("Ce créneau n'est plus disponible", 409)

        # Create booking
        c.execute("UPDATE slots SET statut='reserve' WHERE id=?", (slot_id,))
        c.execute("""INSERT INTO reservations (slot_id, agence_nom, contact_nom, email)
                    VALUES (?, ?, ?, ?)""", (slot_id, agence_nom, contact_nom, email))
        conn.commit()

        # Get receptif info
        c.execute("SELECT r.nom, r.pays, r.contact_nom FROM receptifs r JOIN slots s ON s.receptif_id = r.id WHERE s.id=?", (slot_id,))
        rec = c.fetchone()
        conn.close()

        self.json_response({
            "success": True,
            "message": f"Rendez-vous confirmé avec {rec['nom']} ({rec['pays']}) à {slot['heure']}",
            "details": {
                "receptif": rec['nom'],
                "pays": rec['pays'],
                "interlocuteur": rec['contact_nom'],
                "heure": slot['heure'],
                "date": EVENT_DATE
            }
        })


class AdminHandler(BaseHandler):
    def get(self):
        token = self.get_argument("token", None)
        if not token:
            return self.error("Token manquant", 401)
        conn = self.get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM receptifs WHERE admin_token=?", (token,))
        receptif = c.fetchone()
        if not receptif:
            conn.close()
            return self.error("Token invalide", 401)

        c.execute("""
            SELECT s.*, r.agence_nom, r.contact_nom as resa_contact, r.email as resa_email
            FROM slots s
            LEFT JOIN reservations r ON s.id = r.slot_id
            WHERE s.receptif_id = ?
            ORDER BY s.heure
        """, (receptif['id'],))
        slots = [dict(s) for s in c.fetchall()]
        conn.close()
        self.json_response({
            "receptif": dict(receptif),
            "slots": slots,
            "event_date": EVENT_DATE
        })

    def post(self):
        token = self.get_argument("token", None)
        if not token:
            return self.error("Token manquant", 401)
        try:
            data = json.loads(self.request.body)
        except:
            return self.error("JSON invalide")

        slot_id = data.get("slot_id")
        action = data.get("action")  # 'bloquer' or 'debloquer'

        conn = self.get_db()
        c = conn.cursor()
        c.execute("SELECT r.id FROM receptifs r JOIN slots s ON s.receptif_id = r.id WHERE r.admin_token=? AND s.id=?", (token, slot_id))
        if not c.fetchone():
            conn.close()
            return self.error("Non autorisé", 403)

        c.execute("SELECT statut FROM slots WHERE id=?", (slot_id,))
        slot = c.fetchone()
        if not slot:
            conn.close()
            return self.error("Créneau introuvable", 404)

        if action == 'bloquer' and slot['statut'] == 'disponible':
            c.execute("UPDATE slots SET statut='bloque' WHERE id=?", (slot_id,))
            conn.commit()
            conn.close()
            self.json_response({"success": True, "statut": "bloque"})
        elif action == 'debloquer' and slot['statut'] == 'bloque':
            c.execute("UPDATE slots SET statut='disponible' WHERE id=?", (slot_id,))
            conn.commit()
            conn.close()
            self.json_response({"success": True, "statut": "disponible"})
        else:
            conn.close()
            self.error("Action impossible sur ce créneau")


class ContinentsHandler(BaseHandler):
    def get(self):
        conn = self.get_db()
        c = conn.cursor()
        c.execute("SELECT DISTINCT continent FROM receptifs ORDER BY continent")
        continents = [r[0] for r in c.fetchall()]
        c.execute("SELECT DISTINCT pays FROM receptifs ORDER BY pays")
        pays = [r[0] for r in c.fetchall()]
        conn.close()
        self.json_response({"continents": continents, "pays": pays})


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        public_dir = os.path.join(os.path.dirname(__file__), 'public')
        with open(os.path.join(public_dir, 'index.html'), 'r', encoding='utf-8') as f:
            self.write(f.read())


def make_app():
    public_dir = os.path.join(os.path.dirname(__file__), 'public')
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/admin", MainHandler),
        (r"/api/receptifs", ReceptifsHandler),
        (r"/api/receptifs/(\d+)/slots", SlotsHandler),
        (r"/api/bookings", BookingHandler),
        (r"/api/admin", AdminHandler),
        (r"/api/filters", ContinentsHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": public_dir}),
    ])


if __name__ == "__main__":
    init_db()
    app = make_app()
    port = int(os.environ.get("PORT", 5001))
    app.listen(port)
    print(f"✅ Serveur démarré sur http://localhost:{port}")
    print(f"📅 Événement : Petits Déjs Virtuels - {EVENT_DATE}")
    print(f"🔗 Ouvrir : http://localhost:{port}")
    tornado.ioloop.IOLoop.current().start()
