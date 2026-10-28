# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII „Comanda 12.1”), pachetul `firme2`: 475, 498, 143.

  * 475 — „Stocuri: Același articol «grau» de două ori în stoc.” (a) NIR-ul la cost cu două linii ale aceluiași articol nou („grau”) face un
    singur articol; (b) datele de dinainte de reparație (două „grau” create tacit, ca borderoul de până la 450): după migrarea
    `core/migrare_articole_dublate.py`, situația stocului arată „grau” o dată, cu cantitatea amândurora.
  * 498 — „Balanță: textul din antet prea lung.” Antetul spune luna, conturile și notele validate; de unde vin cifrele e o notă pliată
    („De unde vin cifrele”, închisă), iar ciornele nevalidate rămân în caseta lor (150 / R36).
  * 143 — „General: derulare laterală la 1920 px (Balanță, MF, Declarații).” Fiecare fereastră a firmei (toate cardurile vizibile), la
    1366 × 768 și la 1920 × 1080: nicio derulare laterală și nimic tăiat la dreapta (corpul ferestrei nu derulează lateral, deci un
    tabel mai lat decât el s-ar pierde fără să se vadă).

DATE DE PORNIRE fără ecran (declarate): notele cu sume mari intră pe rutele aplicației (`POST jurnal`, `POST jurnal/{id}/valideaza`);
cele două articole „grau” dublate se scriu cu INSERT — aplicația nu le mai poate produce (exact asta repară 475), deci starea de dinainte
se refăcea numai așa; migrarea e chemată cum o cheamă publicarea (`aplica` pe schema firmei). Furnizorul: DANTE INTERNATIONAL SA,
CUI 14399840 (cifra de control verificată cu algoritmul din CLAUDE.md).

Temei: N/A — reguli de produs (CLAUDE.md §9: „Fereastra încape pe ecran fără derulare”; „Textele dau instrucțiuni directe, în limba
contabilului”), nu fiscale."""
import datetime as _dt
import re

import pytest

from conftest import firma_noua, linie_nota, sql

AZI = _dt.date.today()
LUNA = "%02d/%d" % (AZI.month, AZI.year)


@pytest.fixture(scope="module")
def firma_f2_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_f2(patron, firma_f2_noua):
    """Firma nouă, cu Date firmă (stocul la cost, cantitativ-valoric), vectorul fiscal, seria și nomenclatorul (idempotent)."""
    from e2e_bloc_a import pregateste_firma
    pregateste_firma(patron, firma_f2_noua, platitor=True, regim_fiscal="profit")
    return firma_f2_noua


def _api(e, metoda, cale, corp=None):
    from e2e_bloc_a import _api as a
    return a(e, metoda, cale, corp)


def _ok(r, ce):
    from e2e_bloc_a import _ok as o
    return o(r, ce)


def _note_mari(patron, firma):
    """Două note validate în luna curentă, cu sume de 7 cifre (cazul măsurat al balanței late, DS cap.9 v2.96) — o singură dată."""
    tid, s = firma["tenant_id"], firma["schema"]
    for desc, linii in (("Vânzare E2E 143", [linie_nota("4111", "707", "9876543.21"), linie_nota("4111", "4427", "2074074.07")]),
                        ("Încasare E2E 143", [linie_nota("5121", "4111", "8765432.10")])):
        if not sql('SELECT 1 FROM "%s".inregistrari WHERE descriere = %%s' % s, (desc,)):
            r = _ok(_api(patron, "POST", "/tenants/%d/jurnal" % tid, {"descriere": desc, "data": AZI.isoformat(),
                                                                    "document_ref": "PV E2E 143", "linii": linii}), "nota " + desc)
            _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (tid, r["id"])), "validare " + desc)


def _situatia(patron):
    """Rândurile situației stocului: [(articol, UM, cantitate validată, valoare în ciornă)] (coloanele: Articol, UM, Gestiune, Cantitate, CMP,
    Valoare, În ciornă — [lotul 14, 696] tabelul arată stocul VALIDAT, iar ce e încă în ciornă stă în coloana lui)."""
    pg = patron.pg
    pg.wait_for_selector(".fereastra:last-of-type #s-situatie-tabel", timeout=30000)
    return pg.evaluate("() => [...[...document.querySelectorAll('.fereastra')].pop().querySelectorAll('#s-situatie-tabel tbody tr')]"
                       ".map((r) => [r.cells[0].innerText.trim(), r.cells[1].innerText.trim(), r.cells[3].innerText.trim(), r.cells[6].innerText.trim()])")


# ── 475 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_475_nirul_cu_doua_linii_ale_aceluiasi_articol_nou_face_un_singur_articol(patron, firma_f2):
    """475, drumul NIR-ului. Pașii: Stocuri -> „+ NIR nou” -> număr, dată, furnizor, CUI, „Factura furnizorului a sosit?” Nu -> linia 1:
    „+ articol nou…” „Grâu E2E 475” 5 kg la 2 lei, 11% -> „+ articol” -> linia 2: „+ articol nou…” „grau e2e 475” 3 la 2,50, 11% ->
    „Salvează NIR” -> „NIR salvat” -> situația stocului: articolul o singură dată, 8 (înainte: două rânduri, 5 și 3)."""
    from e2e_bloc_a import _card
    patron.firma(firma_f2["nume"])
    _card(patron, "stocuri", "#sn-toggle")
    pg = patron.pg
    pg.click("#sn-toggle")
    pg.fill("#sn-numar", "E2E-475-%d" % (int(_dt.datetime.now().timestamp()) % 100000))
    pg.fill("#sn-data", AZI.isoformat())
    pg.fill("#sn-furn", "DANTE INTERNATIONAL SA")
    pg.fill("#sn-cui", "14399840")
    pg.select_option("#sn-factura-sosita", "false")
    for i, (den, q, pret) in enumerate((("Grâu E2E 475", "5", "2"), ("grau e2e 475", "3", "2.5"))):
        if i:   # ecranul se deschide cu un rând de articol; „+ articol” numai pentru al doilea (altfel rămâne un rând gol, refuzat — corect)
            pg.click("#sn-plus")
        pg.select_option("#nir-l%d-articol" % i, "nou")
        pg.wait_for_selector("#nir-l%d-denumire" % i, timeout=10000)
        pg.fill("#nir-l%d-denumire" % i, den)
        pg.fill("#nir-l%d-cantitate" % i, q)
        pg.fill("#nir-l%d-pret_achizitie" % i, pret)
        pg.select_option("#nir-l%d-cota_tva" % i, "11")
    assert pg.locator("#sn-linii .nir-linie").count() == 2   # cele două rânduri completate, niciunul gol
    pg.click("#sn-salveaza")
    pg.wait_for_function("() => (document.querySelector('#s-mesaj') || {innerText: ''}).innerText.includes('NIR salvat')", timeout=30000)
    randuri = [r for r in _situatia(patron) if r[0].lower().replace("â", "a").startswith("grau e2e 475")]
    patron.captura()
    assert len(randuri) == 1 and randuri[0][0] == "Grâu E2E 475", randuri
    # [lotul 14, 696] NIR-ul e în ciornă: stocul validat e 0, iar cele două linii (5 × 2 + 3 × 2,50) stau împreună, pe UN rând, în coloana „În ciornă”
    assert randuri[0][2] == "0" and randuri[0][3] == "17,50", randuri
    assert sql('SELECT count(*) FROM "%s".articole WHERE lower(denumire) IN (%%s, %%s)' % firma_f2["schema"],
               ("grâu e2e 475", "grau e2e 475")) == [(1,)]


def test_def_475_vechi_doua_articole_grau_dublate_se_unesc(patron, firma_f2):
    """475, datele de dinainte de reparație (F1: „grau” nr. 5, 200 kg, BA-2, și nr. 6, 10 kg, BA-3, create tacit de borderou). Pașii:
    starea veche (două articole „grau e2e vechi”, 200 și 10 kg) -> migrarea publicării (`migrare_articole_dublate.aplica`) -> Stocuri:
    situația stocului arată articolul o singură dată, cu 210 kg."""
    from core import migrare_articole_dublate as mig
    from conftest import _db
    from e2e_bloc_a import _card
    s = firma_f2["schema"]
    if not sql('SELECT 1 FROM "%s".articole WHERE denumire = %%s' % s, ("grau e2e vechi",)):
        for q, doc in ((200, "BA-2 E2E 475"), (10, "BA-3 E2E 475")):
            # date-de-pornire: articolul dublat tacit de borderoul de dinainte de reparația 475 (codul de azi nu mai dublează)
            aid = sql('INSERT INTO "%s".articole (denumire, um) VALUES (%%s, %%s) RETURNING id' % s, ("grau e2e vechi", "kg"))[0][0]
            # date-de-pornire: intrarea în stoc a articolului dublat de mai sus, cum o lăsa borderoul vechi
            sql('INSERT INTO "%s".miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document) '
                "VALUES (%%s, %%s, 'intrare', %%s, 1, %%s, %%s)" % s, (aid, AZI.isoformat(), q, q, doc))
    patron.firma(firma_f2["nume"])
    _card(patron, "stocuri", "#s-situatie-tabel")
    inainte = [r for r in _situatia(patron) if r[0] == "grau e2e vechi"]
    patron.captura("vechi_inainte")
    assert len(inainte) == 2, inainte
    db = _db()
    with db.get_conn() as c:
        r = mig.aplica(c, s)
        c.commit()
    assert [len(u) for _p, u, _n in r["unite"]] == [1] and not r["neunite"], r
    patron.firma(firma_f2["nume"])
    _card(patron, "stocuri", "#s-situatie-tabel")
    dupa = [r for r in _situatia(patron) if r[0] == "grau e2e vechi"]
    patron.captura("vechi_dupa")
    assert len(dupa) == 1 and dupa[0][1] == "kg" and re.match(r"^210(,0+)?$", dupa[0][2]), dupa


# ── 498 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_498_antetul_balantei_spune_luna_si_cifrele_iar_sursa_lor_e_pliata(patron, firma_f2):
    """498. Pașii: firma cu două note validate în luna curentă -> „Balanță de verificare”: antetul „Luna LL/AAAA · N conturi · 2 note
    validate în luna asta”, fără explicația lungă (înainte: „… rulajele lunii vin din 2 note validate — aceleași pe care le arată Registrul
    jurnal pe luna asta, în afară de ciorne; notele lunilor anterioare și, în anul preluării, rulajele aduse din balanța de deschidere stau
    în «sume precedente»”); „De unde vin cifrele” închis -> clic -> explicația întreagă (ciornele nu intră; „Sume precedente”)."""
    from e2e_bloc_a import _card
    _note_mari(patron, firma_f2)
    patron.firma(firma_f2["nume"])
    _card(patron, "balanta", "#b-intro")
    pg = patron.pg
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #b-intro') || {innerText: ''}).innerText.includes('validat')",
                         timeout=30000)
    intro = " ".join(pg.inner_text(".fereastra:last-of-type #b-intro").replace("← luna", "").replace("luna →", "").split())
    assert intro.startswith("Luna %s · " % LUNA) and intro.endswith("· 2 note validate în luna asta"), intro
    assert "Registrul jurnal" not in intro and "precedente" not in intro and "ciorne" not in intro, intro
    assert pg.inner_text(".fereastra:last-of-type [data-card='surse']").strip() == "De unde vin cifrele"   # [lotul 14, 687] cardul, închis la deschidere
    assert pg.locator("#b-surse").count() == 0
    patron.captura("antet")
    pg.click(".fereastra:last-of-type [data-card='surse']")
    pg.wait_for_selector(".fereastra:last-of-type #b-surse", timeout=15000)
    nota = " ".join(pg.inner_text(".fereastra:last-of-type #b-surse").split())
    patron.captura("de_unde_vin_cifrele")
    assert "aceleași pe care le arată Registrul jurnal pe luna asta; ciornele nu intră" in nota, nota
    assert "stau în „Sume precedente”" in nota, nota


# ── 143 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
MASOARA = """() => {
  const f = [...document.querySelectorAll('.fereastra')].pop();
  if (!f) return ['nicio fereastră deschisă'];
  const corp = f.querySelector('.fereastra-corp') || f, out = [];
  if (corp.scrollWidth > corp.clientWidth + 1) out.push('conținut tăiat la dreapta: ' + corp.scrollWidth + ' > ' + corp.clientWidth + ' px');
  for (const e of f.querySelectorAll('*')) {
    const s = getComputedStyle(e);
    if (/(auto|scroll)/.test(s.overflowX) && e.clientWidth > 0 && e.scrollWidth > e.clientWidth + 1)
      out.push('derulare laterală în ' + (e.id ? '#' + e.id : (e.className || e.tagName)) + ': ' + e.scrollWidth + ' > ' + e.clientWidth);
  }
  const r = f.getBoundingClientRect();
  if (r.right > innerWidth + 1 || r.left < -1) out.push('fereastra iese din ecran');
  if (document.documentElement.scrollWidth > innerWidth + 1) out.push('pagina derulează lateral');
  return out;
}"""


def test_def_143_nicio_fereastra_a_firmei_nu_deruleaza_lateral_la_1366(patron, firma_f2):
    """143, clasa: toate ferestrele firmei. Pașii: ecran 1366 × 768 -> firma (cu sume de 7 cifre în luna curentă) -> fiecare card vizibil
    al ferestrei firmei, unul câte unul: fereastra deschisă nu derulează lateral și nu taie nimic la dreapta."""
    _ferestrele_firmei(patron, firma_f2, 1366, 768)


def test_def_143_nicio_fereastra_a_firmei_nu_deruleaza_lateral_la_1920(patron, firma_f2):
    """143 (cazul lui Costin: 1920 px). Aceiași pași, la 1920 × 1080."""
    _ferestrele_firmei(patron, firma_f2, 1920, 1080)


def _ferestrele_firmei(patron, firma_f2, lat, inalt):
    _note_mari(patron, firma_f2)
    pg = patron.pg
    pg.set_viewport_size({"width": lat, "height": inalt})
    patron.firma(firma_f2["nume"])
    carduri = pg.evaluate("() => [...document.querySelectorAll('button.firme-optiune[id^=\"fa-\"]')]"
                          ".filter((b) => b.offsetParent !== null && !b.disabled).map((b) => b.id)")
    assert len(carduri) >= 20, carduri
    gasite = {}
    for cid in carduri:
        patron.firma(firma_f2["nume"])
        pg.click("#" + cid)
        try:
            pg.wait_for_load_state("networkidle", timeout=30000)
        except Exception:   # noqa: BLE001 — o cerere lungă (ANAF) nu oprește măsurătoarea; fereastra se măsoară cum e
            pass
        pg.wait_for_timeout(1200)
        rez = pg.evaluate(MASOARA)
        if rez:
            gasite[cid] = rez
            patron.captura("%s_%d" % (cid, lat))
    assert not gasite, gasite


def test_def_143_nicio_fereastra_a_cabinetului_nu_deruleaza_lateral(patron, firma_f2):
    """143, clasa, restul ferestrelor-tabel: cardurile paginii principale a cabinetului (Firme, Asistenți, coada, activitatea cabinetului
    …), la 1366 × 768 și la 1920 × 1080: fereastra deschisă nu derulează lateral și nu taie nimic la dreapta."""
    pg = patron.pg
    gasite = {}
    for lat, inalt in ((1366, 768), (1920, 1080)):
        pg.set_viewport_size({"width": lat, "height": inalt})
        patron.acasa()
        chei = pg.evaluate("() => [...document.querySelectorAll('button.cab-card [data-cheie]')].map((e) => e.dataset.cheie)"
                           ".filter((c, i, a) => a.indexOf(c) === i)")
        assert len(chei) >= 5, chei
        for ch in chei:
            patron.acasa()
            pg.click("button.cab-card:has([data-cheie='%s'])" % ch)
            try:
                pg.wait_for_load_state("networkidle", timeout=30000)
            except Exception:   # noqa: BLE001 — o cerere lungă nu oprește măsurătoarea
                pass
            pg.wait_for_timeout(1200)
            rez = pg.evaluate(MASOARA)
            if rez and rez != ["nicio fereastră deschisă"]:
                gasite["%s@%d" % (ch, lat)] = rez
                patron.captura("cabinet_%s_%d" % (ch, lat))
    assert not gasite, gasite


# ── C133: motivul scutirii de contribuția minimă ────────────────────────────────────────────────────────────────────────────────
# OPANAF 605/2026 anexa 2, secțiunea „Date de identificare ale asiguratului”, pct.12: „Motivul exceptării - se completează în cazul în
# care caseta de la pct.11 a fost completată cu valoarea "1"” — motivele 1–5 (CF art.146 alin.(5^7) lit.a–e); „4” = pensionarii pentru
# limită de vârstă.
CNP_C133 = "1900101410011"     # cifra de control verificată (test_412_cim_salariat)
CNP_C133_VECHI = "1960101078916"   # cifra de control verificată (test_import_saga.CNP_OK)


def test_def_c133_salariatul_scutit_cere_motivul_scutirii(patron, firma_f2):
    """C133. Pașii: Salariați -> „+ Salariat nou” -> completat, „Scutit contribuție minimă” = Nu: „Motivul scutirii” nu se vede -> Da:
    apare, fără nimic ales -> Salvează: refuz lângă câmp („Alege …”), nimic salvat -> motivul „pensionar pentru limită de vârstă” ->
    Salvează: formularul se golește; în fișă `motiv_exceptare` = 4."""
    from e2e_bloc_a import _card
    f = firma_f2
    sql('DELETE FROM "%s".salariati WHERE cnp = %%s' % f["schema"], (CNP_C133,))
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "salariati", "#sp-salariat-nou")
    pg.click("#sp-salariat-nou")
    pg.wait_for_selector("#sn-salveaza", timeout=20000)
    for sel, v in (("#sn-nume", "PENSIONAR"), ("#sn-prenume", "ION"), ("#sn-cnp", CNP_C133), ("#sn-data_angajare", "2024-01-01"),
                   ("#sn-salariu_brut", "2000"), ("#sn-judet_casa", "B")):
        pg.fill(sel, v)
    for sel, v in (("#sn-tip_norma", "intreaga"), ("#sn-declaratie_copii", "false"), ("#sn-functie_baza", "true"),
                   ("#sn-scutit_contrib_minim", "false")):
        pg.click(".alegere-butoane:has(+ %s) button[data-valoare='%s']" % (sel, v))   # [lotul 13, 676] listele scurte = butoane alăturate
    assert pg.locator(".alegere-butoane:has(+ #sn-motiv_exceptare)").is_visible() is False
    pg.click(".alegere-butoane:has(+ #sn-scutit_contrib_minim) button[data-valoare='true']")
    assert pg.locator(".alegere-butoane:has(+ #sn-motiv_exceptare)").is_visible() and pg.eval_on_selector("#sn-motiv_exceptare", "s => s.value") == ""
    pg.fill("#sn-cor-cauta", "241107")
    pg.wait_for_selector("#sn-cor-rez [data-cod='241107']", timeout=20000)
    pg.click("#sn-cor-rez [data-cod='241107']")
    pg.click("#sn-salveaza")
    pg.wait_for_selector('.msg-eroare[data-camp="sn-motiv_exceptare"]', timeout=20000)
    patron.captura("motiv_cerut")
    assert sql('SELECT count(*) FROM "%s".salariati WHERE cnp = %%s' % f["schema"], (CNP_C133,)) == [(0,)]
    pg.click(".alegere-butoane:has(+ #sn-motiv_exceptare) button[data-valoare='4']")
    pg.click("#sn-salveaza")
    pg.wait_for_function("() => !(document.querySelector('#sn-nume') || {}).value", timeout=30000)
    patron.captura("salvat")
    assert sql('SELECT scutit_contrib_minim, motiv_exceptare FROM "%s".salariati WHERE cnp = %%s' % f["schema"], (CNP_C133,)) == [(True, 4)]


def test_def_c133_vechi_salariatul_scutit_fara_motiv_se_completeaza_din_de_verificat(patron, firma_f2):
    """C133, datele de dinainte de reparație: un salariat scutit fără motiv (cum intra până acum, pe ecran sau din import). Pașii: migrarea
    publicării (`migrare_motiv_scutire.aplica`) -> Salariați: rândul spune „motivul scutirii de contribuția minimă de ales (D112 îl
    declară)” -> „De verificat” -> „Motivul scutirii” (vizibil, nimic ales) -> „elev sau student…” -> „Confirmă” -> „datele de verificat
    sunt confirmate”; în fișă motivul 1, marcajul gol."""
    from core import migrare_motiv_scutire as mig
    from conftest import _db
    f, s = firma_f2, firma_f2["schema"]
    sql('DELETE FROM "%s".salariati WHERE cnp = %%s' % s, (CNP_C133_VECHI,))
    # date-de-pornire: salariatul scutit fără motiv, cum intra înainte de C133 (ecranul de azi cere motivul)
    sid = sql('INSERT INTO "%s".salariati (cnp, nume, prenume, data_angajare, scutit_contrib_minim, motiv_exceptare, cor, judet_casa, '
              "functie_baza, part_time) VALUES (%%s, 'VECHI', 'ANA', '2024-01-01', true, NULL, '241107', 'B', true, false) RETURNING id" % s,
              (CNP_C133_VECHI,))[0][0]
    # date-de-pornire: salariul aceluiași salariat vechi
    sql('INSERT INTO "%s".salariu_istoric (salariat_id, valabil_din, salariu_brut) VALUES (%%s, %%s, 2000)' % s, (sid, "2024-01-01"))
    db = _db()
    with db.get_conn() as c:
        assert sid in mig.aplica(c, s)
        c.commit()
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-salariati")
    # [lotul 13, 677] statul arată semnul „de verificat”; avertismentul și „De verificat” sunt în fereastra salariatului
    from e2e_lot13_sal_ajutor import deschide_salariat_id
    deschide_salariat_id(patron, sid)
    pg.wait_for_selector("[data-verif='%s']:not([disabled])" % sid, timeout=30000)
    assert "motivul scutirii de contribuția minimă de ales (D112 îl declară)" in patron.fereastra()
    patron.captura("vechi_stat_avertisment")
    pg.click("[data-verif='%s']" % sid)
    pg.wait_for_selector(".alegere-butoane:has(+ #dv-motiv)", timeout=20000)
    assert pg.locator(".alegere-butoane:has(+ #dv-motiv)").is_visible() and pg.eval_on_selector("#dv-motiv", "s => s.value") == ""
    pg.click(".alegere-butoane:has(+ #dv-motiv) button[data-valoare='1']")
    pg.click("#dv-save")
    pg.wait_for_function("() => document.body.innerText.includes('datele de verificat sunt confirmate')", timeout=20000)
    patron.captura("vechi_confirmat")
    assert sql('SELECT motiv_exceptare, de_verificat FROM "%s".salariati WHERE id = %%s' % s, (sid,)) == [(1, [])]


# ── C127: notele de salarii scrise înainte de încheierea lunii ──────────────────────────────────────────────────────────────────
def test_def_c127_vechi_nota_validata_scrisa_inainte_de_incheierea_lunii_e_semnalata(patron, firma_f2):
    """C127, datele de dinainte de reparația 216 (F5: „Stat de plata 11/2026”, validată, scrisă pe 06.10.2026; ciorna „SAL 10/2026”
    scrisă pe 08.10.2026). Starea veche: o notă de salarii VALIDATĂ datată în luna viitoare și o ciornă de salarii a lunii în curs, scrise
    azi. Pașii: migrarea publicării (`migrare_note_luna_neincheiata.aplica`): ciorna se scoate, nota validată rămâne -> Registru jurnal ->
    „luna →”: rândul notei validate are caseta „Nota a fost scrisă pe …, înainte ca luna … să se încheie …” -> „← luna”: ciorna lunii în
    curs nu mai e."""
    from core import migrare_note_luna_neincheiata as mig
    from conftest import _db
    from e2e_bloc_b import _deschide_rand, _jurnal, _mergi_la_luna, _nota_jn
    s = firma_f2["schema"]
    urm = (AZI.replace(day=1) + _dt.timedelta(days=32)).replace(day=28)
    if not sql('SELECT 1 FROM "%s".inregistrari WHERE descriere = %%s' % s, ("Salarii E2E C127 validată",)):
        for desc, data, st in (("Salarii E2E C127 validată", urm, "validata"), ("Salarii E2E C127 ciornă", AZI, "ciorna")):
            # date-de-pornire: nota de salarii scrisă înainte de încheierea lunii, cum o scria codul de dinainte de 216 (azi refuzată)
            iid = sql('INSERT INTO "%s".inregistrari (data, descriere, sursa, status, document_ref) VALUES (%%s, %%s, \'salarii\', '
                      "'ciorna', 'Stat de plată E2E C127') RETURNING id" % s, (data.isoformat(), desc))[0][0]
            # date-de-pornire: rândul notei vechi de salarii de mai sus
            sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, \'641\', \'421\', 5000)'
                % s, (iid,))
            if st == "validata":
                # date-de-pornire: validarea notei vechi datate în luna viitoare (starea lăsată de codul de dinainte de 216)
                sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = %%s' % s, (iid,))
    db = _db()
    with db.get_conn() as c:
        r = mig.aplica(c, s)
        c.commit()
    assert sql('SELECT count(*) FROM "%s".inregistrari WHERE descriere = %%s' % s, ("Salarii E2E C127 ciornă",)) == [(0,)], r
    vid = sql('SELECT id FROM "%s".inregistrari WHERE descriere = %%s' % s, ("Salarii E2E C127 validată",))[0][0]
    _jurnal(patron, firma_f2, (urm.year, urm.month))
    pg = patron.pg
    # [lotul 12, 617] caseta „scrisă înainte de încheierea lunii” stă în detaliul rândului: rândul notei validate, deschis
    pg.wait_for_selector("tbody.tn-nota[data-nota-id='%d']" % vid, timeout=30000)
    _deschide_rand(patron, _nota_jn(patron, vid))
    pg.wait_for_selector("#jn-inainte-%d" % vid, timeout=30000)
    t = " ".join(pg.inner_text("#jn-inainte-%d" % vid).split())
    patron.captura("vechi_nota_validata_semnalata")
    assert t.startswith("Nota a fost scrisă pe ") and ("înainte ca luna %02d/%d să se încheie" % (urm.month, urm.year)) in t, t
    assert "nota validată nu se modifică" in t, t
    _mergi_la_luna(patron, AZI.year, AZI.month)
    assert "Salarii E2E C127 ciornă" not in patron.fereastra()
    patron.captura("vechi_ciorna_scoasa")
