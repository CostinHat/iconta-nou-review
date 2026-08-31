# -*- coding: utf-8 -*-
"""ABSENȚĂ DECLARATĂ: poziția 116 din nomenclatorul obligațiilor D100 nu se poate declara.

Costin, 31.08.2026: *«Poziția 116 — absență declarată, nu construcție. Zero din 19 firme o
datorează; cod fără nicio instanță pe care să se probeze e clasa cu valori implicite fabricate. Ce
nu se acceptă e tăcerea de azi: D100 nu poate declara obligația și nici nu spune că nu poate. Dacă
apare o firmă purtătoare, se află atunci, nu la depunere.»*

**DE CE NU SE CONSTRUIEȘTE.** Nu din lipsă de timp. `d100.py` cunoaște două coduri de obligație
(`121` micro, `103` profit), iar codul pentru 116 n-ar avea nicio instanță pe care să se probeze:
zero firme purtătoare, deci zero date, deci fiecare câmp al lui ar fi o alegere fără verificare — și
asta e chiar clasa care produce valori implicite fabricate. Un motor scris pe zero exemple nu e un
motor, e o ipoteză cu sintaxă.

**DE CE NICI TĂCEREA NU E ACCEPTABILĂ.** Astăzi D100 pur și simplu **nu știe** că obligația există.
O firmă purtătoare ar genera o declarație în care lipsește o obligație datorată, iar absența s-ar
afla **la depunere** — adică de la ANAF, nu de la noi.

**CINE DATOREAZĂ, citit la sursă** (OUG 24/2026 art. 2, adus în corpus 31.08.2026): operatorii
economici **titulari de acorduri petroliere** care extrag țiței din zăcăminte de pe teritoriul
României și obțin venituri din comercializarea lui (lit. a), sau care îl prelucrează — direct ori
prin persoane afiliate — și obțin venituri din comercializarea produselor energetice (lit. b).

**ȘI O A DOUA CONDIȚIE, care schimbă natura absenței:** contribuția se datorează **exclusiv pentru
lunile în care prețul mediu lunar Brent depășește 70 USD/baril** (art. 2 alin. (2)). Adică obligația
nu depinde doar de *cine e firma*, ci de un **preț de piață** — un fapt pe care aplicația nu-l are și
pentru care nu are nicio sursă. Chiar dacă mâine ar apărea o firmă purtătoare, calculul ar rămâne
neconstruibil fără cotația Brent. **Se scrie, ca să nu fie descoperit ca surpriză.**
"""
from core.common import Temei

MODUL = "d100_pozitia_116"

#: Poziția din nomenclator. NU e `cod_oblig` — vezi `d100.COD_BUGETAR`: poziția din tabel și codul
#: XML sunt lucruri diferite, iar codul XML al poziției 116 **nu se cunoaște**: nu apare în
#: OPANAF 602/2026, care numește doar poziția. Se scrie ca necunoscut, nu se ghicește.
POZITIA = 116
COD_OBLIG_XML = None

TEMEI_NOMENCLATOR = Temei(
    "OPANAF", 602, 2026, art="I", alin="pct. 1",
    data_in="2026-05-15", verificat_la="2026-08-31", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/opanaf_602_2026_modificare_opanaf_587_2016_formulare.txt",
    text_citat=("La anexa nr. 3 «Nomenclatorul obligatiilor de plata la bugetul de stat», dupa "
                "pozitia 115 se introduce o noua pozitie, pozitia 116, cu urmatorul cuprins: "
                "116. Contributie de solidaritate — Ordonanta de urgenta a Guvernului nr. 24/2026"))

TEMEI_CINE_DATOREAZA = Temei(
    "OUG", 24, 2026, art="2", alin="1",
    data_in="2026-04-03", verificat_la="2026-08-31", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/oug_24_2026_contributie_solidaritate.txt",
    text_citat=("datoreaza contributia de solidaritate urmatorii operatori economici: a) operatorii "
                "economici, titulari de acorduri petroliere, care extrag titei din zacaminte "
                "situate pe teritoriul Romaniei si obtin venituri din comercializarea acestuia; "
                "b) operatorii economici, titulari de acorduri petroliere, care extrag titei din "
                "zacaminte situate pe teritoriul Romaniei si care, direct sau prin persoanele "
                "afiliate, prelucreaza acest titei si obtin venituri din comercializarea "
                "produselor energetice"))

TEMEI_CAND_SE_DATOREAZA = Temei(
    "OUG", 24, 2026, art="2", alin="2",
    data_in="2026-04-03", verificat_la="2026-08-31", de_cine="Code/Costin", nivel_sursa="MO",
    url="anaf_surse/oug_24_2026_contributie_solidaritate.txt",
    text_citat=("Contributia de solidaritate prevazuta la alin. (1) se datoreaza exclusiv pentru "
                "lunile in care pretul mediu lunar al titeiului sortiment/clasa Brent depaseste "
                "nivelul de 70 USD/baril"))

#: Codurile de motiv. Nomenclator INCHIS — garda asertează pe COD, nu pe cuvinte din propoziție.
#: A treia oară în trei zile când o probă căuta un cuvânt într-un mesaj; de fiecare dată reparația
#: a fost aceeași: mesajul devine obiect.
MOTIVE = ("caen_in_zona", "caen_in_afara", "fara_caen")

#: CAEN-urile care ar putea indica un purtător. **PROXY, nu criteriul legii** — criteriul e
#: *titular de acord petrolier*, un atribut pe care aplicația nu-l are deloc. Direcția erorii se
#: scrie: proxy-ul poate RATA un purtător al cărui CAEN nu reflectă activitatea, deci lista de
#: purtători găsiți e un **plafon INFERIOR**. Nu poate însă inventa unul: un CAEN de panificație nu
#: nimerește aici din greșeală.
CAEN_POSIBIL_PURTATOR = ("0610", "0620", "1920", "3520", "4671", "4730", "4612")

#: Ce lipsește ca obligația să se poată declara. Se scrie ca DATE, nu ca proză, ca să poată fi
#: citit de o gardă și arătat pe ecran fără să fie repovestit.
CE_LIPSESTE = (
    "codul de obligație XML al poziției 116 (OPANAF 602/2026 numește poziția, nu codul)",
    "cotația medie lunară Brent, de care depinde dacă obligația se datorează în luna respectivă",
    "atributul «titular de acord petrolier» pe firmă — aplicația nu-l are sub nicio formă",
    "o firmă purtătoare pe care calculul să se poată proba",
)


def poate_datora(profil):
    """`(posibil, cod, motiv)` — firma ar putea fi purtătoare? PUR, se probează fără bază.

    Întoarce `True` doar pe proxy-ul de CAEN. **Nu afirmă că firma datorează** — afirmă că nu se
    poate exclude, iar diferența e chiar miezul: un `False` aici înseamnă «CAEN-ul nu indică», nu
    «nu datorează». `cod` e din `MOTIVE`, ca o gardă să nu caute cuvinte în propoziție.
    """
    caen = str((profil or {}).get("caen") or "").strip()
    if not caen:
        return False, "fara_caen", "firma n-are CAEN în profil — proxy-ul nu se poate aplica"
    if caen in CAEN_POSIBIL_PURTATOR:
        return True, "caen_in_zona", (
            "CAEN %s e în zona țiței/produse energetice; criteriul legii e însă «titular de acord "
            "petrolier», pe care aplicația nu-l cunoaște" % caen)
    return False, "caen_in_afara", "CAEN %s nu indică activitate de țiței/produse energetice" % caen


#: Pragul de care atârnă obligația, ca DATĂ, nu ca număr într-o propoziție: o gardă întreabă
#: `PRAG_BRENT_USD == 70`, nu dacă apare șirul „70 USD" undeva.
PRAG_BRENT_USD = 70


def constatare(profil):
    """Ce nu poate D100, ca OBIECT cu câmpuri. `None` dacă firma nu intră în discuție.

    Costin: *«D100 nu poate declara obligația și nici nu spune că nu poate.»* Asta e partea a doua —
    iar ea e un obiect, nu o propoziție, exact ca afirmațiile despre datele firmei (DS cap. 25).
    """
    posibil, cod, motiv = poate_datora(profil)
    if not posibil:
        return None
    from core.afirmatii import afirmatie
    return afirmatie(
        "verificare_rupta", tip="obligatie_nedeclarabila",
        motiv="Firma ar putea datora contribuția de solidaritate, iar D100 nu o poate declara",
        eroare="; ".join(CE_LIPSESTE),
        **{
        "ce": "obligatie_nedeclarabila",
        "pozitia": POZITIA,
        "cod_oblig_xml": COD_OBLIG_XML,
        # NU `motiv`: `afirmatie()` are deja un parametru cu numele asta. A doua oara aceeasi
        # ciocnire in doua zile (prima: `fel`, in registre_art321) — de-aia cheile proprii primesc
        # acum prefix.
        "motiv_cod": cod,
        "motiv_proxy": motiv,
        "ce_lipseste": list(CE_LIPSESTE),
        "prag_brent_usd": PRAG_BRENT_USD,
        "temei_nomenclator": str(TEMEI_NOMENCLATOR),
        "temei_cine": str(TEMEI_CINE_DATOREAZA),
        "temei_cand": str(TEMEI_CAND_SE_DATOREAZA),
        })


def avertisment(profil):
    """Propoziția pentru om, COMPUSĂ din constatare. `None` dacă nu e cazul."""
    c = constatare(profil)
    if c is None:
        return None
    return (
        "D100: firma ar putea datora **contribuția de solidaritate** (poziția %d din Nomenclatorul "
        "obligațiilor de plată, introdusă de %s), iar aplicația **nu o poate declara**. %s. "
        "Ce lipsește: %s. Obligația se datorează doar în lunile cu prețul Brent peste %d USD/baril "
        "(%s) — verifică manual și depune separat dacă e cazul."
        % (c["pozitia"], c["temei_nomenclator"], c["motiv_proxy"], "; ".join(c["ce_lipseste"]),
           c["prag_brent_usd"], c["temei_cand"]))
