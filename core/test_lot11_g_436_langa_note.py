# -*- coding: utf-8 -*-
"""Lotul 11, subagentul G — 436 (afișare), clasa „paragraful repetă ce arată butoanele” (comanda Costin 11.1, verbatim în DECIZII
„Comanda 11.1”: „în D100, începutul casetei roșii e ascuns sub antetul fix; paragraful repetă notele pe care le arată butoanele.”).

Lângă butoanele „Deschide nota …” (`static/js/ecrane/coada_trimite.js::legaturiNote`), care numesc fiecare notă, refuzul / avertismentul
cozii nu le mai enumeră: le NUMĂRĂ („1 notă nevalidată”). Textul cu lista rămâne (`mesaj`, `avertismente_poarta`) pentru locurile fără
butoane (ecranul de după intrarea în coadă, „De depus”, API-ul). Drumurile cozii care pun note lângă text, toate acoperite aici:
  1. poarta TVA cu notele care mișcă 4427 / 4426 (deficiența 284) — `uc_coada.mesaje_refuz_tva`;
  2. poarta TVA / D406 cu diferență și ciorne în perioadă (MESAJ_CIORNE_BLOCAJ) — `uc_coada.decizie_poarta`;
  3. ciornele fără diferență (MESAJ_CIORNE_POARTA, avertisment la intrare) — `uc_coada.avertisment_langa_note`;
  4. notele nevalidate ale declarației din evidență (436, D100 / D101 / bilanț) — `coada_api.blocaj_note_nevalidate` + așteptarea;
  și 1, 2, 4 primesc așteptarea (MESAJ_ASTEPTARE) pe ambele fraze (`uc_coada._cu_asteptare`).
N/A temei fiscal — schimbare de afișare."""
import ast
import io
import os
import re

from core import coada_api
from core import uc_coada as uq

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIORNE = [{"nota_id": 11, "data": "2026-09-09", "eticheta": "nota din 09.09.2026 — DP-G436, 100,00 lei"},
          {"nota_id": 12, "data": "2026-09-10", "eticheta": "nota din 10.09.2026 — DP-G437, 50,00 lei"}]


def _fara_etichete(text, note):
    return not any(n["eticheta"] in text or n["eticheta"].split(" — ")[1] in text for n in note)


def test_ciorne_cu_diferenta_fraza_langa_note_le_numara():
    """Drumul 2: o diferență față de balanță (refuzul D406, fără note proprii) și două ciorne în perioadă."""
    refuz = {"cod": "D406_DIFERA_DE_BALANTA", "mesaj": "Declarația nu intră în coadă: D406 nu se potrivește cu balanța."}
    blocaj, avert = uq.decizie_poarta(refuz, CIORNE)
    assert avert is None
    # textul cu lista rămâne neschimbat (locurile fără butoane)
    assert blocaj["mesaj"] == refuz["mesaj"] + uq.MESAJ_CIORNE_BLOCAJ % "nota din 09.09.2026 — DP-G436, 100,00 lei; nota din 10.09.2026 — DP-G437, 50,00 lei"
    langa = blocaj["mesaj_langa_note"]
    assert langa.startswith(refuz["mesaj"] + " Perioada are 2 note nevalidate — dacă ele corectează diferența"), langa
    assert _fara_etichete(langa, CIORNE), langa
    assert blocaj["note"] == CIORNE


def test_avertismentul_ciornelor_fara_diferenta_le_numara_langa_butoane():
    """Drumul 3: ciornele fără diferență — avertismentul la intrare (R36) are și varianta de lângă butoane."""
    _b, avert = uq.decizie_poarta(None, CIORNE)
    # textul întreg le numește (ecranul de după intrare n-are butoane) — egalitatea pe valoarea întreagă (core/test_garzi_pe_text.py)
    assert avert == ("Comparația cu balanța s-a făcut pe notele validate. Notele nevalidate ale perioadei: %s; %s. Declarația intră în "
                     "coadă; validează-le înainte de depunere." % (CIORNE[0]["eticheta"], CIORNE[1]["eticheta"])), avert
    langa = uq.avertisment_langa_note(CIORNE)
    assert langa == ("Comparația cu balanța s-a făcut pe notele validate. Perioada are 2 note nevalidate. Declarația intră în coadă; "
                     "validează-le înainte de depunere."), langa
    assert uq.avertisment_langa_note([]) is None and uq.avertisment_langa_note(CIORNE[:1]).count("1 notă nevalidată") == 1


def test_refuzul_tva_cu_notele_care_misca_contul_le_numara_pe_cont():
    """Drumul 1 (284): pe 4427 notele explică diferența, pe 4426 nu o acoperă toată — fraza de lângă butoane spune asta pe cont, cu
    numărul notelor, fără numărul din Registrul-jurnal, documentul și suma lor (le arată butoanele)."""
    n1 = {"nota_id": 21, "nr_curent": 21, "document": "Factură F1A4 din 16.09.2026", "suma": "42.00"}
    n2 = {"nota_id": 22, "eticheta_nota": "din 17.09.2026", "document": "NIR 7", "suma": "10.00"}
    n3 = {"nota_id": 23, "eticheta_nota": "din 18.09.2026", "document": "NIR 8", "suma": "5.00"}
    dif = [{"cont": "4427", "rand": "R17_2", "eticheta": "TVA colectată", "declarat": "42.00", "contabil": "0.00", "diferenta": "42.00",
            "note": [n1], "note_explica": True},
           {"cont": "4426", "rand": "R27_2", "eticheta": "TVA deductibilă", "declarat": "0.00", "contabil": "30.00", "diferenta": "-30.00",
            "note": [n2, n3], "note_explica": False}]
    mesaj, langa = uq.mesaje_refuz_tva(dif)
    assert mesaj == (   # 284, neschimbat — mesajul întreg
        "Declarația nu intră în coadă: TVA-ul ei nu se potrivește cu balanța lunii — TVA colectată (rândul R17_2): declarat 42,00, contul "
        "4427 are 0,00, diferență 42,00 lei; TVA deductibilă (rândul R27_2): declarat 0,00, contul 4426 are 30,00, diferență -30,00 lei. "
        "Toleranța e rotunjirea la leu. Diferența o explică pe contul 4427: nr. crt. 21 — Factură F1A4 din 16.09.2026, 42,00 lei. Note "
        "nevalidate (nu acoperă toată diferența) pe contul 4426: nota din 17.09.2026 — NIR 7, 10,00 lei; nota din 18.09.2026 — NIR 8, "
        "5,00 lei. Validatorul ANAF verifică structura, nu cifrele: corectează documentele (o factură necontată, o notă nevalidată, o "
        "achiziție fără factură) și generează din nou."), mesaj
    assert " Diferența pe contul 4427 o explică 1 notă nevalidată." in langa, langa
    assert " Pe contul 4426, 2 note nevalidate nu acoperă toată diferența." in langa, langa
    assert "nr. crt. 21" not in langa and "Factură F1A4" not in langa and "NIR 7" not in langa, langa
    # diferențele pe conturi și îndemnul de corectare rămân în ambele (nu sunt pe butoane)
    for bucata in ("contul 4427 are 0,00, diferență 42,00 lei", "Toleranța e rotunjirea la leu.", "Validatorul ANAF verifică structura"):
        assert bucata in mesaj and bucata in langa, bucata
    # fără note numite: cele două fraze sunt aceeași
    fara = [dict(d, note=[]) for d in dif]
    assert uq.mesaje_refuz_tva(fara)[0] == uq.mesaje_refuz_tva(fara)[1]


def test_notele_nevalidate_ale_declaratiei_din_evidenta_asteptarea_pe_ambele_fraze():
    """Drumul 4 (436): refuzul notelor nevalidate (D100 / D101 / bilanț) primește așteptarea și în fraza de lângă butoane."""
    bl = uq._cu_asteptare(coada_api.blocaj_note_nevalidate("s1005", CIORNE))
    asteptare = uq.MESAJ_ASTEPTARE % "notelor"
    assert bl["mesaj"].endswith(asteptare) and bl["mesaj_langa_note"].endswith(asteptare), bl
    assert bl["mesaj_langa_note"].startswith("Declarația nu se depune până la validarea notelor: cifra ei nu cuprinde 2 note nevalidate "
                                             "din perioada ei. Validează-le"), bl["mesaj_langa_note"]
    assert _fara_etichete(bl["mesaj_langa_note"], CIORNE) and not _fara_etichete(bl["mesaj"], CIORNE)
    unu = uq._cu_asteptare(coada_api.blocaj_note_nevalidate("d100", CIORNE[:1]))
    assert unu["mesaj_langa_note"].endswith(uq.MESAJ_ASTEPTARE % "notei"), unu


# ── GARDA: clasa nu poate reapărea în cozi ───────────────────────────────────────────────────────────────────────────────────────────
def _apeluri_dict(cale):
    arbore = ast.parse(io.open(os.path.join(RAD, cale), encoding="utf-8").read())
    for nod in ast.walk(arbore):
        if isinstance(nod, ast.Call) and isinstance(nod.func, ast.Name) and nod.func.id == "dict":
            yield nod, {k.arg: k.value for k in nod.keywords if k.arg}
        elif isinstance(nod, ast.Dict):
            yield nod, {k.value: v for k, v in zip(nod.keys, nod.values) if isinstance(k, ast.Constant)}


def test_garda_orice_refuz_cu_note_din_uc_coada_are_fraza_de_langa_butoane():
    """GARDĂ. În `uc_coada.py`, orice refuz (dicționar cu `mesaj`) care pune `note` (le arată butoanele) sau își lungește `mesaj` cu MESAJ_ASTEPTARE /
    MESAJ_CIORNE_BLOCAJ poartă și `mesaj_langa_note`. MUTAȚIE: `mesaj_langa_note=` scos din `decizie_poarta` / `_cu_asteptare` /
    `poarta_tva_balanta` -> pică, cu linia."""
    lipsa, vazute = [], 0
    for nod, chei in _apeluri_dict("core/uc_coada.py"):
        mesaj = chei.get("mesaj")
        lungit = mesaj is not None and any(isinstance(x, ast.Name) and x.id in ("MESAJ_ASTEPTARE", "MESAJ_CIORNE_BLOCAJ")
                                           for x in ast.walk(mesaj))
        lungit = lungit or (mesaj is not None and any(isinstance(x, ast.Name) and x.id == "a" for x in ast.walk(mesaj))
                            and isinstance(mesaj, ast.BinOp))   # `_cu_asteptare`: `a` = MESAJ_ASTEPTARE % …
        if chei.keys() >= {"note", "mesaj"} or lungit:   # un REFUZ (are `mesaj`) cu note; datele simple (`surse_declaratiei`) nu
            vazute += 1
            if "mesaj_langa_note" not in chei:
                lipsa.append(nod.lineno)
    assert vazute >= 3, vazute   # calibrare: decizie_poarta, _cu_asteptare, poarta_tva_balanta
    assert not lipsa, "refuz cu note fără `mesaj_langa_note` în core/uc_coada.py, liniile %s" % lipsa


def test_garda_coada_adauga_pune_asteptarea_numai_prin_cu_asteptare():
    """GARDĂ. Așteptarea (MESAJ_ASTEPTARE) se adaugă numai în `_cu_asteptare` — singurul loc care o pune pe ambele fraze. MUTAȚIE:
    forma veche `mesaj=_bl_note["mesaj"] + MESAJ_ASTEPTARE % …` scrisă înapoi în `coada_adauga` -> pică."""
    sursa = io.open(os.path.join(RAD, "core/uc_coada.py"), encoding="utf-8").read()
    folosiri = [m.start() for m in re.finditer(r"MESAJ_ASTEPTARE\s*%", sursa)]
    definitie = sursa.index("def _cu_asteptare(")
    sfarsit = sursa.index("\ndef ", definitie + 1)
    assert folosiri and all(definitie < p < sfarsit for p in folosiri), "MESAJ_ASTEPTARE % în afara lui _cu_asteptare"
    assert sursa.count("_cu_asteptare(_bl_note)") == 1 and sursa.count("_cu_asteptare(_blocaj)") == 1


def test_garda_ecranul_cozii_arata_fraza_de_langa_butoane():
    """GARDĂ. `coada_trimite.js`: refuzul cu note arată `mesaj_langa_note`, avertismentul cu notele perioadei
    `avertismente_poarta_langa_note`, amândouă prin `mesajLangaNote` (textul întreg numai fără butoane). MUTAȚIE: textul refuzului
    readus la `e.mesaj || det.mesaj` -> pică."""
    from core.arbore_js import apeluri, arbore_js, functia, noduri
    # apelurile și ramura ca noduri acorn, nu șiruri în sursă (core/test_garzi_pe_text.py)
    arb, cod = arbore_js("coada_trimite.js")
    ap = apeluri(arb, cod, "mesajLangaNote")
    assert any(a[:2] == ("cuNote", "det.mesaj_langa_note") for a in ap), ap
    assert ("cuNote", "r.avertismente_poarta_langa_note", "r.avertismente_poarta") in ap, ap
    assert [cod(r) for r in noduri(functia(arb, "mesajLangaNote"), "ReturnStatement")][-1:] == ["return cuNote && areLanga ? langa : intreg;"]
    # fiecare apel `legaturiNote(...)` (afară de definiție) stă într-o funcție care, ÎNAINTEA lui, alege textul cu `mesajLangaNote(...)`
    # — ca noduri acorn (funcția care îl cuprinde, apelurile ei), nu ca fereastră de 400 de caractere în sursă
    functii = [f for t in ("FunctionDeclaration", "FunctionExpression", "ArrowFunctionExpression") for f in noduri(arb, t)]
    chemari = [c for c in noduri(arb, "CallExpression") if cod(c["callee"]) == "legaturiNote"]
    assert chemari, "ANTI-VACUU: niciun apel legaturiNote în coada_trimite.js"
    fara_text = []
    for c in chemari:
        f = min((f for f in functii if f["start"] <= c["start"] and c["end"] <= f["end"]), key=lambda f: f["end"] - f["start"])
        alese = [m for m in noduri(f, "CallExpression") if cod(m["callee"]) == "mesajLangaNote" and m["start"] < c["start"]]
        fara_text += [] if alese else [cod(c)[:120]]
    assert fara_text == [], fara_text
