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
#: [lotul 11] numele câmpului în refuzul coloanelor ambigue (`import_tabel.coloana`), în limba contabilului — nu cheia internă
#: (garda: core/test_lot11_import_etichete_camp.py)
ETICHETE_CAMP = {
    "tip": "tipul declarației",
    "an": "anul",
    "luna": "luna raportării",
    "data": "data depunerii",
    "suma": "suma declarată",
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
    col = lambda camp, exclus=(): _it.coloana(antet, CAMPURI[camp], exclus=exclus, camp=ETICHETE_CAMP[camp])
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


#: [389, retestul 19.10.2026: „perioada apare 03/2026 și 06/2026 în loc de T1/2026, T2/2026”] declarațiile TRIMESTRIALE ale firmei, după
#: profilul ei: D100 la impozitul pe profit / micro (CF art.41 alin.(1); CF art.56 alin.(1) — trimestrial), D300 / D394 la decontul trimestrial
#: (CF art.322 alin.(2)-(3)). Restul (D112, D390 …) rămân lunare.
def trimestriala(tip, profil):
    """Declarația `tip` e trimestrială pentru firma cu `profil` ({tip_decont, regim_fiscal})."""
    profil = profil or {}
    if tip == "D100":
        return str(profil.get("regim_fiscal") or "").lower() in ("profit", "micro")
    if tip in ("D300", "D394"):
        return str(profil.get("tip_decont") or "").lower().startswith("t")
    return False


def cu_perioada(randuri, profil):
    """PURĂ: fiecare rând primește `perioada` — cum o scrie formularul: „anuală 2026”, „T1/2026” (luna de sfârșit a trimestrului, la o
    declarație trimestrială a firmei), „03/2026”. Luna care nu încheie un trimestru se arată lunar, cum a venit."""
    for r in randuri or []:
        an, luna, tip = r.get("an"), r.get("luna"), str(r.get("tip") or "").upper()
        try:
            luna = int(luna)
        except (TypeError, ValueError):
            luna = None
        if r.get("anuala"):
            r["perioada"] = "anuală %s" % (an or "—")
        elif luna and an and 1 <= luna <= 12 and luna % 3 == 0 and trimestriala(tip, profil):
            r["perioada"] = "T%d/%s" % (luna // 3, an)
        elif luna and an and 1 <= luna <= 12:
            r["perioada"] = "%02d/%s" % (luna, an)
        else:
            r["perioada"] = "%s %s" % (r.get("luna") or "—", an or "—")
    return randuri


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
        # [lotul 13, deficiența 586, comanda Costin 13.1: „D100 cu luna 02 intră fără să spună cum a fost citit (lunar, ex. impozit pe
        # dividende, vs trimestrial).”] D100 pe o lună care nu încheie un trimestru se citește ca D100 LUNARĂ — ex. impozitul pe dividende,
        # CF art.43 alin.(2): „se declară și se plătește la bugetul de stat, până la data de 25 inclusiv a lunii următoare celei în care se
        # plătește dividendul” —, nu ca trimestrul impozitului pe profit / micro (CF art.41 alin.(1), art.56 alin.(1): luna de sfârșit a
        # trimestrului). Spus pe rând, cu ce trebuie scris dacă era trimestrială.
        try:
            _l = int(r.get("luna") or 0)
        except (TypeError, ValueError):
            _l = 0
        if tip == "D100" and 1 <= _l <= 12 and _l % 3:
            out.append(semnaleaza("declarație depusă", i, "d100_lunara",
                                  "%s: luna %02d nu încheie un trimestru — rândul e citit ca D100 lunară (de exemplu impozitul pe dividende, "
                                  "declarat în luna de după plată); dacă era D100 trimestrială (impozit pe profit sau micro), scrie luna de "
                                  "sfârșit a trimestrului (%02d = T%d)" % (per, _l, (_l + 2) // 3 * 3, (_l + 2) // 3)))
        if tip == "D100" and r.get("suma") is None and not str(r.get("suma_brut") or "").strip():
            out.append(semnaleaza("declarație depusă", i, "suma_lipsa_d100",
                                  "%s: fără suma declarată — la impozitul pe profit, D100 de pe trimestrele următoare n-o poate scădea "
                                  "(o va cere până o completezi)" % per))
    return out


def _perioade(perechi):
    """[426] (an, luna) -> „din 01/2025 până în 09/2026” (sau „pe 03/2026” când e una singură); fără perechi -> „—”."""
    ps = sorted((int(a), int(l or 12)) for a, l in perechi if a)
    if not ps:
        return "—"
    def f(p):   # formatul perioadei din previzualizare (DS cap.4: „03/2026”)
        return "%02d/%d" % (p[1], p[0])
    return ("pe %s" % f(ps[0])) if ps[0] == ps[-1] else ("din %s până în %s" % (f(ps[0]), f(ps[-1])))


def existent(conn, tenant_id):
    """[lotul 10, deficiența 426 — clasa] Istoricul preluat la migrare (sursa='migrare') al firmei și ce se sprijină pe el:
    {randuri, tipuri, perioade, depuse_iconta: {numar, ani}} — `depuse_iconta` = declarațiile depuse prin iConta în anii istoricului
    preluat: termenele, restanțele și suma D100 deja declarată pe trimestrele anterioare se socotesc pe istoric."""
    with conn.cursor() as cur:
        cur.execute("SELECT tip, an, luna FROM public.declaratii_depuse WHERE tenant_id=%s AND sursa='migrare'", (tenant_id,))
        rs = cur.fetchall()
        ani = sorted({int(r[1]) for r in rs})
        cur.execute("SELECT count(*) FROM public.declaratii_depuse WHERE tenant_id=%s AND sursa <> 'migrare' AND an = ANY(%s)",
                    (tenant_id, ani))
        ni = cur.fetchone()[0]
    return {"randuri": len(rs), "tipuri": sorted({str(r[0]).upper() for r in rs}), "perioade": _perioade([(r[1], r[2]) for r in rs]),
            "depuse_iconta": {"numar": int(ni or 0), "ani": ani}}


def totaluri(randuri):
    """[426] Ce aduce fișierul, pe rândurile care intră: {randuri, tipuri, perioade}."""
    rs = randuri or []
    return {"randuri": len(rs), "tipuri": sorted({str(r.get("tip") or "").strip().upper() for r in rs} - {""}),
            "perioade": _perioade([(r.get("an"), r.get("luna")) for r in rs]),
            "citite": getattr(randuri, "citite", None)}   # [lotul 13, 583] câte rânduri s-au citit (`migrare_api.RanduriCareIntra`)


def text_inlocuire(vechi, nou):
    """[426] „spune că există deja […], arată [ce e] vechi și nou […]; dacă există [date dependente], spune” — textul comun avertismentului
    din previzualizare și refuzului de la salvare: declarațiile și perioadele, vechi și noi, și depunerile prin iConta din anii lor."""
    def _parte(x):
        return "%s (%s), %s" % (_cate(x["randuri"], "declarație", "declarații"), ", ".join(x["tipuri"]) or "—", x["perioade"])
    from core.migrare_api import text_fisier_nou as _tfn   # [583]
    t = ("Firma are deja un istoric de declarații preluat: %s. Fișierul nou: %s. Salvarea înlocuiește istoricul preluat; declarațiile "
         "depuse prin iConta rămân." % (_parte(vechi), _tfn(_parte(nou), nou["randuri"], nou.get("citite"))))
    di = vechi.get("depuse_iconta") or {}
    if di.get("numar"):
        t += (" În %s %s %s prin iConta: termenele, restanțele și suma D100 deja declarată pe trimestrele anterioare se socotesc "
              "pe istoricul nou." % ("anul" if len(di["ani"]) == 1 else "anii", ", ".join(str(a) for a in di["ani"]),
                                     "s-a depus o declarație" if di["numar"] == 1 else "s-au depus " + _cate(di["numar"], "declarație",
                                                                                                             "declarații")))
    return t


def importa(conn, tenant_id, randuri, inlocuieste=False):
    """DELETE doar randurile de migrare ale firmei + INSERT. NU atinge sursa='iconta'.
    Ridica ValueError daca randurile nu pot intra (vezi verifica_randuri).
    [lotul 10, deficiența 426 — clasa] un istoric preluat existent se înlocuiește NUMAI cu `inlocuieste=True` (confirmarea de pe ecran);
    fără ea -> `migrare_api.InlocuireNeconfirmata` (409), cu declarațiile și perioadele vechi și noi."""
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
    bune_nr = [(_it.nr_rand(r, i), r) for i, r in enumerate(randuri, start=2) if _it.nr_rand(r, i) not in respinse_idx]
    bune = [r for _n, r in bune_nr]
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
    vechi, nou = existent(conn, tenant_id), totaluri(bune)
    from core import migrare_api as _mig
    _mig.cere_confirmarea_inlocuirii(vechi["randuri"] > 0, inlocuieste, text_inlocuire(vechi, nou), vechi, nou,
                                     vechi["depuse_iconta"])   # [426] poarta comună a clasei
    import json as _json
    from core import chei_unice as _chei
    with conn.cursor() as cur:
        cod_d100 = _cod_d100(cur, tenant_id)
        cur.execute("DELETE FROM public.declaratii_depuse WHERE tenant_id=%s AND sursa='migrare'",
                    (tenant_id,))
        n = 0
        for nr, r in bune_nr:
            _tip = str(r["tip"]).strip().upper()
            _luna = r.get("luna") if str(r.get("luna") or "").strip() not in ("", "0") else (12 if _tip in TIPURI_ANUALE else None)
            # [377] la D100, suma declarată se păstrează ca obligația ei (forma unei depuneri prin iConta: `randuri.obligatii`), pe codul
            # impozitului firmei — `d100.profit_trimestru` o scade din cumulat și arată de unde vine
            randuri_json = (_json.dumps({"obligatii": [{"cod_oblig": cod_d100, "suma_dat": int(r["suma"]), "suma_plata": int(r["suma"])}],
                                         "sursa": "istoric preluat la migrare"})
                            if _tip == "D100" and r.get("suma") is not None and cod_d100 else None)
            # [lotul 10, C73 / U3] rândul istoric ia `nr_depunere` 1 (implicit): pe o perioadă pe care firma are deja prima depunere scrisă
            # prin iConta.eu (sau marcată, `sursa` ≠ migrare — nu se șterge mai sus), PK-ul îl refuza și tot importul cădea cu 500. Acum
            # rândul acela se respinge NUMIT, ca orice rând care nu intră (C25: „rândul problemă se arată, restul se salvează”).
            try:
                with _chei.refuza_dublura(cur, ("declaratii_depuse_pkey",), _refuz_deja_depusa(tenant_id, _tip, r.get("an"), _luna)):
                    cur.execute("""
                        INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, data_depunere, sursa, randuri)
                        VALUES (%s,%s,%s,%s,%s,'migrare',%s::jsonb)
                    """, (tenant_id, r.get("an"), _luna,
                          str(r["tip"]).strip().lower(),   # [tip_lowercase] canonic la STOCARE (CHECK-ul il impune)
                          r.get("data_depunere"), randuri_json))
            except _chei.CheieDublata as e:
                er.append(respinge("declarație depusă", nr, "deja_exista", str(e)))
                continue
            n += 1
        if not n:   # niciun rând n-a intrat: importul nu șterge istoricul vechi ca să nu pună nimic în loc (ca la `bune` gol, mai sus)
            raise ValueError("Niciun rând nu poate intra: %s." % "; ".join("rand %s: %s" % (x["rand"], x["mesaj"]) for x in er[:6]))
    return {"importati": n, "respinse": er, "semnalate": semnale_randuri(bune), "inlocuit": vechi if vechi["randuri"] else None}


def _refuz_deja_depusa(tenant_id, tip, an, luna):
    """[lotul 10, C73 / U3] `refuz` pentru rândul istoric a cărui perioadă are deja depunerea ei (nu din istoric): numește depunerea
    curentă (cum s-a depus și când), citită după `ROLLBACK TO SAVEPOINT` (`repo_control_fiscal_api.select_depusa_curenta`)."""
    def refuz(cur, _e):
        from core import chei_unice as _chei, repo_control_fiscal_api as _rcf
        ex = _rcf.select_depusa_curenta(cur, tenant_id, an, luna, tip.lower())
        if not ex:
            return None
        data, sursa = ex
        cum = {"iconta": "prin iConta.eu la %s" % _data_ro(data), "extern": "în afara iConta.eu, la %s" % _data_ro(data),
               # `contabil_anterior`: data depunerii nu se cunoaște (`uc_control_fiscal`), deci nu se arată
               "contabil_anterior": "de contabilul anterior"}.get(sursa, "la %s" % _data_ro(data))
        return _chei.CheieDublata("%s e deja depusă %s: rândul din istoric nu se importă peste ea."
                                  % (_perioada_txt(tip, int(an), luna), cum), valoare=tip)
    return refuz


def _cod_d100(cur, tenant_id):
    """Codul obligației D100 după regimul firmei: impozit pe profit 103, microîntreprindere 121 (nomenclatorul D100, `core/d100.py`)."""
    cur.execute("SELECT schema_name FROM public.tenants WHERE id = %s", (tenant_id,))
    r = cur.fetchone()
    if not r:
        return None
    cur.execute('SELECT regim_fiscal FROM "%s".firma_profil WHERE id = 1' % str(r[0]).replace('"', ""))
    reg = ((cur.fetchone() or [None])[0] or "").strip().lower()
    return {"profit": "103", "micro": "121"}.get(reg)
