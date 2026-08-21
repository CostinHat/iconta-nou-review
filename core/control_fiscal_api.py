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


def neaplicabile_selector(vector, *, ic_fapt=None):
    """[S1 plimbare 14.08.2026] NEaplicabile pt SELECTORUL de declaratii: forma + VECTORUL TVA.

    FAPTUL BATE VECTORUL (21.08.2026, decis de Costin - tiparul tenant_006). `ic_fapt` e un callback
    fara argumente care intoarce True (s-au gasit operatiuni intracomunitare REALE), False (nu s-au
    gasit, iar evidenta e completa cat putem sti) sau None (evidenta e INCOMPLETA - exista documente
    neprocesate, deci absenta nu se poate afirma). D390/D301 se blocheaza DOAR pe False.

    DE CE. Vectorul e o AFIRMATIE a cuiva; faptul e o OBSERVATIE. Cand se contrazic, faptul castiga si
    vectorul devine ce trebuie corectat - altfel un selector care blocheaza pe bifa il impiedica pe
    contabil sa declare o obligatie pe care firma o ARE (exact ce s-a intamplat pe tenant_006: vectorul
    zicea fara IC, firma avea achizitii intracomunitare reale).

    Cand faptul LIPSESTE si vectorul spune nu, blocajul RAMANE - si nu devine „nu pot verifica", ca la
    cele trei D301. Diferenta e reala: acolo tacea un TABEL (absenta unei observatii), aici a raspuns
    un OM. Masurat 21.08: campul e tri-stare cu placeholder gol, iar salvarea e refuzata cu mesaj
    propriu daca ramane necompletat (`date_firma.js`), backendul respinge None (IC_LIPSA), si 17 din 17
    firme il au completat. Vectorul NEcompletat produce deja gri in semafor, nu blocaj.

    LIMITA declarata: sonda de fapt citeste facturile IC (ambele directii) si tabelul manual D301; NU
    citeste `d390_manual`. O firma care are DOAR linii manuale D390 ramane blocata in selector - dar
    semaforul ii arata obligatia, si remediul (corecteaza Vectorul) e in mesaj.
    """
    neap = neaplicabile_forma(vector.get("tip_firma"))
    platitor = vector.get("platitor_tva")
    ic = vector.get("operatiuni_ic")
    if platitor is False:
        neap.setdefault("d300", "D300 nu se datorează — firma nu e înregistrată în scopuri de TVA (art. 316).")
        neap.setdefault("d394", "D394 nu se datorează — firma nu e plătitoare de TVA.")
    if platitor is True:
        neap.setdefault("d301", "D301 nu se datorează — e pentru neînregistrații în scopuri de TVA (firma e plătitoare).")
    if ic is False:
        fapt = ic_fapt() if ic_fapt else False
        if fapt is True:
            return neap          # faptul contrazice bifa -> NU blocam; semaforul semnaleaza contradictia
        if fapt is None:
            return neap          # evidenta incompleta -> absenta nu se poate afirma
        # [absenta_observatie 21.08.2026] Motivul isi numeste SURSA si poarta remediul: nu afirma despre
        # lume dintr-o bifa, spune cine a declarat si unde se corecteaza.
        neap.setdefault("d390", "D390 nu se datorează — Vectorul fiscal declară că firma nu are "
                                "operațiuni intracomunitare. Dacă firma a avut livrări sau achiziții "
                                "intracomunitare, corectează Vectorul fiscal.")
        if platitor is False:
            neap.setdefault("d301", "D301 nu se datorează — Vectorul fiscal declară că firma nu are "
                                    "operațiuni intracomunitare. Dacă firma a avut achiziții de la "
                                    "furnizori din UE, corectează Vectorul fiscal.")
    return neap


def ic_fapt_din_db(conn, schema, an):
    """Sonda de FAPT pentru selector: exista operatiuni intracomunitare in `an-1`..`an`?
    True = da (facturi IC pe oricare directie, sau linii manuale D301).
    None = nu am gasit, DAR evidenta e incompleta (e-Facturi descarcate de la SPV, neinregistrate inca)
           -> absenta nu se poate afirma.
    False = nu am gasit si nu stiu de nimic in asteptare.
    Citire pura (SELECT); nu scrie nimic."""
    import datetime as _dt

    from core import control_incrucisat as _ci
    try:
        fic = _ci.facturi_ic(conn, schema, _dt.date(an - 1, 1, 1), _dt.date(an + 1, 1, 1))
        if any(fic.get(k) for k in ("primita", "emisa")):
            return True
        for a in (an - 1, an):
            if _ci.d301_luni_operatiuni(conn, schema, a):
                return True
    except Exception:
        return None                      # nu pot citi faptul -> nu afirm absenta (fail-safe)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass(%s)", (schema + ".efactura_primite",))
            if cur.fetchone()[0]:
                cur.execute("SELECT count(*) FROM " + schema + ".efactura_primite "
                            "WHERE status = 'descarcata'")
                if cur.fetchone()[0]:
                    return None          # documente descarcate, neinregistrate -> evidenta incompleta
    except Exception:
        # MASCA MOTIVATA: daca nu pot CITI faptul, nu am voie sa afirm absenta lui. Tacerea aici
        # inseamna None = „nu pot sti", care DEBLOCHEAZA selectorul - deci esecul citirii nu poate
        # produce niciodata un blocaj. Directia opusa (except -> False) ar transforma o eroare de
        # citire intr-o afirmatie despre lume, exact clasa absenta_observatie.
        return None
    return False


def obligatii_datorate(vector, are_salariati, azi=None, *, jos=None, sus_zile=PRAG_URMARIT_ZILE, d390_fapt=None, d112_fapt=None, existenta_fapt=None, d100_fapt=None, d390_incomplet=None):
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
    d100_fapt = callback optional (an, luna_final_trim) -> bool|None pentru D100 micro pe FAPT (baza de venituri),
             simetric cu d390_fapt/d112_fapt. D100 pe zero e STRUCTURAL invalid la DUKIntegrator (sectiunea
             <obligatie> obligatorie >=1, anaf_surse/d100_struct_anaf.txt) -> un trimestru INCHIS fara venituri NU
             are D100 de depus (nu e restanta falsa). True=are baza venituri -> restanta; False=trimestru inchis
             fara venituri (si fara facturi nefacturate) -> neaplic cu temei; None=nu se poate sti (ex. facturi
             necontabilizate) -> emit (reminder). Consultat DOAR pe restante (jos None, termen<azi); obligatia
             curenta/viitoare se emite normal. d100_fapt=None (implicit) -> comportament vechi (regim decide),
             apara matricea de 64. Gateaza DOAR micro (impozit pe venituri); profit (D101) neatins.
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

    # [C - regula 4] declaratie de EXISTENTA (D100/D101/D406-neplatitor): o RESTANTA pe un an in care NU pot
    # demonstra ca firma exista/era activa NU se emite ca lipsa (verdict nesustinut) -> GRI "necunoscut
    # declarat" o data pe (declaratie, an). existenta_fapt(an) -> "da" (activitate demonstrabila, emite) sau
    # MOTIV (string gri). None in teste/matrice -> comportament vechi. Doar restantele (termen < azi) se
    # filtreaza (jos None); obligatia curenta/viitoare (termen >= azi) se emite normal.
    _gri_ex = set()
    def _adauga_existenta(tip, a, luna_perioada, perioada_txt, tip_scad):
        if existenta_fapt is not None and jos is None and _termen(a, luna_perioada, tip=tip_scad) < azi:
            st = existenta_fapt(a)
            if st != "da":
                k = (tip.lower(), a)
                if k not in _gri_ex:
                    _gri_ex.add(k)
                    neclar.append({"tip": tip.lower(), "an": a, "cauza": st})
                return
        adauga(tip, a, luna_perioada, perioada_txt, tip_scad)

    def _adauga_d100_micro(a, luna_final, perioada_txt):
        # [#d100_fapt - audit tenant_006 18.08.2026] D100 micro pe FAPT (baza venituri), simetric cu d390_fapt.
        # Intai poarta de EXISTENTA (an nedemonstrabil -> gri, ca _adauga_existenta). Apoi, pe RESTANTE (jos None,
        # termen<azi), poarta de VENITURI: un trimestru INCHIS fara venituri NU are D100 (nil-ul D100 e structural
        # invalid la DUK - sectiunea <obligatie> obligatorie). d100_fapt False -> neaplic (nu restanta falsa);
        # True/None -> emit. Obligatia curenta/viitoare (termen>=azi) se emite normal (reminder), fara poarta.
        if existenta_fapt is not None and jos is None and _termen(a, luna_final, tip="d100") < azi:
            st = existenta_fapt(a)
            if st != "da":
                k = ("d100", a)
                if k not in _gri_ex:
                    _gri_ex.add(k)
                    neclar.append({"tip": "d100", "an": a, "cauza": st})
                return
        if d100_fapt is not None and jos is None and _termen(a, luna_final, tip="d100") < azi:
            if d100_fapt(a, luna_final) is False:
                neaplic_luna("D100", a, luna_final,
                    "D100 nu se datorează pe %s %d — fără venituri în trimestru (bază 0). Impozitul pe veniturile "
                    "microîntreprinderilor se declară numai pentru trimestrele cu venituri; declarația fără "
                    "obligație e respinsă de validatorul ANAF (secțiunea obligație e obligatorie)." % (perioada_txt, a))
                return
            # True (are bază) sau None (nu se poate ști, ex. facturi necontabilizate) -> emit (reminder)
        adauga("D100", a, luna_final, perioada_txt, "d100")

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
        # [A - regula 4] platitor CU marginit dar FARA data de inregistrare TVA cunoscuta (tva_inreg None):
        # nu pot demonstra DE CAND e inregistrata -> NU emit RESTANTA pe lunile trecute (verdict nesustinut).
        # Suprim restanta necunoscuta si emit UN singur GRI "necunoscut declarat"; obligatia curenta/viitoare
        # (termen >= azi, in fereastra) se emite normal. Doar la semafor (jos None): la termene (jos set,
        # privire inainte) restantele-s deja excluse de fereastra, deci nimic de gri-uit.
        necunoscut_data = marginit and tva_inreg is None and jos is None
        supr = [False]
        def _emite(a, luna_final, txt):
            if necunoscut_data and _termen(a, luna_final, tip=tip_scad) < azi:
                supr[0] = True   # restanta pe luna necunoscuta -> suprimata; GRI o data mai jos
                return
            adauga(tip, a, luna_final, txt, tip_scad)
        if d == "T":
            for a, tri, lf in per_trim:
                if _dupa_inreg(a, lf):
                    _emite(a, lf, f"T{tri}")
        elif d == "L":
            for a, m in per_luni:
                if _dupa_inreg(a, m):
                    _emite(a, m, _LUNI_NUME[m])
        else:
            gri(tip, cauza_periodicitate)   # S/A: periodicitate TVA neuzuala, nesuportata in semafor
            return
        if necunoscut_data and supr[0]:
            gri(tip, "necunoscut declarat: nu pot demonstra de când e firma înregistrată în scopuri de TVA "
                     "pentru restanțele trecute — completați „Data înregistrării în scopuri de TVA” "
                     "în Vectorul fiscal.")

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
        gri("D300", "Plătitor de TVA necompletat în Vectorul fiscal — nu pot ști dacă datorezi D300.")
    elif platitor_tva:
        emite_tva("D300", "d300", "Tip decont TVA necompletat — nu pot ști periodicitatea D300 (lunar/trimestrial).", marginit=True)
    # platitor_tva == False -> nu se datoreaza D300 (cunoscut)

    # D394 informativa livrari/achizitii nationale — doar platitori normali de TVA (art.316),
    # periodicitate = perioada fiscala TVA. Termen 30 luna urmatoare (scadente.py d394).
    # OPANAF 3769/2015, actualizat OPANAF 2194/2025.
    if platitor_tva is None:
        gri("D394", "Plătitor de TVA necompletat — nu pot ști dacă datorezi D394.")
    elif platitor_tva:
        emite_tva("D394", "d394", "Tip decont TVA necompletat — nu pot ști periodicitatea D394.", marginit=True)
    # neplatitor -> fara D394

    # D112 salariati (lunar) — datorat per-luna DOAR daca firma avea >=1 salariat ACTIV in luna respectiva.
    # [#6] are_salariati era un snapshot boolean pe CURRENT_DATE aplicat la TOATE lunile -> o firma cu primul
    # salariat angajat la mijloc de an primea D112 restant pe lunile de dinainte de angajare. d112_fapt =
    # callback (an, luna)->bool dat de evalueaza_firma (are conn_schema); None in teste/matrice -> comportament
    # vechi (are_salariati boolean pe toate lunile, apara matricea de 64). Simetric cu d390_fapt.
    if d112_fapt is None:
        if are_salariati:
            for a, m in per_luni:
                adauga("D112", a, m, _LUNI_NUME[m], "d112")
    else:
        for a, m in per_luni:
            term = _termen(a, m, tip="d112")
            if _in_fereastra(term) and d112_fapt(a, m):   # interogam faptul DOAR pentru lunile din fereastra
                adauga("D112", a, m, _LUNI_NUME[m], "d112")

    # D100 (micro, trimestrial) / D101 (profit, anual) — declaratii de PERSOANA JURIDICA (impozit micro/
    # profit). PFA/partida simpla NU le datoreaza: impozitul pe venit PFA se depune prin Declaratia unica
    # (D212), rutata separat (rip_api/d212_engine). Deci "nu se datoreaza" (cunoscut), NU gri. Vezi DECIZII 23.07.
    if partida_simpla:
        neaplic("D100", _NEAP_FORMA_SIMPLA["d100"])   # [G1] temei din constanta unica
        neaplic("D101", _NEAP_FORMA_SIMPLA["d101"])
    elif regim_fiscal is None:
        cauza_r = "Regim fiscal necompletat — nu pot ști dacă datorezi D100 (micro) sau D101 (profit)."
        gri("D100", cauza_r)
        gri("D101", cauza_r)
    else:
        regim = regim_fiscal.strip().lower()
        if regim == "micro":
            for a, tri, lf in per_trim:
                _adauga_d100_micro(a, lf, f"T{tri}")
        elif regim == "profit":
            # D101 pentru anul precedent, termen 25 martie an curent (existenta an-1 demonstrabila -> altfel gri)
            _adauga_existenta("D101", an - 1, 12, f"anual {an-1}", "d101")

    # D390 operatiuni intracomunitare — pe FAPT lunar (nu obligatie fixa). Se depune NUMAI pentru lunile in care ia
    # nastere exigibilitatea operatiunilor IC (instr. completare D390, anexa OPANAF 705/2020 anexa 2 pct.1.2 (anterior OPANAF 394/2017, abrogat)).
    # FAPTUL PRIMEAZA: d390_fapt=True -> datorat INDIFERENT de bifa operatiuni_ic; bifa conteaza DOAR cand faptul e
    # None (luna deschisa, nu se poate sti inca). Fara callback (matrice/teste) -> bifa decide (compat istoric).
    if d390_fapt is None:
        # COMPAT — comportament istoric NESCHIMBAT (matricea de 64 il apara): bifa decide.
        if operatiuni_ic is None:
            gri("D390", "Operațiuni intracomunitare necompletat — nu pot ști dacă datorezi D390.")
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
                    # [21.08.2026] POARTA INTARITA: „luna inchisa" inseamna doar ca luna calendaristica
                    # s-a terminat, NU ca evidenta e completa. Daca stim de documente in asteptare pe
                    # luna aia, nu AFIRMAM absenta - dar nici nu convertim toata clasa in necunoastere:
                    # gri doar pe lunile cu semnal CONCRET (vezi d390.evidenta_incompleta).
                    _inc = d390_incomplet(a, m) if d390_incomplet else None
                    if _inc:
                        gri("D390", _inc)
                    else:
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
                        gri("D390", "Operațiuni intracomunitare necompletat — nu pot ști dacă datorezi D390.")
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
            gri("D390", "Operațiuni intracomunitare necompletat — nu pot ști dacă datorezi D390.")
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
        gri("D406", "Plătitor de TVA necompletat — nu pot ști periodicitatea D406.")
    elif platitor_tva:
        emite_tva("D406", "d406", "Tip decont TVA necompletat — nu pot ști periodicitatea D406.", marginit=True)
    else:
        for a, tri, lf in per_trim:   # neplatitor de TVA (partida dubla) -> trimestrial
            _adauga_existenta("D406", a, lf, f"T{tri}", "d406")

    return {"datorate": datorate, "neclar": neclar, "neaplicabile": neaplicabile}


def declaratii_datorate(vector, are_salariati, azi=None, *, d390_fapt=None, d112_fapt=None, existenta_fapt=None, d100_fapt=None, d390_incomplet=None):
    """Semaforul (privire inapoi): fereastra [restante ... azi+7], fara limita inferioara.
    Wrapper subtire peste obligatii_datorate - comportament NESCHIMBAT fara callback-uri de fapt
    (matricea de 64 il apara). d390_fapt/d112_fapt/existenta_fapt/d100_fapt = callback-uri pe fapt, date de
    evalueaza_firma (are conn_schema); None in teste/matrice."""
    return obligatii_datorate(vector, are_salariati, azi, d390_fapt=d390_fapt, d112_fapt=d112_fapt,
                              existenta_fapt=existenta_fapt, d100_fapt=d100_fapt,
                              d390_incomplet=d390_incomplet)


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
            # [absenta_observatie 21.08.2026 — a PATRA instanta a clasei, dupa cele trei D301 (R2')]
            # „niciun rulaj pe 457" NU e un fapt despre lume: e absenta unei inregistrari in registrul
            # NOSTRU. Poarta `are_note` cere o SINGURA nota validata pe an - o nota din ianuarie face
            # din tacerea restului anului un „fapt". Criteriul de separare e REMEDIUL (harta casetelor):
            # aici omul are de verificat DACA faptul a existat (hotarare AGA, extras de cont), nu de
            # completat un atribut - deci apartine lui „Nu pot verifica", NICIODATA lui „Nu se datoreaza".
            # PROBA care a fortat reincadrarea (sonda R6, 21.08): BETA PROFIT (t8397) are D205/12-2025
            # DEPUS, in timp ce semaforul spunea ca nu se datoreaza. Depunerea e proba vie a incadrarii
            # gresite. PRECEDENT: tenant_006, unde acelasi tipar a produs „nu se datoreaza" pe o firma
            # cu achizitii intracomunitare REALE.
            neclar.append({"tip": "d205",
                           "motiv": f"D205 — nu pot verifica: am note validate pe {Y}, dar niciun rulaj "
                                    f"pe contul 457 (dividende). Absența unei înregistrări nu dovedește "
                                    f"absența distribuirii — verifică hotărârea AGA și extrasul de cont "
                                    f"pentru {Y}."})
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
            # [absenta_observatie 20.08.2026] NU „nu se datorează", ci „nu pot verifica". Tabelul gol
            # nu e un fapt despre lume — e absența unei OBSERVAȚII în datele noastre, iar absența unei
            # înregistrări nu e absența unui fapt. Spre deosebire de d100_fapt/d390_fapt, calea asta
            # n-are NICIO verificare de completitudine: nici lună închisă, nici „nimic în așteptare".
            # PRECEDENT: pe tenant_006 exact asta a produs „nu se datorează" pe baza vectorului, în
            # timp ce firma avea achiziții intracomunitare REALE — verificam conformarea la vectorul
            # declarat, nu realitatea operațiunilor. Decis 20.08 (R2′), vezi DECIZII.
            neclar.append({"tip": "d301",
                           "cauza": "nu am nicio înregistrare de operațiune intracomunitară — "
                                    "verifică dacă firma a avut achiziții de la furnizori din UE "
                                    "(facturi primite, e-facturi, extrase). Absența înregistrărilor "
                                    "nu dovedește absența operațiunilor."})
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


def depuneri_fara_obligatie(datorate, neaplicabile, neclar, depuse):
    """TRECEREA INVERSA (R6, 21.08.2026): peste `depuse`, nu peste `datorate`. PURA.

    `_clasifica` itereaza pe obligatii si consulta `depuse` ca DICTIONAR - deci o depunere care
    n-are obligatie pereche nu e VIZITATA niciodata. Nu e o omisiune, e o proprietate a formei:
    „nu se datoreaza" si „s-a depus" nu se ciocneau nicaieri, deci o contradictie era invizibila
    PRIN CONSTRUCTIE. Masurat pe baza (17 firme): 7 depuneri contraziceau un „nu se datoreaza".

    Intoarce lista de {tip, an, luna, data, fel, mesaj}:
      fel="contrazice"  depunere pe o perioada declarata NEAPLICABILA. Cele doua afirmatii nu pot
                        fi amandoua adevarate. Semnal, nu blocare - aceeasi forma ca `contradictie`
                        de la D390 (profil fara IC vs facturi IC reale).
      fel="opinie"      depunere pe un tip aflat in „nu pot verifica". NU stinge necunoasterea: ca
                        s-a depus dovedeste ca firma a CONSIDERAT ca datoreaza, nu ca a considerat
                        corect, si nu spune nimic despre perioadele in care N-A depus - care e chiar
                        intrebarea. Daca ar stinge-o, firma care a depus tot ar parea complet
                        verificata, desi ea e tocmai cea despre care nu stii daca a depus tot.
                        Se ARATA ca informatie; NU se numara ca obligatie stinsa.
    O depunere in afara ferestrei `datorate` nu e niciuna: fereastra e o alegere de AFISARE, nu o
    afirmatie despre obligatie.

    MESAJUL nu citeaza motivul; citatul sta separat, in `motiv_citat`. Pe ecran motivul e randat
    imediat deasupra semnalului, iar citatul il dubla - acelasi paragraf de patru randuri de doua ori
    la rand, vazut in captura. Consumatorii care NU afiseaza motivul (audit_tenant) il compun ei.

    PERIOADA se scrie „luna/an", nu „decembrie 2025": pentru declaratiile trimestriale/anuale luna
    din inregistrare e ANCORA de codificare ANAF (D394 T3 -> luna 09), nu luna calendaristica. A o
    traduce in nume de luna ar repeta exact misdiagnosticul D394/003.
    """
    dat = {(d["tip"], d["an"], d["luna"]) for d in datorate}
    neap_per = {(n["tip"], n.get("an"), n.get("luna")) for n in neaplicabile if n.get("an")}
    neap_tip = {n["tip"] for n in neaplicabile if not n.get("an")}
    # Motivul se ia de la INTRAREA POTRIVITA, nu de la prima cu acelasi tip. Prima versiune tinea un
    # dictionar pe tip si a produs „D100 pe 3/2026 ... nu se datoreaza: «nu se datoreaza pe T4 2025»" -
    # un mesaj care citeaza alta perioada, adica exact clasa de defect pe care gardul asta o vaneaza.
    motive_per, motive_tip = {}, {}
    for n_ in list(neaplicabile) + list(neclar):
        m_ = (n_.get("motiv") or n_.get("cauza") or "").strip()
        if n_.get("an"):
            motive_per[(n_["tip"], n_.get("an"), n_.get("luna"))] = m_
        else:
            motive_tip.setdefault(n_["tip"], m_)

    def _motiv(t_, an_, luna_):
        return motive_per.get((t_, an_, luna_)) or motive_tip.get(t_) or "—"

    neclar_tip = {n["tip"] for n in neclar}

    out = []
    for (tip, an, luna), data in sorted(depuse.items(), key=lambda k: (str(k[0][0]), k[0][1] or 0, k[0][2] or 0)):
        t = (tip or "").lower()
        if (t, an, luna) in dat:
            continue                       # are obligatie pereche - o trateaza _clasifica
        per = "%s/%s" % (luna, an)
        d_txt = (" (%s)" % _dmy(data.isoformat())) if data else ""
        if (t, an, luna) in neap_per or t in neap_tip:
            out.append({"tip": t, "an": an, "luna": luna, "data": data, "fel": "contrazice",
                        "motiv_citat": _motiv(t, an, luna),
                        "mesaj": ("Neconcordanță în iConta: %s pe perioada marcată %s e DEPUSĂ%s, deși "
                                  "motivul înregistrat spune că nu se datorează — cele două nu pot fi "
                                  "amândouă adevărate. Nu e o greșeală a ta și n-ai ce retrage: cel mai "
                                  "probabil motivul nostru e greșit." % (t.upper(), per, d_txt))})
        elif t in neclar_tip:
            out.append({"tip": t, "an": an, "luna": luna, "data": data, "fel": "opinie",
                        "motiv_citat": _motiv(t, an, luna),
                        "mesaj": ("%s pe perioada marcată %s e DEPUSĂ%s. Cineva a considerat că se "
                                  "datorează — e o informație în plus, nu un răspuns: nu spune nimic "
                                  "despre perioadele în care nu s-a depus."
                                  % (t.upper(), per, d_txt))})
    return out


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
         "temei": "Plătitor de TVA setat manual în firmă vs. starea din snapshot ANAF v9 (scpTVA)."}
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
    from core import control_incrucisat as _ci_sal
    _d390_fapt = lambda a, l: _d390.d390_are_operatiuni(conn_schema, schema, a, l, azi)
    # [#6] D112 pe FAPT lunar (salariat activ in luna), nu snapshot are_sal pe CURRENT_DATE.
    _d112_fapt = lambda a, l: _ci_sal.are_salariat_activ_luna(conn_schema, schema, a, l)
    # [C - regula 4] existenta/activitate demonstrabila pe an: creat_la (public.tenants) + activitate reala din
    # schema (facturi/salariati/note, prin puntea control_incrucisat.existenta_firma_an). D100/D101/D406-neplatitor
    # pe un an nedemonstrabil -> GRI "necunoscut declarat", NU restanta.
    with conn_public.cursor() as _curt:
        _curt.execute("SELECT (creat_la AT TIME ZONE 'Europe/Bucharest')::date FROM public.tenants WHERE id=%s", (tenant_id,))
        _rt = _curt.fetchone()
        _creat_la = _rt[0] if _rt else None
    def _existenta_fapt(an):
        if _ci_sal.existenta_firma_an(conn_schema, schema, an):
            return "da"                                  # activitate reala in an -> restanta sustinuta
        if _creat_la and an < _creat_la.year:
            return ("necunoscut declarat: nu pot demonstra că firma exista/era activă în %d — firma a fost "
                    "creată în aplicație în %d, iar pentru %d nu există facturi, salariați sau note." % (an, _creat_la.year, an))
        return ("necunoscut declarat: nu pot demonstra că firma exista/era activă în %d — nu există facturi, "
                "salariați sau note pe %d în evidență; completați vectorul/activitatea firmei." % (an, an))
    def _d100_fapt(a, luna_final):
        # [#d100_fapt] D100 micro pe baza de venituri a trimestrului (aceeasi sursa ca generatorul d100:
        # pull + deriva_obligatii). True=are obligatie (venituri>0); False=trimestru fara venituri SI fara
        # facturi emise (genuin gol -> D100 pe zero = structural invalid la DUK, nu restanta); None=venituri 0
        # dar exista facturi emise (posibil necontabilizate) -> nu pot sti, emit reminder.
        from core import d100 as _d100
        from core.common import Perioada as _Per
        try:
            trim = (luna_final + 2) // 3
            per = _Per(a, trim=trim)
            prof, venituri, cheltuieli = _d100.pull(conn_schema, schema, per)
            obl, _av = _d100.deriva_obligatii(prof, venituri, cheltuieli, a, luna_final, None)
            if obl:
                return True
            inc, sf = per.interval()
            with conn_schema.cursor() as _cf:
                _cf.execute("SELECT count(*) FROM facturi WHERE directie='emisa' "
                            "AND data_emitere >= %s AND data_emitere < %s", (inc.isoformat(), sf.isoformat()))
                nf = _cf.fetchone()[0]
            return None if nf else False
        except Exception:
            # MASCA MOTIVATA: fail-safe DELIBERAT - daca nu pot calcula baza de venituri (pull/DB esueaza),
            # intorc None -> semaforul EMITE D100 (reminder), NU suprima. Suprimarea (neaplic) se face DOAR pe
            # False (fapt DEMONSTRAT fara venituri), niciodata pe o eroare de citire (ar ascunde o obligatie reala).
            return None
    # [21.08.2026] Inainte de a AFIRMA ca o luna n-a avut operatiuni IC, intrebam daca evidenta lunii
    # e completa cat putem sti (e-Facturi descarcate si neinregistrate). Poarta intarita, nu convertita.
    _d390_incomplet = lambda a, l: _d390.evidenta_incompleta(conn_schema, schema, a, l)
    rez = declaratii_datorate(vector, are_sal, azi, d390_fapt=_d390_fapt, d112_fapt=_d112_fapt,
                              existenta_fapt=_existenta_fapt, d100_fapt=_d100_fapt,
                              d390_incomplet=_d390_incomplet)
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
    # [R6 21.08.2026] Trecerea INVERSA peste `depuse`. NU escaladeaza pastila si NU se randeaza inca:
    # ecranul Control fiscal e STOP pana la confirmarea lui Costin asupra a CE se vede. Consumator viu
    # azi: frontend_test/audit_tenant.py (F7) + gard. Ramane in raspuns ca sa fie un singur loc unde se
    # calculeaza, nu doua cand se cabla si UI-ul.
    depuneri_contra = depuneri_fara_obligatie(datorate, neaplicabile, neclar_m, depuse)
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
                "temei": ("Puntea control_incrucisat.reconciliaza_declaratii a ridicat; contractul ei e să "
                          "nu ridice. Un except->gri ar ascunde ruptura ca verdict permanent gri."),
                "remediu": None}],
                "explicatie": "", "limita": "Reconcilierea surse<->declarații nu a rulat.",
                "modul": "control_incrucisat", "reguli": ""}
        # severitatea vine din constatari (pastila_firma), NU dintr-un literal - un rosu de reconciliere urca
        # pastila firmei; gri-ul (nu pot verifica) NU o urca. Vezi DECIZII 23.07 + common.pastila_firma.
        stare = pastila_firma(stare, [regim_tva_anaf] + list(reconciliere.get("constatari") or []))

    return {"stare": stare, "datorate": len(datorate), "depuse": len(depuse),
            "depuneri_fara_obligatie": depuneri_contra,
            "lipsa": lipsa, "urmarit": urmarit, "confirmate": confirmate,
            "cu_intarziere": cu_intarziere,
            "neclar": neclar_m, "neaplicabile": neaplicabile,
            "regim_tva_anaf": regim_tva_anaf,
            "reconciliere_surse": reconciliere}
