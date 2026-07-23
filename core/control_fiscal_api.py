"""
core/control_fiscal_api.py — semafor de conformare fiscala per firma (cross-portfolio).

Pentru fiecare firma:
  1. citeste vectorul fiscal (firma_profil: regim_fiscal, platitor_tva, tip_decont, operatiuni_ic)
     + are_salariati (din tabelul salariati)
  2. deriva ce declaratii sunt DATORATE pe perioadele trecute (scadentar in cod)
  3. compara cu public.declaratii_depuse
  4. intoarce semafor (verde/galben/gri/rosu) + lista lipsuri + lista neclar

Principiu (v2, dupa 5 patch-uri): semaforul NU inventeaza un raspuns plauzibil cand
nu stie. Un atribut de vector necompletat -> declaratia care depinde de el iese GRI
cu cauza declarata, NU un default tacut. "Nu stiu" e o stare vizibila, nu verde.

Scadentar: sursa UNICA e core/scadente.py (F081, verificat la calendarul oficial ANAF
2026) — 25 ale lunii urmatoare pentru D100/D112/D300/D390, 25 martie an urmator pentru
D101, mutat la prima zi lucratoare cu SARBATORILE legale (Paste mobil inclus). Nu se
mai reimplementeaza aici (D1: weekend-only ignora sarbatorile -> fals rosu; D4: ziua 25
hardcodata cu D101 lipit pe langa).
"""
from __future__ import annotations
import datetime

from core import scadente  # sursa unica de scadente + zile lucratoare (fara import circular)
from core.common import azi_ro, pastila_firma  # [fus] ziua RO; [semafor] escaladare unica din constatari
from core import firma_profil_api as _fp  # [F180] stare_tva_anaf (comparatie platitor_tva vs snapshot)

PRAG_URMARIT_ZILE = 7   # termen in <= 7 zile, nedepus -> galben

# nume scurt de perioada pentru afisare
_LUNI_NUME = ["", "ian", "feb", "mar", "apr", "mai", "iun", "iul", "aug", "sep", "oct", "noi", "dec"]


def _termen(an, luna=None, tip="d300"):
    """Termenul de depunere al declaratiei `tip` pentru perioada (an, luna), delegat la
    core/scadente.py (25/martie per tip + prima zi lucratoare cu sarbatori legale).
    Semnatura pastreaza forma (an, luna) folosita de termene_api._termen."""
    return scadente.scadenta_data(tip, an, luna=luna)


def declaratii_datorate(vector, are_salariati, azi=None):
    """
    Intoarce {"datorate": [...], "neclar": [...]}.
      - datorate: declaratiile cu termen trecut sau in fereastra de urmarire (fapt cunoscut).
      - neclar:   declaratiile pe care NU le pot stabili fiindca lipseste un atribut din vector
                  (fiecare cu {tip, cauza}). Se afiseaza GRI, cu buton catre Vectorul fiscal.
    vector = dict cu regim_fiscal, platitor_tva, tip_decont, operatiuni_ic (oricare poate fi None).
    """
    azi = azi or azi_ro()   # [fus] verdict de zi (lipsa vs urmarit) = zi RO
    an = azi.year
    limita = azi + datetime.timedelta(days=PRAG_URMARIT_ZILE)
    datorate, neclar, neaplicabile = [], [], []

    # D2: perioadele candidate pornesc de la decembrie / T4 al anului precedent (termen 25 ian
    # an curent), altfel decembrie an-1 e invizibil PERMANENT (in an-1 termenul e viitor, in an
    # bucla nu-l acopera). Filtrul term<=limita taie singur ce e in viitor.
    per_luni = [(an - 1, 12)] + [(an, m) for m in range(1, 13)]
    per_trim = [(an - 1, 4, 12)] + [(an, tri, lf) for tri, lf in enumerate([3, 6, 9, 12], start=1)]

    # [tip_lowercase] tip = CHEIE de join (canonic lowercase, ca dispecerul/CHEIE_DUK); forma ANAF
    # uppercase traieste in CHEIE_DUK + se face upper() DOAR la randare, nu in coloana. Vezi DECIZII.
    def adauga(tip, a, luna_perioada, perioada_txt, tip_scad):
        term = _termen(a, luna_perioada, tip=tip_scad)
        if term <= limita:
            datorate.append({"tip": tip.lower(), "an": a, "luna": luna_perioada,
                             "termen": term.isoformat(), "perioada": perioada_txt})

    def gri(tip, cauza):
        neclar.append({"tip": tip.lower(), "cauza": cauza})

    def neaplic(tip, motiv):
        # "nu se datoreaza" (cunoscut), NU gri ("nu pot verifica"). Se afiseaza in grupul Nu se datoreaza.
        neaplicabile.append({"tip": tip.lower(), "motiv": motiv})

    def emite_tva(tip, tip_scad, cauza_periodicitate, marginit=False):
        """Emite `tip` pe perioada fiscala TVA (lunar/trimestrial dupa tip_decont). tip_decont necunoscut la
        un platitor -> gri cu cauza (principiul D3). [B1] marginit=True (D300/D394): sare perioadele DE
        DINAINTE de inregistrarea in scopuri de TVA (tva_inreg, fapt ANAF) - nu sunt restante, nu apar deloc."""
        d = (tip_decont or "").strip().lower()
        def _dupa_inreg(a, luna_final):     # perioada e datorata daca firma era inregistrata pana la finalul ei
            return not (marginit and tva_inreg and (a, luna_final) < tva_inreg)
        if d == "trimestrial":
            for a, tri, lf in per_trim:
                if _dupa_inreg(a, lf):
                    adauga(tip, a, lf, f"T{tri}", tip_scad)
        elif d == "lunar":
            for a, m in per_luni:
                if _dupa_inreg(a, m):
                    adauga(tip, a, m, _LUNI_NUME[m], tip_scad)
        else:
            gri(tip, cauza_periodicitate)

    platitor_tva = vector.get("platitor_tva")
    tip_decont = vector.get("tip_decont")
    regim_fiscal = vector.get("regim_fiscal")
    operatiuni_ic = vector.get("operatiuni_ic")
    # [B1] (an, luna) de la care D300/D394 se datoreaza = inceperea inregistrarii TVA (fapt ANAF). None = fara margine.
    _tvi = vector.get("tva_data_inceput")
    if hasattr(_tvi, "year"):
        tva_inreg = (_tvi.year, _tvi.month)
    elif isinstance(_tvi, str) and len(_tvi) >= 7:
        tva_inreg = (int(_tvi[:4]), int(_tvi[5:7]))
    else:
        tva_inreg = None
    # partida_simpla (PFA/II/PFL): derivat din tip_firma prin migrare_api.regim_contabil (fapt UNIC, NU
    # atribut nou). D406: PFA/persoane fizice sunt excluse NECONDITIONAT (OPANAF 407/2025 Anexa 5 pct.4 lit.a);
    # nici PFA in partida dubla nu datoreaza (conditia de partida dubla e doar la lit.n asociatii). DECIZII 23.07.
    partida_simpla = bool(vector.get("partida_simpla"))

    # D300 TVA — depinde de platitor_tva (DACA datoreaza) + tip_decont (PERIODICITATEA)
    if platitor_tva is None:
        gri("D300", "Platitor de TVA necompletat in vectorul fiscal - nu pot sti daca datorezi D300.")
    elif platitor_tva:
        emite_tva("D300", "d300", "Tip decont TVA necompletat - nu pot sti periodicitatea D300 (lunar/trimestrial).", marginit=True)
    # platitor_tva == False -> nu se datoreaza D300 (cunoscut)

    # D394 informativa livrari/achizitii nationale — doar platitori normali de TVA (art.316),
    # periodicitate = perioada fiscala TVA. Termen 30 luna urmatoare (scadente.py d394).
    # OPANAF 3769/2015, actualizat OPANAF 2194/2025.
    if platitor_tva is None:
        gri("D394", "Platitor de TVA necompletat - nu pot sti daca datorezi D394.")
    elif platitor_tva:
        emite_tva("D394", "d394", "Tip decont TVA necompletat - nu pot sti periodicitatea D394.", marginit=True)
    # neplatitor -> fara D394

    # D112 salariati (lunar) — are_salariati e fapt din DB, mereu cunoscut
    if are_salariati:
        for a, m in per_luni:
            adauga("D112", a, m, _LUNI_NUME[m], "d112")

    # D100 (micro, trimestrial) / D101 (profit, anual) — declaratii de PERSOANA JURIDICA (impozit micro/
    # profit). PFA/partida simpla NU le datoreaza: impozitul pe venit PFA se depune prin Declaratia unica
    # (D212), rutata separat (rip_api/d212_engine). Deci "nu se datoreaza" (cunoscut), NU gri. Vezi DECIZII 23.07.
    if partida_simpla:
        neaplic("D100", "D100 nu se datorează — impozitul pe veniturile microîntreprinderilor e al persoanelor "
                        "juridice; PFA (partidă simplă) depune Declarația unică (D212).")
        neaplic("D101", "D101 nu se datorează — impozitul pe profit e al persoanelor juridice; PFA (partidă "
                        "simplă) depune Declarația unică (D212).")
    elif regim_fiscal is None:
        cauza_r = "Regim fiscal necompletat - nu pot sti daca datorezi D100 (micro) sau D101 (profit)."
        gri("D100", cauza_r)
        gri("D101", cauza_r)
    else:
        regim = regim_fiscal.strip().lower()
        if regim == "micro":
            for a, tri, lf in per_trim:
                adauga("D100", a, lf, f"T{tri}", "d100")
        elif regim == "profit":
            # D101 pentru anul precedent, termen 25 martie an curent
            term = _termen(an - 1, tip="d101")
            if term <= limita:
                datorate.append({"tip": "d101", "an": an - 1, "luna": 12,
                                 "termen": term.isoformat(), "perioada": f"anual {an-1}"})

    # D390 operatiuni intracomunitare (lunar). Se depune de persoanele inregistrate art. 316 (platitor normal)
    # SAU art. 317 (special, pt achizitii/servicii IC). [B2] La neplatitor cu operatiuni IC nu STIM daca e
    # inregistrat art. 317 -> gri cu temei, NU emitem tacut si NU omitem tacut.
    if operatiuni_ic is None:
        gri("D390", "Operatiuni intracomunitare necompletat - nu pot sti daca datorezi D390.")
    elif operatiuni_ic:
        if platitor_tva:                       # inregistrat art. 316 -> D390 lunar
            for a, m in per_luni:
                adauga("D390", a, m, _LUNI_NUME[m], "d390")
        else:                                  # neplatitor cu operatiuni IC: art. 317? faptul lipseste -> gri
            gri("D390", "D390 se depune de persoanele înregistrate conform art. 316 sau art. 317 "
                        "(OPANAF 705/2020, pct. 1.1). Nu avem înregistrată calitatea art. 317 pentru această firmă.")

    # D406 SAF-T — obligatorie tuturor din 2025 (mici de la 01.01.2025). Periodicitate:
    # la PLATITORII de TVA = perioada fiscala TVA (lunar/trimestrial); la NEplatitori =
    # TRIMESTRIAL (nu au perioada fiscala TVA). Sursa: OPANAF 1783/2021 Anexa nr.4,
    # verificat 17.07.2026 la legislatie.just.ro/public/DetaliiDocument/248326 ("Contribuabilii
    # care nu sunt inregistrati in scopuri de TVA transmit Declaratia D406 trimestrial").
    # Termen: ultima zi a lunii urmatoare perioadei (scadente.py d406).
    # PFA/II/PFL EXCLUSE NECONDITIONAT de la D406 (OPANAF 407/2025, Anexa 5 pct.4 lit.a), enumerare
    # neconditionata; conditia de partida dubla e DOAR la lit.n) pt asociatii fara scop patrimonial; pct.3
    # lit.s) vizeaza doar persoane juridice). Deci nici PFA in partida dubla nu datoreaza. Restul: dupa TVA.
    if partida_simpla:
        neaplic("D406", "D406 (SAF-T) nu se datorează — OPANAF 407/2025, Anexa 5 pct.4 lit.q) exclude "
                        "persoanele fizice (PFA/II/PFL) de la obligația SAF-T (enumerare necondiționată).")
    elif platitor_tva is None:
        gri("D406", "Platitor de TVA necompletat - nu pot sti periodicitatea D406.")
    elif platitor_tva:
        emite_tva("D406", "d406", "Tip decont TVA necompletat - nu pot sti periodicitatea D406.")
    else:
        for a, tri, lf in per_trim:   # neplatitor de TVA (partida dubla) -> trimestrial
            adauga("D406", a, lf, f"T{tri}", "d406")

    return {"datorate": datorate, "neclar": neclar, "neaplicabile": neaplicabile}


def _dmy(iso):
    """'YYYY-MM-DD' -> 'zz.ll.aaaa' (pentru motiv, text afisat)."""
    if not iso:
        return ""
    s = str(iso)[:10]
    return "%s.%s.%s" % (s[8:10], s[5:7], s[0:4]) if len(s) == 10 else s


def declaratii_fapt(conn_schema, schema, vector, azi):
    """Declaratiile care se datoreaza pe FAPT, nu pe vector: D205 (dividende = rulaj 457) si D301
    (operatiuni IC pe luna). Citeste faptul prin PUNTEA din control_incrucisat (motoare separate -
    DECIZII 18.07 B: semaforul CHEAMA functia de fapt, n-o absoarbe). Intoarce {datorate, neaplicabile,
    neclar}; datorate poarta `fapt` (de ce se datoreaza)."""
    from core import control_incrucisat as _ci, scadente
    an = azi.year
    limita = azi + datetime.timedelta(days=PRAG_URMARIT_ZILE)
    datorate, neaplicabile, neclar = [], [], []
    platitor_tva = vector.get("platitor_tva")

    # D205 — anuala pentru anul precedent (termen ultima zi februarie an curent). Fapt: rulaj 457.
    Y = an - 1
    term205 = scadente.scadenta_data("d205", Y)
    if term205 <= limita:
        suma, are_note = _ci.dividende_distribuite(conn_schema, schema, Y)
        if suma > 0:
            datorate.append({"tip": "d205", "an": Y, "luna": 12, "perioada": f"anual {Y}",
                             "termen": term205.isoformat(),
                             "fapt": f"dividende distribuite în {Y} (rulaj cont 457)"})
        elif are_note:
            neaplicabile.append({"tip": "d205",
                                 "motiv": f"D205 nu se datorează — niciun rulaj pe cont 457 în {Y} (fără dividende distribuite)"})
        else:
            neclar.append({"tip": "d205",
                           "motiv": f"D205 — nu pot verifica: lipsesc note validate pe {Y} (nu știu dacă s-au distribuit dividende)"})

    # D301 — lunar, DOAR neplatitori de TVA cu operatiuni IC (fapt: tabelul d301_operatiuni pe luna).
    if platitor_tva is True:
        neaplicabile.append({"tip": "d301",
                             "motiv": "D301 nu se datorează — firma e plătitoare de TVA (D301 e pentru neînregistrați în scopuri de TVA)"})
    else:
        luni_an = {a: _ci.d301_luni_operatiuni(conn_schema, schema, a) for a in (an - 1, an)}
        vreo = False
        for a, m in [(an - 1, 12)] + [(an, mm) for mm in range(1, 13)]:
            if m in luni_an.get(a, set()):
                term = scadente.scadenta_data("d301", a, luna=m)
                if term <= limita:
                    datorate.append({"tip": "d301", "an": a, "luna": m, "perioada": _LUNI_NUME[m],
                                     "termen": term.isoformat(),
                                     "fapt": f"operațiuni intracomunitare înregistrate în {_LUNI_NUME[m]} {a}"})
                    vreo = True
        if not vreo:
            neaplicabile.append({"tip": "d301",
                                 "motiv": "D301 nu se datorează — nicio operațiune intracomunitară înregistrată"})
    return {"datorate": datorate, "neaplicabile": neaplicabile, "neclar": neclar}


def _clasifica(datorate, depuse, azi):
    """Pur: din datorate + depuse -> (lipsa, urmarit, confirmate), FIECARE cu `motiv` (de ce culoarea,
    inclusiv verde). depuse: dict (tip,an,luna) -> data_depunere (date) sau None."""
    # [C1] motiv = doar ce NU e in antet (tip·perioada·termen se randeaza structurat in rand). Confirmate:
    # data depunerii + la/dupa termen (info noua). Lipsa/urmarit: DOAR faptul (D205/D301 "de ce e datorat");
    # statusul "nedepusa/termen depasit" e implicit din sectiune (Restante) + termenul rosu din antet.
    lipsa, urmarit, confirmate = [], [], []
    for d in datorate:
        cheie = (d["tip"], d["an"], d["luna"])
        fapt = d.get("fapt") or ""
        fapt_sufix = (" · " + fapt) if fapt else ""
        term = datetime.date.fromisoformat(d["termen"])
        e = dict(d)
        if cheie in depuse:
            dd = depuse[cheie]
            data_txt = (" " + _dmy(dd.isoformat())) if dd else ""
            la_termen = ("" if not dd else (" la termen" if dd <= term else " după termen"))
            e["motiv"] = f"Depusă{data_txt}{la_termen}{fapt_sufix}"
            confirmate.append(e)
        elif term < azi:
            e["motiv"] = fapt                 # restanta: temeiul e structurat (antet + sectiune); doar faptul e nou
            lipsa.append(e)
        else:
            e["motiv"] = fapt                 # de urmarit: idem
            urmarit.append(e)
    return lipsa, urmarit, confirmate


def _stare(lipsa, urmarit, neclar):
    """Prioritate: rosu (restanta cunoscuta) > galben (termen apropiat) > gri (nu pot sti) > verde.
    Gri nu poate fi ascuns ca verde."""
    if lipsa:
        return "rosu"
    if urmarit:
        return "galben"
    if neclar:
        return "gri"
    return "verde"


def constatare_regim_tva(local, anaf, data=None):
    """[F180] Constatare 'Regim TVA vs ANAF' din platitor_tva(local) vs snapshot ANAF(anaf).
    PURA. Contract control_incrucisat: stare(verde/rosu/gri) + temei + limita, iar pe rosu
    +mesaj +remediu (investigatie — NICIODATA buton auto pe regimul fiscal). Vezi DECIZII 22.07 F180."""
    st = _fp.stare_tva_anaf(local, anaf)
    _txt = lambda b: "plătitoare TVA" if b else "neplătitoare TVA"
    data_txt = data.isoformat() if hasattr(data, "isoformat") else (data or "—")
    c = {"eticheta": "Regim TVA vs ANAF", "stare": st, "local": local, "anaf": anaf,
         "data_anaf": data_txt,
         "temei": "firma_profil.platitor_tva (setat manual) vs snapshot ANAF v9 scpTVA."}
    if st == "gri":
        c["mesaj"] = "Regimul TVA nu a fost comparat cu ANAF (fără snapshot)."
        c["limita"] = ("Fără valoare ANAF stocată — se populează la onboarding sau la "
                       "salvarea regimului TVA.")
    elif st == "verde":
        c["mesaj"] = "Regimul TVA din iConta coincide cu ANAF."
        c["limita"] = ("Comparat cu snapshot ANAF de la %s; ANAF poate fi în urmă cu o "
                       "mențiune recentă." % data_txt)
    else:  # rosu
        c["mesaj"] = ("Regim TVA în iConta: %s; la ANAF: %s (snapshot %s)."
                      % (_txt(local), _txt(anaf), data_txt))
        c["limita"] = ("Comparat cu snapshot ANAF de la %s; ANAF poate fi în urmă cu o "
                       "mențiune recentă." % data_txt)
        c["remediu"] = {"fel": "investigatie",
                        "actiune": ("Verifică în SPV statutul de plătitor TVA. Corectează Vectorul "
                                    "fiscal dacă valoarea din iConta e greșită, sau depune mențiuni la ANAF.")}
    return c


def evalueaza_firma(conn_schema, conn_public, tenant_id, schema, azi=None):
    """
    Intoarce {stare, datorate, depuse, lipsa, urmarit, confirmate, neclar, neaplicabile}.
    stare: 'verde' / 'galben' / 'gri' / 'rosu'. Fiecare linie poarta `motiv` (pe orice culoare).
    Acopera 9/9: D100/D101/D112/D300/D390/D394/D406 (vector) + D205/D301 (fapt, punte control_incrucisat).
    conn_schema: search_path pe schema firmei; conn_public: public (declaratii_depuse).
    """
    azi = azi or azi_ro()   # [fus] verdict de zi (lipsa vs urmarit) = zi RO

    # vector + salariati
    with conn_schema.cursor() as cur:
        cur.execute("SELECT regim_fiscal, platitor_tva, tip_decont, operatiuni_ic, "
                    "platitor_tva_anaf, platitor_tva_anaf_data, tip_firma, platitor_tva_anaf_inceput "
                    "FROM firma_profil LIMIT 1")
        row = cur.fetchone()
        vector = {}
        if row:
            from core.migrare_api import regim_contabil
            vector = {"regim_fiscal": row[0], "platitor_tva": row[1],
                      "tip_decont": row[2], "operatiuni_ic": row[3],
                      "platitor_tva_anaf": row[4], "platitor_tva_anaf_data": row[5],
                      "tip_firma": row[6],
                      # [B1] data inceperii inregistrarii TVA (fapt ANAF) -> margineste fereastra D300/D394
                      "tva_data_inceput": row[7],
                      # partida_simpla din regim_contabil (FAPTUL intr-un singur loc, nu recopiat). DECIZII 23.07.
                      "partida_simpla": regim_contabil(row[6]) == "simpla"}
        cur.execute("SELECT to_regclass('salariati')")
        are_sal = False
        if cur.fetchone()[0]:
            cur.execute("SELECT count(*) FROM salariati WHERE activ=true")
            are_sal = cur.fetchone()[0] > 0

    if not vector:
        return {"stare": "gri", "datorate": 0, "depuse": 0, "lipsa": [], "urmarit": [],
                "confirmate": [], "neaplicabile": [],
                "neclar": [{"tip": "—", "motiv": "Vector fiscal necompletat — nu pot evalua obligațiile firmei."}],
                "mesaj": "vector fiscal necompletat"}

    rez = declaratii_datorate(vector, are_sal, azi)
    datorate = list(rez["datorate"])
    neclar = list(rez["neclar"])

    # D205/D301 pe fapt (punte)
    fapt = declaratii_fapt(conn_schema, schema, vector, azi)
    datorate += fapt["datorate"]
    # neaplicabile = D100/D101/D406 (partida simpla, din declaratii_datorate) + D205/D301 pe fapt.
    neaplicabile = list(rez.get("neaplicabile", [])) + fapt["neaplicabile"]
    neclar += fapt["neclar"]

    # depuse din public (cu data depunerii, pentru motivul verde)
    with conn_public.cursor() as cur:
        cur.execute("SELECT tip, an, luna, (data_depunere AT TIME ZONE 'Europe/Bucharest')::date AS data_depunere "
                    "FROM public.declaratii_depuse_curente WHERE tenant_id=%s", (tenant_id,))  # [F163v2] vederea = depunerea curentă (nr_depunere max)
        depuse = {}
        for t, a, l, dd in cur.fetchall():
            depuse[(t, a, l)] = dd.date() if hasattr(dd, "date") else dd

    lipsa, urmarit, confirmate = _clasifica(datorate, depuse, azi)
    # neclar uniformizat pe campul `motiv` (declaratii_datorate foloseste `cauza`)
    neclar_m = [{"tip": n["tip"], "motiv": n.get("motiv") or n.get("cauza", "")} for n in neclar]
    stare = _stare(lipsa, urmarit, neclar_m)

    # [F180] regim TVA local vs snapshot ANAF — divergenta = constatare cu remediu investigatie. Escaladarea
    # peste starea de declaratii se face prin pastila_firma (severitatea vine din constatare, NU literal) -
    # un singur loc unde se decide severitatea, cf. DECIZII 23.07. _stare(lipsa,urmarit) de mai sus e SURSA
    # axei de declaratii, nu escaladare - ramane neatins.
    regim_tva_anaf = constatare_regim_tva(vector.get("platitor_tva"), vector.get("platitor_tva_anaf"),
                                          vector.get("platitor_tva_anaf_data"))
    stare = pastila_firma(stare, [regim_tva_anaf])

    return {"stare": stare, "datorate": len(datorate), "depuse": len(depuse),
            "lipsa": lipsa, "urmarit": urmarit, "confirmate": confirmate,
            "neclar": neclar_m, "neaplicabile": neaplicabile,
            "regim_tva_anaf": regim_tva_anaf}
