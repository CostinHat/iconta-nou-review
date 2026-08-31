# -*- coding: utf-8 -*-
"""Eticheta unei alerte devine o PREDICTIE CONFRUNTABILA, nu un verdict.

Costin, 31.08.2026, dupa ce masuratoarea de mana a inversat etichetele pe amandoua actele zilei:
*«A gresit pe 2 din 2 acte, in directii opuse — asta nu e o constatare, e RATA LUI DE EROARE pe tot
esantionul existent. E palnia de intrare: tot ce vine de la ANAF se prioritizeaza pe el. Ce trebuie
sa fie adevarat dupa: eticheta e o predictie confruntabila cu impactul masurat, nu un verdict. Azi
am aflat ca minte doar fiindca am masurat de mana.»*

CE ERA GRESIT, mecanic — nu «modelul a gresit», ci FORMA intrebarii. Clasificatorul intorcea
`relevanta: mare|medie`, adica **o judecata de ansamblu, fara motive**. O judecata fara motive nu se
poate contrazice: cand impactul real iese altfel, n-ai ce compara cu ce. De-aia a putut minti doua
zile fara ca nimic sa se aprinda.

CE SE SCHIMBA. Nu se cere o judecata mai buna; se cer **doua fapte verificabile**, iar relevanta se
DERIVA din ele:

  1. **incotro merge documentul** — de la ANAF CATRE contribuabil (decizii, referate, proceduri ale
     organului fiscal) sau de la contribuabil CATRE ANAF (declaratii). Prima categorie nu ne atinge
     aproape niciodata: nu producem noi documentele alea.
  2. **ce declaratii atinge** — codurile pe care aplicatia le produce.

Amandoua se pot confrunta cu masuratoarea, fiindca masuratoarea raspunde la aceleasi doua intrebari.
Asta e diferenta dintre o predictie si un verdict.

INSTANTA FONDATOARE, cu cifra ei: **2 din 2 gresite**, in directii OPUSE.
  - `603/2026` prezis **mare**, impact **zero**: proceduri si formulare pe care ANAF le emite CATRE
    contribuabil, pe un capitol de CASS pe care nu-l calculam.
  - `602/2026` prezis **medie**, impact **real**: adauga pozitia 116 in nomenclatorul obligatiilor
    D100 si o declara lunar.
Amandoua ar fi iesit corect din cele doua fapte, fara nicio judecata de ansamblu.
"""

#: Ce campuri cere prompt-ul in raspunsul JSON. Exista ca DATE ca sa se poata confrunta cu
#: prompt-ul fara sa cautam cuvinte in proza lui: garda intreaba «multimea ceruta e asta?», nu
#: «apare sirul X undeva in text».
CAMPURI_CERUTE = ("titlu", "rezumat", "directie", "declaratii_atinse", "data_vigoare")

#: Campul pe care prompt-ul NU are voie sa-l mai ceara: verdictul. Daca reapare, derivarea din cod
#: devine decor.
CAMP_INTERZIS = "relevanta"

#: Incotro merge documentul. Nomenclator INCHIS — un al patrulea sens n-ar fi o nuanta, ar fi o
#: intrebare la care predictia n-a raspuns, si atunci nu se poate confrunta.
DIRECTII = ("catre_contribuabil", "catre_anaf", "necunoscut")

#: Verdictele posibile. `mare` si `medie` raman, ca sa nu se rupa ce citeste azi coloana; se ADAUGA
#: `zero`, care lipsea si care e chiar raspunsul corect pentru 603/2026. Fara el, un act care nu ne
#: atinge deloc trebuia botezat `medie` — adica minciuna era ceruta de nomenclator.
RELEVANTE = ("mare", "medie", "zero", "info")

#: Ce a masurat cineva, dupa. Acelasi nomenclator ca predictia, plus `nemasurat`.
MASURATORI = ("mare", "medie", "zero", "nemasurat")


def relevanta_din(directie, declaratii_atinse):
    """Relevanta, DERIVATA din cele doua fapte. Functie PURA — se poate proba fara baza si fara AI.

    Regula, scrisa ca sa poata fi contrazisa:
      - document care merge CATRE CONTRIBUABIL si nu atinge nicio declaratie de-a noastra -> `zero`.
        Nu-l producem noi; il primeste clientul de la ANAF.
      - atinge cel putin o declaratie pe care o producem -> `mare`, indiferent de directie. Un act
        care schimba un formular pe care il emitem e cea mai scumpa clasa de schimbare.
      - restul -> `medie`. Include si `necunoscut`, DELIBERAT: o directie pe care predictia n-a
        putut-o stabili nu se rotunjeste la `zero`.
    """
    if directie not in DIRECTII:
        raise ValueError("directie necunoscuta %r; nomenclatorul e inchis: %s"
                         % (directie, ", ".join(DIRECTII)))
    atinge = bool(declaratii_atinse)
    if atinge:
        return "mare"
    if directie == "catre_contribuabil":
        return "zero"
    return "medie"


def gresita(prezis, masurat):
    """Predictia a gresit? `nemasurat` NU e o greseala — e o absenta de proba."""
    if masurat in (None, "", "nemasurat"):
        return False
    return prezis != masurat


def confruntare(conn):
    """Confruntarea, ca AFIRMATII TIPATE — nu dictionare de proza (decizia din 21.08).

    O predictie care s-a dovedit gresita e literalmente o **contradictie**: doua afirmatii despre
    acelasi act care nu pot fi amandoua adevarate. `sursele` le NUMESTE pe amandoua — fara ele
    nimeni nu poate arbitra care a gresit, iar rata ar fi o cifra fara continut.
    """
    from psycopg2.extras import RealDictCursor
    from core.afirmatii import afirmatie
    from core.unde import Unde
    out = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, titlu, relevanta, impact_masurat, motiv_masurat, masurat_la "
                    "FROM public.alerte_fiscale "
                    "WHERE impact_masurat IS NOT NULL AND impact_masurat <> 'nemasurat' "
                    "ORDER BY id")
        for r in cur.fetchall():
            rau = gresita(r["relevanta"], r["impact_masurat"])
            comun = {"id_alerta": r["id"], "titlu": r["titlu"], "prezis": r["relevanta"],
                     "masurat": r["impact_masurat"], "gresit": rau}
            if rau:
                out.append(afirmatie(
                    "contradictie", tip="predictie_alerta",
                    motiv="Eticheta prezisa nu se potriveste cu impactul masurat",
                    sursele=["clasificator: %s" % r["relevanta"],
                             "masuratoare %s: %s" % (r["masurat_la"], r["impact_masurat"]),
                             r["motiv_masurat"] or ""],
                    unde=Unde("fisier", r["titlu"][:60]), **comun))
            else:
                out.append(afirmatie(
                    "fapt", tip="predictie_alerta",
                    motiv="Eticheta prezisa se potriveste cu impactul masurat",
                    temei_completitudine=("confruntarea acopera alertele care AU o masuratoare "
                                          "inregistrata; cele nemasurate nu se numara nici ca "
                                          "reusita, nici ca greseala"),
                    an=None, luna=None, unde=Unde("fisier", r["titlu"][:60]), **comun))
    return out


def rata(conn):
    """{masurate, gresite} — cifra pe care sta clichetul.

    NU se raporteaza ca procent: la doua masuratori un procent ar arata ca o proprietate stabila a
    clasificatorului, cand e o proba de doua. Se raporteaza ca `gresite din masurate`.
    """
    c = confruntare(conn)
    return {"masurate": len(c), "gresite": sum(1 for x in c if x["gresit"])}

