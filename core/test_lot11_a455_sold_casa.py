# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 455, PRIORITAR] „casa F1 are două solduri în același moment: 294 la refuzul plății, 42 în registrul de casă.
Registrul de casă, contul 5311 și verificarea de sold negativ folosesc aceeași cifră, din aceeași sursă.”

Cauza (măsurată pe F1, 22.10.2026): registrul își aduna soldul din `casa_operatiuni` (numai ce s-a scris din ecranul Casă), iar refuzul
ieșirii din notele pe 5311 — cele două rapoarte Z (5311 = 707, 131 + 121 lei, ciornă) erau în casă pentru refuz (294) și lipseau din
registru (42). Acum o singură sursă: `casa_sold.note_casa` (soldurile de preluare + notele pe 5311); registrul, refuzul la salvare și la
validare și soldul de la 1 ale lunii o citesc pe ea.

Temei: OMFP 2634/2015 anexa 2, Registrul de casă (cod 14-4-7A), anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt: „Registrul de casă
servește ca: - document de înregistrare operativă a încasărilor și plăților în numerar (lei sau valută), efectuate prin casieria entității;
- document de stabilire, la sfârșitul fiecărei zile, a soldului de casă; - document de înregistrare în contabilitate a operațiunilor de
casă. Registrul de casă se întocmește zilnic, pe baza documentelor justificative de încasări și plăți.” Iar la Chitanță (14-4-1): „În
condițiile utilizării aparatelor de marcat electronice fiscale [...] documentul în baza căruia se înregistrează în contabilitate veniturile
aferente încasărilor zilnice este Raportul fiscal de închidere zilnică”.

Schemă efemeră din template, ștearsă la ieșire. Datele de PORNIRE scrise direct (declarat): nota raportului Z și notele manuale pe 5311
sunt scrierile ALTOR module (raportul Z, jurnalul) — aici se probează registrul, nu modulele care le scriu.
"""
import ast
import datetime
import io
import pathlib
import re
from decimal import Decimal

import pytest

from core import casa_api as _ca, casa_sold as _cs, db as _db, jurnal_api as _j, tenant_provisioning as _tprov

_SCH = "efemer_lot11_a455"
_RAD = pathlib.Path(__file__).resolve().parent.parent


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open(_RAD / "tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("SET LOCAL search_path TO %s, public" % _SCH)
            cur.execute("""INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,email,telefon,caen,declarant_nume,declarant_prenume,
                           declarant_functie,platitor_tva) VALUES (1,'F1 SRL','RO14399840','s','B','B','e@x.ro','07','4690','P','I','A',true)""")
        c.commit()
    with _db.get_conn(_SCH) as c:
        with c.cursor() as cur:   # [lotul 13, 683] avansul spre decontare se dă unui salariat din evidență (CNP cu cifra de control verificată)
            cur.execute("INSERT INTO salariati (id, cnp, nume, prenume, data_angajare) OVERRIDING SYSTEM VALUE "
                        "VALUES (1, '1900101400012', 'Popescu', 'Ion', '2026-01-01')")
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _nota(conn, data, debit, credit, suma, sursa, descriere, status="ciorna"):
    """Nota scrisă de ALT modul (raport Z, jurnal) — date de pornire, declarate în antet."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, document_ref) VALUES (%s,%s,%s,%s,%s) RETURNING id",
                    (data, descriere, sursa, status, "DOC " + descriere[:20]))
        iid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)",
                    (iid, debit, credit, Decimal(str(suma))))
    return iid


def _op(data, cat, suma, doc):
    return {"data": data, "categorie": cat, "suma": suma, "document": doc, "partener": "X SRL", "cui": "14399840",
            "avans_destinatie": "stocuri"}


def _sold_zi(reg, zi):
    """Soldul registrului la sfârșitul zilei `zi` (ultimul rând din zi sau de dinainte)."""
    s = reg["sold_initial"]
    for o in reg["operatiuni"]:
        if o["data"] <= zi:
            s = o["sold"]
    return Decimal(s)


def test_f1_registrul_si_refuzul_au_aceeasi_cifra(conn):
    """Cazul F1, refăcut: încasare 242, plată 100, plată 100 (ciornă), rapoartele Z 131 + 121 (ciornă). Refuzul plății de 400 pe 21.10
    spunea 294; registrul spunea 42. Acum amândouă 294, din aceeași sursă."""
    assert _ca.adauga(conn, _SCH, _op("2026-10-08", "ridicare_banca", 242, "DI1")).get("eroare") is None
    assert _ca.adauga(conn, _SCH, _op("2026-10-09", "plata_furnizor", 100, "DP1")).get("eroare") is None
    assert _ca.adauga(conn, _SCH, _op("2026-10-20", "plata_furnizor", 100, "DP3")).get("eroare") is None
    _nota(conn, "2026-10-20", "5311", "707", 131, "horeca_z", "Raport Z 2026-10-20 nr 0042")
    _nota(conn, "2026-10-21", "5311", "707", 121, "horeca_z", "Raport Z 2026-10-21 nr 0043")
    reg = _ca.registru(conn, _SCH, 2026, 10)
    r = _ca.adauga(conn, _SCH, _op("2026-10-21", "plata_furnizor", 400, "DP4"))
    assert r["cod"] == _cs.COD
    cifra_refuz = Decimal(re.search(r"în registru, e ([\d.,]+) lei", r["eroare"]).group(1).replace(".", "").replace(",", "."))
    # OMFP 2634/2015 14-4-7A: registrul stabilește „la sfârșitul fiecărei zile, soldul de casă” — același cu cel din refuz
    assert (cifra_refuz, _sold_zi(reg, "2026-10-21")) == (Decimal("294.00"), Decimal("294.00")), (r["eroare"], reg)
    with conn.cursor() as cur:
        assert _cs.sold_inainte(cur, _SCH, "5311", datetime.date(2026, 10, 22)) == Decimal("294.00")
    assert reg["sold_final"] == "294.00"
    # raportul Z e rând în registru (document de încasare în numerar, 14-4-1), fără acțiuni de Casă
    z = [o for o in reg["operatiuni"] if o["alt_modul"]]
    assert [(o["data"], o["tip"], o["suma"], o["id"], o["categorie_eticheta"]) for o in z] == [
        ("2026-10-20", "incasare", "131.00", None, "notă din raportul Z"), ("2026-10-21", "incasare", "121.00", None, "notă din raportul Z")]


def test_registrul_e_soldul_notelor_in_fiecare_zi(conn):
    """Proprietatea care face reapariția imposibilă: în fiecare zi a lunii, soldul registrului = soldul casei din `casa_sold` (toate
    notele), iar `sold_final_validat` = evidența validată (fișa contului 5311). Și o notă manuală validată 401 = 5311 scrisă din jurnal
    (cazul F2) e rând în registru."""
    _ca.adauga(conn, _SCH, _op("2026-10-05", "ridicare_banca", 1000, "DI1"))
    _nota(conn, "2026-10-06", "401", "5311", 100, "manual", "Plată manuală", status="validata")
    _nota(conn, "2026-10-07", "5311.01", "707", 50, "horeca_z", "Raport Z analitic")
    _ca.adauga(conn, _SCH, dict(_op("2026-10-08", "avans_decontare", 30, "DP1"), salariat_id=1))   # [683] avansul are salariat
    reg = _ca.registru(conn, _SCH, 2026, 10)
    with conn.cursor() as cur:
        for zi in range(1, 32):
            d = datetime.date(2026, 10, zi)
            assert _sold_zi(reg, d.isoformat()) == _cs.sold_inainte(cur, _SCH, "5311", d + datetime.timedelta(days=1)), d
        assert Decimal(reg["sold_final_validat"]) == _cs.sold_inainte(cur, _SCH, "5311", datetime.date(2026, 11, 1), doar_validate=True)
    assert reg["sold_final"] == "920.00" and reg["sold_final_validat"] == "-100.00", reg


def test_raportul_z_nu_intra_in_plafonul_pe_persoana(conn):
    """Raportul Z (încasări de la populație, nenumite) intră în soldul zilei, nu în plafonul de 5.000 lei de la o persoană
    (Legea 70/2015 art.3 alin.(1) lit.a: „în limita unui plafon zilnic de 5.000 lei de la o persoană”)."""
    _nota(conn, "2026-10-20", "5311", "707", 6000, "horeca_z", "Raport Z mare")
    reg = _ca.registru(conn, _SCH, 2026, 10)
    assert [a["cod"] for a in reg["avertismente"]] == [], reg["avertismente"]
    assert reg["sold_final"] == "6000.00"


def test_validarea_e_cel_putin_la_fel_de_stricta_ca_registrul(conn):
    """Două ieșiri în ciornă scrise din jurnal (fără refuz la salvare): validarea celei de 50 trecea pe evidența validată (100 - 50), deși
    registrul (toate notele) arăta casa la -30. Acum validarea o refuză, numind registrul."""
    i = _ca.adauga(conn, _SCH, _op("2026-10-05", "ridicare_banca", 100, "DI1"))
    assert _j.valideaza(conn, _SCH, i["inregistrare_id"]).get("eroare") is None
    _nota(conn, "2026-10-06", "401", "5311", 80, "manual", "Plată 80")
    n50 = _nota(conn, "2026-10-07", "401", "5311", 50, "manual", "Plată 50")
    r = _j.valideaza(conn, _SCH, n50)
    assert r.get("cod") == _cs.COD, r
    # mesajul întreg (câmpul `eroare`), nu un fragment din el: refuzul numește registrul, ziua și soldul lui
    assert r["eroare"] == ("Nota de 50,00 lei nu se validează: în registrul de casă (contul 5311, toate notele, și ciornele, cu ea inclusă) "
                           "soldul pe 07.10.2026 e -30,00 lei, iar casa ajunge la -30,00 lei pe 07.10.2026. Numerarul din casă nu poate fi "
                           "negativ. Înregistrează întâi încasarea sau ridicarea de numerar din care s-a plătit, sau șterge ieșirea în ciornă "
                           "care nu s-a făcut."), r["eroare"]
    reg = _ca.registru(conn, _SCH, 2026, 10)
    assert reg["sold_final"] == "-30.00"   # registrul arată ce e scris; validarea nu lasă cifra în evidență


# ---- GARDA STRUCTURALĂ: nu poate apărea un al doilea calcul al soldului casei ---------------------------------------------------------

_CASA = re.compile(r"""['"]531[14]?%*['"]|LIKE\s+'531""", re.I)
_SUM = re.compile(r"\bsum\s*\(", re.I)
#: singurele SQL-uri care însumează note pe un cont de casă fără să fie soldul casei — fiecare cu motivul (ratchet: unul nou pică)
_PERMISE = {
    ("core/repo_d205_reconciliere.py", "456"): "plata dividendelor interimare (456 = 512x / 531x), nu soldul casei",
}
#: funcțiile soldului casei și singurele module care le cheamă (registrul, refuzul) — un al doilea apelant ar fi un al doilea registru
_APELANTI = {"note_casa": {"core/casa_sold.py", "core/casa_api.py"}, "sold_inainte": {"core/casa_sold.py", "core/casa_api.py"},
             "registru_casa": {"core/casa.py", "core/casa_api.py"}, "sold_final": {"core/casa.py", "core/casa_api.py"}}


def _surse():
    for p in sorted((_RAD / "core").rglob("*.py")) + [_RAD / "main.py"]:
        if p.name.startswith("test_"):   # `rglob("*.py")` nu intră în `__pycache__` (acolo sunt numai `.pyc`)
            continue
        yield p.relative_to(_RAD).as_posix(), ast.parse(p.read_text(encoding="utf-8"))


def _texte(tree):
    for n in ast.walk(tree):
        if isinstance(n, ast.JoinedStr):
            yield "".join(v.value if isinstance(v, ast.Constant) and isinstance(v.value, str) else "{}" for v in n.values)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            yield n.value


def _incalcari(surse):
    out = []
    for f, tree in surse:
        for s in _texte(tree):
            if not _SUM.search(s):
                continue
            # identificatorii SQL-ului (tabele, coloane, literalii), nu sub-șiruri: `casa_operatiuni_arhiva` nu e `casa_operatiuni`
            ident = set(re.findall(r"\w+", s.lower()))
            pe_note = bool(ident & {"inregistrari_linii", "solduri_initiale"}) and _CASA.search(s)
            # SUM pe operațiunile de casă = soldul registrului din `casa_operatiuni` (forma de dinainte de 455); permis numai pe NIR
            pe_operatiuni = ident >= {"casa_operatiuni"} and not ident >= {"nir_id"}
            if f == "core/casa_sold.py" or not (pe_note or pe_operatiuni):
                continue
            if pe_note and any(f == pf and ident >= {k} for pf, k in _PERMISE):
                continue
            out.append((f, s[:120]))
        for n in ast.walk(tree):
            if isinstance(n, ast.Call):
                nm = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", None)
                if nm in _APELANTI and f not in _APELANTI[nm]:
                    out.append((f, "apel %s la linia %d" % (nm, n.lineno)))
    return out


def test_garda_un_singur_calcul_al_soldului_casei():
    """Pică dacă apare în cod un al doilea calcul al soldului casei: un SQL care însumează note / solduri pe 531x în afara
    `casa_sold.py`, un SUM pe `casa_operatiuni` (registrul de dinainte de 455), sau un apelant nou al funcțiilor soldului."""
    assert _incalcari(list(_surse())) == []


def test_garda_prinde_al_doilea_calcul():
    """Garda nu e tautologică: forma veche (registrul din `casa_operatiuni`) și o copie a SQL-ului soldului în alt modul sunt prinse."""
    rau = ast.parse('def f(cur):\n'
                    '    cur.execute("SELECT sum(CASE WHEN tip=\'incasare\' THEN suma ELSE -suma END) FROM casa_operatiuni")\n'
                    '    cur.execute("SELECT sum(l.suma) FROM inregistrari_linii l WHERE l.cont_debit = \'5311\'")\n'
                    '    return _m.registru_casa([], 0)\n')
    assert len(_incalcari([("core/kpi_client.py", rau)])) == 3


def test_692_nota_borderoului_in_casa_nu_e_nota_din_facturile(conn):
    """[lotul 13, 692 / clasa 603] Nota unui borderou de achiziție (sursa `facturi`, factură cu `tip = 'borderou'`) apărea în Registrul de casă
    „notă din facturile”; borderoul (OMFP 2634/2015, cod 14-4-13) nu e o factură. Eticheta se ia și după documentul legat, ca în jurnal.
    MUTAȚIA: `fel_document.get(...)` -> `None` în `casa_api` -> „notă din facturile” -> pică."""
    iid = _nota(conn, "2026-10-12", "371", "5311", 150, "facturi", "Achiziție de la neînregistrat")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, tip, directie) VALUES ('BORD-1', '2026-10-12', 'borderou', 'primita') RETURNING id")
        cur.execute("UPDATE inregistrari SET factura_id = %s WHERE id = %s", (cur.fetchone()[0], iid))
    reg = _ca.registru(conn, _SCH, 2026, 10)
    et = [o["categorie_eticheta"] for o in reg["operatiuni"] if o["alt_modul"]]
    assert et == ["notă din borderoul de achiziție"], et
