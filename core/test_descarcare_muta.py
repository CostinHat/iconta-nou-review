# -*- coding: utf-8 -*-
"""[R131, 04.09.2026] GARD: o descarcare care esueaza spune DE CE.

Cele 13 locuri care descarca un fisier binar nu pot trece prin `api.get`, deci cheama `fetch`
direct — si ocolesc `_refuzNevazut` din `api.js`. Masurat la 04.09.2026 cu
`core/scan_descarcare_muta.py`: **toate 13** aruncau motivul serverului si puneau in locul lui
propriul numar (`throw new Error("eroare " + r.status)`). Serverul spunea *„chitanta
inexistenta"*; omul citea *„eroare 404"*, iar la doua locuri *„Eroare — reincearca"* — un sfat
care nu poate reusi niciodata, fiindca factura tot nu exista la a doua apasare.

Reparatia e UNA (`cereBlob`/`descarca`/`deschide` in `api.js`), iar gardul asta o tine: clichetul
e **0** si nu are voie sa creasca. Un `fetch` nou care inghite motivul PICA aici.

Calibrarea e in AMBELE directii (METODA §22, interdictia 76): instrumentul e pus sa gaseasca o
forma muta injectata, sa NU acuze una buna, si sa nu clasifice gresit forma in lant din `app.js`.
"""
import pytest

from core import scan_descarcare_muta as S

#: Masurat la 04.09.2026, dupa reparatie. **Nu are voie sa creasca.**
CLICHET_MUTE = 0

#: Cate cereri directe trateaza corect refuzul, la aceeasi masuratoare. Aserteaza ca instrumentul
#: CHIAR VEDE codul: un scan cu domeniul gresit raporteaza „0 mute" despre o lume pe care n-o
#: vede. (Vezi „gardul care nu se verifica pe sine".)
MINIM_CU_MOTIV = 12


def test_niciun_fetch_nu_inghite_motivul_serverului():
    mute, cu_motiv, _fara = S.scaneaza()
    assert len(mute) <= CLICHET_MUTE, (
        "cereri directe care arunca motivul serverului: %d (clichet %d)\n%s"
        % (len(mute), CLICHET_MUTE, "\n".join("  %s:%d  %s" % x for x in mute)))


def test_instrumentul_chiar_vede_codul():
    """Anti-vacuu: daca radacina ar fi gresita, scanul ar raporta verde despre nimic."""
    _mute, cu_motiv, _fara = S.scaneaza()
    assert len(cu_motiv) >= MINIM_CU_MOTIV, (
        "scanul vede doar %d cereri directe tratate — sub cele %d masurate la 04.09.2026. "
        "Ori s-au sters, ori instrumentul nu mai gaseste fisierele." % (len(cu_motiv), MINIM_CU_MOTIV))


# ── calibrare NEGATIVA: forma muta, injectata, trebuie gasita ────────────────────────────
_MUT = """
async function ia() {
  const r = await fetch(`/tenants/${id}/facturi/${fid}/pdf`, { headers: { Authorization: t } });
  if (!r.ok) throw new Error("eroare " + r.status);
  const blob = await r.blob();
}
"""

_MUT_FARA_TEXT = """
async function ia() {
  const resp = await fetch(`/x/y`, { method: "POST" });
  if (!resp.ok) throw new Error();
  const blob = await resp.blob();
}
"""


@pytest.mark.parametrize("sursa", [_MUT, _MUT_FARA_TEXT])
def test_gaseste_forma_muta_injectata(sursa):
    mute, cu_motiv, fara = S.analizeaza_text(sursa, "<injectat>")
    assert len(mute) == 1, "forma muta n-a fost gasita: mute=%r cu_motiv=%r fara=%r" % (mute, cu_motiv, fara)


# ── calibrare POZITIVA: forma buna nu se acuza ───────────────────────────────────────────
_BUN = """
async function ia() {
  const r = await fetch(`/x/y`);
  if (!r.ok) { const d = await r.json(); throw { cod: r.status, mesaj: d.detail }; }
  return await r.blob();
}
"""

_BUN_IN_LANT = """
fetch("/public/magic-login", { method: "POST", body: JSON.stringify({ token: t }) })
  .then((r) => r.json().then((d) => ({ ok: r.ok, d })))
  .then(({ ok, d }) => { if (!ok) { banner(d.detail); return; } intra(d); });
"""


@pytest.mark.parametrize("sursa", [_BUN, _BUN_IN_LANT])
def test_nu_acuza_forma_buna(sursa):
    mute, cu_motiv, fara = S.analizeaza_text(sursa, "<injectat>")
    assert not mute, "instrumentul acuza o forma care CITESTE motivul: %r" % (mute,)
    assert len(cu_motiv) == 1, (
        "forma buna trebuie clasata `cu_motiv`, nu `fara ramura`: cu_motiv=%r fara=%r"
        % (cu_motiv, fara))


# ── calibrare pe PROPRIUL mod de esec: blocul nu are voie sa inghita apelul urmator ──────
_DOUA_LIPITE = """
async function ia() {
  const a = await fetch("/unu");
  if (!a.ok) { const d = await a.json(); throw d; }
  const b = await fetch("/doi");
  if (!b.ok) throw new Error("eroare " + b.status);
  return b;
}
"""


def test_blocul_nu_inghite_apelul_urmator():
    """Daca blocul primului `fetch` s-ar intinde peste al doilea, `.json()` de la primul ar
    „acoperi" tacerea celui de-al doilea — iar gardul ar raporta verde despre un defect real.
    E chiar modul in care instrumentul asta poate gresi."""
    mute, cu_motiv, _fara = S.analizeaza_text(_DOUA_LIPITE, "<injectat>")
    assert len(cu_motiv) == 1 and len(mute) == 1, (
        "cele doua cereri trebuie clasate separat: cu_motiv=%r mute=%r" % (cu_motiv, mute))
    assert mute[0][2].startswith("const b"), "s-a acuzat cererea gresita: %r" % (mute,)


def test_exceptiile_sunt_numite_si_motivate():
    """Doua fisiere ies din masuratoare. Fiecare are motivul scris LANGA lista, nu in alt loc.
    *O exceptie fara motiv se invecheste tacut: peste un an nimeni nu mai stie daca mai e
    valabila, iar instrumentul tace verde despre doua fisiere pe care nu le mai vede nimeni.*"""
    import inspect
    assert S._EXCEPTATE == {"api.js", "versiune.js"}
    sursa = inspect.getsource(S)
    # cele 8 linii dinaintea listei — acolo, si numai acolo, se scrie de ce iese un fisier.
    cap = sursa[:sursa.index("_EXCEPTATE = {")].split("\n")[-9:]
    motive = [l for l in cap if l.startswith("#:")]
    text = "\n".join(motive)
    for nume in S._EXCEPTATE:
        assert nume in text, (
            "`%s` e exceptat fara motiv scris in comentariul de deasupra listei." % nume)
    assert len(motive) >= len(S._EXCEPTATE), "cel putin un rand de motiv per exceptie"
