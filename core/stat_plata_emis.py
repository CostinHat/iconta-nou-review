# -*- coding: utf-8 -*-
"""core/stat_plata_emis.py — statul de plată ca DOCUMENT EMIS, nu ca vedere recalculată.

DE CE. Până azi `stat_plata()` recalcula totul la fiecare afișare. Un fluturaș tipărit în ianuarie și
redeschis în iulie putea ieși ALTFEL — nu fiindcă greșise cineva, ci fiindcă între timp se schimbase o
cotă, salariul minim sau codul. Pentru un act semnat și dat unui om, cifra din mâna lui și cifra din
aplicație trebuie să fie același document. (DATORIE 29.07.2026, restatuată 20.08.2026.)

ACTUL, decis 21.08.2026:
  - `emite()` îngheață exemplarul: cifrele (JSONB) + AMPRENTA lor. Idempotent — apăsat de două ori nu
    produce două documente.
  - `verifica()` compară amprenta EMISĂ cu recalculul de ACUM. Contradicția e DERIVATĂ din comparație,
    nu ținută într-un câmp: nu există nimic de pus pe zero ca să dispară.
  - `motiveaza()` o marchează ASUMATĂ (cu cine + când). Rămâne în listă. «Nu se stinge prin ignorare.»
  - `corectie()` scrie AL DOILEA EXEMPLAR, care îl referă pe primul. Primul nu se atinge — el e cel
    care a ajuns la salariat. Corecția o apasă CONTABILUL; `verifica()` nu emite niciodată nimic.

AMPRENTA acoperă sumele documentului + CNP-ul (identitatea celui plătit), nu numele afișat și nu
starea interfeței. Motivul e practic: o corectare de diacritice în nume sau un câmp nou de editare ar
aprinde gardul pe toate fluturașii din istorie, iar un gard cu fals-pozitive se dezactivează și moare
(GĂRZI regula 3). CNP-ul e altceva: dacă s-a schimbat, documentul chiar e al altcuiva.

CE NU POATE SPUNE. Amprenta nu știe dacă fluturașul a fost PREDAT salariatului — știe doar că a fost
emis. Predarea e un al doilea act, necablat azi (nu există canal de livrare în aplicație). Până
atunci, «emis» e cea mai tare afirmație pe care o poate face.
"""
import json
from decimal import ROUND_HALF_UP, Decimal

from core import amprenta_declaratie as _amp
from core import db

# Sumele care FAC documentul. Tot ce nu e aici (nume afișat, flaguri de interfață, câmpuri de
# editare, IBAN, COR) se poate schimba fără ca fluturașul dat omului să devină alt fluturaș.
CAMPURI = (
    "brut", "cas", "cass", "impozit", "deducere", "net", "cam",
    "cas_suprataxa", "cass_suprataxa",
    "tichete_nominal", "tichete_zile", "tichete_vacanta", "tichete_cultural", "tichete_cresa",
    "cadou", "cass_tichete", "impozit_tichete", "impozit_salariu", "retinut_tichete",
    "valoare_tichete", "total_disponibil", "cost",
    "cm_zile", "cm_brut", "cm_net", "salariu_baza", "facilitate",
)

DDL = """
ALTER TABLE "{s}".state_plata ADD COLUMN IF NOT EXISTS exemplar    INTEGER NOT NULL DEFAULT 1;
ALTER TABLE "{s}".state_plata ADD COLUMN IF NOT EXISTS amprenta    TEXT;
ALTER TABLE "{s}".state_plata ADD COLUMN IF NOT EXISTS date        JSONB;
ALTER TABLE "{s}".state_plata ADD COLUMN IF NOT EXISTS emis_de     TEXT;
ALTER TABLE "{s}".state_plata ADD COLUMN IF NOT EXISTS emis_la     TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE "{s}".state_plata ADD COLUMN IF NOT EXISTS corectie_la INTEGER;
ALTER TABLE "{s}".state_plata ADD COLUMN IF NOT EXISTS motiv       TEXT;
ALTER TABLE "{s}".state_plata ADD COLUMN IF NOT EXISTS motiv_de    TEXT;
ALTER TABLE "{s}".state_plata ADD COLUMN IF NOT EXISTS motiv_la    TIMESTAMPTZ;
-- Vechea UNIQUE (salariat_id, luna) interzicea STRUCTURAL al doilea exemplar: schema codifica statul
-- ca VEDERE (un rand per om per luna), nu ca DOCUMENT. Corectia e un act nou, deci cheia cuprinde si
-- numarul exemplarului.
ALTER TABLE "{s}".state_plata DROP CONSTRAINT IF EXISTS state_plata_salariat_id_luna_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_state_plata_sal_luna_ex
  ON "{s}".state_plata (salariat_id, luna, exemplar);
"""


def aplica(conn, schema):
    """Idempotent. Mirror în tenant_template.sql; tenanții existenți prin `-m core.migrare_stat_emis`."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


# ------------------------------------------------------------------ motorul (pur)

def _bani(v):
    """Sumele se canonizează HALF_UP la doi zecimali — nu `round()` (bancar), ca peste tot la sume."""
    return str(Decimal(str(v or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def canonic(rand):
    """Reprezentarea stabilă a documentului: chei sortate, sume la doi zecimali, restul ignorat."""
    d = {c: _bani(rand.get(c)) for c in CAMPURI}
    d["cnp"] = (rand.get("cnp") or "").strip()
    return json.dumps(d, sort_keys=True, ensure_ascii=False)


def amprenta_rand(rand):
    """SHA-256 al documentului canonizat. Aceeași funcție de amprentă ca la declarațiile depuse
    (`amprenta_declaratie.amprenta`) — o singură implementare, nu două care se pot despărți.
    Normalizarea ei e pe XML (spații între taguri) și e inofensivă pe JSON canonic."""
    return _amp.amprenta(canonic(rand))


def ultimul(exemplare, salariat_id):
    """Documentul CURENT al salariatului: exemplarul cu numărul cel mai mare (corecția, dacă există)."""
    ale_lui = [x for x in exemplare if x["salariat_id"] == salariat_id]
    return max(ale_lui, key=lambda x: x["exemplar"]) if ale_lui else None


def contradictii(exemplare, recalcul):
    """Divergențele DERIVATE: document emis ≠ recalcul de acum. O listă calculată, nu un câmp citit.

    Cine n-are exemplar emis nu apare — absența unui document nu e o divergență (regula bazei nule în
    direcția corectă). Cine are exemplar dar a dispărut din recalcul apare cu `amprenta_curenta=None`:
    un document emis pentru cineva pe care calculul nu-l mai produce e tot o contradicție, nu o
    coincidență."""
    dupa_id = {int(r.get("id") or 0): r for r in recalcul}
    out = []
    for sid in sorted({x["salariat_id"] for x in exemplare}):
        ex = ultimul(exemplare, sid)
        r = dupa_id.get(sid)
        curenta = amprenta_rand(r) if r is not None else None
        if curenta == ex["amprenta"]:
            continue
        out.append({
            "salariat_id": sid,
            "exemplar_id": ex["id"],
            "exemplar": ex["exemplar"],
            "amprenta_emisa": ex["amprenta"],
            "amprenta_curenta": curenta,
            "fel": "lipsa_din_recalcul" if r is None else "cifre_diferite",
            "asumata": bool(ex.get("motiv")),
            "motiv": ex.get("motiv"),
            "motiv_de": ex.get("motiv_de"),
            "motiv_la": ex.get("motiv_la"),
        })
    return out


# ------------------------------------------------------------------ actul (pe bază)

def _luna(an, luna):
    from datetime import date
    return date(an, luna, 1)


def _randuri(conn, schema, an, luna):
    from core import stat_plata_api as _sp
    return _sp.stat_plata(conn, schema, an, luna)


def citeste(conn, schema, an, luna, salariat_id=None):
    """Exemplarele emise pentru luna dată. NU recalculează nimic: întoarce ce s-a dat oamenilor."""
    q = ('SELECT id, salariat_id, exemplar, amprenta, date, emis_de, emis_la, corectie_la, '
         'motiv, motiv_de, motiv_la FROM "%s".state_plata WHERE luna = %%s '
         # `amprenta IS NULL` = rand VECHI, scris ca efect secundar al unui GET /stat-plata (scos pe
         # 20.08, RFC 9110 §9.2.1). Nu e un document emis: n-are cifre inghetate si nimeni nu l-a
         # dat unui om. Masurat 21.08: 2 randuri ramase, pe tenant_003/2026-08. Fara filtrul asta,
         # fluturasul le-ar fi luat drept exemplare si ar fi tiparit NIMIC.
         "AND amprenta IS NOT NULL" % schema)
    p = [_luna(an, luna)]
    if salariat_id is not None:
        q += " AND salariat_id = %s"
        p.append(salariat_id)
    q += " ORDER BY salariat_id, exemplar"
    with conn.cursor() as cur:
        cur.execute(q, p)
        col = [d[0] for d in cur.description]
        return [dict(zip(col, r)) for r in cur.fetchall()]


def _insereaza(conn, schema, r, an, luna, exemplar, de_cine, corectie_la=None):
    with conn.cursor() as cur:
        cur.execute(
            'INSERT INTO "%s".state_plata (salariat_id, luna, venit_brut, zile_lucrate, exemplar, '
            "amprenta, date, emis_de, corectie_la) VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s) "
            "RETURNING id" % schema,
            (int(r["id"]), _luna(an, luna), r.get("brut") or 0, int(r.get("tichete_zile") or 0),
             exemplar, amprenta_rand(r), json.dumps(r, ensure_ascii=False, default=str),
             de_cine, corectie_la))
        return cur.fetchone()[0]


def emite(conn, schema, an, luna, de_cine):
    """Îngheață statul lunii. IDEMPOTENT: cine are deja un exemplar nu primește al doilea — un al
    doilea exemplar e o CORECȚIE, și aia se apasă explicit, nu se produce din reemitere."""
    if not (de_cine or "").strip():
        raise ValueError("emiterea cere autorul: un document fără emitent nu e un act")
    deja = {x["salariat_id"] for x in citeste(conn, schema, an, luna)}
    out = []
    for r in _randuri(conn, schema, an, luna):
        sid = int(r.get("id") or 0)
        if sid in deja:
            continue
        out.append({"id": _insereaza(conn, schema, r, an, luna, 1, de_cine), "salariat_id": sid})
    return out


def verifica(conn, schema, an, luna):
    """Contradicțiile lunii. CITEȘTE — nu scrie, nu emite, nu corectează. Clasa a fost deja arsă o
    dată: o sondă «de audit» a lăsat 24 de rânduri în exact tabelul ăsta (`test_get_fara_scriere`)."""
    ex = citeste(conn, schema, an, luna)
    if not ex:
        return []
    return contradictii(ex, _randuri(conn, schema, an, luna))


def motiveaza(conn, schema, exemplar_id, motiv, de_cine):
    """Asumă o contradicție. Nu o șterge: `contradictii()` o întoarce mai departe, cu `asumata=True`.
    Fără text și fără autor nu se poate — o asumare anonimă nu e o decizie, e o tăcere."""
    if not (motiv or "").strip():
        raise ValueError("motivul nu poate fi gol: o contradicție se asumă cu o rațiune scrisă")
    if not (de_cine or "").strip():
        raise ValueError("motivul cere autorul: cine asumă divergența")
    with conn.cursor() as cur:
        cur.execute('UPDATE "%s".state_plata SET motiv=%%s, motiv_de=%%s, motiv_la=now() '
                    "WHERE id=%%s" % schema, (motiv.strip(), de_cine.strip(), exemplar_id))
        if cur.rowcount != 1:
            raise ValueError("exemplarul %r nu există — nu are ce să asume nimeni" % exemplar_id)


def corectie(conn, schema, salariat_id, an, luna, de_cine):
    """Al doilea exemplar, cu referință la primul. Primul rămâne neatins — el e documentul care a
    ajuns la om, iar un act dat nu se rescrie, se corectează printr-un act nou."""
    if not (de_cine or "").strip():
        raise ValueError("corecția cere autorul")
    ex = citeste(conn, schema, an, luna, salariat_id=salariat_id)
    if not ex:
        raise ValueError("salariatul %r nu are stat emis pe %d-%02d — nu există ce corecta"
                         % (salariat_id, an, luna))
    ultim = max(ex, key=lambda x: x["exemplar"])
    r = next((x for x in _randuri(conn, schema, an, luna) if int(x.get("id") or 0) == salariat_id),
             None)
    if r is None:
        raise ValueError("recalculul nu mai produce niciun rând pentru salariatul %r: contradicția e "
                         "de alt fel (lipsă din calcul), nu se repară cu o corecție de sume"
                         % salariat_id)
    if amprenta_rand(r) == ultim["amprenta"]:
        raise ValueError("nimic de corectat: documentul emis coincide cu recalculul de acum, deci "
                         "corecția ar fi un act fără obiect")
    nid = _insereaza(conn, schema, r, an, luna, ultim["exemplar"] + 1, de_cine,
                     corectie_la=ultim["id"])
    return {"id": nid, "salariat_id": salariat_id, "exemplar": ultim["exemplar"] + 1,
            "corectie_la": ultim["id"], "amprenta": amprenta_rand(r)}
