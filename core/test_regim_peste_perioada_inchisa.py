# -*- coding: utf-8 -*-
"""GARD [R46, 26.08.2026]: un câmp care decide CE SE DATOREAZĂ nu se schimbă peste o perioadă închisă.

De unde vine. R46 era deschisă din 25.08 și n-avea decât o constatare. S-a reaprins **mecanic**:
condiția ei numea `core/firma_profil_api.py`, iar `core/test_reaprindere.py` a oprit un commit care
atingea fișierul pentru **altceva**. Prima reaprindere reală de când mecanismul există.

Decizia lui Costin: **refuz**, nu trecere consemnată. *„O schimbare de date fiscale ale firmei
într-o perioadă închisă nu e o corecție, e o rescriere a trecutului."* Trecerea consemnată e
potrivită unde actul e legitim și rar — redeschiderea unei perioade (R58); acolo omul ia o decizie
**despre perioadă**. Aici ar lua o decizie **despre trecut** fără să redeschidă nimic.

Și o limitare cerută tot de el, care e jumătate din valoare: refuzul se aplică **doar** câmpurilor
care decid ce se datorează. *„Altfel un contabil nu mai poate corecta un număr de telefon pe o
firmă cu ianuarie închis."*

CE FACE IMPOSIBIL: una din cele trei căi care schimbă vectorul, regimul sau CUI-ul fără să întrebe
dacă există perioade închise · lărgirea tăcută a mulțimii `CAMPURI_CARE_DECID` peste ce e în
`CAMPURI_FISCALE` · un refuz care nu spune pe ce cale se face totuși schimbarea.

CE NU FACE, declarat: nu verifică a doua jumătate a condiției lui R46 — *„declarații depuse pe
regimul vechi în intervalul atins"*. Poarta de azi e pe **perioada închisă**, care e proxy-ul
mecanic; declarațiile depuse fără perioadă închisă rămân neacoperite, iar asta se spune.
"""
import ast
import io
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# cele trei căi care ating câmpuri ce decid ce se datorează
_CAI = {
    "core/vector_fiscal_api.py": "salveaza",          # vectorul
    "main.py": "firma_profil_regim_tva",              # regimul de TVA
    "core/firma_profil_api.py": "salveaza_date",      # CUI-ul, prin CAMPURI_CARE_DECID
}


def _arbore(cale):
    return ast.parse(io.open(os.path.join(_RAD, cale), encoding="utf-8").read())


def _functii(arb):
    return {n.name: n for n in ast.walk(arb)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _cheama(fn, nume):
    return any(isinstance(n, ast.Call)
               and (getattr(n.func, "attr", None) == nume or getattr(n.func, "id", None) == nume)
               for n in ast.walk(fn))


def test_ANTI_VACUU_cele_trei_cai_se_gasesc():
    lipsa = [(c, f) for c, f in _CAI.items() if f not in _functii(_arbore(c))]
    assert not lipsa, "căi negăsite: %s — gardul s-ar uita în gol" % lipsa


def test_fiecare_cale_intreaba_daca_exista_perioade_inchise():
    rele = [c for c, f in _CAI.items()
            if not _cheama(_functii(_arbore(c))[f], "cere_perioade_deschise")]
    assert not rele, (
        "căi care schimbă ce se datorează fără să întrebe de perioade închise: %s — "
        "o schimbare peste o lună depusă rescrie trecutul" % rele)


def test_multimea_care_DECIDE_e_o_submultime_declarata():
    """Lărgirea ei blochează munca de zi cu zi; îngustarea o deschide tăcut. Ambele se văd aici."""
    arb = _arbore("core/firma_profil_api.py")
    val = {}
    for n in ast.walk(arb):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id in ("CAMPURI_FISCALE", "CAMPURI_CARE_DECID"):
                    val[t.id] = set(ast.literal_eval(n.value))
    assert set(val) >= {"CAMPURI_CARE_DECID"}, "`CAMPURI_CARE_DECID` a dispărut"
    assert val["CAMPURI_CARE_DECID"], "mulțimea e goală — poarta de pe `salveaza_date` nu mai apără nimic"
    assert val["CAMPURI_CARE_DECID"] <= val["CAMPURI_FISCALE"], (
        "câmpuri care «decid» dar nu se pot salva de acolo: %s"
        % sorted(val["CAMPURI_CARE_DECID"] - val["CAMPURI_FISCALE"]))
    assert val["CAMPURI_CARE_DECID"] >= {"cui"}, (
        "`cui` a ieșit din mulțime — CUI-ul leagă tot ce s-a depus")


def test_refuzul_SPUNE_pe_ce_cale_se_face_totusi():
    """Structural, ca la R66: mesajul e COMPUS din `UNDE_PERIOADE`. Un refuz care doar oprește
    mută munca fără s-o îndrume — iar aici calea există și e mai bună decât schimbarea tăcută."""
    arb = _arbore("core/mesaje.py")
    compus = set()
    for n in ast.walk(arb):
        if isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "MESAJ_PESTE_PERIOADA_INCHISA"
                for t in n.targets):
            compus = {x.id for x in ast.walk(n.value) if isinstance(x, ast.Name)}
    assert compus >= {"UNDE_PERIOADE"}, (
        "refuzul nu mai spune unde se redeschide perioada (referă: %s)" % sorted(compus))


_FARA_POARTA = chr(10).join([
    "def salveaza(conn_schema, regim_fiscal):",
    "    if exista:",
    "        cur.execute('UPDATE tabela_de_proba SET regim_fiscal = %s', (regim_fiscal,))",
    "    return {'ok': True}",
])


def test_CALIBRARE_o_cale_fara_poarta_e_prinsa():
    """Calibrare negativă: scrierea există, poarta nu. Un gard care ar verifica doar că funcția
    există — sau că fișierul pomenește perioade — ar trece verde pe asta."""
    fn = _functii(ast.parse(_FARA_POARTA))["salveaza"]
    assert not _cheama(fn, "cere_perioade_deschise"), (
        "calibrarea nu mai deosebește o cale gardată de una negardată")
