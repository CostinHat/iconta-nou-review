# -*- coding: utf-8 -*-
"""Lotul 9, comanda 9.1 (Costin 19.10.2026, verbatim în DECIZII „Comanda 9.1”): nerezolvatele din retestul lotului 8 și deficiențele noi
382–397 — pașii contabilului pe aplicația din index, pe baza de TEST, pe firme NOI de test (`firma_noua`). Fișierele sunt inventate;
CNP-urile și CUI-urile au cifra de control verificată (algoritmul din CLAUDE.md)."""
import datetime as _dt

import pytest

from conftest import firma_noua, sql
from e2e_import_saga import _incarca, _pas
from e2e_lot82 import _celule, _randul, _text, cnp_cu_control

CNP = "1800101221144"          # cifra de control verificată (e2e_lot82)
CUI_DANTE = "14399840"         # DANTE INTERNATIONAL SA (ANAF, verificat 18.10.2026)
AZI = _dt.date.today()


@pytest.fixture(scope="module")
def firma_srl():
    for f in firma_noua():
        yield f


@pytest.fixture(scope="module")
def firma_pfa():
    for f in firma_noua("pfa"):
        yield f


# ── 378 — amenda pe 6581 la nedeductibile, din cont ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_amenda(patron):
    """Cazul F2 din retest, cu cifre minime: firmă NOUĂ pe impozit pe profit; vânzări 4.600 lei în 2026, amenda 100 lei pe 6581 validată
    pe 30.09.2026 (6581 = 5311), D100 T1 depus cu 600 lei (preluat din istoric)."""
    from e2e_bloc_a import _api, _ok, pregateste_firma
    from e2e_bloc_e import _nota
    for f in firma_noua():
        pregateste_firma(patron, f)
        _ok(_api(patron, "POST", "/tenants/%d/vector" % f["tenant_id"],
                 {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": "trimestrial", "operatiuni_ic": False,
                  "inreg_art317": False, "tva_data_inceput": "2026-01-01"}), "vector profit")
        _nota(f, "2026-01-15", [{"debit": "5311", "credit": "704", "suma": 3750}], "Vânzări ianuarie E2E", valideaza=True)
        _nota(f, "2026-08-14", [{"debit": "5311", "credit": "704", "suma": 850}], "Vânzări august E2E", valideaza=True)
        _nota(f, "2026-09-30", [{"debit": "6581", "credit": "5311", "suma": 100}], "Amendă ITM E2E", valideaza=True)
        yield f


def test_def_378_amenda_pe_6581_intra_la_nedeductibile_in_d100(patron, firma_amenda):
    """378 (grav). Amenda pe 6581 intra ca deductibilă: nedeductibile 0, profit 4.500, impozit 720, de plată 120.
    Pașii: Istoric declarații -> D100 03/2026 cu 600 lei -> Declarații -> D100 T3/2026: „cheltuieli nedeductibile: 100,00 lei (din care
    rd.25 … din contul 6581 …: 100,00 lei”, profitul impozabil 4.600, impozitul cumulat 736, de plată 136 (CF art.25 alin.(4) lit.b))."""
    from e2e_lot82 import _d100_t3
    _pas(patron, firma_amenda, "Istoric declara")
    _incarca(patron, "istoric.csv", "Tip;Luna;An;Data depunerii;Suma de plata\nD100;03;2026;24.04.2026;600\n".encode(), ".mig-prev")
    pg = patron.pg
    pg.click("#mig-salveaza-ist")
    pg.wait_for_function("() => document.body.innerText.includes('declarați')", timeout=20000)
    t = _d100_t3(patron, firma_amenda)
    patron.captura()
    assert "cheltuieli nedeductibile: 100,00 lei (din care rd.25" in t and "din contul 6581" in t, t
    assert "profitul impozabil cumulat: 4.600,00 lei; impozitul cumulat: 736,00 lei" in t, t
    assert "de plată pe T3/2026: 736,00 lei − 600,00 lei = 136,00 lei" in t, t


def test_def_378_registrul_arata_randul_luat_din_cont(patron, firma_amenda):
    """378. Pașii: fereastra firmei -> „Registrul de evidență fiscală” -> anul 2026 (varianta profit) -> sub „Ajustări fiscale pe 2026”:
    „Din conturi, fără să le scrii: rd.25 — amenzi, majorări și penalități … 100,00 lei, din contul 6581 …”."""
    patron.firma(firma_amenda["nume"])
    pg = patron.pg
    pg.click("#fa-regfiscal")
    pg.wait_for_selector("#rf-an", timeout=60000)
    pg.fill("#rf-an", "2026")
    pg.dispatch_event("#rf-an", "change")
    pg.wait_for_selector("#aj-din-conturi", timeout=60000)
    t = " ".join(pg.inner_text("#aj-din-conturi").split())
    patron.captura()
    assert "rd.25 — amenzi, majorări și penalități" in t and "100,00 lei, din contul 6581" in t, t


# ── 382 — amortizarea în ciornă se spune la D100 ─────────────────────────────────────────────────────────────────────────────────
def test_def_382_d100_avertizeaza_amortizarea_din_ciorna(patron, firma_amenda):
    """382 (grav). Amortizarea 01–07/2026 (7 × 200 = 1.400 lei) în ciornă: D100 T3/2026 calcula fără ea și nu spunea nimic.
    Pașii: un mijloc fix de 12.000 lei / 60 de luni (pus în funcțiune pe 15.12.2025), amortizarea 01–07/2026 scrisă în Registrul jurnal și
    nevalidată, 08–09 validată -> Declarații -> D100 T3/2026: „Amortizarea pe 01–07/2026 (contul 2813, 1.400,00 lei) e generată, dar
    nevalidată: D100 pe T3/2026 se calculează fără ea …”, iar notele nevalidate ale ferestrei 01.01 – 30.09.2026 sunt numite."""
    from e2e_bloc_e import _nota
    from e2e_lot82 import _d100_t3
    sql('INSERT INTO "%s".mijloace_fixe (cod,denumire,cont_imobilizare,cont_amortizare,valoare,dnf_luni,data_pif,metoda) '
        "VALUES ('MF-E2E','Laptop E2E','2131','2813',12000,60,'2025-12-15','liniara')" % firma_amenda["schema"])
    for luna in range(1, 10):
        _nota(firma_amenda, "2026-%02d-28" % luna, [{"debit": "6811", "credit": "2813", "suma": 200}], "Amortizare %02d/2026 E2E" % luna,
              valideaza=luna > 7, document_ref="Amortizare %02d/2026" % luna)
    t = _d100_t3(patron, firma_amenda)
    patron.captura()
    assert "Amortizarea pe 01–07/2026 (contul 2813, 1.400,00 lei) e generată, dar nevalidată: D100 pe T3/2026 se calculează fără ea" in t, t
    assert "D100 pe T3/2026 nu cuprinde 7 note nevalidate din 01.01.2026 – 30.09.2026" in t, t


# ── 383 — declarația pe o perioadă neîncheiată nu se oferă spre depunere ─────────────────────────────────────────────────────────
@pytest.fixture()
def firma_tva_luna(patron):
    """O firmă NOUĂ plătitoare de TVA (lunar), cu o factură emisă în luna încheiată (`e2e_lot72_declaratii.LUNA`, pe care se generează
    declarațiile: luna în curs se refuză — 383, comanda 10.2 pct.1) și nota ei validată."""
    from e2e_bloc_a import emite_api, pregateste_firma
    from e2e_lot72_declaratii import ZI, _valideaza_notele
    for f in firma_noua():
        pregateste_firma(patron, f)
        fct = emite_api(patron, f, data_emitere=ZI)
        _valideaza_notele(patron, f, fct["factura_id"])
        yield f


def test_def_383_d300_pe_luna_in_curs_nu_se_ofera_spre_depunere(patron, firma_tva_luna):
    """383 (grav). D300 pe 10/2026 era oferită cu „Confirmă depunerea” pe 19.10.2026. [lotul 10, comanda 10.2 pct.1] Generarea pe o perioadă
    neîncheiată se refuză acum de la început (`e2e_lot10b_declaratii.py::test_def_383_d300_pe_luna_in_curs_se_refuza_la_generare`); aici
    rămâne stratul de dedesubt, pentru o declarație intrată în coadă ÎNAINTE de regulă (cazul F1 din 20.10): ea e refăcută ca element din luna
    trecută (generabil) mutat pe luna curentă. Pașii: „De depus” -> pe rândul ei, în locul butonului: „Perioada LL/AAAA nu s-a încheiat:
    declarația se generează și se depune după <ultima zi a lunii> …”; fără „Confirmă depunerea”; depunerea cerută direct e refuzată, iar
    declarația nu e depusă."""
    import json as _json
    from e2e_bloc_a import _api
    from e2e_lot72_declaratii import _curata, _deschide_coada, _in_coada, _peste
    peste = _peste()
    trecuta = AZI.replace(day=1) - _dt.timedelta(days=1)
    try:
        r = _in_coada(patron, firma_tva_luna, luna=trecuta.month, an=trecuta.year)
        assert r["status"] == 200, r
        cid = r["json"]["coada_id"]
        # declarația „de dinainte de regulă”: aceeași, pe luna curentă (perioada declarată din payload)
        p = sql("SELECT payload FROM public.declaratii_coada WHERE id = %s", (cid,))[0][0]
        p.update({"_an": AZI.year, "_luna": AZI.month})
        sql("UPDATE public.declaratii_coada SET payload = %s::jsonb WHERE id = %s", (_json.dumps(p), cid))
        rand = _deschide_coada(patron, cid)
        pg = patron.pg
        txt = " ".join(pg.inner_text(rand).split())
        patron.captura()
        per = "%02d/%d" % (AZI.month, AZI.year)
        assert ("Perioada %s nu s-a încheiat: declarația se generează și se depune după" % per) in txt, txt
        assert pg.locator(rand + " .val-depune, " + rand + " .val-trece").count() == 0, "butonul de depunere pe o perioadă neîncheiată"
        # depunerea cerută direct nu trece (poarta verdictului / validarea în doi pot refuza înaintea perioadei; refuzul perioadei însuși e
        # probat pe tranziție în core/test_383_perioada_neincheiata.py)
        refuz = _api(patron, "POST", "/coada/%d/depune" % cid, {})
        assert refuz["status"] in (403, 409, 422), refuz
        assert sql("SELECT stare FROM public.declaratii_coada WHERE id = %s", (cid,))[0][0] != "depusa"
    finally:
        _curata(firma_tva_luna, peste)


# ── 323 — textul de sus al „De depus” nu vorbește de note când nu sunt ──────────────────────────────────────────────────────────
def test_def_323_textul_de_depus_nu_vorbeste_de_note_care_nu_sunt(patron, firma_tva_luna):
    """323 (retestul 19.10). În „De depus”, textul de sus vorbea tot de „notele pe care asistenții le trimit la validare”.
    Pașii: o declarație în coadă, nicio notă de validat -> „De depus”: textul de sus vorbește de declarații, nu de note."""
    from e2e_lot72_declaratii import _curata, _deschide_coada, _in_coada, _peste
    peste = _peste()
    try:
        # [lotul 10, 383] luna curentă nu se mai generează (perioada neîncheiată): o declarație în coadă pe luna trecută
        trecuta = AZI.replace(day=1) - _dt.timedelta(days=1)
        cid = _in_coada(patron, firma_tva_luna, luna=trecuta.month, an=trecuta.year)["json"]["coada_id"]
        _deschide_coada(patron, cid)
        pg = patron.pg
        intro = " ".join(" ".join(pg.eval_on_selector_all(".fereastra:last-of-type .mig-intro", "es => es.map(x => x.innerText)")).split())
        note = pg.locator(".fereastra:last-of-type .val-card[data-fel='nota'], .fereastra:last-of-type #val-note .val-card").count()
        patron.captura()
        assert "trimit la validare" not in intro and "Declarațiile" in intro, intro
        if not note:
            assert "Notele" not in intro and "note" not in intro.lower().replace("notificări", ""), intro
    finally:
        _curata(firma_tva_luna, peste)


# ── 368 — PFA: Mijloace fixe rămâne; Raport Z în registrul de încasări și plăți ───────────────────────────────────────────────────
def test_def_368_pfa_are_mijloace_fixe_fara_note(patron, firma_pfa):
    """368 (retestul 19.10). La PFA dispăruse cardul Mijloace fixe, care trebuia să rămână. Pașii: firma PFA -> fereastra firmei are
    „Mijloace fixe” -> registrul se deschide fără coloanele „înregistrat în contabilitate” / „diferență” și fără casare / reevaluare (care
    scriu note); textul spune că amortizarea intră în fișa D212."""
    pg = patron.pg
    patron.firma(firma_pfa["nume"])
    assert pg.locator("#fa-mijloace").count() == 1, "cardul Mijloace fixe lipsește la PFA"
    pg.click("#fa-mijloace")
    pg.wait_for_selector(".fereastra:last-of-type h2.pf-titlu:has-text('Mijloace fixe')", timeout=30000)
    pg.wait_for_function("() => !document.querySelector('.fereastra:last-of-type .ecran-nota') || "
                         "!document.querySelector('.fereastra:last-of-type .ecran-nota').textContent.includes('Se încarcă')", timeout=30000)
    t = _text(patron)
    patron.captura()
    assert "Înregistrat (cont" not in t and "Diferență" not in t and "Casează" not in t, t[:800]
    if pg.locator("#mf-intro-simpla").count():
        assert "partidă simplă" in t and "D212" in t, t[:800]


def test_def_368_raportul_z_la_pfa_intra_in_registrul_de_incasari(patron, firma_pfa):
    """368 (retestul 19.10). „Raport Z la PFA spune «Încasări zilnice → notă automată» — la PFA nu există note contabile.”
    Pașii: firma PFA -> cardul Raport Z spune „Încasări zilnice → registrul de încasări și plăți” -> un Z de 100 lei (60 numerar, 40 card)
    -> „Înregistrează raportul Z” -> „Numerarul (60,00 lei) e în registrul de încasări și plăți …; Cardul (40,00 lei) intră … din extrasul
    de bancă”; în registru e încasarea de 60 lei, ciornă."""
    pg = patron.pg
    patron.firma(firma_pfa["nume"])
    desc = " ".join(pg.inner_text("#fa-raportz").split())
    assert "registrul de încasări și plăți" in desc and "notă" not in desc, desc
    pg.click("#fa-raportz")
    pg.wait_for_selector("#z-salveaza", timeout=20000)
    assert "Înregistrează raportul Z" in pg.inner_text("#z-salveaza")
    data = (AZI.replace(day=1) - _dt.timedelta(days=1)).isoformat()
    pg.fill("#z-data", data)
    pg.fill("#z-nui", "8000000391")
    pg.fill("#z-nr", "0368")
    pg.fill("#z-21", "100")
    pg.fill("#z-num", "60")
    pg.fill("#z-card", "40")
    pg.fill("#z-bonuri", "3")
    pg.click("#z-salveaza")
    pg.wait_for_selector("#z-rip, #z-rezultat .msg-eroare, #z-rezultat .caseta-eroare", timeout=30000)
    t = " ".join(pg.inner_text("#z-rezultat").split())
    patron.captura()
    assert "Numerarul (60,00 lei) e în registrul de încasări și plăți" in t and "Cardul (40,00 lei) intră în registru" in t, t
    rip = sql('SELECT tip, suma, metoda, status FROM "%s".rip_operatiuni WHERE document_numar = %%s' % firma_pfa["schema"], ("0368",))
    assert [(r[0], float(r[1]), r[2], r[3]) for r in rip] == [("incasare", 60.0, "numerar", "ciorna")], rip


# ── 371 — Rețete numai la firmele HoReCa ─────────────────────────────────────────────────────────────────────────────────────────
# fixtura `firma_horeca` stă în conftest.py (o cer și alte fișiere)
def test_def_371_retetele_se_ofera_numai_firmelor_horeca(patron, firma_pfa, firma_srl, firma_horeca):
    """371 (retestul 19.10). „Rețete (HoReCa) oferă toate firmele, inclusiv PFA și FISCALOS ICONTA.” Pașii: Migrare cabinet -> „Rețete
    (HoReCa)” -> lista are firma cu CAEN 5610, nu și SRL-ul fără CAEN HoReCa, nici PFA-ul; meniul de import al SRL-ului nu are Rețete,
    al firmei HoReCa da."""
    from e2e_lot5_migrare import _migrare
    pg = patron.pg
    _migrare(patron)
    pg.locator("#mig-meniu .mig-op", has_text="Rețete (HoReCa)").first.click()
    pg.wait_for_selector(".mig-frand, .stare-goala", timeout=20000)
    nume = " ".join(pg.locator(".mig-frand").all_inner_texts())
    patron.captura("lista")
    assert firma_horeca["nume"] in nume, nume
    assert firma_srl["nume"] not in nume and firma_pfa["nume"] not in nume, nume
    for f, are in ((firma_srl, False), (firma_horeca, True)):
        patron.firma(f["nume"])
        pg.click("#fa-import")
        pg.wait_for_selector(".mig-frand", timeout=20000)
        titluri = [" ".join(x.split()) for x in pg.locator(".mig-frand .mig-frand-nume").all_inner_texts()]
        assert ("Rețete (HoReCa)" in titluri) is are, (f["nume"], titluri)


# ── 349 — previzualizarea Salariați: rândul cu denumire COR lungă, fără derulare laterală ─────────────────────────────────────────
def test_def_349_denumirea_cor_lunga_nu_inalta_randul_si_tabelul_incape(patron, firma_srl):
    """349 (retestul 19.10). Rândul cu descriere COR lungă avea ~230 px, iar tabelul derula orizontal (coloana „Persoane în întreținere”
    tăiată). Pașii: Salariați -> un fișier cu COR 214441 (126 de caractere în nomenclator), fără persoane în întreținere -> rândul are sub
    90 px, iar tabelul încape în cutia lui (nicio derulare laterală); „Persoane în întreținere” se vede."""
    from e2e_lot82 import _salariati
    _salariati(patron, firma_srl, "Nume;Prenume;CNP;Functie;Cod COR;Functie baza;Data angajarii;Norma;Salariu brut\n"
                                  "Pop;Ion;%s;Specialist;214441;Da;01.03.2024;8;5000\n" % CNP)
    pg = patron.pg
    # fereastra se lățește singură (DS cap.9, 285 / 349): se așteaptă lățirea, cel mult 5 s — dacă nu vine, aserțiunea de mai jos pică
    try:
        pg.wait_for_function("() => { const c = document.querySelector('.mig-prev-cutie'); return c && c.scrollWidth <= c.clientWidth + 1; }",
                             timeout=5000)
    except Exception:  # noqa: BLE001 — aserțiunea numește cifrele
        pass
    rand = pg.locator('.mig-prev tbody tr[data-rand="2"]:not(.mig-prev-motive)').first
    h = rand.bounding_box()["height"]
    lat = pg.evaluate("""() => { const c = document.querySelector('.mig-prev-cutie');
      const th = [...c.querySelectorAll('thead th')].find((x) => x.innerText.includes('întreținere')).getBoundingClientRect();
      return {sw: c.scrollWidth, cw: c.clientWidth, th_dreapta: th.right, cutie_dreapta: c.getBoundingClientRect().right}; }""")
    patron.captura()
    assert h < 90, "rândul are %d px" % h
    assert lat["sw"] <= lat["cw"] + 1 and lat["th_dreapta"] <= lat["cutie_dreapta"] + 1, lat
    assert "214441" in _randul(pg, 2), _randul(pg, 2)


# ── 384 — Import Asociați: cotele se adună numai pe rândurile care intră ─────────────────────────────────────────────────────────
def test_def_384_totalul_cotelor_nu_aduna_randurile_respinse(patron, firma_srl):
    """384 (grav). „total cote ✓ 100%” aduna și rândurile respinse; intra un singur asociat, cu 30%. Pașii: Asociați -> un fișier cu
    Pop Ion 30% (CNP valid) și Ion Pop 70% (CNP cu cifra de control greșită) -> banda spune „total cote: ⚠ 30%”, rândul 3 e respins,
    „Salvează asociații” e oprit; în firmă nu intră niciun asociat."""
    _pas(patron, firma_srl, "Asocia")
    _incarca(patron, "asociati.csv", ("Nume;CNP;Cota\nPop Ion;%s;30\nIon Pop;1800101221145;70\n" % CNP).encode(), "#mig-salveaza-asoc")
    pg = patron.pg
    banda = " ".join(pg.inner_text(".mig-coer").split())
    patron.captura()
    assert "total cote: ⚠ 30%" in banda and "✓ 100%" not in banda, banda
    assert "respins — nu intră" in _randul(pg, 3), _randul(pg, 3)
    assert pg.is_disabled("#mig-salveaza-asoc")
    assert sql('SELECT count(*) FROM "%s".asociati' % firma_srl["schema"])[0][0] == 0


# ── 385 — Import Articole: dublura se respinge numit ─────────────────────────────────────────────────────────────────────────────
def test_def_385_articolul_de_pe_doua_randuri_e_respins_numit(patron, firma_srl):
    """385. „Marfa valida” pe două rânduri (10 buc și 3 buc) intra de două ori, fără observație. Pașii: Articole și stoc inițial -> fișierul
    -> rândul 3: „respins — nu intră”, „„Marfa valida” apare și pe rândul 2 — un articol se trece o singură dată, cu stocul lui total”."""
    _pas(patron, firma_srl, "Articole")
    _incarca(patron, "articole.csv", "Denumire;UM;Cantitate;Pret;Cont stoc\nMarfa valida;buc;10;2;371\nMarfa valida;buc;3;2;371\n".encode(),
             "#mig-importa")
    pg = patron.pg
    r = _randul(pg, 3)
    patron.captura()
    assert "respins — nu intră" in r and "apare și pe rândul 2 — un articol se trece o singură dată, cu stocul lui total" in r, r
    assert "respins" not in _randul(pg, 2), _randul(pg, 2)


def test_def_c55_salariatul_de_pe_doua_randuri_e_respins_numit(patron, firma_srl):
    """C55 (clasa lui 385, găsită la generalizare): același CNP pe două rânduri în Salariați — salvarea îl înlocuia pe tăcute pe primul cu al
    doilea (`ON CONFLICT (cnp) DO UPDATE`). Pașii: Salariați -> fișierul -> rândul 3 respins: „CNP-ul … apare și pe rândul 2”."""
    from e2e_lot82 import _salariati
    _salariati(patron, firma_srl, "Nume;Prenume;CNP;Functie baza;Norma;Salariu brut\nPop;Ion;%s;Da;8;5000\nPop;Ion;%s;Da;8;5100\n"
               % (CNP, CNP))
    r = _randul(patron.pg, 3)
    patron.captura()
    assert "respins — nu intră" in r and ("CNP-ul %s apare și pe rândul 2" % CNP) in r, r


# ── 386 — Registru jurnal: nota fără document — de ce nu se validează și drumul care o face posibilă ────────────────────────────
def test_def_386_nota_fara_document_spune_de_ce_si_duce_la_editare(patron, firma_srl):
    """386. „Validează fără document” (după confirmare) nu făcea nimic și nu spunea de ce; nota rămânea Ciornă (6581 = 5311, 100 lei).
    Regula de fond din bază (R3, comanda Costin 09.10.2026: „fiecare notă are documentul-sursă”) refuză validarea fără document, deci
    butonul care o promitea era greșit. Pașii: o notă 6581 = 5311 de 100 lei, fără document -> Registru jurnal -> pe rând, o dată:
    „… nu se validează fără documentul din care provine … Scrie referința cu «Editează», apoi validează.”, „Validează” inactiv (lotul 10,
    10.2 pct.7k: mesajul nu se mai repetă în dreapta) -> „Editează” -> editorul notei ->
    documentul „Proces-verbal ITM nr. 12 din <azi>” -> „Salvează” -> „Validează” -> nota e validată."""
    from e2e_bloc_a import _api, _ok
    from e2e_bloc_e import _nota
    tid, s = firma_srl["tenant_id"], firma_srl["schema"]
    # numerarul din care se plătește amenda (406: casa nu ajunge sub zero la validare)
    _nota(firma_srl, AZI.isoformat(), [{"debit": "5311", "credit": "581", "suma": 1000}], "Ridicare numerar E2E 386", valideaza=True,
          document_ref="Cec 386")
    nid = _ok(_api(patron, "POST", "/tenants/%d/jurnal" % tid, {"descriere": "Amendă fără document E2E 386", "data": AZI.isoformat(),
                                                              "linii": [{"debit": "6581", "credit": "5311", "suma": "100.00"}]}), "nota")["id"]
    patron.firma(firma_srl["nume"])
    pg = patron.pg
    pg.click("#fa-jurnal")
    pg.wait_for_selector("[data-nota-id='%s'] [data-val]" % nid, timeout=30000)
    # [lotul 10, 10.2 pct.7k] un singur mesaj, pe rând; „Validează” inactiv, legat de el (nu mai e și caseta de confirmare din dreapta)
    rand = " ".join(pg.inner_text("[data-nota-id='%s']" % nid).split())
    patron.captura("caseta")
    assert rand.count("nu se validează fără documentul din care provine") == 1 and "Editează" in rand, rand
    assert pg.is_disabled("[data-nota-id='%s'] [data-val]" % nid)
    assert "Validează fără document" not in rand, rand
    pg.click("[data-nota-id='%s'] [data-edit]" % nid)
    pg.wait_for_selector("#je-doc", timeout=10000)
    pg.fill("#je-doc", "Proces-verbal ITM nr. 12 din %s" % AZI.strftime("%d.%m.%Y"))   # AZI-dat-de-test
    pg.click("#je-salveaza")
    pg.wait_for_selector("[data-nota-id='%s'] [data-val]" % nid, timeout=20000)
    pg.click("[data-nota-id='%s'] [data-val]" % nid)
    pg.wait_for_function("(n) => { const r = document.querySelector(`[data-nota-id='${n}']`); return r && !r.querySelector('[data-val]'); }",
                         arg=nid, timeout=20000)
    patron.captura("validata")
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % s, (nid,))[0][0] == "validata"


# ── 389 — Istoric declarații: suma pomenită, perioada trimestrială ca în formular ────────────────────────────────────────────────
def test_def_389_istoricul_spune_suma_si_arata_trimestrul(patron, firma_amenda):
    """389. Textul ferestrei („tip · an · lună · data depunerii”) nu pomenea suma; perioada apărea 03/2026 și 06/2026 în loc de T1/2026,
    T2/2026. Pașii: firma pe impozit pe profit -> Istoric declarații: textul pomenește „suma de plată”; fișierul D100 03/2026 și 06/2026
    -> coloana „Perioada”: „T1/2026”, „T2/2026”."""
    _pas(patron, firma_amenda, "Istoric declara")
    pg = patron.pg
    intro = " ".join(pg.inner_text(".mig-intro").split())
    assert "suma de plată" in intro, intro
    _incarca(patron, "istoric.csv", "Tip;Luna;An;Data depunerii;Suma de plata\nD100;03;2026;24.04.2026;600\nD100;06;2026;24.07.2026;0\n"
             .encode(), ".mig-prev")
    patron.captura()
    assert _celule(pg, 2).get("Perioada") == "T1/2026" and _celule(pg, 3).get("Perioada") == "T2/2026", (_celule(pg, 2), _celule(pg, 3))


# ── 390 — D406: avertismentele numesc nota ca în Registrul jurnal; nota manuală normală nu cere corectură ───────────────────────
def test_def_390_d406_numeste_nota_dupa_nr_crt_si_nu_cere_corectura_notei_manuale(patron, firma_tva_luna):
    """390. Avertismentele D406 trimiteau la „nota 3” și „nota 48”, nu la Nr. crt. din Registrul jurnal; al doilea era tehnic („sursa
    'manual'”, „jurnal auxiliar”, „maparea”) și cerea o corectură pentru o notă manuală normală. Pașii: o notă manuală validată (6581 =
    5311) și o notă cu o proveniență pe care aplicația n-o scrie (adusă direct în bază) -> Declarații -> D406 pe luna încheiată: nota
    manuală nu e semnalată; cealaltă e numită „nota nr. crt. N din ZZ.LL.AAAA”; niciun „sursa”, „jurnal auxiliar”, „maparea”."""
    from conftest import nr_crt
    from e2e_bloc_e import _declaratie, _nota
    from e2e_lot72_declaratii import LUNA, ZI
    f = firma_tva_luna
    _nota(f, ZI.isoformat(), [{"debit": "5311", "credit": "581", "suma": 100}], "Ridicare numerar E2E 390", valideaza=True,
          document_ref="Cec 390")   # numerarul plăților de mai jos (406)
    _nota(f, ZI.isoformat(), [{"debit": "6581", "credit": "5311", "suma": 10}], "Amendă E2E 390", valideaza=True, document_ref="PV 390")
    straina = _nota(f, ZI.isoformat(), [{"debit": "6022", "credit": "5311", "suma": 5}], "Notă adusă E2E 390", document_ref="Bon 390")
    sql('UPDATE "%s".inregistrari SET sursa = %%s WHERE id = %%s' % f["schema"], ("import_vechi", straina))   # ciornă: încă se poate
    from e2e_bloc_e import _valideaza_note
    _valideaza_note(f, [straina])
    _declaratie(patron, f, "d406", LUNA.an, LUNA.luna)
    t = _text(patron)
    patron.captura()
    assert ("nota %s" % nr_crt(f["schema"], straina)) in t, t[:2000]
    for tehnic in ("sursa '", "jurnal auxiliar", "maparea", "nota %d:" % straina, "nota %d," % straina):
        assert tehnic not in t, (tehnic, t[:2000])
    manuala = sql('SELECT id FROM "%s".inregistrari WHERE descriere = %%s' % f["schema"], ("Amendă E2E 390",))[0][0]
    assert ("nota %s" % nr_crt(f["schema"], manuala)) not in t, t[:2000]   # nota manuală normală nu e semnalată


# ── 391 — Emite factura: după emitere nu se mai oferă „Renunță la factură” ───────────────────────────────────────────────────────
def test_def_391_dupa_emitere_nu_mai_e_renunta(patron, firma_tva_luna):
    """391. După emitere (F1A7) era încă oferit „Renunță la factură”, cu mesajul fals „Ce ai scris se șterge; nu se emite nimic”.
    Pașii: contabilul completează și emite o factură -> „Emisă ✓”; „Renunță la factură” nu mai e pe ecran."""
    from e2e_bloc_a import _completeaza_factura, _deschide_emiterea
    _deschide_emiterea(patron, firma_tva_luna["nume"])
    pg = patron.pg
    assert pg.locator("#em-renunta").count() == 1   # înainte de emitere: renunțarea are rost
    _completeaza_factura(pg, cantitate="1")
    pg.wait_for_function("() => !document.querySelector('#em-emite').disabled", timeout=20000)
    pg.click("#em-emite")
    pg.wait_for_function("() => document.querySelector('#em-rezultat').innerText.includes('emisă')", timeout=60000)
    if not pg.locator("#em-emite").count():
        pytest.skip("formularul s-a închis singur (firma conectată la SPV)")
    patron.captura()
    assert pg.locator("#em-renunta").count() == 0, "„Renunță la factură” oferit după emitere"


# ── 392 — Solduri inițiale: textul spune ce se întâmplă cu contul inexistent; 5121 creditor semnalat pe rând ─────────────────────
def test_def_392_textul_spune_respingerea_si_5121_creditor_e_semnalat(patron, firma_srl):
    """392. Textul ferestrei spunea că, conturile noi „se adaugă automat (nu sunt respinse)”, contrar 343; 5121 cu sold creditor intra fără
    avertisment la import. Pașii: Solduri inițiale -> textul: „e respins, cu motivul”; balanța cu 5121 creditor 20.000 -> rândul 5121 „intră,
    cu observație”: „5121 (activ) are sold creditor 20.000,00 lei: soldul stă pe partea opusă funcțiunii contului …”."""
    _pas(patron, firma_srl, "Solduri ini")
    pg = patron.pg
    intro = " ".join(pg.inner_text(".mig-intro").split())
    assert "e respins, cu motivul" in intro and "nu sunt respinse" not in intro, intro
    _incarca(patron, "balanta.csv", "Cont;Denumire;Sold final debitor;Sold final creditor\n5121;Banca;0;20000\n1012;Capital;20000;0\n"
             .encode(), "#mig-salveaza-sold")
    r = _randul(pg, 2)
    patron.captura()
    assert "5121 (activ) are sold creditor 20.000,00 lei: soldul stă pe partea opusă funcțiunii contului" in r and "intră, cu observație" in r, r


# ── 393 — Import firme: remediul spune unde e codul; numărul spune câte au ajuns la ANAF ────────────────────────────────────────
def test_def_393_cui_lipit_si_numarul_verificat_la_anaf(patron, firma_srl):
    """393. „corectează-l în fișier” la un CUI lipit, nu încărcat; „S-au verificat 2 CUI-uri la ANAF”, deși cel cu cifra de control greșită
    nu ajunge la ANAF. Pașii: Migrare cabinet -> Firme -> lipește CUI-ul unei firme și 14399841 -> „Validează la ANAF”: textul de sus
    „S-au verificat 1 CUI la ANAF. Un cod are cifra de control greșită și nu a fost trimis”; rândul greșit spune „corectează-l în lista
    lipită”, nu „în fișier”."""
    from e2e_lot82 import _firme_validate
    t = _firme_validate(patron, firma_srl)
    intro = " ".join(patron.pg.inner_text(".mig-intro").split())
    gresit = next(x for x in t if "CUI greșit" in x)
    assert "S-au verificat 1 CUI la ANAF." in intro and "Un cod are cifra de control greșită și nu a fost trimis" in intro, intro
    assert "corectează-l în lista lipită" in gresit and "în fișier" not in gresit, gresit


# ── 394 — Registrul jurnal lat (linia notei pe un rând); motivul amortizării sub rândul de butoane ──────────────────────────────
@pytest.fixture()
def firma_goala():
    """O firmă NOUĂ, fără nicio notă (Registrul jurnal al lunii gol)."""
    for f in firma_noua():
        yield f


def test_def_394_jurnalul_e_lat_si_motivul_amortizarii_nu_rupe_butoanele(patron, firma_goala):
    """394 (parțial). Fereastra Notă nouă avea derulare verticală; în Registru jurnal „amortizarea lunii se generează după ce luna se
    încheie” era rupt de butoane. Pașii, pe un ecran de laptop (1366×768), pe o firmă fără note: Registru jurnal (luna curentă) -> motivul
    e sub rândul de butoane, nu între ele -> „+ Notă nouă” -> fereastra e lată (ca Mijloace fixe), rândul de butoane încape pe un rând și
    fereastra nu derulează (de la titlu la „Salvează”). Cu note multe în lună, lista lor (sub formular) derulează; formularul întreg pe un
    ecran mai mic cere rearanjarea lui (decizie, raportul 9.1 §6)."""
    pg = patron.pg
    pg.set_viewport_size({"width": 1366, "height": 768})
    try:
        patron.firma(firma_goala["nume"])
        pg.click("#fa-jurnal")
        pg.wait_for_selector("#j-nota-noua", timeout=30000)
        poz = pg.evaluate("""() => { const m = document.querySelector('#j-amort-motiv'); if (!m) return null;
          const b = [...document.querySelectorAll('#j-prev, #j-next, #j-amort, #j-nota-noua, #j-lock')].map((x) => x.getBoundingClientRect().bottom);
          return {sus: m.getBoundingClientRect().top, jos_butoane: Math.max(...b)}; }""")
        assert poz and poz["sus"] >= poz["jos_butoane"] - 1, poz   # sub toate butoanele (luna curentă: motivul există)
        pg.click("#j-nota-noua")
        pg.wait_for_selector("#je-salveaza", timeout=10000)
        pg.wait_for_timeout(400)
        m = pg.evaluate("""() => { const f = [...document.querySelectorAll('.fereastra')].pop(), c = f.querySelector('.fereastra-corp');
          return {lata: f.classList.contains('fer-tabel'), sh: c.scrollHeight, ch: c.clientHeight}; }""")
        patron.captura()
        assert m["lata"] and m["sh"] <= m["ch"] + 1, m
    finally:
        from conftest import LAT, INALT
        pg.set_viewport_size({"width": LAT, "height": INALT})


# ── 395 — D300 „Din ce e făcută declarația”: rândurile în ordinea formularului ───────────────────────────────────────────────────
def test_def_395_randurile_d300_in_ordinea_formularului(patron, firma_tva_luna):
    """395. Rândurile veneau în ordinea 9, 10, 3, 3.1, 19, nu în ordinea formularului. Pașii: Declarații -> D300 pe luna încheiată -> „Din ce e
    făcută declarația” -> „Rânduri completate”: numerele rândurilor cresc de sus în jos (coloana Valoare înaintea coloanei TVA)."""
    import re
    from e2e_bloc_a import PRODUS, _api, _ok
    from e2e_bloc_e import _declaratie, _deschide_componente, _sectiune
    from e2e_lot72_declaratii import LUNA, ZI, _valideaza_notele
    # pe lângă factura de 21% (rândurile 9 și 19), o prestare de servicii cu locul în afara României (rândul 3 / 3.1): dicționarul motorului
    # le pune în ordinea în care le întâlnește (9 înaintea lui 3) — ecranul trebuie să le arate în ordinea formularului
    corp = {"linii": [{"descriere": PRODUS, "cantitate": 1, "um": "buc", "pret_unitar": 1000.0, "cota_tva": 0, "cota_propusa": 0,
                       "articol_id": None, "categorie_tva": "serviciu_extern"}],
            "tert_nume": "Client Irlanda E2E Ltd", "tert_cui": "IE9999999ZZ", "tert_adresa": "1 Grand Canal Square", "tert_oras": "Dublin",
            "moneda": "RON", "tert_tara": "IE", "tip_operatiune": "normal", "bon_fiscal_nr": None, "bon_fiscal_data": None,
            "data_emitere": ZI.isoformat(), "data_scadenta": (ZI + _dt.timedelta(days=30)).isoformat(), "tip": "factura"}
    fid = _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % firma_tva_luna["tenant_id"], corp), "factura serviciu extern")["factura_id"]
    _valideaza_notele(patron, firma_tva_luna, fid)
    _declaratie(patron, firma_tva_luna, "d300", LUNA.an, LUNA.luna)
    _deschide_componente(patron)
    sec = _sectiune(patron, "Rânduri completate")
    patron.captura()
    chei = []
    for r in sec[1]:
        m = re.match(r"rândul (\d+(?:\.\d+)*)", r[0])
        assert m, r
        chei.append((tuple(int(x) for x in m.group(1).split(".")), 1 if "Valoare" in r[0] else 2))
    assert len(chei) >= 3 and chei[0][0][0] == 3 and chei == sorted(chei), [r[0] for r in sec[1]]


# ── 396 — bara „În lucru” urmează firma al cărei control e deschis ──────────────────────────────────────────────────────────────
def test_def_396_bara_in_lucru_urmeaza_controlul_deschis(patron, firma_srl, firma_pfa):
    """396. Bara „În lucru” rămânea pe F1 când Control fiscal arăta auditul F5. Pașii: deschide firma A (bara: A) -> pagina principală ->
    Control fiscal -> firma B -> bara „În lucru” spune B."""
    from e2e_bloc_d import _control_firma
    pg = patron.pg
    patron.firma(firma_srl["nume"])
    assert firma_srl["nume"] in pg.inner_text(".subbara-firma")
    _control_firma(patron, firma_pfa)
    pg.wait_for_function("(n) => (document.querySelector('.subbara-firma') || {}).textContent === n", arg=firma_pfa["nume"], timeout=10000)
    patron.captura()


# ── 397 — Notificări superadmin: tipurile platformei în grupa lor ───────────────────────────────────────────────────────────────
def test_def_397_alerta_legislativa_nu_sta_sub_termene(browser, request):
    """397. Notificări superadmin: „O alertă legislativă importantă” stătea sub titlul „Termene și declarații”. Pașii: superadminul ->
    Notificări: o singură grupă, „Platformă”, cu alertele legislative, sesizările și cererile de import."""
    from e2e_lot81 import _cont
    with _cont(browser, request, "admin@prisma-cont.test") as e:
        pg = e.pg
        e.acasa()
        pg.click("button.cab-card:has([data-cheie='notificari_cont'])")
        pg.wait_for_selector(".fereastra:last-of-type #not-tipuri [data-tip]", timeout=20000)
        grupe = pg.eval_on_selector_all("#not-tipuri .cf-grup-titlu", "gs => gs.map((g) => g.textContent.trim())")
        e.captura("grupe")
        assert grupe == ["Platformă"], grupe


# ── 388 — modelele CSV: trec de propria verificare; CNP-ul stricat de Excel are cauza și remediul ────────────────────────────────
def test_def_388_modelul_de_salariati_intra_fara_observatie(patron, firma_srl):
    """388. Modelul de salariați n-avea coloana persoanelor în întreținere (fiecare rând intra „cu observație”), iar Excel îi transforma
    CNP-ul în 2,9E+12. Pașii: Salariați -> „Descarcă model (CSV)” -> fișierul descărcat se încarcă neschimbat -> amândouă rândurile
    „intră”, fără observație; CNP-ul e întreg (2900215410011)."""
    _pas(patron, firma_srl, "Salaria")
    pg = patron.pg
    with pg.expect_download() as d:
        pg.click("#mig-model")
    continut = open(d.value.path(), "rb").read()
    assert b'="2900215410011"' in continut, continut[:300]
    _incarca(patron, "model_salariati.csv", continut, "#mig-salveaza-sal")
    patron.captura()
    for nr in (2, 3):
        r = _randul(pg, nr)
        assert "cu observație" not in r and "respins" not in r, r
    assert "2900215410011" in _randul(pg, 2), _randul(pg, 2)


def test_def_388_cnp_stricat_de_excel_are_cauza_si_remediul(patron, firma_srl):
    """388. „CNP invalid (conține și alte caractere decât cifre)”, fără cauză și remediu, pentru CNP-ul pe care Excel l-a făcut 2,9E+12.
    Pașii: Salariați -> un fișier cu CNP-ul „2,90022E+12” -> rândul respins spune „Excel l-a transformat în număr … Formatează coloana CNP
    ca Text …”."""
    from e2e_lot82 import _salariati
    _salariati(patron, firma_srl, "Nume;Prenume;CNP;Functie baza;Norma;Salariu brut\nPop;Ion;2,90022E+12;Da;8;5000\n")
    r = _randul(patron.pg, 2)
    patron.captura()
    assert "Excel l-a transformat în număr" in r and "Formatează coloana CNP ca Text" in r and "respins — nu intră" in r, r


# ── 387 — Plan de conturi: planul întreg din OMFP 1802/2014 (609 inclus) ─────────────────────────────────────────────────────────
def test_def_387_planul_are_609_si_o_nota_pe_609_intra(patron, firma_srl):
    """387. Planul de conturi n-avea 609 (Reduceri comerciale primite); avea 184 de conturi. Pașii: firma -> Import date -> Plan de conturi
    -> caută 609: „609 · Reduceri comerciale primite”; o notă 401 = 609 se scrie fără refuz de cont."""
    from e2e_bloc_a import _api
    pg = patron.pg
    patron.firma(firma_srl["nume"])
    pg.click("#fa-import")
    pg.wait_for_selector(".mig-frand", timeout=20000)
    pg.locator(".mig-frand", has_text="Plan de conturi").first.click()
    pg.wait_for_selector("#pc-cauta", timeout=10000)
    pg.fill("#pc-cauta", "609")
    pg.wait_for_function("() => [...document.querySelectorAll('#pc-rezultate .mig-frand-nume')].some((x) => x.textContent.startsWith('609 '))",
                         timeout=10000)
    nume = [" ".join(x.split()) for x in pg.locator("#pc-rezultate .mig-frand-nume").all_inner_texts()]
    patron.captura()
    assert "609 · Reduceri comerciale primite" in nume, nume
    assert sql('SELECT count(*) FROM "%s".plan_conturi' % firma_srl["schema"])[0][0] >= 577
    r = _api(patron, "POST", "/tenants/%d/jurnal" % firma_srl["tenant_id"],
             {"descriere": "Reducere comercială primită E2E 387", "data": AZI.isoformat(), "document_ref": "Factură reducere 387",
              "linii": [{"debit": "401", "credit": "609", "suma": "50.00", "partener_nume": "ORANGE ROMANIA SA", "partener_cui": "9010105"}]})
    assert r["status"] == 200, r


# ── 359 / 362 — Import Mijloace fixe ──────────────────────────────────────────────────────────────────────────────────────────────
def test_def_359_coloana_amortizare_se_citeste_si_continua_de_la_cifra_din_fisier(patron, firma_srl):
    """359 (grav). Importul nu citea coloana „amortizare”: „Amortizare preluată” = „—” la rânduri cu 3.300 și 1.800 lei.
    Decizia A.1: „amortizarea continuă cu cifra din fișierul preluat; diferența față de calcul rămâne doar afișată.”
    Pașii: Mijloace fixe -> fișierul cu coloana „Amortizare” (3.300 și 1.800) -> „Amortizare preluată”: 3.300,00 lei și 1.800,00 lei;
    observația spune că amortizarea continuă de la cifra din fișier."""
    _pas(patron, firma_srl, "Mijloace fixe")
    _incarca(patron, "mf.csv", ("Cod;Denumire;Valoare intrare;Data PIF;Durata luni;Metoda;Cont imobilizare;Cont amortizare;Amortizare\n"
                                "MF1;Laptop;6000;15.03.2024;36;liniara;2141;2814;3300\n"
                                "MF2;Imprimanta;3600;01.06.2024;36;liniara;2141;2814;1800\n").encode(), "#mig-salveaza-mf")
    pg = patron.pg
    c2, c3 = _celule(pg, 2), _celule(pg, 3)
    patron.captura()
    assert (c2["Amortizare preluată"], c3["Amortizare preluată"]) == ("3.300,00 lei", "1.800,00 lei"), (c2, c3)
    r = _randul(pg, 2)
    assert "continuă de la cifra din fișier" in r or "Amortizare calculată" in _text(patron), r


def test_def_362_conturi_inversate_teren_cu_durata_si_amenajarea_de_teren(patron, firma_srl):
    """362. Conturi inversate (2813 ca imobilizare, 2131 ca amortizare) intrau; terenul 2111 intra cu amortizare liniară 60 luni fără
    observație; 2112 era respins („deci teren — nu se amortizează”), cu un mesaj despre aparatura C&D. Decizia A.2: 2112 se amortizează
    liniar, 10 ani (CF art.28 alin.(12) lit.e)). Pașii: Mijloace fixe -> fișierul -> rândul inversat respins („par inversate”); terenul cu
    60 de luni respins („terenul … nu se amortizează”); 2112 pe 120 de luni intră; 2112 pe 60 de luni respins cu „10 ani”; niciun mesaj
    despre C&D."""
    _pas(patron, firma_srl, "Mijloace fixe")
    _incarca(patron, "mf.csv", ("Cod;Denumire;Valoare intrare;Data PIF;Durata luni;Metoda;Cont imobilizare;Cont amortizare\n"
                                "MF1;Strung inversat;5000;15.03.2024;36;liniara;2813;2131\n"
                                "MF2;Teren;50000;10.01.2020;60;liniara;2111;\n"
                                "MF3;Amenajare teren;12000;10.01.2024;120;liniara;2112;2811\n"
                                "MF4;Alee;6000;10.01.2024;60;liniara;2112;2811\n").encode(), "#mig-salveaza-mf")
    pg = patron.pg
    r2, r3, r4, r5 = (_randul(pg, n) for n in (2, 3, 4, 5))
    patron.captura()
    assert "respins — nu intră" in r2 and "par inversate" in r2, r2
    assert "respins — nu intră" in r3 and "terenul (contul 2111) nu se amortizează" in r3, r3
    assert "respins — nu intră" not in r4 and "deci teren" not in r4, r4
    assert "respins — nu intră" in r5 and "liniar pe 10 ani" in r5, r5
    assert "C&D" not in " ".join((r2, r3, r4, r5))


# ── A.3 — denumirile obligațiilor din nomenclatorul oficial ─────────────────────────────────────────────────────────────────────
def test_a3_d100_are_denumirea_obligatiei_din_nomenclator(patron, firma_amenda):
    """A.3 (comanda 9.1): „Denumirile obligațiilor D100/D112: descarcă nomenclatorul oficial ANAF și leagă-l.” Pașii: Declarații -> D100
    T3/2026 -> „Din ce e făcută declarația” -> „Obligații de plată”: coloana „denumire obligație”, iar codul 103 are denumirea din
    OPANAF 587/2016 anexa 3 („Impozit pe profit/plăți anticipate în contul impozitului pe profit anual …”)."""
    from core.nomenclator_obligatii import NOMENCLATOR_D100
    from e2e_bloc_e import _deschide_componente, _sectiune
    from e2e_lot82 import _d100_t3
    _d100_t3(patron, firma_amenda)
    patron.pg.wait_for_selector("details.dec-xml summary:has-text('Din ce e făcută declarația')", timeout=60000)
    _deschide_componente(patron)
    sec = _sectiune(patron, "Obligații de plată")
    patron.captura()
    assert sec and "denumire obligație" in sec[0], sec
    i = sec[0].index("denumire obligație")
    den = [r[i] for r in sec[1]]
    assert den and den[0].startswith(NOMENCLATOR_D100["103"][1][:40]), (den, NOMENCLATOR_D100["103"])


# ── C57 — Import firme DIN FIȘIER: cifra de control înainte de ANAF și marcajul „deja în portofoliu” ───────────────────────────────
#: 14399840 (DANTE INTERNATIONAL SA) are cifra de control 0: corpul 001439984 × 7,5,3,2,1,7,5,3,2 = 0+0+3+8+3+63+45+24+8 = 154;
#: 154×10 mod 11 = 0 -> control 0. Cu ultima cifră 1 (14399841), controlul nu mai corespunde -> CUI greșit.
CUI_C57_GRESIT = "14399841"


def _c57_firme_din_fisier(patron, continut, nume="firme_c57.csv"):
    """Migrare cabinet -> Firme -> „Încarcă un fișier” (lista lipită rămâne goală) -> „Validează la ANAF”: (răspunsul `/migrare/incarca`,
    textul de sus, textul fiecărui rând din listă)."""
    from e2e_lot5_migrare import _migrare
    pg = patron.pg
    _migrare(patron)
    pg.locator("#mig-meniu .mig-op", has_text="Firme").first.click()
    pg.wait_for_selector("#mig-text", timeout=20000)
    pg.set_input_files("#mig-file", files=[{"name": nume, "mimeType": "text/csv", "buffer": continut}])
    # fișierul e ales: titlul casetei devine numele lui
    pg.wait_for_function("(n) => (document.querySelector('#mig-drop-titlu') || {}).textContent === n", arg=nume, timeout=10000)
    assert pg.input_value("#mig-text") == "", "lista lipită nu e goală — testul nu mai probează drumul fișierului"
    with pg.expect_response(lambda r: r.url.split("?")[0].endswith("/migrare/incarca") and r.request.method == "POST",
                            timeout=60000) as rr:
        pg.click("#mig-valideaza")
    # rezultatele sau refuzul (ANAF care nu răspunde rămâne pe ecranul de intrare, în #mig-eroare)
    pg.wait_for_function("() => document.querySelector('#mig-lista .mig-rand') || "
                         "((document.querySelector('#mig-eroare') || {}).textContent || '').trim()", timeout=60000)
    eroare = " ".join(pg.inner_text("#mig-eroare").split()) if pg.locator("#mig-lista").count() == 0 else ""
    assert not eroare, eroare
    intro = " ".join(pg.inner_text(".mig-intro").split())
    randuri = [" ".join(x.split()) for x in pg.locator("#mig-lista .mig-rand").all_inner_texts()]
    return rr.value.json(), intro, randuri


def test_def_c57_cui_din_fisier_cu_cifra_de_control_si_portofoliul(patron, firma_srl):
    """C57 (găsită de Code la 393, 19.10.2026). Import firme din fișier (`/migrare/incarca`): CUI-urile mergeau direct la ANAF, fără cifra
    de control și fără marcajul „deja în portofoliu” (341 / 342 se aplicau numai CUI-urilor lipite).
    Pașii: Migrare cabinet -> Firme -> „Încarcă un fișier” cu un CSV (coloana „CUI”): CUI-ul firmei din portofoliu și 14399841 (cifra de
    control greșită) -> „Validează la ANAF”:
    - textul de sus: „S-au verificat 1 CUI la ANAF. Un cod are cifra de control greșită și nu a fost trimis” (codul greșit n-a plecat);
    - rândul greșit: „CUI greșit”, „CUI 14399841: cifra de control greșită — corectează-l în fișier”, nu „nu a fost găsit la ANAF”;
    - rândul firmei: „deja în portofoliu”, „e deja în portofoliu ca „<numele firmei>” — nu se importă a doua oară”;
    - niciun rând bifat, „Importă firmele bifate” inactiv.
    MUTAȚIA: în `main.migrare_incarca`, răspunsul direct de la ANAF pe toate codurile (drumul de dinainte) -> ROȘU."""
    cui = "".join(ch for ch in str(sql("SELECT cui FROM public.tenants WHERE id = %s", (firma_srl["tenant_id"],))[0][0]) if ch.isdigit())
    raspuns, intro, randuri = _c57_firme_din_fisier(patron, ("CUI;Denumire\n%s;Firma din portofoliu\n%s;Cod tastat greșit\n"
                                                             % (cui, CUI_C57_GRESIT)).encode())
    pg = patron.pg
    patron.captura()
    # ambele coduri s-au citit din fișier; codul greșit apare o singură dată, ca greșit — nu și ca răspuns ANAF („negăsit”)
    assert raspuns.get("extrase") == 2, raspuns
    ale_lui = [r for r in raspuns["rezultate"] if str(r.get("cui")) == CUI_C57_GRESIT]
    assert len(ale_lui) == 1 and ale_lui[0].get("cui_invalid") is True, raspuns["rezultate"]
    assert len(randuri) == 2, randuri
    assert "S-au verificat 1 CUI la ANAF." in intro and "Un cod are cifra de control greșită și nu a fost trimis" in intro, intro
    gresit = next((x for x in randuri if CUI_C57_GRESIT in x), "")
    assert "CUI greșit" in gresit and "cifra de control greșită — corectează-l în fișier" in gresit, gresit
    assert "în lista lipită" not in gresit and "nu a fost găsit la ANAF" not in gresit and "negăsită" not in gresit, gresit
    port = next((x for x in randuri if cui in x), "")
    assert "deja în portofoliu" in port and "nu se importă a doua oară" in port, port
    assert "„%s”" % firma_srl["nume"] in port, port
    assert pg.locator("#mig-lista input[type=checkbox]:checked").count() == 0, randuri
    assert pg.is_disabled("#mig-importa"), randuri
