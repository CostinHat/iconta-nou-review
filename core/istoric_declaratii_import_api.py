"""
core/istoric_declaratii_import_api.py — import istoric declaratii (stratul 7) per firma.

Citeste o lista de declaratii deja depuse (.xlsx/.csv): tip, an, luna, data depunere.
Scrie in tabelul global public.declaratii_depuse cu sursa='migrare' (ca sa nu apara fals
restanta). Import per firma: DELETE WHERE tenant_id=X AND sursa='migrare', apoi INSERT.
NU sterge declaratiile depuse prin iConta (sursa='iconta').

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from __future__ import annotations

from core.migrare_api import respinge, semnaleaza  # [P8/C] respingerea e o afirmatie, cu regula din nomenclator
import re as _re
from core.pdf_util import data_ro as _data_ro   # DS cap.4: data din text, canonic
from core.common import cate as _cate

from core import import_tabel as _it

# [C25, 14.10.2026] UN SINGUR nomenclator: `TIPURI_CUNOSCUTE` (mai jos) — previzualizarea folosea `_TIPURI` (9 tipuri), salvarea
# `TIPURI_CUNOSCUTE` (15); un D212 era „necunoscut” în previzualizare și cunoscut la salvare, iar avertismentul de previzualizare
# (o afirmație) răsturna salvarea cu un 422 de model.
CAMPURI = {
    "tip": ("tip declaratie", "tipul declaratiei", "cod formular", "tip", "declaratie", "formular"),
    "an": ("=an", "anul", "an raportare", "an fiscal"),
    "luna": ("luna raportare", "=luna", "perioada", "luna*"),
    "data": ("data depunerii", "data depunere", "depunere", "depus*", "=data"),
    # [deficiența 377, comanda Costin 8.2] suma declarată: „istoricul preia și suma declarată acolo unde o declarație ulterioară se calculează
    # cumulat (D100 profit)”
    "suma": ("suma de plata", "suma de plată", "suma declarata", "suma declarată", "=suma", "suma*", "impozit*"),
}


def _intreg(v):
    try:
        return int(round(float(str(v).strip().replace(",", ".")))) if str(v).strip() else 0
    except ValueError:
        return 0


def _normalizeaza_tip(v):
    """'100' / 'd100' / 'Declaratia 100' / 'S1003' -> ('D100' / 'S1003', True). Necunoscut -> (textul, False)."""
    t = str(v or "").strip().upper().replace(" ", "")
    if t in TIPURI_CUNOSCUTE:
        return t, True
    for tip in sorted(TIPURI_CUNOSCUTE, key=len, reverse=True):     # „D394A” înaintea lui „D394”
        if tip in t:
            return tip, True
    cifre = "".join(ch for ch in t if ch.isdigit())
    if cifre and "D" + cifre in TIPURI_CUNOSCUTE:
        return "D" + cifre, True
    return (t or "?"), False   # necunoscut




def _perioada(v):
    """`(luna, an)` dintr-o celulă de perioadă „09/2026”, „09.2026”, „2026-09”; altfel `(None, None)`."""
    s = str(v or "").strip()
    m = _re.fullmatch(r"(\d{1,2})[./-](\d{4})", s) or None
    if m:
        return int(m.group(1)), int(m.group(2))
    m = _re.fullmatch(r"(\d{4})[./-](\d{1,2})", s)
    if m:
        return int(m.group(2)), int(m.group(1))
    return None, None


def extrage(continut, nume_fisier=""):
    """Intoarce [{tip, an, luna, data_depunere, tip_cunoscut, ok, avertisment, rand_fisier}].

    `avertisment` = textele respingerilor rândului, din ACEEAȘI verificare pe care o aplică salvarea (`verifica_randuri`)."""
    brut = _it.citeste(continut, nume_fisier)
    if not brut or all(_it.rand_gol(r) for r in brut):
        return []
    try:
        antet, start = _it.gaseste_antet(brut, CAMPURI, obligatorii=("tip",), nume_fisier=nume_fisier)
    except _it.FisierNecitit as e:
        if isinstance(e, _it.ColoaneAmbigue):
            raise
        raise ValueError("nu se găsește coloana cu tipul declarației (tip/declarație/formular) - fișier nerecunoscut")
    col = lambda camp, exclus=(): _it.coloana(antet, CAMPURI[camp], exclus=exclus, camp=camp)
    i_tip = col("tip")
    i_an = col("an", (i_tip,))
    i_luna = col("luna", (i_tip, i_an))
    i_data = col("data", (i_tip, i_an, i_luna))
    i_suma = col("suma", (i_tip, i_an, i_luna, i_data))

    out = []
    for nr, r in enumerate(brut[start:], start=start + 1):
        tip_raw = _it.celula(r, i_tip)
        # [comanda Costin 8.2 pct.4] se sare numai rândul complet gol; fără tip, rândul se arată respins (`tip_necunoscut`)
        if _it.rand_gol(r):
            continue
        tip, cunoscut = _normalizeaza_tip(tip_raw)
        luna, an = _perioada(_it.celula(r, i_luna))
        if luna is None:
            luna = _intreg(_it.celula(r, i_luna))
            an = _intreg(_it.celula(r, i_an))
        elif i_an >= 0 and _it.celula(r, i_an):
            an = _intreg(_it.celula(r, i_an))
        data_dep = _it.data(_it.valoare(r, i_data)) if i_data >= 0 else None
        suma_brut = _it.celula(r, i_suma) if i_suma >= 0 else ""
        out.append({"tip": tip, "an": an, "luna": luna, "data_depunere": data_dep,
                    "data_brut": str(_it.valoare(r, i_data) or "") if i_data >= 0 else "", "suma": _suma(suma_brut),
                    "suma_brut": str(suma_brut or ""), "tip_cunoscut": cunoscut, "anuala": tip in TIPURI_ANUALE, "rand_fisier": nr})
    eticheteaza(out)
    return out


def _suma(v):
    """Suma declarată (lei, întreg — D100 se declară în lei întregi), sau None dacă celula e goală / nu e număr."""
    s = str(v or "").strip().replace(" ", "")
    if not s:
        return None
    from decimal import ROUND_HALF_UP, Decimal
    from core import numere as _nr
    try:
        return int(Decimal(str(_nr.numar(s, strict=True))).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    except (TypeError, ValueError, ArithmeticError):
        return None


def eticheteaza(randuri, azi=None):
    """[comanda Costin 8.2 pct.4] Starea fiecărui rând, din ACEEAȘI verificare pe care o aplică salvarea: `stare` ∈ ok / semnalat (intră,
    cu observația ei) / respins (nu intră, cu motivul ei); `motive` = textele, în ordinea lor."""
    er, sem = verifica_randuri(randuri, azi), semnale_randuri(randuri, azi)
    for r in randuri:
        resp = [e["mesaj"] for e in er if e.get("rand") == r["rand_fisier"]]
        obs = [e["mesaj"] for e in sem if e.get("rand") == r["rand_fisier"]]
        r["stare"] = "respins" if resp else ("semnalat" if obs else "ok")
        r["motive"] = resp or obs
    return randuri


def rezumat(conn, tenant_id):
    """{are_istoric, randuri} pentru o firma (doar randurile din migrare).
    Coloana `sursa` e garantata de migrare_declaratii_depuse_randuri (public), nu mai lazy."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.declaratii_depuse WHERE tenant_id=%s AND sursa='migrare'",
                    (tenant_id,))
        n = cur.fetchone()[0]
    return {"are_istoric": n > 0, "randuri": n}


def rezumat_lot(conn, tenant_ids):
    """`{tenant_id: {are_istoric, randuri}}` pentru TOT portofoliul, într-o SINGURĂ interogare.

    **DE CE EXISTĂ [P3, 09.09.2026].** `rezumat()` de mai sus e corectă și rămâne — o cheamă
    ecranele unei singure firme. Dar `/migrare/istoric-declaratii` o chema **într-o buclă peste
    portofoliu**, cu o conexiune proprie per firmă: măsurat, `1.004` interogări și `1.003`
    conexiuni la 1000 de firme, adică `q = 4 + 1*N`, `c = 3 + 1*N`.

    Aceeași sursă, același predicat, aceeași formă a răspunsului — se schimbă doar **de câte ori**
    se întreabă. O firmă fără niciun rând primește `0`, exact ce întorcea `count(*)` pentru ea.
    *Nu e un cache și nu e un model de citire: e aceeași citire, făcută o dată.*"""
    ids = [t for t in (tenant_ids or []) if t is not None]
    if not ids:
        return {}
    with conn.cursor() as cur:
        cur.execute("SELECT tenant_id, count(*) FROM public.declaratii_depuse "
                    " WHERE tenant_id = ANY(%s) AND sursa = 'migrare' "
                    " GROUP BY tenant_id", (ids,))
        gasite = dict(cur.fetchall())
    return {t: {"are_istoric": gasite.get(t, 0) > 0, "randuri": gasite.get(t, 0)} for t in ids}


TIPURI_CUNOSCUTE = ("D100", "D101", "D112", "D205", "D300", "D301", "D390", "D394",
                    "D406", "D212", "S1003", "S1005", "D394A", "D311", "D207")

# Declarațiile ANUALE se țin în `declaratii_depuse` pe luna 12 — convenția aplicației (`control_fiscal_api`: D101 și D205 cu
# `luna: 12`, „12 la an”). Un rând anual fără lună primește 12; unul lunar / trimestrial fără lună se refuză numit.
TIPURI_ANUALE = ("D101", "D205", "D212", "S1003", "S1005")


def _perioada_txt(tip, an, luna):
    return ("%s pe %s" % (tip or "?", an)) if (tip in TIPURI_ANUALE or not luna) else ("%s pe %02d/%s" % (tip or "?", int(luna), an))


def verifica_randuri(randuri, azi=None):
    """PURĂ: respingerile [{rand, motiv, mesaj}] — rândurile care NU intră. [comanda Costin 8.2] 353: rândul dublat (aceeași declarație pe
    aceeași perioadă) intră o dată, a doua apariție se respinge numită; 354: depunerea datată înaintea SFÂRȘITULUI perioadei raportate
    (D112 pe martie depus pe 10.03) sau în viitor se respinge; suma care nu e număr se respinge."""
    import calendar
    import datetime as _dt
    azi = azi or _dt.date.today()
    er, vazute = [], {}
    for i, r in enumerate(randuri or [], start=2):
        tip = str(r.get("tip") or "").strip().upper()   # VALIDARE contra TIPURI_CUNOSCUTE (uppercase, nomenclator ANAF)
        an = int(r.get("an") or 0)
        luna = r.get("luna")
        i = _it.nr_rand(r, i)
        luna_lipsa = False
        if str(luna or "").strip() in ("", "0") and tip not in TIPURI_ANUALE:
            luna_lipsa = True                    # perioada nu se știe: comparația cu data depunerii n-are sens
            er.append(respinge("declarație depusă", i, "luna_invalida",
                               "%s/%s: luna lipsește (declarația %s nu e anuală)" % (tip or "?", an, tip or "?")))
            luna = None
        elif str(luna or "").strip() in ("", "0"):
            luna = None                          # anuală: luna 12 la scriere
        if tip and tip not in TIPURI_CUNOSCUTE:
            er.append(respinge("declarație depusă", i, "tip_necunoscut",
                               "tipul declarației lipsește" if tip == "?" else "declarația %s nu există în nomenclatorul ANAF" % tip))
        if not (2000 <= an <= azi.year + 1):
            er.append(respinge("declarație depusă", i, "an_invalid",
                               "%s: anul %s e în afara intervalului" % (tip or "?", an)))
        l = None
        if luna is not None and str(luna).strip() != "":
            try:
                l = int(luna)
                if not (1 <= l <= 12):
                    er.append(respinge("declarație depusă", i, "luna_invalida",
                                       "%s: luna %s (așteptat 1-12)" % (tip or "?", l)))
                    l = None
            except (TypeError, ValueError):
                er.append(respinge("declarație depusă", i, "luna_invalida",
                                   "%s: luna %r nu e număr" % (tip or "?", luna)))
        if tip in TIPURI_ANUALE:
            l = 12
        cheie = (tip, an, l)
        if tip and not luna_lipsa and cheie in vazute:
            er.append(respinge("declarație depusă", i, "rand_dublat",
                               "%s apare și pe rândul %s: se importă o singură dată" % (_perioada_txt(tip, an, l), vazute[cheie])))
        elif tip and not luna_lipsa:
            vazute[cheie] = i
        d = r.get("data_depunere")
        if not d and str(r.get("data_brut") or "").strip():
            er.append(respinge("declarație depusă", i, "data_invalida",
                               "%s: data depunerii %r nu se înțelege" % (tip or "?", r.get("data_brut"))))
        if d and not luna_lipsa:
            try:
                dd = d if isinstance(d, _dt.date) else _dt.date.fromisoformat(str(d)[:10])
                if dd > azi:
                    er.append(respinge("declarație depusă", i, "data_viitor",
                                       "%s: depusă la %s, o dată din viitor" % (_perioada_txt(tip, an, l), _data_ro(dd))))
                elif l and 2000 <= an <= 2100:
                    sfarsit = _dt.date(an, l, calendar.monthrange(an, l)[1])
                    if dd < sfarsit:
                        er.append(respinge("declarație depusă", i, "data_inainte_de_perioada",
                                           "%s: depusă la %s, înainte de sfârșitul perioadei raportate (%s)"
                                           % (_perioada_txt(tip, an, l), _data_ro(dd), _data_ro(sfarsit))))
            except ValueError:
                er.append(respinge("declarație depusă", i, "data_invalida",
                                   "%s: data depunerii %r nu se înțelege" % (tip or "?", d)))
        if str(r.get("suma_brut") or "").strip() and r.get("suma") is None:
            er.append(respinge("declarație depusă", i, "suma_invalida",
                               "%s: suma %r nu e un număr" % (_perioada_txt(tip, an, l), r.get("suma_brut"))))
    return er


def semnale_randuri(randuri, azi=None):
    """PURĂ: semnalele [{rand, motiv, mesaj}] — rândurile care INTRĂ, cu observația lor (comanda Costin 8.2): 355 fără data depunerii;
    356 anul mai vechi decât anul curent și precedentul (ecranul importă anul curent); 377 D100 fără suma declarată."""
    import datetime as _dt
    azi = azi or _dt.date.today()
    out = []
    for i, r in enumerate(randuri or [], start=2):
        i = _it.nr_rand(r, i)
        tip = str(r.get("tip") or "").strip().upper()
        an = int(r.get("an") or 0)
        per = _perioada_txt(tip, an, r.get("luna"))
        if not r.get("data_depunere") and not str(r.get("data_brut") or "").strip():
            out.append(semnaleaza("declarație depusă", i, "data_depunere_lipsa",
                                  "%s: fără data depunerii — se importă (nu mai e cerută ca restanță), dar termenul ei nu se poate "
                                  "confrunta" % per))
        if 2000 <= an < azi.year - 1:
            out.append(semnaleaza("declarație depusă", i, "an_vechi",
                                  "%s: anul %s e mai vechi decât anii pe care îi urmărește aplicația (%s și %s) — se importă, dar nu "
                                  "schimbă nimic în termenele de azi" % (per, an, azi.year - 1, azi.year)))
        if tip == "D100" and r.get("suma") is None and not str(r.get("suma_brut") or "").strip():
            out.append(semnaleaza("declarație depusă", i, "suma_lipsa_d100",
                                  "%s: fără suma declarată — la impozitul pe profit, D100 de pe trimestrele următoare n-o poate scădea "
                                  "(o va cere până o completezi)" % per))
    return out


def importa(conn, tenant_id, randuri):
    """DELETE doar randurile de migrare ale firmei + INSERT. NU atinge sursa='iconta'.
    Ridica ValueError daca randurile nu pot intra (vezi verifica_randuri)."""
    # [probare invalid, 03.09.2026] UN IMPORT GOL STERGEA ISTORICUL, IN TACERE.
    # `randuri=[]` trecea de verificare (n-are ce respinge), ajungea la DELETE-ul de mai jos, care
    # sterge TOATE randurile de migrare ale firmei, nu insera nimic, si raspundea `200 {"importati": 0}`.
    # Adica exact forma cea mai rea: o pierdere de date raportata ca succes. Un fisier gol, o coloana
    # necitita, un filtru care n-a potrivit nimic — oricare din ele ajungea aici.
    # Istoricul declaratiilor depuse sta la baza termenelor si a controlului fiscal.
    if not randuri:
        raise ValueError("nu ai trimis niciun rând. Importul ar fi șters istoricul de declarații "
                         "încărcat până acum pentru firma asta și n-ar fi pus nimic în loc. "
                         "Dacă chiar vrei să golești istoricul importat, e altă operațiune.")
    er = verifica_randuri(randuri)
    # [C25, decizia Costin 14.10.2026, verbatim în DECIZII: „fără blocare la salvare; rândul problemă se arată, restul se
    # salvează”] Rândurile respinse nu intră și se întorc numite; numai un import fără niciun rând bun se refuză întreg.
    respinse_idx = {x["rand"] for x in er}
    bune = [r for i, r in enumerate(randuri, start=2) if _it.nr_rand(r, i) not in respinse_idx]
    if not bune:
        # [probare invalid, 03.09.2026] Se numără RÂNDURILE, nu erorile: un singur rând gol
        # produce două erori, iar mesajul spunea „2 rânduri nu pot intra" despre un rând. O
        # cifră falsă într-un refuz e mai rea decât un refuz sec — omul caută al doilea rând.
        _nr = len({x["rand"] for x in er})
        raise ValueError("%s nu %s intra: %s. Istoricul declarațiilor stă la "
                         "baza termenelor și a controlului fiscal."
                         % ("Un rând" if _nr == 1 else _cate(_nr, "rând", "rânduri"),
                            "poate" if _nr == 1 else "pot",
                            "; ".join("rand %s: %s" % (x["rand"], x["mesaj"]) for x in er[:6])))
    import json as _json
    with conn.cursor() as cur:
        cod_d100 = _cod_d100(cur, tenant_id)
        cur.execute("DELETE FROM public.declaratii_depuse WHERE tenant_id=%s AND sursa='migrare'",
                    (tenant_id,))
        n = 0
        for r in bune:
            _tip = str(r["tip"]).strip().upper()
            _luna = r.get("luna") if str(r.get("luna") or "").strip() not in ("", "0") else (12 if _tip in TIPURI_ANUALE else None)
            # [377] la D100, suma declarată se păstrează ca obligația ei (forma unei depuneri prin iConta: `randuri.obligatii`), pe codul
            # impozitului firmei — `d100.profit_trimestru` o scade din cumulat și arată de unde vine
            randuri_json = (_json.dumps({"obligatii": [{"cod_oblig": cod_d100, "suma_dat": int(r["suma"]), "suma_plata": int(r["suma"])}],
                                         "sursa": "istoric preluat la migrare"})
                            if _tip == "D100" and r.get("suma") is not None and cod_d100 else None)
            cur.execute("""
                INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, data_depunere, sursa, randuri)
                VALUES (%s,%s,%s,%s,%s,'migrare',%s::jsonb)
            """, (tenant_id, r.get("an"), _luna,
                  str(r["tip"]).strip().lower(),   # [tip_lowercase] canonic la STOCARE (CHECK-ul il impune)
                  r.get("data_depunere"), randuri_json))
            n += 1
    return {"importati": n, "respinse": er, "semnalate": semnale_randuri(bune)}


def _cod_d100(cur, tenant_id):
    """Codul obligației D100 după regimul firmei: impozit pe profit 103, microîntreprindere 121 (nomenclatorul D100, `core/d100.py`)."""
    cur.execute("SELECT schema_name FROM public.tenants WHERE id = %s", (tenant_id,))
    r = cur.fetchone()
    if not r:
        return None
    cur.execute('SELECT regim_fiscal FROM "%s".firma_profil WHERE id = 1' % str(r[0]).replace('"', ""))
    reg = ((cur.fetchone() or [None])[0] or "").strip().lower()
    return {"profit": "103", "micro": "121"}.get(reg)
