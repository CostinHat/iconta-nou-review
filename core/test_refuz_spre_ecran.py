# -*- coding: utf-8 -*-
"""GARD — refuzul care trimite în alt ecran duce la CÂMPUL pe care îl cere (retest Costin 08.10.2026, completarea pct.2, verbatim în
DECIZII): „Butonul «Deschide Date firmă» din refuzul chitanței deschide pagina de sus; trebuie să ducă direct la secțiunea
«Chitanțe», cu câmpul seriei în focus.”

CLASA: fiecare refuz cu `ecran = "date_firma"` (seria chitanței, metoda de stoc, exceptarea AMEF, forma juridică / capitalul) poartă
`camp_ecran` = id-ul DOM al câmpului din Date firmă (contractul DS cap.6), dintr-o singură tabelă (`core/mesaje.CAMP_ECRAN_PE_COD`,
plus `capital_social.CAMP_LIPSA` pentru lipsurile capitalului); butonul îl dă ecranului, care îl aduce în vedere și îi dă focus.

CE FACE IMPOSIBIL: un cod de refuz spre Date firmă fără câmp; un câmp care nu există în ecran; un emițător NOU spre Date firmă pe
care tabela nu-l știe (fișierele care scriu `"date_firma"` sunt numărate); refuzul seriei fără câmp (instanța).
"""
import io
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DF = io.open(os.path.join(_RAD, "static", "js", "ecrane", "date_firma.js"), encoding="utf-8").read()

#: fișierele care emit un refuz spre Date firmă și codurile lor (citite la sursă, 08.10.2026)
EMITATORI = {
    "core/uc_tenants.py": {"SERIE_CHITANTA_LIPSA"},
    "core/metoda_stoc.py": {"METODA_STOC_NEDECLARATA", "METODA_STOC_NESUPORTATA", "METODA_STOC_ALTA"},
    "core/activitati_amef.py": {"AMEF_EXCEPTARE_NEDECLARATA"},
    "core/d394.py": {"AMEF_EXCEPTARE_NEDECLARATA"},
    "core/capital_social.py": {"CAPITAL_SOCIAL_LIPSA", "METODA_STOC_NEDECLARATA", "METODA_STOC_NESUPORTATA", "METODA_STOC_ALTA"},
    "core/uc_comun.py": set(),   # `refuz_spre_ecran` / `_UNDE_ECRAN`: transportă codul primit, nu emite unul propriu
}


def test_niciun_emitator_spre_date_firma_necunoscut():
    """MUTAȚIE: un fișier nou care scrie `"date_firma"` -> pică (tabela trebuie să-l știe)."""
    gasite = set()
    for d in ("core",):
        for f in sorted(os.listdir(os.path.join(_RAD, d))):
            if f.endswith(".py") and not f.startswith("test_"):
                if io.open(os.path.join(_RAD, d, f), encoding="utf-8").read().count('"date_firma"'):
                    gasite.add("%s/%s" % (d, f))
    assert gasite == set(EMITATORI), sorted(gasite ^ set(EMITATORI))


def test_fiecare_cod_are_campul_lui_si_campul_exista_in_ecran():
    """MUTAȚIE: `SERIE_CHITANTA_LIPSA` scos din `CAMP_ECRAN_PE_COD` -> pică; un id greșit (care nu e în date_firma.js) -> pică."""
    from core import mesaje, capital_social
    coduri = set().union(*EMITATORI.values()) - {capital_social.COD_REFUZ}
    assert {c for c in coduri if not mesaje.camp_ecran(c)} == set()
    campuri = set(mesaje.CAMP_ECRAN_PE_COD.values()) | set(capital_social.CAMP_LIPSA.values())
    assert {c for c in campuri if _DF.count('id="%s"' % c) != 1} == set()
    # fiecare lipsă posibilă a capitalului are câmp — enumerate FUNCȚIONAL, pe câte un profil sintetic pentru fiecare ramură
    lipsuri = set(capital_social.lipsa({"tip_firma": "srl"}))
    for forma, (_t, cere) in capital_social.FORME.items():
        lipsuri |= set(capital_social.lipsa({"tip_firma": "srl", "forma_juridica": forma}))
    assert lipsuri and lipsuri == set(capital_social.CAMP_LIPSA), lipsuri ^ set(capital_social.CAMP_LIPSA)


def test_refuzul_seriei_chitantei_poarta_campul_seriei():
    """Instanța din retest: refuzul chitanței fără serie duce la `df-serie_chitanta`. MUTAȚIE: `camp_ecran` scos din
    `refuz_spre_ecran` -> pică."""
    from core import uc_comun, mesaje
    d = uc_comun.refuz_spre_ecran(mesaje.MESAJ_SERIE_CHITANTA_LIPSA, mesaje.COD_SERIE_CHITANTA_LIPSA, "date_firma",
                                  "OMFP 2634/2015 anexa 1 pct.24")
    assert (d["ecran"], d["camp_ecran"]) == ("date_firma", "df-serie_chitanta")


def test_ecranul_tinta_aduce_campul_in_vedere_si_ii_da_focus():
    """Plumbul până la ecran: butonul trimite `camp`, Date firmă îl caută și îi dă focus. MUTAȚIE: `_tinta.focus()` scos -> pică."""
    dest = io.open(os.path.join(_RAD, "static", "js", "ecrane", "ecran_destinatie.js"), encoding="utf-8").read()
    assert dest.count("opt.camp || null") == 1 and dest.count("randeazaDateFirma(c2, nav, tenantId, { inapoiLa, camp })") == 1
    assert _DF.count("focusFaraSalt(_tinta)") == 1 and _DF.count("scrollIntoView") >= 1   # [159] focusul fără salt (api.js)
