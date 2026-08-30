# -*- coding: utf-8 -*-
"""Registrul de evidenta fiscala. Sunt DOUA registre distincte, nu unul.

Asta a fost si greseala: pe 30.08 am scris ca registrul „nu se poate construi, s-ar inventa un
model", dupa ce citisem art. 19 si art. 68 din Codul fiscal si vazusem ca art. 68 alin. (9) trimite
modelul la un ordin care nu era in corpus. **Concluzia era falsa pentru varianta pe profit**, al
carei continut e specificat INTEGRAL in normele art. 19 (HG 1/2016, pct. 8). Erau doua registre, si
numai al doilea avea nevoie de ordin. Lectia a urcat la METODA §30.

**A. PROFIT** — art. 19 alin. (7) CF + HG 1/2016 pct. 8. Sapte categorii numite in norma, plus
„orice informatie cuprinsa in declaratia fiscala". Totalizare **pe trimestru si/sau an fiscal**,
evidentiere **pe natura economica**. Se DERIVA: sursa e D101 (aceleasi campuri P din care iese
declaratia) plus contabilitatea, pentru desfacerea pe natura.

**B. PERSOANE FIZICE** — art. 68 alin. (8)-(9) CF + **OMFP 3254/2017**, adus in corpus pe 30.08.
Anual, pe fiecare sursa din fiecare categorie de venit: venit brut, cheltuieli deductibile, venit
net / pierdere neta.

CE NU ACOPERA, masurat: **lista de randuri a modelului din Anexa nr. 1 la OMFP 3254/2017 e ELIDATA
in corpus** — portalul pune `...` in locul tabelului, si la fel in .html, si la fel in .txt. Am
cautat a doua aparitie in acelasi fisier (regula din METODA §30, prima instanta): nu exista, e o
singura aparitie. Deci randurile variantei B se construiesc din **articolele 3-5**, care spun ce
intra si ce NU intra, iar `MODEL_ANEXA1_ELIDAT` tine constatarea vizibila in loc s-o piarda.
"""
from decimal import Decimal

from core.afirmatii import afirmatie
from core.common import Temei
from core.unde import Unde

MODUL = "registru_evidenta_fiscala"

#: Nomenclator INCHIS. Cele doua registre au temeiuri, contribuabili si continut diferite.
VARIANTE = ("profit", "venituri_pf")

#: Constatare, nu scuza — si ca OBIECT, nu ca proza: modelul variantei B nu se poate cita rand cu
#: rand din corpus. Campurile spun CE lipseste, DE UNDE, UNDE s-a cautat si CU CE s-a inlocuit; o
#: propozitie ar fi cerut cititorului sa le extraga din text, iar unei garzi sa caute cuvinte in ea.
MODEL_ANEXA1_ELIDAT = {
    "act": "OMFP 3254/2017",
    "unde": "Anexa nr. 1",
    "ce_lipseste": "lista de randuri a modelului (coloana «Elemente de calcul»)",
    "cum_apare": "elidata — trei puncte in locul tabelului",
    "fisiere_verificate": ("anaf_surse/omfp_3254_2017_registru_evidenta_fiscala_persoane_fizice.txt",
                           "anaf_surse/omfp_3254_2017_registru_evidenta_fiscala_persoane_fizice.html"),
    "aparitii_in_fisier": 1,   # cautata a doua aparitie (METODA §30, prima instanta): nu exista
    "de_unde_vine_continutul": "articolele 3-5 ale ordinului, care spun ce se inscrie si ce NU",
    "verificat_la": "2026-08-30",
}

TEMEI_PROFIT = Temei(
    "HG", 1, 2016, art="norme art.19", alin="pct. 8",
    data_in="2016-01-01", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/hg_1_2016_norme_cod_fiscal.txt",
    text_citat=("In aplicarea prevederilor art. 19 alin. (7) din Codul fiscal, pentru calculul "
                "rezultatului fiscal contribuabilii sunt obligati sa intocmeasca un registru de "
                "evidenta fiscala, tinut in forma scrisa sau electronica, cu respectarea "
                "dispozitiilor Legii nr. 82/1991, republicata, referitoare la utilizarea sistemelor "
                "informatice de prelucrare automata a datelor. In registrul de evidenta fiscala "
                "trebuie inscrise veniturile si cheltuielile inregistrate conform reglementarilor "
                "contabile aplicabile, potrivit art. 19 alin. (1) din Codul fiscal, veniturile "
                "neimpozabile potrivit art. 23 din Codul fiscal, deducerile fiscale, elementele "
                "similare veniturilor, elementele similare cheltuielilor, cheltuielile "
                "nedeductibile, potrivit art. 25 din Codul fiscal, precum si orice informatie "
                "cuprinsa in declaratia fiscala, obtinuta in urma unor prelucrari ale datelor "
                "furnizate de inregistrarile contabile. Evidentierea veniturilor si a cheltuielilor "
                "aferente se efectueaza pe natura economica, prin totalizarea acestora pe trimestru "
                "si/sau an fiscal, dupa caz"))

TEMEI_PF = Temei(
    "OMFP", 3254, 2017, art="1-6",
    data_in="2018-01-05", verificat_la="2026-08-30", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/omfp_3254_2017_registru_evidenta_fiscala_persoane_fizice.txt",
    text_citat=("Registrul de evidenta fiscala are ca scop inscrierea informatiilor care stau la "
                "baza determinarii venitului net anual/pierderii nete anuale cuprins/cuprinse in "
                "Declaratia privind venitul realizat din Romania. Registrul de evidenta fiscala se "
                "completeaza anual cu totalul veniturilor si totalul cheltuielilor efectuate in "
                "scopul realizarii acestora. Registrul se tine pe fiecare sursa de venit din cadrul "
                "fiecarei categorii de venit. TVA colectata nu reprezinta venit si nu se "
                "inregistreaza in Registrul de evidenta fiscala. TVA dedusa nu reprezinta "
                "cheltuiala si nu se inregistreaza in Registrul de evidenta fiscala. Nu se "
                "inregistreaza cheltuielile care depasesc limitele prevazute la art. 68 alin. (5), "
                "cele efectuate in conditiile art. 68 alin. (7), si nici contributiile sociale "
                "obligatorii"))

TEMEI = {"profit": TEMEI_PROFIT, "venituri_pf": TEMEI_PF}

#: Cele SAPTE categorii pe care norma le enumera pentru varianta pe profit, plus a opta („orice
#: informatie cuprinsa in declaratia fiscala"). Ordinea e cea din norma, nu una aleasa de mine.
#: Fiecare poarta campurile D101 din care se compune — aceleasi din care iese declaratia, ca sa nu
#: existe doua adevaruri despre acelasi an.
CATEGORII_PROFIT = (
    ("venituri_contabile", "Venituri înregistrate conform reglementărilor contabile",
     "CF art. 19 alin. (1)", ("P1", "P4")),
    ("cheltuieli_contabile", "Cheltuieli înregistrate conform reglementărilor contabile",
     "CF art. 19 alin. (1)", ("P2", "P5")),
    ("venituri_neimpozabile", "Venituri neimpozabile",
     "CF art. 23", ("P17", "P18", "P19", "P20")),
    ("deduceri_fiscale", "Deduceri fiscale",
     "CF art. 19 alin. (1), art. 26", ("P11", "P12", "P13", "P14", "P15")),
    ("elemente_similare_venituri", "Elemente similare veniturilor",
     "CF art. 19 alin. (1)", ("P8",)),
    ("elemente_similare_cheltuieli", "Elemente similare cheltuielilor",
     "CF art. 19 alin. (1)", ("P9",)),
    ("cheltuieli_nedeductibile", "Cheltuieli nedeductibile",
     "CF art. 25", tuple("P%d" % n for n in range(23, 34))),
    ("informatii_din_declaratie", "Informații cuprinse în declarația fiscală",
     "HG 1/2016 pct. 8, teza finală", ("P22", "P35", "P40", "P41")),
)

#: Perioadele de totalizare pe care norma le admite: *„pe trimestru si/sau an fiscal, dupa caz"*.
#: Nomenclator INCHIS — o totalizare lunara ar fi o invenție.
TOTALIZARI = ("trimestru", "an")


class RegistruNeconstruibil(ValueError):
    """Registrul nu se poate intocmi din ce exista. Poarta `motiv` si `temei` ca DATE.

    Nu e acelasi lucru cu „registru gol": gol inseamna ca s-a putut construi si n-are randuri.
    """

    def __init__(self, mesaj, motiv=None, temei=None):
        super().__init__(mesaj)
        self.motiv = motiv
        self.temei = temei


def _i(x):
    return int(x or 0)


def _dec(x):
    return Decimal(str(x or 0))


def compune_profit(P, totalizare="an", perioada=None):
    """Cele opt categorii, compuse din campurile D101 — PUR, fara baza de date.

    De ce din D101 si nu dintr-un calcul propriu: norma spune ca registrul cuprinde *„orice
    informatie cuprinsa in declaratia fiscala, obtinuta in urma unor prelucrari ale datelor
    furnizate de inregistrarile contabile"*. Un al doilea motor ar putea da alte cifre decat
    declaratia depusa — si atunci registrul, care exista tocmai ca sa justifice declaratia, ar
    contrazice-o.
    """
    if totalizare not in TOTALIZARI:
        raise ValueError("totalizare necunoscuta %r; norma admite: %s"
                         % (totalizare, ", ".join(TOTALIZARI)))
    sectiuni = []
    for cod, eticheta, temei, campuri in CATEGORII_PROFIT:
        randuri = [{"camp": c, "valoare": _i(P.get(c))} for c in campuri]
        sectiuni.append({
            "cod": cod, "eticheta": eticheta, "temei": temei,
            "randuri": randuri,
            "total": sum(r["valoare"] for r in randuri),
        })
    return {"totalizare": totalizare, "perioada": perioada, "sectiuni": sectiuni}


# ─────────────────────────────────────────────────────────────────────────────────────────────
# B. VARIANTA PERSOANE FIZICE — CF art. 68 alin. (8)-(9) + OMFP 3254/2017
#
# Constatarea care a facut-o necesara nu e a mea, e scrisa in cod: `core/d212.py`, in `pull()` —
# *„D212 e MANUALA pe persoana fizica; firma nu are registru PF."* Venitul brut si cheltuielile
# deductibile se introduc direct in declaratie si NU se pastreaza nicaieri. Ori exact asta e rostul
# registrului (art. 2 din ordin): sa tina informatiile CARE STAU LA BAZA declaratiei. Fara el,
# declaratia n-are in spate niciun document care s-o justifice la control.
# ─────────────────────────────────────────────────────────────────────────────────────────────

#: Nomenclatorul OFICIAL de categorii, luat din structura D220 (`core/d220.py`: categ_venit 1-7),
#: nu inventat aici. Registrul se tine *„pe fiecare sursa de venit din cadrul fiecarei categorii"*,
#: iar categoria trebuie sa fie aceeasi cu cea din declaratie — altfel registrul ar clasifica altfel
#: decat documentul pe care il justifica.
CATEGORII_VENIT_PF = {
    1: "venituri comerciale",
    2: "venituri din profesii liberale",
    3: "venituri din drepturi de proprietate intelectuala",
    4: "venituri din activitati agricole",
    5: "venituri din silvicultura",
    6: "venituri din piscicultura",
    7: "venituri din cedarea folosintei bunurilor",
}

#: Modul de stabilire a venitului net, tot din structura D220 (`det_venit`). El decide CE PARTE din
#: registru se completeaza — nu o preferinta, ci art. 1 alin. (1)-(3) din ordin.
MOD_VENIT_NET = {1: "sistem real", 2: "cote forfetare", 3: "norma de venit"}

#: Cine completeaza NUMAI partea de venituri. Art. 1 alin. (2): la norma de venit; alin. (3):
#: drepturile de proprietate intelectuala POT completa numai partea de venituri.
DOAR_VENITURI = (3,)  # `det_venit` = norma de venit


def cheltuielile_se_inscriu(mod_venit_net, categorie):
    """Regula conditionala din art. 1. Scrisa ca FUNCTIE, nu ca un `if` ingropat in validare, ca sa
    poata fi probata direct: la norma de venit nu se inscriu cheltuieli, iar la drepturi de
    proprietate intelectuala inscrierea e OPTIONALA (alin. (3) zice „pot completa numai partea
    referitoare la venituri")."""
    if mod_venit_net in DOAR_VENITURI:
        return "nu"
    if categorie == 3:
        return "optional"
    return "da"


def valideaza_pf(date):
    """Refuza inscrierea incompleta sau pe o clasificare din afara nomenclatorului.

    `cheltuieli_deductibile` NU primeste niciodata default din `venit_brut` si nici zero tacut:
    zero inseamna *„nu s-au avut cheltuieli"*, iar lipsa inseamna *„nu s-a stabilit inca"*. Intr-un
    registru din care iese venitul net, cele doua duc la aceeasi cifra si la doua adevaruri diferite.
    """
    if date.get("categorie") not in CATEGORII_VENIT_PF:
        raise InregistrareIncompletaPF(
            "categorie de venit necunoscuta %r; nomenclatorul (D220, categ_venit) e inchis: %s"
            % (date.get("categorie"), ", ".join(str(k) for k in sorted(CATEGORII_VENIT_PF))),
            camp="categorie", temei=str(TEMEI_PF))
    if date.get("mod_venit_net") not in MOD_VENIT_NET:
        raise InregistrareIncompletaPF(
            "mod de stabilire a venitului net necunoscut %r" % date.get("mod_venit_net"),
            camp="mod_venit_net", temei=str(TEMEI_PF))
    for c in ("sursa_venit", "venit_brut"):
        if date.get(c) is None or (isinstance(date.get(c), str) and not date[c].strip()):
            raise InregistrareIncompletaPF(
                "Registrul cere «%s», iar campul e gol. Norma: %s" % (c, TEMEI_PF),
                camp=c, temei=str(TEMEI_PF))
    cer = cheltuielile_se_inscriu(date["mod_venit_net"], date["categorie"])
    ch = date.get("cheltuieli_deductibile")
    if cer == "da" and (ch is None or (isinstance(ch, str) and not ch.strip())):
        raise InregistrareIncompletaPF(
            "venitul net se stabileste in sistem real, deci cheltuielile deductibile se inscriu. "
            "Zero e un raspuns valid («nu s-au avut cheltuieli»); gol nu e. Norma: %s" % TEMEI_PF,
            camp="cheltuieli_deductibile", temei=str(TEMEI_PF))
    if cer == "nu" and ch not in (None, "", 0, "0"):
        raise InregistrareIncompletaPF(
            "la norma de venit nu se inscriu cheltuieli in registru (art. 1 alin. (2)); a fost data "
            "valoarea %r" % ch, camp="cheltuieli_deductibile", temei=str(TEMEI_PF))
    return cer


class InregistrareIncompletaPF(ValueError):
    """Refuz la inscrierea in registrul PF. Poarta `camp` si `temei` ca DATE."""

    def __init__(self, mesaj, camp=None, temei=None):
        super().__init__(mesaj)
        self.camp = camp
        self.temei = temei


def venit_net(venit_brut, cheltuieli_deductibile):
    """Venitul net anual / pierderea neta anuala. Se CALCULEAZA — stocat, ar putea contrazice
    randurile din care iese. Poate fi NEGATIV: «pierdere neta anuala» e chiar termenul ordinului,
    deci taierea la zero ar sterge o informatie pe care declaratia o cere."""
    return _dec(venit_brut) - _dec(cheltuieli_deductibile or 0)


def adauga_pf(conn, schema, an, date):
    """Inscrie un rand. `nr_crt` se DERIVA, pe (an, categorie, sursa) — registrul se tine pe fiecare
    sursa din fiecare categorie, deci si numerotarea curge acolo, nu global."""
    valideaza_pf(date)
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(MAX(nr_crt), 0) + 1 FROM {s}.registru_fiscal_pf "
                    "WHERE an = %s AND categorie_venit = %s AND sursa_venit = %s".format(s=schema),
                    (an, str(date["categorie"]), date["sursa_venit"]))
        nr = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO {s}.registru_fiscal_pf (an, categorie_venit, sursa_venit, nr_crt, "
            "venit_brut, cheltuieli_deductibile, rectificare, motiv_rectificare) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id".format(s=schema),
            (an, str(date["categorie"]), date["sursa_venit"], nr,
             date["venit_brut"], date.get("cheltuieli_deductibile") or 0,
             bool(date.get("rectificare")), date.get("motiv_rectificare")))
        iid = cur.fetchone()[0]
    conn.commit()
    return {"id": iid, "nr_crt": nr}


def randuri_pf(conn, schema, an):
    from psycopg2.extras import RealDictCursor
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM {s}.registru_fiscal_pf WHERE an = %s "
                    "ORDER BY categorie_venit, sursa_venit, nr_crt".format(s=schema), (an,))
        return [dict(r) for r in cur.fetchall()]


def registru_pf(conn, schema, an):
    """Registrul PF, ca afirmatie, grupat pe sursa din cadrul categoriei — cum cere art. 3 alin. (3)."""
    import datetime

    def _s(v):
        if isinstance(v, Decimal):
            return float(v)
        if isinstance(v, (datetime.date, datetime.datetime)):
            return v.isoformat()
        return v

    grupe = {}
    for r in randuri_pf(conn, schema, an):
        r = {k: _s(v) for k, v in r.items()}
        r["venit_net"] = float(venit_net(r["venit_brut"], r["cheltuieli_deductibile"]))
        cheie = (r["categorie_venit"], r["sursa_venit"])
        grupe.setdefault(cheie, []).append(r)

    sectiuni = []
    for (cat, sursa), rs in sorted(grupe.items()):
        try:
            eticheta = CATEGORII_VENIT_PF[int(cat)]
        except (ValueError, KeyError):
            eticheta = None   # o categorie iesita din nomenclator NU se boteaza la loc din cod
        sectiuni.append({
            "categorie": cat, "categorie_eticheta": eticheta, "sursa": sursa,
            "randuri": rs,
            "total_venit_brut": sum(x["venit_brut"] for x in rs),
            "total_cheltuieli": sum(x["cheltuieli_deductibile"] for x in rs),
            "venit_net": sum(x["venit_net"] for x in rs),
        })

    return afirmatie(
        "fapt", tip="registru_evidenta_fiscala_pf",
        motiv="Registrul de evidență fiscală pentru persoane fizice, CF art. 68 alin. (8)-(9)",
        temei_completitudine=(
            "toate rândurile înscrise pentru anul %d, grupate pe sursă din cadrul categoriei, cum "
            "cere art. 3 alin. (3). **Registrul cuprinde ce s-a înscris** — venitul brut și "
            "cheltuielile deductibile nu se derivă din evidența firmei: pe persoană fizică nu există "
            "contabilitate din care să iasă, iar D212 le primește azi direct în declarație. **Ce nu "
            "face încă:** nu alimentează D212 — declarația se completează în continuare separat, "
            "iar potrivirea dintre ele nu e gardată." % an),
        an=an, luna=None, unde=Unde("registru", "evidenta_fiscala_pf"),
        **{
        "varianta": "venituri_pf",
        "temei": str(TEMEI_PF),
        "model_elidat": dict(MODEL_ANEXA1_ELIDAT),
        "categorii": {str(k): v for k, v in CATEGORII_VENIT_PF.items()},
        "moduri_venit_net": {str(k): v for k, v in MOD_VENIT_NET.items()},
        "sectiuni": sectiuni,
        })


#: DE CE totalizarea pe TRIMESTRU nu se construieste aici, desi norma o admite. Categoriile
#: „informatii din declaratia fiscala" ies din formulele D101, care sunt ANUALE prin constructie:
#: rezerva legala deductibila are plafon pe capital si pe rezerva existenta la inceput de an, iar
#: pierderea reportata se scade din rezultatul anului. Aplicate pe un trimestru, ele n-ar da „acelasi
#: lucru, mai des" — ar da o cifra GRESITA, intr-un registru al carui rost e sa justifice o
#: declaratie. Un registru trimestrial se construieste cand exista o compunere trimestriala proprie,
#: nu prin rularea formulelor anuale pe trei luni.
TRIMESTRU_NECONSTRUIT = (
    "totalizarea pe trimestru cere o compunere proprie: formulele D101 (rezerva legală deductibilă, "
    "pierderea reportată) sunt anuale prin construcție, iar rulate pe un trimestru ar produce o "
    "cifră greșită într-un document care există ca să justifice declarația")


def poate_totaliza(totalizare):
    """`(da, motiv)` — se poate produce registrul pe totalizarea ceruta?

    Extrasa din `registru_profit` dupa ce RED-proof-ul a aratat ca proba de acolo era pe FORMA
    («functia contine un raise»), iar functia mai avea unul, pentru totalizarea necunoscuta: mutatia
    care stergea refuzul trecea verde. O decizie care se poate chema direct se poate si proba direct.
    """
    if totalizare not in TOTALIZARI:
        raise ValueError("totalizare necunoscuta %r; norma admite: %s"
                         % (totalizare, ", ".join(TOTALIZARI)))
    if totalizare == "trimestru":
        return False, TRIMESTRU_NECONSTRUIT
    return True, None


def refuz_totalizare(an, totalizare):
    """Refuzul, ca AFIRMAtIE. `eroare` e obligatorie la `verificare_rupta` fiindca fara ea nimeni nu
    poate incepe s-o repare — aici spune exact ce lipseste: o compunere trimestriala proprie."""
    _da, motiv = poate_totaliza(totalizare)
    return afirmatie(
        "verificare_rupta", tip="registru_evidenta_fiscala_profit",
        motiv="Registrul de evidență fiscală nu se poate întocmi pe totalizarea cerută",
        eroare=motiv,
        an=an, luna=None, unde=Unde("registru", "evidenta_fiscala_profit"),
        **{"varianta": "profit", "totalizare": totalizare, "temei": str(TEMEI_PROFIT),
           "totalizari_admise": list(TOTALIZARI)})


def registru_profit(conn, schema, an, totalizare="an"):
    """Registrul variantei PROFIT, ca afirmatie, pe datele firmei.

    Trece prin `d101.genereaza` — acelasi drum din care iese declaratia, inclusiv portile lui de
    reconciliere. Costa mai mult decat un calcul propriu si CADE cand cade si D101; amandoua sunt
    intentionate: un registru care se construieste cand declaratia nu se poate genera ar afirma
    despre un an ceva ce nu se poate depune.
    """
    from core import d101 as _d
    from core.common import Perioada
    da, motiv = poate_totaliza(totalizare)
    if not da:
        raise RegistruNeconstruibil(motiv, motiv="trimestru_neconstruit",
                                    temei=str(TEMEI_PROFIT))
    _xml, rez = _d.genereaza(conn, schema, Perioada(an))
    P = rez.P
    corp = compune_profit(P, totalizare, perioada=str(an))
    return afirmatie(
        "fapt", tip="registru_evidenta_fiscala_profit",
        motiv="Registrul de evidență fiscală (impozit pe profit), art. 19 alin. (7) din Codul fiscal",
        temei_completitudine=(
            "cele opt categorii pe care le enumeră HG 1/2016 pct. 8, compuse din **aceleași câmpuri "
            "din care iese D101** pe anul %d — nu dintr-un al doilea calcul. **Ce nu acoperă:** "
            "desfacerea pe natură economică dincolo de câmpul D101; norma o cere, iar aici fiecare "
            "categorie se oprește la rândul de declarație." % an),
        an=an, luna=None, unde=Unde("registru", "evidenta_fiscala_profit"),
        **{
        "varianta": "profit",
        "temei": str(TEMEI_PROFIT),
        "totalizari_admise": list(TOTALIZARI),
        "corp": corp,
        })
