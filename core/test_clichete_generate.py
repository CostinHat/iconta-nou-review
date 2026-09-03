# -*- coding: utf-8 -*-
"""GARD [31.08.2026]: tabelul clichetelor vii din predare se RECALCULEAZĂ, nu se citează.

DE UNDE VINE, cu măsurătoarea ei. `PREDARE_LANT.md` purta un tabel de patru clichete, fiecare cu
numele instrumentului lui pe rând, sub propoziția *«se recalculează, nu se citesc de aici»*. Pe
31.08 s-au recalculat toate patru:

    77  datorie        61  — scris 61    ✔ PLAFONAT (`core/test_refuzuri.py`, contra BASELINE)
    50  apare_oricum 1222  — scris 1222  ✔ PLAFONAT (clichetul 50)
    R80 rute GRI        7  — scris 7     ✔ PLAFONAT
    77u UMBRA         781  — scris 779   ✘ NEPLAFONATĂ, deliberat

**Cele trei plafonate erau corecte. A patra, singura fără clichet, circula în aceeași zi în TREI
valori** — `778` în mesajul commitului `2200432` care a născut instrumentul, `779` în predare și în
`GARZI.md`, `781` în cod. Reconstituit mecanic, pe worktree-uri detașate: 778 la `2200432`, 779 la
`edaada7^`, 781 de la `edaada7` încoace (reparația căii jurnalului a adăugat două refuzuri într-un
modul care nu citează legea). Niciun om și niciun gard n-au văzut mișcarea.

*Propoziția care spune că o cifră se recalculează nu o recalculează. Ce ține o cifră adevărată e un
gard; ce a ținut cele trei cifre corecte au fost cele trei clichete.*

CE FACE IMPOSIBIL:
  1. o cifră de clichet, scrisă în predare, care nu se mai potrivește cu codul;
  2. un rând editat cu mâna — comparația e pe STRUCTURA tabelului, nu pe text (METODA §23);
  3. un clichet **măsurat și nescris** — dacă instrumentul îl produce, tabelul îl poartă;
  4. o cifră a UMBREI scrisă în proza predării, în afara blocului generat (v. ultimele teste).

O SINGURĂ SCUTIRE, structurală: **tabelul cifrelor invalidate**. E, prin construcție, locul unde
valorile vechi trebuie să stea — apartenența la el *este* declarația că nu mai sunt curente, deci
scutirea nu redeschide gaura. Are anti-vacuu propriu (secțiunea trebuie să existe, să fie una, și
tăierea să nu înghită documentul) și calibrare pe direcția care contează: o cifră pusă în proza
obișnuită e tot prinsă.

CE NU FACE, declarat:
  - **nu plafonează umbra.** Decizia lui Costin, 31.08: *«cele din umbră rămân nemăsurate,
    definitiv»* — populația nu se auditează, niciodată. Gardul nu-i pune plafon; îi interzice doar
    să fie **scrisă din memorie**. Un plafon pe ea ar transforma o cifră deliberat nedeplafonată
    într-un clichet de facto, cu costul unuia și fără protecția lui — exact defectul reparat în
    `core/test_refuzuri.py::test_norma_77_isi_scrie_LIMITA_pe_umbra`.
  - **nu acoperă naratiunea DATATĂ** din `GARZI.md`, `ISTORIC.md`, `CONFORMITATE.md`, `METODA_*`.
    Acolo o cifră e o afirmație despre CÂND s-a măsurat, și are voie să îmbătrânească — de-aia are
    dată. `PREDARE_LANT.md` e altceva: e fișier de STARE CURENTĂ, se suprascrie, deci orice cifră
    din el pretinde că e de acum.
  - **nu verifică dacă instrumentele numără BINE.** Fiecare are calibrarea lui. Aici se apără doar
    egalitatea document ↔ instrument.
"""
import io
import os
import re
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from scripts import scan_ramas as sr  # noqa: E402

_DOC = os.path.join(_RAD, "PREDARE_LANT.md")

#: Codurile pe care instrumentul TREBUIE să le producă. Scrise ca date, ca să se vadă că un clichet
#: care dispare din instrument nu trece drept «nu mai e nimic de raportat» — un zero greșit se
#: citește ca terminat (lecția `INSTRUMENT: 0` din `scan_ramas`, 31.08).
CODURI_ASTEPTATE = {"77", "77u", "50", "R80"}


def _document():
    return io.open(_DOC, encoding="utf-8").read()


def _bloc_din_document(doc=None):
    """Blocul generat, extras din predare. Întoarce `None` dacă marcajele lipsesc."""
    d = _document() if doc is None else doc
    a = d.find(sr.MARCA_CLICHETE_START)
    b = d.find(sr.MARCA_CLICHETE_STOP)
    if a < 0 or b < 0:
        return None
    return d[a:b + len(sr.MARCA_CLICHETE_STOP)]


def _randuri_tabel(bloc):
    """Tabelul markdown, parsat în STRUCTURĂ: [{cod, acum, ce, instrument}].

    Se compară pe obiecte cu câmpuri, nu pe șiruri (METODA §23 / clichetul 50). Diferența nu e de
    stil: o comparație pe text spune «documentul s-a schimbat», una pe structură spune CARE cifră
    s-a mutat și de la ce la ce — iar cine citește eșecul nu mai trebuie să caute singur.
    """
    out = []
    for linie in bloc.split("\n"):
        celule = [c.strip() for c in linie.strip().strip("|").split("|")]
        if len(celule) != 4:
            continue
        cod = celule[0].strip("*").strip()
        if not cod or cod.startswith("---") or cod == "cod":
            continue
        out.append({"cod": cod,
                    "acum": celule[1].strip("*").strip(),
                    "ce": celule[2].strip(),
                    "instrument": celule[3].strip("`").strip()})
    return out


def _din_instrument():
    return [{"cod": x["cod"], "acum": x["dimensiune"], "ce": x["ce"], "instrument": x["sursa"]}
            for x in sr.clichete()]


# ── doc ↔ cod ─────────────────────────────────────────────────────────────────────────────────

def test_blocul_de_clichete_EXISTA_in_predare():
    """Fără marcaje, toate testele de mai jos ar trece vacuu pe o listă goală — forma de orbire
    prin construcție cea mai ieftină de produs: ștergi blocul, gardul tace."""
    assert _bloc_din_document() is not None, (
        "PREDARE_LANT.md n-are blocul CLICHETE-VII. A fost șters? Fără el, cifrele clichetelor se "
        "scriu iar din memorie — și exact așa a ajuns umbra să circule în trei valori într-o zi. "
        "Regenerare: ./venv/bin/python scripts/scan_ramas.py --clichete-md")


def test_fiecare_CIFRA_din_bloc_e_cea_de_ACUM():
    """Comparația care contează, pe structură: cod cu cod, cifră cu cifră."""
    scris = {r["cod"]: r for r in _randuri_tabel(_bloc_din_document())}
    acum = {r["cod"]: r for r in _din_instrument()}
    gresite = [(c, scris[c]["acum"], acum[c]["acum"])
               for c in sorted(set(scris) & set(acum))
               if scris[c]["acum"] != acum[c]["acum"]]
    assert not gresite, (
        "cifre de clichet învechite în PREDARE_LANT.md (cod, scris, acum): %s%s"
        "Nu le corecta cu mâna — regenerează: "
        "./venv/bin/python scripts/scan_ramas.py --clichete-md" % (gresite, chr(10)))


def test_niciun_clichet_MASURAT_nu_lipseste_din_tabel_si_niciunul_INVENTAT():
    """Direcția pe care egalitatea de cifre n-o vede: un clichet pe care instrumentul îl produce și
    tabelul nu-l poartă. Cifrele scrise ar fi toate corecte, iar tabelul ar tăcea despre el."""
    scris = {r["cod"] for r in _randuri_tabel(_bloc_din_document())}
    acum = {r["cod"] for r in _din_instrument()}
    assert not sorted(acum - scris), (
        "clichete recalculate și NEscrise în tabel: %s — dacă se măsoară, se și scrie"
        % sorted(acum - scris))
    assert not sorted(scris - acum), (
        "rânduri în tabel fără clichet care să le producă: %s — tabelul ar afirma ceva ce nu s-a "
        "măsurat" % sorted(scris - acum))


def test_blocul_e_IDENTIC_caracter_cu_caracter():
    """Peste comparația structurală: și punctuația e generată. Prinde ce structura tolerează —
    o etichetă rescrisă cu mâna, un instrument redenumit în document și nu în cod."""
    din_doc, generat = _bloc_din_document(), sr.redare_clichete_md()
    if din_doc != generat:
        ld, lg = din_doc.split("\n"), generat.split("\n")
        i = next((k for k in range(max(len(ld), len(lg)))
                  if (ld[k] if k < len(ld) else None) != (lg[k] if k < len(lg) else None)), 0)
        raise AssertionError(
            "blocul de clichete nu mai e cel generat, prima diferență la linia %d:%s"
            "  doc:   %r%s  acum:  %r%s"
            "Regenerează: ./venv/bin/python scripts/scan_ramas.py --clichete-md"
            % (i + 1, chr(10), ld[i] if i < len(ld) else "(lipsește)", chr(10),
               lg[i] if i < len(lg) else "(lipsește)", chr(10)))


# ── ANTI-VACUU: instrumentul chiar măsoară ────────────────────────────────────────────────────

def test_ANTI_VACUU_instrumentul_produce_cele_patru_clichete_cu_cifre():
    """Un gard care compară o listă goală cu o listă goală raportează verde despre o lume pe care
    n-o vede. Aici: dacă un import se rupe, `clichete()` prinde excepția și rândul dispare — deci
    absența unui cod e un eșec al instrumentului, nu o veste bună."""
    r = _din_instrument()
    coduri = {x["cod"] for x in r}
    assert coduri >= CODURI_ASTEPTATE, (
        "[anti-vacuu] clichete dispărute din instrument: %s — `scan_ramas.clichete()` înghite "
        "excepțiile de import, deci un rând lipsă înseamnă un instrument rupt, nu un clichet închis"
        % sorted(CODURI_ASTEPTATE - coduri))
    necifre = [(x["cod"], x["acum"]) for x in r if not re.fullmatch(r"\d+", x["acum"])]
    assert not necifre, (
        "[anti-vacuu] rânduri fără cifră (instrumentul a întors o eroare): %s" % necifre)
    umbra = next(x for x in r if x["cod"] == "77u")
    assert int(umbra["acum"]) > 100, (
        "[anti-vacuu] umbra a căzut la %s — o populație de sute care se golește peste noapte e un "
        "scan orb, nu o reparație" % umbra["acum"])


# ── CALIBRARE pe modul propriu de eșec (METODA §22), în AMÂNDOUĂ direcțiile ───────────────────

def test_CALIBRARE_o_cifra_mutata_cu_MANA_e_prinsa():
    """Modul de eșec al regulii, exact cum s-a produs: cineva (eu) actualizează cifra «din cap».
    Se probează pe forma reală — cifra umbrei mutată de la 781 înapoi la 779."""
    bloc = sr.redare_clichete_md()
    umbra = next(x for x in _din_instrument() if x["cod"] == "77u")
    stricat = bloc.replace("**%s**" % umbra["acum"], "**%d**" % (int(umbra["acum"]) - 2), 1)
    assert stricat != bloc, "calibrarea n-a putut strica blocul — s-a schimbat forma tabelului"
    scris = {r["cod"]: r["acum"] for r in _randuri_tabel(stricat)}
    assert scris["77u"] != umbra["acum"], "o cifră mutată cu mâna nu se vede în parsarea structurală"


def test_CALIBRARE_un_rand_STERS_e_prins():
    """A doua direcție, și e cea mai ieftină de produs: nu muți cifra, ștergi rândul. Toate cifrele
    rămase sunt corecte, iar tabelul tace despre un clichet întreg."""
    bloc = sr.redare_clichete_md()
    ciuntit = "\n".join(l for l in bloc.split("\n") if l.find("| **77u** |") < 0)
    assert ciuntit != bloc, "calibrarea n-a putut șterge rândul — s-a schimbat forma tabelului"
    coduri = {r["cod"] for r in _randuri_tabel(ciuntit)}
    assert not (CODURI_ASTEPTATE <= coduri), "un rând șters nu se vede în parsarea structurală"


def test_CALIBRARE_marcajele_STERSE_sunt_prinse():
    """A treia direcție: nu atingi tabelul, scoți marcajele. Blocul devine proză obișnuită, iar
    comparația n-ar mai avea ce compara."""
    fals = _document().replace(sr.MARCA_CLICHETE_START, "", 1)
    assert _bloc_din_document(fals) is None, (
        "marcajul de start șters nu se vede — gardul ar compara pe nimic")


def test_CALIBRARE_blocul_NU_poarta_ora_sau_data():
    """Direcția care ar fi rupt gardul din prima zi: dacă blocul ar purta ora, s-ar schimba la
    fiecare rulare, comparația ar pica ÎNTOTDEAUNA, iar cineva l-ar scoate ca să poată comite.
    (Aceeași lecție ca la `test_predare_cifre` și la inventarul din `GARZI.md`.)"""
    r = sr.clichete()
    assert sr.redare_clichete_md(r) == sr.redare_clichete_md(r), (
        "blocul nu e stabil la două redări pe aceleași rânduri")
    bloc = sr.redare_clichete_md(r)
    ceas = re.findall(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", bloc)
    assert not ceas, "blocul poartă o oră (%s) — s-ar schimba la fiecare rulare" % ceas
    data = re.findall(r"\b\d{2}\.\d{2}\.20\d{2}\b|\b20\d{2}-\d{2}-\d{2}\b", bloc)
    assert not data, "blocul poartă o dată (%s) — la fel" % data


# ── Umbra nu se mai scrie din memorie NICĂIERI în predare ──────────────────────────────────────

#: Cât text se citește în jurul cuvântului, ca să prindă și «UMBRA de <cifră>», și «<cifră> în umbră».
_RAZA = 90

#: SINGURA scutire, și e structurală, nu un comentariu-magic în document. Tabelul cifrelor
#: invalidate e, **prin construcție**, locul unde valorile vechi trebuie să stea — regula scrisă
#: acolo e *«o cifră ai cărei termeni nu se mai pot reconstitui se INVALIDEAZĂ, nu se corectează;
#: tabelul se POARTĂ, nu se deleagă în istoric»*. O cifră din tabelul ăla nu poate fi citită ca fiind
#: curentă: apartenența la tabel **e** declarația că nu mai e. De-aia scutirea nu redeschide gaura.
_SECTIUNE_SCUTITA = "## CIFRE INVALIDATE"


def _proza(doc=None):
    """Documentul, fără blocul generat și fără secțiunea scutită. Tăierea e pe STRUCTURĂ — de la
    titlul secțiunii până la următorul titlu de același nivel —, nu pe un marcaj pus cu mâna."""
    d = _document() if doc is None else doc
    bloc = _bloc_din_document(d)
    if bloc:
        d = d.replace(bloc, "")
    a = d.find(_SECTIUNE_SCUTITA)
    if a >= 0:
        b = d.find("\n## ", a + len(_SECTIUNE_SCUTITA))
        d = d[:a] + (d[b:] if b > 0 else "")
    return d


def _cifre_langa_umbra(proza):
    gasite = []
    for m in re.finditer(r"umbr[aăei]", proza, re.IGNORECASE):
        fereastra = proza[max(0, m.start() - _RAZA):m.end() + _RAZA]
        if re.search(r"(?<![\d.,])\d{3,4}(?![\d.,])", fereastra):
            gasite.append(" ".join(fereastra.split()))
    return gasite


def test_SCUTIREA_e_una_singura_si_chiar_exista():
    """Anti-vacuu pe propria scutire. Dacă tabelul cifrelor invalidate se redenumește, tăierea n-ar
    mai potrivi nimic — direcție sigură, garda ar deveni mai strictă, nu mai laxă. Dar dacă cineva
    **mută** conținut sub un titlu care se cheamă la fel, scutirea s-ar lărgi tăcut. Deci se cere
    ca secțiunea să existe, să fie **una**, și să fie mai mică decât documentul."""
    doc = _document()
    assert doc.count(_SECTIUNE_SCUTITA) == 1, (
        "secțiunea scutită %r apare de %d ori — o scutire care se multiplică nu mai e o scutire"
        % (_SECTIUNE_SCUTITA, doc.count(_SECTIUNE_SCUTITA)))
    taiat = len(doc) - len(_proza(doc))
    assert taiat > 0, "tăierea n-a scos nimic — scutirea nu mai potrivește secțiunea"

    # [03.09.2026] CE VERIFICĂ ACUM, și de ce s-a schimbat criteriul.
    #
    # Forma dinainte cerea ca tăierea să fie sub **o treime** din document. Proxy rezonabil, dar
    # măsura raportul greșit: tabelul cifrelor invalidate **doar crește** — regula scrisă acolo e că
    # se POARTĂ, nu se șterge —, în timp ce restul predării se **rescrie** și se scurtează la fiecare
    # rescriere completă. Deci proporția era condamnată să crească până pică, fără ca nimic să fie în
    # neregulă. *S-a întâmplat la rescrierea din 03.09: 17.222 din 39.879 de caractere, adică 43%,
    # pe un document corect.*
    #
    # Ce voia proxy-ul să apere e altceva: **ca sub titlul ăla să nu se mute proză**, lărgind tăcut
    # scutirea. Aia se verifică direct — secțiunea tăiată trebuie să fie, covârșitor, TABEL.
    inceput = doc.find(_SECTIUNE_SCUTITA)
    sectiune = doc[inceput:inceput + taiat]
    linii = [x.strip() for x in sectiune.splitlines() if x.strip()]
    randuri = [x for x in linii if x.startswith("|")]
    assert len(linii) >= 5, "secțiunea scutită e prea mică pentru a fi tabelul: %d linii" % len(linii)
    assert len(randuri) >= len(linii) * 0.7, (
        "doar %d din %d linii ale secțiunii scutite sunt rânduri de tabel — s-a mutat proză sub "
        "titlul scutit, iar scutirea s-ar lărgi tăcut" % (len(randuri), len(linii)))


def test_CALIBRARE_o_cifra_in_afara_scutirii_e_tot_prinsa():
    """Direcția care contează la o scutire: că **nu** amnistiază restul. Se pune o cifră lângă
    «umbră» în proza obișnuită, cu tabelul scutit la locul lui, și trebuie găsită."""
    fals = _document().replace(
        "## DACĂ CONTINUI DE AICI",
        "Umbra are azi 999 de refuzuri.\n\n## DACĂ CONTINUI DE AICI", 1)
    assert _cifre_langa_umbra(_proza(fals)), (
        "o cifră pusă în proza obișnuită nu mai e prinsă — scutirea a devenit portiță")


def test_umbra_NU_are_cifra_scrisa_de_mana_in_proza_predarii():
    """Instanța care a produs gardul: `PREDARE_LANT.md` scria «UMBRA de 779» în tabelul de restanțe,
    la 45 de rânduri sub tabelul de clichete care scria tot 779 — două locuri, aceeași cifră veche,
    într-un fișier de STARE CURENTĂ. Blocul generat e scutit; restul documentului, nu.

    De ce raza și nu o potrivire exactă: cifra veche nu se poate numi în gard (ar fi tot o cifră
    scrisă de mână). Se interzice CLASA — orice număr de trei-patru cifre lângă cuvânt.

    Scutit: blocul generat, și tabelul cifrelor invalidate (v. `_SECTIUNE_SCUTITA`)."""
    gasite = _cifre_langa_umbra(_proza())
    assert not gasite, (
        "cifră scrisă de mână lângă «umbră», în afara blocului generat — %d loc(uri):%s%s%s"
        "Umbra e declarat nedeplafonată și, prin decizia din 31.08, rămâne nemăsurată definitiv: "
        "cifra ei trăiește NUMAI în blocul generat, unde se recalculează. Oriunde altundeva "
        "îmbătrânește în tăcere — a făcut-o deja, 778 → 779 → 781 într-o singură zi."
        % (len(gasite), chr(10), chr(10).join("  · " + g for g in gasite), chr(10)))
