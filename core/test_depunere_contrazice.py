# -*- coding: utf-8 -*-
"""GARD R6 (21.08.2026): o depunere care contrazice un „nu se datorează" nu mai e invizibilă.

DE CE. `_clasifica` iterează pe `datorate` și consultă `depuse` ca DICȚIONAR. O depunere care n-are
obligație pereche nu e VIZITATĂ niciodată — deci „nu se datorează" și „s-a depus" nu se ciocneau
nicăieri. Contradicția era invizibilă **prin construcție**, nu prin omisiune, iar asta e diferența
dintre un bug și o formă care nu poate produce semnalul.

MĂSURAT ÎNAINTE (sondă de citire pe 17 firme, cu probă de nescriere): din 54 de depuneri, 7
contraziceau un „nu se datorează" și 1 cădea pe un „nu pot verifica" — zero semnale produse.

CE NU FACE. O depunere NU stinge un `neclar`. Că s-a depus dovedește că firma a CONSIDERAT că
datorează, nu că a considerat corect, și nu spune nimic despre perioadele în care N-A depus — care e
chiar întrebarea din „nu pot verifica". Dacă ar stinge-o, firma care a depus tot ar părea complet
verificată, deși ea e tocmai cea despre care nu știi dacă a depus tot ce trebuia. Deci: se ARATĂ ca
opinie, NU se numără ca obligație stinsă.
"""
import datetime

from core.control_fiscal_api import depuneri_fara_obligatie

Z = datetime.date(2026, 7, 20)


def _neap(tip, motiv, an=None, luna=None):
    d = {"tip": tip, "motiv": motiv}
    if an:
        d.update({"an": an, "luna": luna})
    return d


def test_depunere_pe_perioada_neaplicabila_e_contrazicere():
    """Cazul care a pornit R6: ALFA MICRO are D100/T4-2025 depus, iar semaforul spune că nu se
    datorează pe T4 2025. Cele două nu pot fi amândouă adevărate."""
    r = depuneri_fara_obligatie(
        datorate=[],
        neaplicabile=[_neap("d100", "D100 nu se datorează pe T4 2025 — fără venituri în trimestru", 2025, 12)],
        neclar=[],
        depuse={("d100", 2025, 12): Z})
    assert len(r) == 1 and r[0]["fel"] == "contrazice", r
    assert "T4 2025" in r[0]["mesaj"] and "DEPUSĂ" in r[0]["mesaj"]
    assert "nu pot fi amândouă adevărate" in r[0]["mesaj"]


def test_motivul_citat_e_al_perioadei_depunerii():
    """Defect prins în construcție: prima versiune ținea motivele într-un dicționar pe TIP și a
    produs «D100 pe 3/2026 … nu se datorează: „nu se datorează pe T4 2025"» — un mesaj care citează
    altă perioadă. Un mesaj care afirmă un fals despre propria constatare e exact clasa vânată."""
    neap = [_neap("d100", "D100 nu se datorează pe T4 2025 — fără venituri", 2025, 12),
            _neap("d100", "D100 nu se datorează pe T1 2026 — fără venituri", 2026, 3)]
    r = depuneri_fara_obligatie([], neap, [], {("d100", 2026, 3): Z})
    assert len(r) == 1
    assert "T1 2026" in r[0]["mesaj"], r[0]["mesaj"]
    assert "T4 2025" not in r[0]["mesaj"], "citează motivul altei perioade: " + r[0]["mesaj"]


def test_depunere_pe_neclar_e_opinie_nu_stingere():
    """Constructii Profit Trim: D300/06-2026 depus, d300 în „nu pot verifica". Se arată, nu se
    stinge — și mesajul spune EXPLICIT ce nu dovedește."""
    r = depuneri_fara_obligatie(
        datorate=[], neaplicabile=[],
        neclar=[{"tip": "d300", "motiv": "nu pot demonstra de când e firma înregistrată în scopuri de TVA"}],
        depuse={("d300", 2026, 6): Z})
    assert len(r) == 1 and r[0]["fel"] == "opinie", r
    assert "nu spune nimic despre perioadele în care nu s-a depus" in r[0]["mesaj"]
    assert "stins" not in r[0]["mesaj"].lower(), "opinia nu are voie să sune a stingere"


def test_depunerea_cu_obligatie_pereche_nu_produce_semnal():
    """Anti-fals-pozitiv: ce are obligație pereche e treaba lui `_clasifica`, nu a trecerii inverse.
    Altfel fiecare declarație depusă normal ar produce zgomot."""
    dat = [{"tip": "d300", "an": 2026, "luna": 6, "termen": "2026-07-25"}]
    assert depuneri_fara_obligatie(dat, [], [], {("d300", 2026, 6): Z}) == []


def test_depunere_in_afara_ferestrei_nu_e_contradictie():
    """Fereastra `datorate` e o alegere de AFIȘARE, nu o afirmație despre obligație. O depunere
    veche nu contrazice nimic — a o semnala ar transforma un contor în acuzație."""
    assert depuneri_fara_obligatie([], [], [], {("d112", 2024, 3): Z}) == []


def test_neaplicabil_fara_perioada_acopera_orice_perioada():
    """`D301 nu se datorează — firma e plătitoare de TVA` n-are an/lună: e un statut, deci
    contrazice o depunere pe ORICE perioadă."""
    r = depuneri_fara_obligatie(
        [], [_neap("d301", "D301 nu se datorează — firma e plătitoare de TVA")], [],
        {("d301", 2026, 4): Z})
    assert len(r) == 1 and r[0]["fel"] == "contrazice"


# ─────────── ANTI-VACUU ───────────

def test_toate_cele_trei_ramuri_sunt_exercitate():
    """Un gard care nu găsește nimic TRECE. Aici cele trei ieșiri posibile (contrazice / opinie /
    tăcere) apar în același apel, ca niciuna să nu poată muri tăcut."""
    r = depuneri_fara_obligatie(
        datorate=[{"tip": "d112", "an": 2026, "luna": 6, "termen": "2026-07-25"}],
        neaplicabile=[_neap("d100", "fără venituri în trimestru", 2026, 6)],
        neclar=[{"tip": "d205", "motiv": "nu pot verifica"}],
        depuse={("d112", 2026, 6): Z, ("d100", 2026, 6): Z, ("d205", 2025, 12): Z,
                ("d394", 2020, 1): Z})
    fel = sorted(x["fel"] for x in r)
    assert fel == ["contrazice", "opinie"], fel


def test_semnalul_ajunge_in_raspunsul_semaforului():
    """Doc-cod: funcția pură poate fi corectă și totuși nefolosită. Cheia trebuie să existe în
    răspunsul lui `evalueaza_firma`, altfel calculul e cod mort."""
    import inspect

    from core import control_fiscal_api
    src = inspect.getsource(control_fiscal_api.evalueaza_firma)
    assert "depuneri_fara_obligatie(datorate" in src, "trecerea inversă nu se apelează în semafor"
    assert '"depuneri_fara_obligatie": depuneri_contra' in src, "rezultatul nu ajunge în răspuns"
