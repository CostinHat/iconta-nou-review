# -*- coding: utf-8 -*-
"""core/inchidere_an.py — propunerea notei de închidere a exercițiului (varianta (a), decizia Costin 13.10.2026, verbatim în DECIZII):

  „Aplicația propune, la cererea contabilului, nota de închidere la 31.12: clasele 6/7 → 121 și regularizarea TVA 4426/4427 →
  4423/4424. Nota apare ca propunere și intră în evidență numai după ce contabilul o validează (R36).”

Din soldurile la 31.12 ale notelor VALIDATE (`bilant_api.sold_la`) se scriu două note CIORNĂ, datate 31.12, `sursa='inchidere_an'`, cu
documentul intern „Notă de calcul” (Legea 82/1991 art.6 alin.(1)):
  1. regularizarea TVA (`motor.regularizare_tva`): 4427 = 4426, diferența 4427 = 4423 sau 4424 = 4426;
  2. închiderea claselor 6 / 7 (`motor.inchidere_din_solduri`): 7xx = 121, 121 = 6xx.
TEMEI: OMFP 1802/2014, funcțiunea contului 121 și a conturilor 4423 / 4424 / 4426 / 4427 (`motor.TEMEI_INCHIDERE`,
`motor.TEMEI_REGULARIZARE_TVA`).

O propunere nevalidată (ciornă, respinsă) a aceluiași 31.12 se înlocuiește la o nouă cerere — documentul ei intern se păstrează, fără
număr nou; o propunere VALIDATĂ nu se atinge: o cerere ulterioară închide numai ce a rămas cu sold (o notă de după validare). O ciornă
aflată la validare în coadă nu se înlocuiește sub ochii cabinetului: refuz.

[deficiența 243, retestul Costin 13.10.2026, comanda 14.10 pct.2, verbatim în DECIZII] „nota de închidere se poate propune pentru un an
neîncheiat; operațiunile ulterioare o fac greșită, iar după validare nu se mai corectează. Fie permiți propunerea numai după 31.12, fie
avertizezi și recalculezi înainte de validare. Alege varianta mai sigură și spune de ce.” Aleasă: propunerea NUMAI după 31.12 (`an_incheiat`)
— înainte de sfârșitul anului operațiunile ulterioare sunt sigure, nu o excepție; un avertisment se poate trece cu vederea, un refuz nu.
Același drum (o notă de închidere care nu mai e a soldurilor) rămâne deschis după 31.12, prin operațiunile anului validate târziu: de aceea
validarea (`refuz_validare`, din `jurnal_api.valideaza` — jurnalul și coada) refuză nota de închidere a unui an neîncheiat ȘI pe cea care
nu mai corespunde soldurilor validate de acum. Nota validată nu se modifică: o operațiune validată după ea redeschide refuzul bilanțului,
iar o nouă propunere închide numai ce a rămas cu sold."""
import datetime
from decimal import Decimal

from core.pdf_util import data_ro as _data_ro

from core import bilant_api as _ba
from core import motor as _m
from core import eticheta_nota as _et
from core import note_derivate as _nd
from core import repo_contabilitate as _rc

SURSA = "inchidere_an"
DESCRIERE_TVA = "Regularizarea TVA la 31.12.%d"
DESCRIERE_INCHIDERE = "Închiderea conturilor de venituri și cheltuieli în 121 la 31.12.%d"


MESAJ_AN_NEINCHEIAT = ("Nota de închidere pe %d se propune după 31.12.%d: până la sfârșitul anului urmează operațiuni care schimbă "
                       "soldurile de închis, iar nota validată nu se mai modifică.")


def an_incheiat(an, azi=None):
    """[243] Anul `an` s-a încheiat = decembrie lui s-a încheiat, după aceeași regulă (și ziua României) ca închiderea lunii, amortizarea
    și salariile (`inchidere_luna.luna_in_curs`, sursa unică; deficiența 216)."""
    from core import inchidere_luna as _il
    return _il.luna_in_curs(an, 12, azi) is None


def propunere(solduri):
    """{"tva": [note], "inchidere": [note], "rezultat": Decimal} — calcul PUR, din soldurile la 31.12."""
    inchidere = _m.inchidere_din_solduri(solduri)
    rez = sum(((n["suma"] if n["credit"] == "121" else -n["suma"]) for n in inchidere), Decimal("0"))
    return {"tva": _m.regularizare_tva(solduri), "inchidere": inchidere, "rezultat": rez}


def _ciorne_existente(cur, schema, zi):
    cur.execute(f"SELECT id, descriere FROM {schema}.inregistrari WHERE sursa = %s AND data = %s AND status = 'ciorna' ORDER BY id",
                (SURSA, zi))
    return [(r["id"], r["descriere"]) if isinstance(r, dict) else (r[0], r[1]) for r in cur.fetchall()]


def propune(cur, schema, an):
    """Scrie propunerea pe 31.12.`an` (cursor RealDictCursor, în tranzacția apelantului). Întoarce {"note": [{id, descriere, linii,
    document}], "rezultat", "inlocuite", "nimic"}; ValueError cu motivul când nu se poate (an dinaintea soldurilor de preluare, o ciornă
    la validare)."""
    from core import coada_api as _coada
    if not an_incheiat(an):
        raise ValueError(MESAJ_AN_NEINCHEIAT % (an, an))
    zi = datetime.date(an, 12, 31)
    s = _ba.sold_la(cur, schema, zi)
    if s is None:
        raise ValueError("Nota de închidere pe %d nu se poate propune: soldurile de la 31.12.%d nu sunt în aplicație (evidența firmei "
                         "începe după soldurile de preluare)." % (an, an))
    vechi = _ciorne_existente(cur, schema, zi)
    for nid, _d in vechi:
        if _coada.nota_la_validare(cur, schema, nid):
            raise ValueError("Propunerea de închidere (nota %s) e la validare în coadă — nu se înlocuiește cât o verifică cabinetul."
                             % _et.nota(cur, schema, nid))
    doc_vechi = {d: _rc.documentul_notei(cur, schema, nid) for nid, d in vechi}
    for nid, _d in vechi:
        if _nd.respinsa(cur, schema, nid):
            _nd.sterge_respinsa(cur, schema, nid)
        else:
            _nd.sterge_ciorna_inlocuita(cur, schema, nid)
    p = propunere(s)
    note = []
    for descriere, linii in ((DESCRIERE_TVA % an, p["tva"]), (DESCRIERE_INCHIDERE % an, p["inchidere"])):
        if not linii:
            continue
        doc = doc_vechi.get(descriere)
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref)
                        VALUES (%s, %s, %s, 'ciorna', %s) RETURNING id""", (zi, descriere, SURSA, doc))
        r = cur.fetchone()
        nid = r["id"] if isinstance(r, dict) else r[0]
        if not doc:
            _rc._cu_document_intern(cur, schema, "nota_calcul", zi, r)
        for n in linii:
            _rc.adauga_linie(cur, schema, nid, n["debit"], n["credit"], n["suma"])
        note.append({"id": nid, "descriere": descriere, "linii": [(n["debit"], n["credit"], str(n["suma"])) for n in linii],
                     "document": _rc.documentul_notei(cur, schema, nid)})
    return {"note": note, "rezultat": p["rezultat"], "inlocuite": [nid for nid, _d in vechi], "nimic": not note}


def _linii(cur, schema, nota_id):
    cur.execute(f"SELECT cont_debit, cont_credit, suma FROM {schema}.inregistrari_linii WHERE inregistrare_id = %s", (nota_id,))
    return sorted((r["cont_debit"], r["cont_credit"], Decimal(r["suma"])) if isinstance(r, dict) else (r[0], r[1], Decimal(r[2]))
                  for r in cur.fetchall())


def corespunde(cur, schema, nota_id, zi):
    """[243] Nota de închidere e încă a soldurilor de la `zi` (31.12) din notele VALIDATE de acum? = liniile ei sunt exact una din cele două
    părți ale propunerii recalculate acum (regularizarea TVA sau închiderea 6 / 7; o parte validată deja nu o schimbă pe cealaltă)."""
    s = _ba.sold_la(cur, schema, zi)
    if s is None:
        return False
    p = propunere(s)
    are = _linii(cur, schema, nota_id)
    return bool(are) and any(are == sorted((n["debit"], n["credit"], Decimal(n["suma"])) for n in parte)
                             for parte in (p["tva"], p["inchidere"]))


def refuz_validare(cur, schema, nota_id, azi=None):
    """[243] Motivul pentru care nota de închidere `nota_id` nu se validează, sau None (nu e o notă de închidere / se poate valida). Chemat
    din `jurnal_api.valideaza`, unicul drum de validare (jurnalul și coada)."""
    cur.execute(f"SELECT data, sursa FROM {schema}.inregistrari WHERE id = %s", (nota_id,))
    r = cur.fetchone()
    zi, sursa = (r["data"], r["sursa"]) if isinstance(r, dict) else (r or (None, None))
    if sursa != SURSA:
        return None
    if not an_incheiat(zi.year, azi):
        return ("Nota de închidere %s nu se validează înainte de 31.12.%d: până la sfârșitul anului urmează operațiuni care schimbă soldurile "
                "de închis, iar nota validată nu se mai modifică. După 31.12.%d propune-o din nou din Bilanț."
                % (_et.nota(cur, schema, nota_id), zi.year, zi.year))
    if not corespunde(cur, schema, nota_id, zi):
        return ("Nota de închidere %s nu mai corespunde soldurilor de la 31.12.%d din notele validate: după propunere s-au validat operațiuni "
                "ale anului sau nota a fost modificată. Propune din nou nota de închidere din Bilanț — o recalculează din soldurile de acum."
                % (_et.nota(cur, schema, nota_id), zi.year))
    return None


def solduri_dupa(cur, schema, s, propuse):
    """[244] Soldurile `s` așa cum vor fi după validarea notelor propuse: celelalte motive ale bilanțului se spun pe ele — un sold pe care îl
    închide o notă propusă (4426 / 4427 din regularizarea TVA) nu e un motiv separat, e aceeași validare."""
    net = {c: Decimal(str(d or 0)) - Decimal(str(cr or 0)) for c, (d, cr) in (s or {}).items()}
    for n in propuse["note"]:
        for d, c, suma in _linii(cur, schema, n["id"]):
            net[d], net[c] = net.get(d, Decimal("0")) + suma, net.get(c, Decimal("0")) - suma
    return {c: ((v, Decimal("0")) if v > 0 else (Decimal("0"), -v)) for c, v in net.items() if v}


def ciorne(cur, schema, an, azi=None):
    """[244] Propunerea care așteaptă validarea la 31.12.`an`: {"an", "luna": 12, "note": [{id, descriere, eticheta}], "la_zi", "incheiat"} sau
    None (`eticheta` = „nr. crt. N din 31.12.AAAA”, cum o arată Registrul jurnal; deficiența 258).
    `la_zi` = toate notele corespund soldurilor validate de acum (`corespunde`)."""
    zi = datetime.date(an, 12, 31)
    note = _ciorne_existente(cur, schema, zi)
    if not note:
        return None
    return {"an": an, "luna": 12, "note": [{"id": nid, "descriere": d, "eticheta": _et.nota(cur, schema, nid)} for nid, d in note],
            "la_zi": all(corespunde(cur, schema, nid, zi) for nid, _d in note), "incheiat": an_incheiat(an, azi)}


# ── REGULARIZAREA TVA LA SFÂRȘITUL PERIOADEI FISCALE (lotul 14, deficiența 688) ──────────────────────────────────────────────────────
# Comanda Costin 14.1, verbatim: „Închiderea lunii nu închide TVA-ul: F1 09/2026 e blocată cu «Nimic nu oprește închiderea», dar balanța
# lunii are 4426 sold final D 210,00 și 4427 sold final C 210,00, fără 4423/4424; în octombrie soldurile se cumulează. La plătitorii de
# TVA, închiderea trebuie să propună nota 4427 = 4426 + 4423/4424 pe perioada fiscală a firmei (lunar sau trimestrial) și să refuze
# blocarea cât 4426/4427 au sold.” Aceeași regularizare ca la 31.12 (`motor.regularizare_tva`, OMFP 1802/2014, conturile 4423 / 4424 /
# 4426 / 4427), dar pe ULTIMA LUNĂ A PERIOADEI FISCALE (luna, sau a treia lună a trimestrului): nota e ciornă, datată în ultima zi a
# lunii, sursa `regularizare_tva`, și intră în evidență numai prin validare. În decembrie regularizarea e a închiderii anului (cele două
# note ale lui `propune`): una singură, nu două.
SURSA_TVA = "regularizare_tva"
DESCRIERE_TVA_LUNA = "Regularizarea TVA la %s"


def _profil_tva(cur, schema):
    cur.execute(f"SELECT platitor_tva, tip_decont FROM {schema}.firma_profil WHERE id = 1")
    r = cur.fetchone()
    if not r:
        return {}
    return dict(r) if isinstance(r, dict) else {"platitor_tva": r[0], "tip_decont": r[1]}


def sfarsit_de_perioada_tva(cur, schema, an, luna):
    """True dacă `luna` încheie perioada fiscală TVA a unei firme PLĂTITOARE de TVA (lunar: orice lună; trimestrial: 3 / 6 / 9 / 12; semestrial
    și anual: 6 / 12 și 12). Tipul perioadei necompletat se tratează ca lunar (cea mai strictă): controlul se aplică, nu se tace."""
    from core.common import Perioada, fereastra_tva, perioada_tva_tip
    prof = _profil_tva(cur, schema)
    if prof.get("platitor_tva") is not True:
        return False
    try:
        tip = perioada_tva_tip(prof)
    except ValueError:
        tip = "L"
    _inc, sf = fereastra_tva(Perioada(an, luna=luna), tip)
    ultima = sf - datetime.timedelta(days=1)
    return (ultima.year, ultima.month) == (int(an), int(luna))


def _sold_tva(solduri):
    """(sold debitor 4426, sold creditor 4427) pe toate analiticele — pentru textul blocajului."""
    d = sum((Decimal(str(sd or 0)) - Decimal(str(sc or 0)) for c, (sd, sc) in (solduri or {}).items() if str(c).split(".")[0] == "4426"),
            Decimal("0"))
    c = sum((Decimal(str(sc or 0)) - Decimal(str(sd or 0)) for ct, (sd, sc) in (solduri or {}).items() if str(ct).split(".")[0] == "4427"),
            Decimal("0"))
    return d, c


def tva_de_regularizat(cur, schema, an, luna):
    """None când nu e nimic de regularizat (firma nu plătește TVA, luna nu încheie perioada fiscală, luna e dinaintea soldurilor de preluare,
    4426 / 4427 fără sold); altfel {"note": [notele regularizării], "sold_4426", "sold_4427", "ciorna": id sau None}. `cur` = RealDictCursor.
    Soldurile sunt cele ale notelor VALIDATE la sfârșitul lunii (`bilant_api.sold_la`)."""
    import calendar
    if not sfarsit_de_perioada_tva(cur, schema, an, luna):
        return None
    zi = datetime.date(an, luna, calendar.monthrange(an, luna)[1])
    s = _ba.sold_la(cur, schema, zi)
    if s is None:
        return None
    note = _m.regularizare_tva(s)
    if not note:
        return None
    d, c = _sold_tva(s)
    ciorne = _ciorne_tva(cur, schema, zi, luna)
    return {"note": note, "sold_4426": d, "sold_4427": c, "ciorna": ciorne[0][0] if ciorne else None}


def _ciorne_tva(cur, schema, zi, luna):
    """Ciornele regularizării perioadei: în decembrie cele ale închiderii anului (descrierea TVA), altfel cele cu sursa regularizării."""
    if luna == 12:
        cur.execute(f"SELECT id, descriere FROM {schema}.inregistrari WHERE sursa = %s AND data = %s AND status = 'ciorna' AND descriere = %s "
                    "ORDER BY id", (SURSA, zi, DESCRIERE_TVA % zi.year))
    else:
        cur.execute(f"SELECT id, descriere FROM {schema}.inregistrari WHERE sursa = %s AND data = %s AND status = 'ciorna' ORDER BY id",
                    (SURSA_TVA, zi))
    return [(r["id"], r["descriere"]) if isinstance(r, dict) else (r[0], r[1]) for r in cur.fetchall()]


def propune_tva_luna(cur, schema, an, luna):
    """Scrie ciorna regularizării TVA a perioadei care se încheie cu (an, luna), datată în ultima zi a lunii (cursor RealDictCursor, în
    tranzacția apelantului). Întoarce {"note": [{id, descriere, linii, document}], "inlocuite", "nimic"}. În decembrie: propunerea închiderii
    anului (`propune`). ValueError cu motivul când nu se poate (luna în curs, luna nu încheie perioada fiscală, o ciornă la validare)."""
    import calendar
    from core import coada_api as _coada, inchidere_luna as _il
    in_curs = _il.luna_in_curs(an, luna)
    if in_curs:
        raise ValueError("Regularizarea TVA se propune după ce luna s-a încheiat: " + in_curs)
    if not sfarsit_de_perioada_tva(cur, schema, an, luna):
        raise ValueError("Regularizarea TVA se face la sfârșitul perioadei fiscale a firmei (lunar, sau trimestrial în lunile 3, 6, 9, 12), "
                         "iar firma e plătitoare de TVA: luna %02d/%d nu încheie o perioadă fiscală." % (luna, an))
    if luna == 12:
        return propune(cur, schema, an)
    zi = datetime.date(an, luna, calendar.monthrange(an, luna)[1])
    s = _ba.sold_la(cur, schema, zi)
    if s is None:
        raise ValueError("Regularizarea TVA nu se poate propune: soldurile de la %s nu sunt în aplicație (evidența firmei începe după "
                         "soldurile de preluare)." % _data_ro(zi))
    vechi = _ciorne_tva(cur, schema, zi, luna)
    for nid, _d in vechi:
        if _coada.nota_la_validare(cur, schema, nid):
            raise ValueError("Propunerea de regularizare a TVA (nota %s) e la validare în coadă — nu se înlocuiește cât o verifică cabinetul."
                             % _et.nota(cur, schema, nid))
    doc_vechi = {d: _rc.documentul_notei(cur, schema, nid) for nid, d in vechi}
    for nid, _d in vechi:
        if _nd.respinsa(cur, schema, nid):
            _nd.sterge_respinsa(cur, schema, nid)
        else:
            _nd.sterge_ciorna_inlocuita(cur, schema, nid)
    linii = _m.regularizare_tva(s)
    note = []
    if linii:
        descriere = DESCRIERE_TVA_LUNA % _data_ro(zi)
        doc = doc_vechi.get(descriere)
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref)
                        VALUES (%s, %s, %s, 'ciorna', %s) RETURNING id""", (zi, descriere, SURSA_TVA, doc))
        r = cur.fetchone()
        nid = r["id"] if isinstance(r, dict) else r[0]
        if not doc:
            _rc._cu_document_intern(cur, schema, "nota_calcul", zi, r)
        for n in linii:
            _rc.adauga_linie(cur, schema, nid, n["debit"], n["credit"], n["suma"])
        note.append({"id": nid, "descriere": descriere, "linii": [(n["debit"], n["credit"], str(n["suma"])) for n in linii],
                     "document": _rc.documentul_notei(cur, schema, nid)})
    return {"note": note, "inlocuite": [nid for nid, _d in vechi], "nimic": not note}


def refuz_validare_tva_luna(cur, schema, nota_id):
    """Motivul pentru care nota de regularizare a TVA `nota_id` (sursa `regularizare_tva`) nu se validează, sau None: ea trebuie să fie încă
    regularizarea soldurilor 4426 / 4427 VALIDATE la sfârșitul lunii ei (o operațiune validată după propunere o face greșită; nota validată
    nu se mai modifică). Chemat din `jurnal_api.valideaza`, ca `refuz_validare`."""
    cur.execute(f"SELECT data, sursa FROM {schema}.inregistrari WHERE id = %s", (nota_id,))
    r = cur.fetchone()
    zi, sursa = (r["data"], r["sursa"]) if isinstance(r, dict) else (r or (None, None))
    if sursa != SURSA_TVA:
        return None
    s = _ba.sold_la(cur, schema, zi)
    p = _m.regularizare_tva(s) if s is not None else []
    if _linii(cur, schema, nota_id) != sorted((n["debit"], n["credit"], Decimal(n["suma"])) for n in p):
        return ("Nota de regularizare a TVA %s nu mai corespunde soldurilor 4426 / 4427 de la %s din notele validate: după propunere s-au "
                "validat operațiuni ale lunii sau nota a fost modificată. Propune din nou regularizarea din Închidere lună — o recalculează "
                "din soldurile de acum." % (_et.nota(cur, schema, nota_id), _data_ro(zi)))
    return None
