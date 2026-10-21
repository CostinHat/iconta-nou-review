# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.2 (Costin 21.10.2026, verbatim în DECIZII), punctele 1 și 6 — declarațiile: 383 (perioada neîncheiată se refuză la
generare) și 436 (declarația care știe că cifra ei nu cuprinde note nevalidate nu se depune până la validare; lunile încheiate fără
amortizare generată se spun). Pașii contabilului pe aplicația din index, pe baza de TEST, pe firme NOI de test (`firma_noua`)."""
import calendar
import datetime as _dt

import pytest

from conftest import firma_noua, sql
from e2e_lot91 import firma_tva_luna  # noqa: F401 — fixtura: firmă nouă plătitoare de TVA lunar, o factură din luna încheiată, nota validată

AZI = _dt.date.today()


# ── 383 — perioada neîncheiată se refuză la generare ────────────────────────────────────────────────────────────────────────────────────
def test_def_383_d300_pe_luna_in_curs_se_refuza_la_generare(patron, firma_tva_luna):
    """383 (grav). „la F1, alegând manual luna octombrie, D300 pe 10/2026 se generează pe 20.10 și «Pune în De depus» e oferit. O declarație
    pe o perioadă neîncheiată se refuză la generare, cu motivul scris, la toate declarațiile.”
    Pașii: Declarații -> D300 -> luna curentă, aleasă manual -> „Continuă”: pasul 2 nu generează; spune „Perioada LL/AAAA nu s-a încheiat:
    declarația se generează și se depune după <ultima zi a lunii> …”; nu există „Trimite în coadă”. Cererea directă de intrare în coadă e
    refuzată cu același motiv și nu lasă nimic în coadă."""
    from conftest import alege_perioada, alege_tipul
    from e2e_bloc_a import _api
    from e2e_bloc_e import _card
    pg = patron.pg
    _card(patron, firma_tva_luna, "declaratii", "#dec-tip")
    alege_tipul(pg, "d300")
    alege_perioada(pg, AZI.year, luna=AZI.month)
    pg.click("#dec-continua")
    pg.wait_for_selector(".dec-eroare, #dec-trimite", timeout=90000)
    t = " ".join(patron.fereastra().split())
    patron.captura()
    per = "%02d/%d" % (AZI.month, AZI.year)
    sfarsit = _dt.date(AZI.year, AZI.month, calendar.monthrange(AZI.year, AZI.month)[1]).strftime("%d.%m.%Y")
    motiv = ("Perioada %s nu s-a încheiat: declarația se generează și se depune după %s, când toate operațiunile perioadei sunt "
             "înregistrate." % (per, sfarsit))
    assert motiv in " ".join(pg.inner_text(".fereastra:last-of-type .dec-eroare").split()), t
    assert pg.locator("#dec-trimite, #dec-gol-da").count() == 0, "«Trimite în coadă» oferit pe o perioadă neîncheiată"
    peste = sql("SELECT COALESCE(max(id), 0) FROM public.declaratii_coada")[0][0]
    r = _api(patron, "POST", "/coada", {"tenant_id": firma_tva_luna["tenant_id"], "tip": "d300", "an": AZI.year, "luna": AZI.month})
    assert r["status"] == 422 and motiv in str(r["json"]), r
    assert sql("SELECT count(*) FROM public.declaratii_coada WHERE id > %s AND tenant_id = %s", (peste, firma_tva_luna["tenant_id"]))[0][0] == 0


# ── 436 — notele nevalidate opresc depunerea; lunile fără amortizare se spun ────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_amortizare(patron):
    """Cazul F2 refăcut pe o firmă NOUĂ pe impozit pe profit: vânzări 10.000 lei pe 15.01.2026 (validate); un mijloc fix de 12.000 lei / 60
    de luni pus în funcțiune pe 15.12.2025 (200 lei/lună din 01/2026); amortizarea 01–07/2026 scrisă în Registrul jurnal și NEVALIDATĂ,
    08–09/2026 negenerată."""
    from e2e_bloc_a import _api, _ok, pregateste_firma
    from e2e_bloc_e import _nota
    for f in firma_noua():
        pregateste_firma(patron, f)
        _ok(_api(patron, "POST", "/tenants/%d/vector" % f["tenant_id"],
                 {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": "trimestrial", "operatiuni_ic": False,
                  "inreg_art317": False, "tva_data_inceput": "2026-01-01"}), "vector profit")
        _nota(f, "2026-01-15", [{"debit": "5311", "credit": "704", "suma": 10000}], "Vânzări ianuarie E2E", valideaza=True)
        sql('INSERT INTO "%s".mijloace_fixe (cod,denumire,cont_imobilizare,cont_amortizare,valoare,dnf_luni,data_pif,metoda) '
            "VALUES ('MF-436','Laptop E2E','2131','2813',12000,60,'2025-12-15','liniara')" % f["schema"])
        f["ciorne"] = [_nota(f, "2026-%02d-28" % luna, [{"debit": "6811", "credit": "2813", "suma": 200}], "Amortizare %02d/2026 E2E" % luna,
                             document_ref="Amortizare %02d/2026" % luna) for luna in range(1, 8)]
        yield f


def test_def_436_d100_cu_note_nevalidate_nu_se_pune_in_de_depus(patron, firma_amortizare):
    """436 (grav). „D100 pe T3/2026 avertizează că amortizarea 01–07/2026 (1.400 lei) e nevalidată [...], dar «Pune în De depus» rămâne
    oferit. Decizie: când declarația știe că are cifra greșită din note nevalidate, depunerea se blochează până la validare, cu motivul
    lângă buton [...]. În plus, 08 și 09/2026 sunt încheiate, dar fără amortizare generată, iar D100 pe T3 nu semnalează.”
    Pașii: Declarații -> D100 T3/2026 -> pasul 2: avertismentele spun amortizarea 01–07 nevalidată ȘI 08–09 neînregistrată; „Trimite în
    coadă” e vizibil, dar inactiv, iar imediat sub el: „Declarația nu se depune până la validarea notelor: cifra ei nu cuprinde 7 note
    nevalidate din perioada ei — …”, cu câte un buton „Deschide nota …”. Cererea directă de intrare în coadă e refuzată la fel. După
    validarea celor 7 note, aceeași generare oferă din nou butonul, activ."""
    from e2e_bloc_a import _api
    from e2e_lot82 import _d100_t3
    pg = patron.pg
    t = _d100_t3(patron, firma_amortizare)
    patron.captura()
    assert "Amortizarea pe 01–07/2026 (contul 2813, 1.400,00 lei) e generată, dar nevalidată: D100 pe T3/2026 se calculează fără ea" in t, t
    assert "Amortizarea pe 08–09/2026 (contul 2813, 400,00 lei) e neînregistrată: D100 pe T3/2026 se calculează fără ea" in t, t
    assert pg.is_disabled("#dec-trimite"), "«Trimite în coadă» activ cu note nevalidate"
    motiv = " ".join(pg.inner_text("#dec-blocaj").split())
    assert motiv.startswith("Declarația nu se depune până la validarea notelor: cifra ei nu cuprinde 7 note nevalidate din perioada ei — "
                            "nota din 28.01.2026 — Amortizare 01/2026, 200,00 lei;"), motiv
    assert pg.locator("#dec-blocaj .coada-note-refuz button").count() == 7
    # motivul stă lângă buton: în aceeași bară fixă, imediat după rândul butonului
    assert pg.evaluate("() => document.querySelector('#dec-trimite').closest('.bara-fixa').contains(document.querySelector('#dec-blocaj'))")
    r = _api(patron, "POST", "/coada", {"tenant_id": firma_amortizare["tenant_id"], "tip": "d100", "an": 2026, "trim": 3})
    assert r["status"] == 422 and "cifra ei nu cuprinde 7 note nevalidate" in str(r["json"]), r
    # după validare: butonul revine activ (calibrarea gărzii)
    sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = ANY(%%s)' % firma_amortizare["schema"], (firma_amortizare["ciorne"],))
    _d100_t3(patron, firma_amortizare)
    assert pg.is_enabled("#dec-trimite") and pg.locator("#dec-blocaj").count() == 0
    patron.captura("dupa_validare")
