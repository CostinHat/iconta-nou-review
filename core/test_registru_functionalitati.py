# -*- coding: utf-8 -*-
"""Garda de integritate a FUNCTIONALITATI.csv (registrul canonic al functionalitatilor).

DE CE E TEST, NU verificator_conformitate.py (DECIZII 22.07): verificatorul iese mereu 0
(raportor de nits DS, nu gate); suita e verde-obligatoriu -> un rand malformat RUPE suita
INAINTE de commit. Integritatea structurii registrului e un INVARIANT, nu o conventie de stil.

DE CE CONTEAZA: core/raportari_ai.py (F152) citeste registrul ca baza de cunostinte a AI-ului
care raspunde clientilor. Filtreaza pe r[7].startswith("LIVE") si scoate r[0]/r[1]/r[4]. Un rand
malformat (ex. virgula neescapata intr-un camp -> campuri decalate) face ca r[7] sa nu mai fie
Starea reala -> functionalitatea devine INVIZIBILA pentru AI (dovada: F183, 22.07 - Acces UI
neescapat spargea randul, F183 nu aparea ca LIVE).

Citim cu csv.reader (NU split pe virgula) exact ca raportari_ai.py, ca sa validam ce vede EL.
Doua checkuri, ambele zero-mentenanta si zero fals-pozitive:
  1. fiecare rand are exact len(header) campuri  (checkul de aur - prinde clasa F183);
  2. ID (coloana 2) = F\\d+                        (prinde decalaje care totalizeaza fortuit N).
NU validam vocabularul de Stare (coloana 7): cupleaza la o lista extensibila -> o stare noua
legitima ar da rosu fals; nu normalizam un rosu fragil (lectia 22.07)."""
import csv
import pathlib
import re

_CALE = pathlib.Path(__file__).resolve().parent.parent / "FUNCTIONALITATI.csv"


def _randuri():
    """Toate randurile, citite exact ca raportari_ai.py (csv.reader, utf-8-sig)."""
    with open(_CALE, encoding="utf-8-sig") as f:
        return list(csv.reader(f))


def test_fiecare_rand_are_numarul_corect_de_campuri():
    randuri = _randuri()
    n = len(randuri[0])  # header = numarul canonic de coloane
    rele = [(i + 1, len(r)) for i, r in enumerate(randuri) if len(r) != n]
    assert not rele, (
        "FUNCTIONALITATI.csv: randuri cu numar gresit de campuri (asteptat %d, dupa header):\n"
        % n
        + "\n".join("  linia %d: %d campuri" % (linia, nr) for linia, nr in rele)
        + "\n-> registrul e baza de cunostinte F152 (raportari_ai.py): un rand decalat face "
          "functionalitatea INVIZIBILA pentru AI (Starea nu mai e pe coloana 7). Cauza tipica: "
          "virgula neescapata intr-un camp descriptiv -> pune campul intre ghilimele."
    )


def test_fiecare_id_este_valid():
    randuri = _randuri()
    idx_id = randuri[0].index("ID")
    rele = [(i + 1, r[idx_id]) for i, r in enumerate(randuri[1:], start=1)
            if not re.fullmatch(r"F\d+", (r[idx_id] or "").strip())]
    assert not rele, (
        "FUNCTIONALITATI.csv: ID-uri ne-conforme pe coloana %d (asteptat F<numar>):\n" % idx_id
        + "\n".join("  linia %d: ID=%r" % (linia, val) for linia, val in rele)
        + "\n-> un ID care nu e F\\d+ semnaleaza un rand decalat care totalizeaza fortuit "
          "numarul corect de campuri (checkul de numar-campuri nu l-ar prinde)."
    )


def test_sursa_cod_refera_fisiere_care_exista():
    """Anti-drift SEMANTIC (nu doar structural): fiecare fisier citat in coloana `Sursa cod`
    pentru o functionalitate LIVE sau PARTIAL trebuie sa existe pe disc, la calea EXACTA scrisa.

    DE CE: registrul e harta de cod pe care se sprijina AI-ul (F152, raportari_ai.py) si pagina
    Functionalitati. O intrare LIVE care trimite catre un modul/ecran disparut (mutat, redenumit,
    eliminat) = registru care MINTE - descrie cod inexistent. Checkul de structura (numar campuri/ID)
    NU prinde asta: campurile pot fi perfect aliniate si totusi calea sa fie moarta.

    NON-LIVE excluse: ELIMINAT/RESPINS/AMANAT/PLANIFICAT au codul LEGITIM absent - coloana lor
    Sursa cod documenteaza unde A STAT codul (ex. F186 admin_gratuite.js, sters corect).

    PRINS REAL 10.08.2026 (Lot 0, baleiaj cap-coada al registrului): 4 intrari LIVE citau nume
    scurte fara cale (F117 admin_sanatate.js, F121 etransport_ecran.js, F152 raportari_api.py,
    F188 firme.js) - fisiere reale, dar in static/js/ecrane/ sau core/; F188 in plus cita
    `register_gratuit`, functie a contului gratuit ELIMINAT 26.07. Normalizate la cale completa."""
    randuri = _randuri()
    header = randuri[0]
    idx_src = header.index("Sursa cod")
    idx_st = header.index("Stare")
    idx_id = header.index("ID")
    path_re = re.compile(r"[\w][\w./-]*\.(?:py|js|sql|html|css)")
    baza = _CALE.parent
    rele = []
    for r in randuri[1:]:
        stare = (r[idx_st] or "").strip()
        if not (stare.startswith("LIVE") or stare.startswith("PARTIAL")):
            continue
        for tok in path_re.findall(r[idx_src] or ""):
            if not (baza / tok).exists():
                rele.append((r[idx_id], stare[:12], tok))
    assert not rele, (
        "FUNCTIONALITATI.csv: intrari LIVE/PARTIAL care citeaza fisiere inexistente la calea scrisa:\n"
        + "\n".join("  %s [%s] -> %s" % (i, s, t) for i, s, t in rele)
        + "\n-> registrul e harta de cod a AI-ului (F152); un fisier citat trebuie sa existe la calea"
          " EXACTA. Nume scurt (firme.js) => pune calea completa (static/js/ecrane/firme.js). Modul"
          " disparut => actualizeaza intrarea sau mut-o la ELIMINAT."
    )


def test_sursa_cod_nu_e_referinta_de_concurenta():
    """Anti-drift: o functionalitate LIVE/PARTIAL nu poate avea Sursa cod = referinta la CONCURENTA
    (SAGA/SmartBill/Oblio/WinMentor/FGO/Keez...).

    DE CE: registrul a fost populat partial din analiza de concurenta (CONCURENTA.csv); la CONSTRUIREA
    feature-ului, coloana Sursa cod TREBUIE actualizata la modulul real. O intrare LIVE care inca trimite
    la un concurent descrie de unde a venit IDEEA, nu unde e CODUL -> harta de cod falsa pentru AI (F152)
    si pentru dezvoltator (checkul de existenta a fisierului nu prinde asta: 'CONCURENTA: Oblio' n-are
    path-token, deci trece de test_sursa_cod_refera_fisiere_care_exista).

    NON-LIVE excluse (AMANAT/PLANIFICAT/RESPINS): acolo referinta la concurenta e LEGITIMA - feature
    neconstruit, doar analizat (ex. F127/F130/F149).

    PRINS REAL 11.08.2026 (Lot 3, generalizare pe clasa): 10 intrari LIVE (F126, F138-F142, F144-F147)
    inca citau 'CONCURENTA: ...' desi codul exista - normalizate la modulul real."""
    randuri = _randuri()
    header = randuri[0]
    idx_src = header.index("Sursa cod")
    idx_st = header.index("Stare")
    idx_id = header.index("ID")
    rele = []
    for r in randuri[1:]:
        stare = (r[idx_st] or "").strip()
        if not (stare.startswith("LIVE") or stare.startswith("PARTIAL")):
            continue
        if (r[idx_src] or "").strip().upper().startswith("CONCURENTA"):
            rele.append((r[idx_id], stare[:12], (r[idx_src] or "")[:45]))
    assert not rele, (
        "FUNCTIONALITATI.csv: intrari LIVE/PARTIAL cu Sursa cod = referinta la CONCURENTA (nu cod real):\n"
        + "\n".join("  %s [%s] -> %s" % (i, s, t) for i, s, t in rele)
        + "\n-> feature-ul e construit: pune modulul real (core/...py, static/js/...). Referinta la"
          " concurent e legitima DOAR pe non-LIVE (feature neconstruit, doar analizat)."
    )


def _live_si_indici():
    randuri = _randuri()
    h = randuri[0]
    iid, inume, ist, iaj = h.index("ID"), h.index("Functionalitate"), h.index("Stare"), h.index("ajutor")
    live = [r for r in randuri[1:] if len(r) > iaj and (r[ist] or "").strip() == "LIVE"]
    return live, iid, inume, iaj


def test_declaratii_live_au_ajutor():
    """Orice functionalitate LIVE de tip 'Declaratia D...' TREBUIE sa aiba explicatie contextuala (ajutor).
    Prinde mecanic o declaratie noua adaugata fara '?' (clasa care a regresat: D104..D311)."""
    live, iid, inume, iaj = _live_si_indici()
    fara = [(r[iid], r[inume]) for r in live
            if r[inume].strip().startswith(("Declaratia D", "Declarația D")) and not (r[iaj] or "").strip()]
    assert not fara, ("Declaratii LIVE fara ajutor contextual (completeaza coloana ajutor):\n"
                      + "\n".join("  %s | %s" % (a, b) for a, b in fara))


# Baseline al functionalitatilor LIVE inca fara ajutor (CLICHET: nu are voie sa CREASCA). Scop: 0.
# Scade pe masura ce se scriu explicatiile; o LIVE noua fara ajutor ridica numarul peste baseline
# -> rosu -> lipsa e prinsa mecanic, nu cu ochiul.
_BASELINE_LIVE_FARA_AJUTOR = 0


def test_acoperire_ajutor_nu_regreseaza():
    live, iid, inume, iaj = _live_si_indici()
    fara = [(r[iid], r[inume]) for r in live if not (r[iaj] or "").strip()]
    assert len(fara) <= _BASELINE_LIVE_FARA_AJUTOR, (
        "Nr. de LIVE fara ajutor a CRESCUT peste baseline (%d -> %d). Orice LIVE nou trebuie sa aiba "
        "explicatie contextuala:\n" % (_BASELINE_LIVE_FARA_AJUTOR, len(fara))
        + "\n".join("  %s | %s" % (a, b) for a, b in fara))


# ── Reconciliere REGISTRU declaratii: cod (DECLARATII) <-> CSV <-> CHEIE_DUK <-> generator ──
# DE CE (16.08.2026): registrul de declaratii era incoerent - randuri duplicate (un rand vechi RESPINS/AMANAT
# fara generator langa unul cu generator real) si nicio garda care sa lege codul de CSV. Sursa UNICA a "ce poate
# produce aplicatia" = dict-ul DECLARATII din declaratii_api. Aici se leaga bijectiv de randul canonic din CSV
# (nume "Declarația D###"), de CHEIE_DUK si de generatorul core/<tip>.py::genereaza(). Impiedica desincronizarea.
import re as _re


def _cod_declaratie(nume):
    m = _re.match(r"Declarația\s+(D\d{3}[A-Za-z]?)\b", nume)
    return m.group(1).lower() if m else None


def _tipuri_dispecer():
    from core.declaratii_api import DECLARATII
    return set(DECLARATII)


def _canonice():
    h = _randuri()[0]
    i_nume, i_id = h.index("Functionalitate"), h.index("ID")
    canon = {}
    for r in _randuri()[1:]:
        c = _cod_declaratie(r[i_nume])
        if c:
            canon.setdefault(c, []).append(r[i_id])
    return canon


def test_fiecare_declaratie_produsa_are_un_singur_rand_canonic():
    """Bijectie DECLARATII (dispecer) <-> randuri 'Declarația D###' din CSV. Prinde: declaratie produsa de cod
    fara rand (INCOMPLET) SI randuri duplicate pt aceeasi declaratie (INCOERENT - stale vechi langa canonic)."""
    canon = _canonice()
    tipuri = _tipuri_dispecer()
    lipsa = sorted(t for t in tipuri if not canon.get(t))
    dubluri = {t: canon[t] for t in tipuri if len(canon.get(t, [])) > 1}
    assert not lipsa, "declaratii in dispecer (DECLARATII) FARA rand 'Declarația D###' in CSV: %s" % lipsa
    assert not dubluri, "declaratii cu randuri canonice DUPLICATE in CSV (unifica): %s" % dubluri


def test_niciun_rand_declaratie_fantoma():
    """Reversul: fiecare rand 'Declarația D###' e ori produs de cod (in DECLARATII), ori marcat explicit
    neprodus (RESPINS/ELIMINAT). Prinde un rand ce pretinde o declaratie pe care aplicatia nu o produce."""
    h = _randuri()[0]
    i_nume, i_st, i_id = h.index("Functionalitate"), h.index("Stare"), h.index("ID")
    tipuri = _tipuri_dispecer()
    fantome = []
    for r in _randuri()[1:]:
        c = _cod_declaratie(r[i_nume])
        if c and c not in tipuri and not r[i_st].startswith(("RESPINS", "ELIMINAT")):
            fantome.append((r[i_id], c, r[i_st][:20]))
    assert not fantome, ("randuri 'Declarația D###' fara generator in DECLARATII si nemarcate RESPINS/ELIMINAT: %s"
                         % fantome)


def test_declaratie_produsa_nu_e_marcata_neprodusa():
    """Randul canonic al unei declaratii pe care codul O PRODUCE (in DECLARATII) nu poate fi RESPINS/ELIMINAT -
    ar fi o stare FALSA (pretinde ca nu se produce ceva ce se produce)."""
    h = _randuri()[0]
    i_nume, i_st, i_id = h.index("Functionalitate"), h.index("Stare"), h.index("ID")
    tipuri = _tipuri_dispecer()
    false_resp = []
    for r in _randuri()[1:]:
        c = _cod_declaratie(r[i_nume])
        if c in tipuri and r[i_st].startswith(("RESPINS", "ELIMINAT")):
            false_resp.append((r[i_id], c, r[i_st][:20]))
    assert not false_resp, "declaratii produse de cod dar marcate RESPINS/ELIMINAT (stare falsa): %s" % false_resp


def test_fiecare_declaratie_produsa_are_duk_si_generator():
    """Fiecare tip din DECLARATII are cheie CHEIE_DUK (poate fi validat) + modul core/<tip>.py cu genereaza()."""
    import importlib
    from core.duk import CHEIE_DUK
    tipuri = _tipuri_dispecer()
    fara_duk = sorted(tipuri - set(CHEIE_DUK))
    assert not fara_duk, "tipuri din dispecer fara CHEIE_DUK: %s" % fara_duk
    fara_gen = []
    for t in sorted(tipuri):
        try:
            mod = importlib.import_module("core.%s" % t)
            if not hasattr(mod, "genereaza"):
                fara_gen.append(t)
        except Exception as e:
            fara_gen.append("%s(import:%s)" % (t, e))
    assert not fara_gen, "tipuri din dispecer fara generator genereaza(): %s" % fara_gen
