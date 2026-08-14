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
from core.common import azi_ro, pastila_firma, perioada_tva_tip  # [fus] ziua RO; [semafor] escaladare; [ruptura] normalizare tip_decont
from core import firma_profil_api as _fp  # [F180] stare_tva_anaf (comparatie platitor_tva vs snapshot)

PRAG_URMARIT_ZILE = 7   # termen in <= 7 zile, nedepus -> galben

# nume scurt de perioada pentru afisare
_LUNI_NUME = ["", "ian", "feb", "mar", "apr", "mai", "iun", "iul", "aug", "sep", "oct", "noi", "dec"]


def _termen(an, luna=None, tip="d300"):
    """Termenul de depunere al declaratiei `tip` pentru perioada (an, luna), delegat la
    core/scadente.py (25/martie per tip + prima zi lucratoare cu sarbatori legale).
    Semnatura pastreaza forma (an, luna) folosita de termene_api._termen."""
    return scadente.scadenta_data(tip, an, luna=luna)


# [G1] SURSA UNICA a temeiului de excludere PRIN FORMA (partida simpla -> declaratii de persoana juridica).
# Constanta de modul: consumata de neaplicabile_forma (API publica) SI de obligatii_datorate (inline, pe
# partida_simpla). Temei nedupli­cat, un singur loc. Vezi DECIZII 23.07.
_NEAP_FORMA_SIMPLA = {
    "d100": "D100 nu se datorează — impozitul pe veniturile microîntreprinderilor e al persoanelor "
            "juridice; PFA (partidă simplă) depune Declarația unică (D212).",
    "d101": "D101 nu se datorează — impozitul pe profit e al persoanelor juridice; PFA (partidă "
            "simplă) depune Declarația unică (D212).",
    "d406": "D406 (SAF-T) nu se datorează — OPANAF 407/2025, Anexa 5 pct.4 lit.q) exclude "
            "persoanele fizice (PFA/II/PFL) de la obligația SAF-T (enumerare necondiționată).",
}


def neaplicabile_forma(tip_firma):
    """Declaratiile NEaplicabile PRIN FORMA pentru o firma cu acest tip_firma (independent de fereastra/fapt).
    Partida simpla (PFA/II/PFL) -> D100/D101/D406 (declaratii de persoana juridica); {} pentru persoane
    juridice (aplicabilitatea lor depinde de FAPTE - platitor_tva/salariati/dividende - nu de forma).
    Refolosit de obligatii_datorate (semafor+termene) SI de declaratii_api (selector + poarta backend).
    O mapare (_NEAP_FORMA_SIMPLA), trei consumatori. Vezi DECIZII 23.07."""
    from core.migrare_api import regim_contabil
    return dict(_NEAP_FORMA_SIMPLA) if regim_contabil(tip_firma) == "simpla" else {}


def obligatii_datorate(vector, are_salariati, azi=None, *, jos=None, sus_zile=PRAG_URMARIT_ZILE, d390_fapt=None):
    """
    SURSA UNICA a mapicarii 'cine ce declaratie datoreaza' (regim/TVA/decont/IC/salariati),
    inclusiv marginirea la inregistrarea TVA (B1) si D390 art.317 gri la neplatitor (B2).
    Intoarce {"datorate": [...], "neclar": [...], "neaplicabile": [...]}, cu termenul in fereastra:
      - sus = azi + sus_zile   (semafor PRAG_URMARIT_ZILE=7 / termene ORIZONT_ZILE=60)
      - jos = None -> fara limita inferioara (semafor: include restantele, 'privire inapoi')
              data -> termen >= jos (termene: doar viitorul, 'privire inainte')
    Consumatori: declaratii_datorate (semafor, wrapper) + termene_api.termene_firma. Maparea obligatiilor
    traieste AICI, intr-un singur loc - NU se recopiaza (drift = bug; ex. termene fabrica candva D100 pe PFA).
      - datorate: declaratiile cu termen in fereastra (fapt cunoscut).
      - neclar:   declaratiile pe care NU le pot stabili fiindca lipseste un atribut din vector
                  (fiecare cu {tip, cauza}). Se afiseaza GRI, cu buton catre Vectorul fiscal.
    vector = dict cu regim_fiscal, platitor_tva, tip_decont, operatiuni_ic, partida_simpla, tva_data_inceput
             (oricare poate fi None; partida_simpla derivat de caller din tip_firma, ca la semafor).
    d390_fapt = callback optional (an, luna) -> bool|None pentru D390 pe FAPT lunar (nu bifa statica):
             True=luna cu operatiuni IC -> datorat; False=luna inchisa fara -> nu se datoreaza (cu temei);
             None=luna deschisa -> apelantul decide dupa directie (jos): semafor gri, termene afiseaza.
             d390_fapt=None (implicit) -> comportament vechi (bifa operatiuni_ic decide), apara matricea de 64.
    """
    azi = azi or azi_ro()   # [fus] verdict de zi (lipsa vs urmarit) = zi RO
    an = azi.year
    # ultima luna INCHISA (perioada de raportare curenta pt D390 pe fapt) - relativ la azi
    ultima_inchisa = (an - 1, 12) if azi.month == 1 else (an, azi.month - 1)
    limita = azi + datetime.timedelta(days=sus_zile)
    datorate, neclar, neaplicabile = [], [], []

    def _in_fereastra(term):
        # sursa UNICA de adevar pentru 'ce intra in fereastra' (jos optional, sus obligatoriu)
        return (jos is None or term >= jos) and term <= limita

    # D2: perioadele candidate pornesc de la decembrie / T4 al anului precedent (termen 25 ian
    # an curent), altfel decembrie an-1 e invizibil PERMANENT (in an-1 termenul e viitor, in an
    # bucla nu-l acopera). Filtrul term<=limita taie singur ce e in viitor.
    # [T4] +an+1: fereastra de termene (60z) poate trece in anul urmator (dec -> termene in ian/feb an+1);
    # bucla veche an=azi.year le rata. Filtrul _in_fereastra e sursa unica de adevar - supra-generarea NU
    # adauga fals la semafor (fereastra de 7z taie orice perioada an+1). Vezi test_termene decembrie 15/28.
    per_luni = [(an - 1, 12)] + [(an, m) for m in range(1, 13)] + [(an + 1, m) for m in range(1, 13)]
    per_trim = ([(an - 1, 4, 12)]
                + [(an, tri, lf) for tri, lf in enumerate([3, 6, 9, 12], start=1)]
                + [(an + 1, tri, lf) for tri, lf in enumerate([3, 6, 9, 12], start=1)])

    # [tip_lowercase] tip = CHEIE de join (canonic lowercase, ca dispecerul/CHEIE_DUK); forma ANAF
    # uppercase traieste in CHEIE_DUK + se face upper() DOAR la randare, nu in coloana. Vezi DECIZII.
    def adauga(tip, a, luna_perioada, perioada_txt, tip_scad, incert=False):
        term = _termen(a, luna_perioada, tip=tip_scad)
        if _in_fereastra(term):
            item = {"tip": tip.lower(), "an": a, "luna": luna_perioada,
                    "termen": term.isoformat(), "perioada": perioada_txt}
            if incert:
                item["incert"] = True   # [P4] perioada DESCHISA (D390 posibil, nu ferm) -> marcaj gri-semafor in UI
            datorate.append(item)

    def gri(tip, cauza):
        neclar.append({"tip": tip.lower(), "cauza": cauza})

    def neaplic(tip, motiv):
        # "nu se datoreaza" (cunoscut), NU gri ("nu pot verifica"). Se afiseaza in grupul Nu se datoreaza.
        neaplicabile.append({"tip": tip.lower(), "motiv": motiv})

    def neaplic_luna(tip, a, luna_p, motiv):
        # neaplicabil pe o LUNA anume (D390 pe fapt) - poarta an/luna in plus fata de neaplic simplu.
        neaplicabile.append({"tip": tip.lower(), "an": a, "luna": luna_p, "motiv": motiv})

    def emite_tva(tip, tip_scad, cauza_periodicitate, marginit=False):
        """Emite `tip` pe perioada fiscala TVA (lunar/trimestrial dupa tip_decont). tip_decont necunoscut la
        un platitor -> gri cu cauza (principiul D3). [B1] marginit=True (D300/D394): sare perioadele DE
        DINAINTE de inregistrarea in scopuri de TVA (tva_inreg, fapt ANAF) - nu sunt restante, nu apar deloc."""
        def _dupa_inreg(a, luna_final):     # perioada e datorata daca firma era inregistrata pana la finalul ei
            return not (marginit and tva_inreg and (a, luna_final) < tva_inreg)
        # [ruptura seed<->control 14.08.2026] tip_decont vine ca litera ("T"/"L" - seed/generatoare) SAU
        # cuvant intreg ("trimestrial"/"lunar" - calea de productie vector_fiscal_api). Egalitatea stricta pe
        # cuvant respingea litera -> gri "necompletat" la TOTI platitorii seed. Normalizam prin acelasi
        # perioada_tva_tip ca generatoarele (imun la ambele conventii).
        try:
            d = perioada_tva_tip({"tip_decont": tip_decont})    # "T"/"L"/"S"/"A" sau ridica
        except ValueError:
            gri(tip, cauza_periodicitate)
            return
        if d == "T":
            for a, tri, lf in per_trim:
                if _dupa_inreg(a, lf):
                    adauga(tip, a, lf, f"T{tri}", tip_scad)
        elif d == "L":
            for a, m in per_luni:
                if _dupa_inreg(a, m):
                    adauga(tip, a, m, _LUNI_NUME[m], tip_scad)
        else:
            gri(tip, cauza_periodicitate)   # S/A: periodicitate TVA neuzuala, nesuportata in semafor

    platitor_tva = vector.get("platitor_tva")
    tip_decont = vector.get("tip_decont")
    regim_fiscal = vector.get("regim_fiscal")
    operatiuni_ic = vector.get("operatiuni_ic")
    inreg_art317 = vector.get("inreg_art317")   # [art.317] inregistrare speciala scopuri TVA -> D390 satisfiabil la neplatitor
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
        neaplic("D100", _NEAP_FORMA_SIMPLA["d100"])   # [G1] temei din constanta unica
        neaplic("D101", _NEAP_FORMA_SIMPLA["d101"])
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
            if _in_fereastra(term):
                datorate.append({"tip": "d101", "an": an - 1, "luna": 12,
                                 "termen": term.isoformat(), "perioada": f"anual {an-1}"})

    # D390 operatiuni intracomunitare — pe FAPT lunar (nu obligatie fixa). Se depune NUMAI pentru lunile in care ia
    # nastere exigibilitatea operatiunilor IC (instr. completare D390, anexa OPANAF 705/2020 anexa 2 pct.1.2 (anterior OPANAF 394/2017, abrogat)).
    # FAPTUL PRIMEAZA: d390_fapt=True -> datorat INDIFERENT de bifa operatiuni_ic; bifa conteaza DOAR cand faptul e
    # None (luna deschisa, nu se poate sti inca). Fara callback (matrice/teste) -> bifa decide (compat istoric).
    if d390_fapt is None:
        # COMPAT — comportament istoric NESCHIMBAT (matricea de 64 il apara): bifa decide.
        if operatiuni_ic is None:
            gri("D390", "Operatiuni intracomunitare necompletat - nu pot sti daca datorezi D390.")
        elif operatiuni_ic:
            if platitor_tva:
                for a, m in per_luni:
                    adauga("D390", a, m, _LUNI_NUME[m], "d390")
            elif inreg_art317:
                for a, m in per_luni:
                    adauga("D390", a, m, _LUNI_NUME[m], "d390")   # [art.317] neplatitor inregistrat -> datorat
            else:
                gri("D390", "D390 se depune de persoanele înregistrate conform art. 316 sau art. 317 "
                            "(OPANAF 705/2020, pct. 1.1). Firma nu are marcată înregistrarea art. 317 în profil — "
                            "completați-o dacă firma e înregistrată.")
        # operatiuni_ic False -> nimic (istoric)
    elif platitor_tva:                          # art. 316: FAPTUL primeaza; bifa decide doar pe luna deschisa
        contradictie = []
        for a, m in per_luni:
            term = _termen(a, m, tip="d390")
            if not _in_fereastra(term):
                continue                        # in afara ferestrei -> nici nu intrebam faptul (economie interogari)
            fapt = d390_fapt(a, m)
            if fapt is True:
                adauga("D390", a, m, _LUNI_NUME[m], "d390")     # datorat, INDIFERENT de bifa
                if operatiuni_ic is False:
                    contradictie.append((a, m))                 # profil "fara IC" vs facturi IC reale -> semnal
            elif fapt is False:
                # luna INCHISA fara operatiuni -> nu se datoreaza (cost asimetric: restanta falsa = acuzatie).
                # Semafor confirma cu temei doar pe ULTIMA luna inchisa; termene skip tacit.
                if jos is None and (a, m) == ultima_inchisa:
                    neaplic_luna("D390", a, m,
                        "D390 nu se datorează pe %s %d — nicio operațiune intracomunitară în lună. Se depune numai "
                        "pentru lunile în care ia naștere exigibilitatea (instr. completare D390, anexa OPANAF "
                        "705/2020 anexa 2 pct.1.2 (anterior OPANAF 394/2017, abrogat))." % (_LUNI_NUME[m], a))
            else:
                # None = luna DESCHISA -> BIFA decide (faptul nu se poate sti inca; cost asimetric: termen ascuns = amenda).
                if operatiuni_ic:               # profil declara IC -> nu putem exclude: termene afiseaza, semafor gri
                    if jos is not None:
                        adauga("D390", a, m, _LUNI_NUME[m], "d390", incert=True)   # [P4] perioada deschisa = posibil, nu ferm
                    else:
                        gri("D390", "Perioada %s %d încă deschisă — nu pot stabili încă exigibilitatea "
                                    "operațiunilor intracomunitare." % (_LUNI_NUME[m], a))
                elif operatiuni_ic is None:      # profil necompletat -> gri necompletat (doar semafor)
                    if jos is None:
                        gri("D390", "Operatiuni intracomunitare necompletat - nu pot sti daca datorezi D390.")
                # operatiuni_ic False + luna deschisa -> profil declara fara IC -> nu emitem
        if contradictie:                        # [contradictie] operatiuni_ic=False vs facturi IC reale -> semnal, nu blocare (ca F185)
            luni_txt = ", ".join("%s %d" % (_LUNI_NUME[m], a) for (a, m) in contradictie)
            gri("D390", "Profilul firmei declară FĂRĂ operațiuni intracomunitare, dar există facturi "
                        "intracomunitare în perioada %s. Verificați Vectorul fiscal (operațiuni intracomunitare) — "
                        "D390 se datorează pentru lunile cu astfel de operațiuni." % luni_txt)
    else:                                        # NEplatitor: D390 e neaplicabil PRIN FORMA pe fapt.
        # POARTA: faptul D390 (d390_fapt -> DB per luna) se consulta DOAR la platitori (art. 316). Un neplatitor nu are
        # D390 pe fapt - obligatia depinde de inregistrarea art. 317, pe care n-o urmarim (facturile IC nu o dovedesc).
        # Decizie pe FLAG, fara DB -> nu atinge tabele care pot lipsi la un tenant de partida simpla (ex. d301_operatiuni).
        if operatiuni_ic is None:
            gri("D390", "Operatiuni intracomunitare necompletat - nu pot sti daca datorezi D390.")
        elif operatiuni_ic:                      # flag True -> art. 317: datorat daca inregistrat, altfel gri
            if inreg_art317:
                for a, m in per_luni:
                    adauga("D390", a, m, _LUNI_NUME[m], "d390")
            else:
                gri("D390", "D390 se depune de persoanele înregistrate conform art. 316 sau art. 317 "
                            "(OPANAF 705/2020, pct. 1.1). Firma nu are marcată înregistrarea art. 317 în profil — "
                            "completați-o dacă firma e înregistrată.")
        # operatiuni_ic False -> neplatitor fara IC declarate -> nimic (D390 neaplicabil prin forma)

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
        neaplic("D406", _NEAP_FORMA_SIMPLA["d406"])   # [G1] temei din constanta unica
    elif platitor_tva is None:
        gri("D406", "Platitor de TVA necompletat - nu pot sti periodicitatea D406.")
    elif platitor_tva:
        emite_tva("D406", "d406", "Tip decont TVA necompletat - nu pot sti periodicitatea D406.")
    else:
        for a, tri, lf in per_trim:   # neplatitor de TVA (partida dubla) -> trimestrial
            adauga("D406", a, lf, f"T{tri}", "d406")

    return {"datorate": datorate, "neclar": neclar, "neaplicabile": neaplicabile}


def declaratii_datorate(vector, are_salariati, azi=None, *, d390_fapt=None):
    """Semaforul (privire inapoi): fereastra [restante ... azi+7], fara limita inferioara.
    Wrapper subtire peste obligatii_datorate - comportament NESCHIMBAT fara d390_fapt (matricea de 64 il apara).
    d390_fapt = callback D390 pe fapt lunar, dat de evalueaza_firma (are conn_schema); None in teste/matrice."""
    return obligatii_datorate(vector, are_salariati, azi, d390_fapt=d390_fapt)


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
        # [ruptura D301<->facturi 14.08.2026] union: tabelul manual d301_operatiuni SI facturile IC primite
        # (fluxul normal). Altfel un neplatitor cu achizitii IC reale ca facturi primea "nicio operatiune IC".
        luni_an = {a: (_ci.d301_luni_operatiuni(conn_schema, schema, a)
                       | _ci.d301_luni_facturi_ic(conn_schema, schema, a)) for a in (an - 1, an)}
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
    lipsa, urmarit, confirmate, cu_intarziere = [], [], [], []
    for d in datorate:
        cheie = (d["tip"], d["an"], d["luna"])
        fapt = d.get("fapt") or ""
        fapt_sufix = (" · " + fapt) if fapt else ""
        term = datetime.date.fromisoformat(d["termen"])
        e = dict(d)
        if cheie in depuse:
            dd = depuse[cheie]
            data_txt = (" " + _dmy(dd.isoformat())) if dd else ""
            tarziu = bool(dd) and dd > term
            la_termen = ("" if not dd else (" la termen" if not tarziu else " după termen"))
            e["motiv"] = f"Depusă{data_txt}{la_termen}{fapt_sufix}"
            # [09.08.2026] Depusă DUPĂ termen -> coş separat cu_intarziere, NU confirmate/La zi.
            # Faptul (dd>term) era deja în motiv, dar categoria o înghiţea la La zi -> "LA ZI (N)"
            # ascundea întârzierile. NU e restanţă (e depusă) -> _stare neatins, nu urcă pastila.
            (cu_intarziere if tarziu else confirmate).append(e)
        elif term < azi:
            e["motiv"] = fapt                 # restanta: temeiul e structurat (antet + sectiune); doar faptul e nou
            lipsa.append(e)
        else:
            e["motiv"] = fapt                 # de urmarit: idem
            urmarit.append(e)
    return lipsa, urmarit, confirmate, cu_intarziere


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


def evalueaza_firma(conn_schema, conn_public, tenant_id, schema, azi=None, *, cu_reconciliere=True):
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
                    "platitor_tva_anaf, platitor_tva_anaf_data, tip_firma, platitor_tva_anaf_inceput, "
                    "inreg_art317 "
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
                      "tva_data_inceput": row[7], "inreg_art317": row[8],
                      # partida_simpla din regim_contabil (FAPTUL intr-un singur loc, nu recopiat). DECIZII 23.07.
                      "partida_simpla": regim_contabil(row[6]) == "simpla"}
        cur.execute("SELECT to_regclass('salariati')")
        are_sal = False
        if cur.fetchone()[0]:
            cur.execute("SELECT count(*) FROM salariati WHERE (data_incetare IS NULL OR data_incetare >= CURRENT_DATE) AND (data_angajare IS NULL OR data_angajare <= CURRENT_DATE)")
            are_sal = cur.fetchone()[0] > 0

    if not vector:
        return {"stare": "gri", "datorate": 0, "depuse": 0, "lipsa": [], "urmarit": [],
                "confirmate": [], "cu_intarziere": [], "neaplicabile": [],
                "neclar": [{"tip": "—", "motiv": "Vector fiscal necompletat — nu pot evalua obligațiile firmei."}],
                "mesaj": "vector fiscal necompletat"}

    # [D390-fapt] semaforul intreaba faptul lunar (facturi IC + manual + d301), nu bifa statica operatiuni_ic.
    from core import d390 as _d390
    _d390_fapt = lambda a, l: _d390.d390_are_operatiuni(conn_schema, schema, a, l, azi)
    rez = declaratii_datorate(vector, are_sal, azi, d390_fapt=_d390_fapt)
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

    lipsa, urmarit, confirmate, cu_intarziere = _clasifica(datorate, depuse, azi)
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

    # [Tura4] Reconciliere SURSA<->DECLARATIE, VIZIBILA in Control fiscal prin ACELASI mecanism ca poarta
    # de generare (control_incrucisat.reconciliaza_declaratii - refoloseste dXXX_reconciliere.reconciliaza,
    # NU un motor nou). Punte, ca declaratii_fapt (motoare separate). Perioada = ultima luna INCHISA
    # (declaratiile se reconciliaza pe perioade incheiate). Escaladeaza pastila prin constatari (rosu urca,
    # gri NU - filozofia control_incrucisat). ANTI-"D300 mort": daca PUNTEA insasi se rupe, NU se inghite
    # tacit -> constatare ROSIE zgomotoasa (nu gri). cu_reconciliere=False dezactiveaza (consumatori usori).
    reconciliere = None
    if cu_reconciliere:
        an_r, luna_r = (azi.year - 1, 12) if azi.month == 1 else (azi.year, azi.month - 1)
        from core import control_incrucisat as _ci_rec
        try:
            reconciliere = _ci_rec.reconciliaza_declaratii(conn_schema, schema, an_r, luna_r)
        except Exception as _e:
            reconciliere = {"an": an_r, "luna": luna_r, "stare": "rosu", "constatari": [{
                "stare": "rosu", "eticheta": "Reconciliere surse<->declaratii - PUNTE RUPTA",
                "mesaj": ("Reconcilierea nu a putut fi apelata (%s: %s) - semnalat, nu ascuns "
                          "(anti-D300 mort)." % (type(_e).__name__, _e)),
                "temei": ("Puntea control_incrucisat.reconciliaza_declaratii a ridicat; contractul ei e sa "
                          "nu ridice. Un except->gri ar ascunde ruptura ca verdict permanent gri."),
                "remediu": None}],
                "explicatie": "", "limita": "Reconcilierea surse<->declaratii nu a rulat.",
                "modul": "control_incrucisat", "reguli": ""}
        # severitatea vine din constatari (pastila_firma), NU dintr-un literal - un rosu de reconciliere urca
        # pastila firmei; gri-ul (nu pot verifica) NU o urca. Vezi DECIZII 23.07 + common.pastila_firma.
        stare = pastila_firma(stare, [regim_tva_anaf] + list(reconciliere.get("constatari") or []))

    return {"stare": stare, "datorate": len(datorate), "depuse": len(depuse),
            "lipsa": lipsa, "urmarit": urmarit, "confirmate": confirmate,
            "cu_intarziere": cu_intarziere,
            "neclar": neclar_m, "neaplicabile": neaplicabile,
            "regim_tva_anaf": regim_tva_anaf,
            "reconciliere_surse": reconciliere}
