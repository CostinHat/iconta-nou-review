# -*- coding: utf-8 -*-
"""[lotul 11, deficiența 439 — PRIORITAR, comanda Costin 11.1 pct.5, verbatim în DECIZII „Comanda 11.1”] Balanța SAGA completă.

Verbatim: „balanța completă SAGA e respinsă, pentru că verificarea omite soldul inițial al anului. După reparare, 425 și 426 trebuie să
poată fi retestate.”

CAUZA (de ce e2e-ul lotului 10 a trecut și balanța reală nu): verificarea citea perechea „… precedente” ca „sume precedente” CU soldul
inițial al anului (forma ecranului de preluare din manualul SAGA, topic12) și cerea `precedente + rulajele lunii = total sume`. Balanța
de verificare din descrierea lui Costin are „rulaje precedente” — rulajele de la 1 ianuarie FĂRĂ soldul inițial —, iar „total sume” le
cuprinde pe toate trei: `sold inițial an + rulaje precedente + rulajele lunii = total sume`. Egalitatea veche omitea soldul inițial, deci
orice cont cu sold la 1 ianuarie pica. Fișierul de probă al lotului 10 era scris de aceeași presupunere ca și codul (sumele precedente
calculate ca `total sume − rulajele lunii`), deci testul confirma presupunerea, nu forma reală a fișierului.

REPARAȚIA: forma fiecărei perechi cumulate (cuprinde sau nu soldul inițial al anului) se stabilește din DATE, pe tot fișierul: se
încearcă întâi ce spune antetul („sume” / „total sume” = cu soldul inițial; „rulaje precedente” / „total rulaje” = fără), apoi
celelalte forme; se păstrează forma pentru care TOATE conturile verifică ecuațiile balanței:
- OMFP 2634/2015 anexa 1 pct.52: „Soldul debitor sau creditor al fiecărui cont se stabilește în funcție de rulajele debitoare și
  creditoare ale contului respectiv, ținându-se seama de soldul de la începutul anului” -> sold inițial + rulaje = sold final, pe cont;
- același pct.52: „Balanța de verificare este documentul contabil utilizat pentru verificarea înregistrării corecte în contabilitate a
  operațiunilor efectuate” — fiecare înregistrare are debit = credit, deci FIECARE coloană (pereche) are totalul debitor egal cu cel
  creditor;
- manualul SAGA C, „Preluare date contabile” (anaf_surse/saga_manual_topic12_preluare_date_contabile.txt): „Debit precedent” / „Credit
  precedent” = „rulajele cumulate (inclusiv soldurile iniţiale)” — forma „sume precedente”, care rămâne acceptată;
- manualul SAGA C, „Balante” (anaf_surse/saga_manual_topic52_balante.txt): „Înainte de generarea balanței se vor seta seriile de
  egalități” — balanța SAGA nu are o singură formă de coloane, deci forma nu se poate fixa din antet.

Balanța de probă e INVENTATĂ (nicio firmă reală): o firmă cu sold la 1 ianuarie pe 13 conturi (capital, rezultat reportat, echipamente,
amortizare, mărfuri, doi furnizori, doi clienți, TVA de plată, două conturi bancare, casa), cu vânzări, încasări, cumpărări, plăți,
descărcarea mărfii, TVA, salarii, amortizare și închiderea lunară pe 121, în forma exportului SAGA: titluri, antet pe două rânduri,
sintetice (401, 4111, 5121) urmate de analiticele lor, totaluri pe clasă și „TOTAL GENERAL”, sumele scrise „16.800,00”, Windows-1250.
"""
import contextlib
import os
import re

import pytest

from core import db as _db, import_tabel as it, solduri_api

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: (cont, denumire, sold inițial debit, sold inițial credit, rulaj debit an, rulaj credit an) — rulajele 01.01–30.09.2026 FĂRĂ soldul
#: inițial; numai analiticele (frunzele). Fiecare operație are debit = credit (verificat de `test_fixtura_echilibrata`).
FRUNZE = [
    ("1012", "Capital subscris vărsat", 0, 16800, 0, 0),
    ("117", "Rezultatul reportat", 0, 4500, 0, 0),
    ("121", "Profit şi pierdere", 0, 0, 38500, 50000),
    ("2131", "Echipamente tehnologice", 15000, 0, 0, 0),
    ("2813", "Amortizarea instalaţiilor", 0, 3000, 0, 1500),
    ("371", "Mărfuri", 2500, 0, 30000, 28000),
    ("401.00001", "Furnizor Şerban SRL", 0, 1200, 25400, 24200),
    ("401.00002", "Furnizor Ţăndărei SRL", 0, 800, 12000, 12100),
    ("4111.00001", "Client Alfa SRL", 1800, 0, 48400, 45000),
    ("4111.00002", "Client Beta SRL", 700, 0, 12100, 12800),
    ("421", "Personal - salarii datorate", 0, 0, 9000, 9000),
    ("4423", "TVA de plată", 0, 600, 4800, 4200),
    ("4426", "TVA deductibilă", 0, 0, 6300, 6300),
    ("4427", "TVA colectată", 0, 0, 10500, 10500),
    ("5121.1", "Cont curent Banca 1", 5000, 0, 45000, 41200),
    ("5121.2", "Cont curent Banca 2", 1500, 0, 12800, 12000),
    ("5311", "Casa în lei", 400, 0, 2000, 0),
    ("607", "Cheltuieli privind mărfurile", 0, 0, 28000, 28000),
    ("641", "Cheltuieli cu salariile personalului", 0, 0, 9000, 9000),
    ("6811", "Cheltuieli de exploatare privind amortizarea imobilizărilor", 0, 0, 1500, 1500),
    ("707", "Venituri din vânzarea mărfurilor", 0, 0, 50000, 50000),
]
#: sinteticele scrise de SAGA deasupra analiticelor lor, cu sumele analiticelor
SINTETICE = {"401": "Furnizori", "4111": "Clienţi", "5121": "Conturi la bănci în lei"}

#: formele coloanelor: (eticheta grupului din antet, ce scrie în ea); `si` = sold inițial an, `rp` = rulaje precedente (fără sold inițial),
#: `sp` = sume precedente (cu sold inițial), `rl` = rulajele lunii, `ts` = total sume (cu sold inițial), `tr` = total rulaje (fără)
FORME = {
    # descrierea lui Costin la 425: „solduri inițiale an, rulaje precedente, rulaje lună, total sume, solduri finale”
    "rulaje_precedente": [("Solduri iniţiale an", "si"), ("Rulaje precedente", "rp"), ("Rulaje lună", "rl"), ("Total sume", "ts")],
    # forma din manualul SAGA, ecranul de preluare: precedentele cuprind soldul inițial
    "sume_precedente": [("Solduri iniţiale an", "si"), ("Sume precedente", "sp"), ("Rulaje lună", "rl"), ("Total sume", "ts")],
    # balanța cu „total rulaje” (fără soldul inițial): sold final = sold inițial + total rulaje
    "total_rulaje": [("Solduri iniţiale an", "si"), ("Rulaje precedente", "rp"), ("Rulaje lună", "rl"), ("Total rulaje", "tr")],
    # balanța cu șase egalități: și total rulaje, și total sume
    "sase_egalitati": [("Solduri iniţiale an", "si"), ("Rulaje precedente", "rp"), ("Rulaje lună", "rl"), ("Total rulaje", "tr"),
                       ("Total sume", "ts")],
}


def _sf(si_d, si_c, r_d, r_c):
    net = si_d - si_c + r_d - r_c
    return (net, 0) if net > 0 else (0, -net)


def _valori(si_d, si_c, r_d, r_c, forma):
    rl = (r_d // 5, r_c // 5)                              # septembrie = o cincime din fiecare rulaj
    rp = (r_d - rl[0], r_c - rl[1])
    col = {"si": (si_d, si_c), "rp": rp, "sp": (si_d + rp[0], si_c + rp[1]), "rl": rl, "tr": (r_d, r_c), "ts": (si_d + r_d, si_c + r_c)}
    out = []
    for _et, g in FORME[forma]:
        out += list(col[g])
    return out + list(_sf(si_d, si_c, r_d, r_c))


def _ro(x):
    """Suma cum o scrie exportul: „16.800,00”."""
    s = "{:,.2f}".format(x)
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def randuri(forma="rulaje_precedente"):
    """Balanța de verificare analitică în forma exportului SAGA (rânduri de celule, ca la citirea unui CSV)."""
    grupuri = [et for et, _g in FORME[forma]] + ["Solduri finale"]
    sus, jos = ["Simbol cont", "Denumirea contului"], ["", ""]
    for et in grupuri:
        sus += [et, ""]
        jos += ["Debit", "Credit"]
    out = [["Balanţă de verificare analitică"], ["SC Firmă Probă Migrare SRL", "CUI: (probă)"], ["Perioada: 01.09.2026 - 30.09.2026"],
           sus, jos]
    n = 2 * len(grupuri)
    tot, clasa, cl = [0] * n, [0] * n, None
    for cont, den, *v in FRUNZE:
        c = cont[0]
        if cl is not None and c != cl:
            out.append(["Total clasa %s" % cl, ""] + [_ro(x) for x in clasa])
            clasa = [0] * n
        cl = c
        sint = next((s for s in SINTETICE if cont.startswith(s + ".")), None)
        if sint and not any(r[0] == sint for r in out):
            fiice = [f for f in FRUNZE if f[0].startswith(sint + ".")]
            sume = [sum(f[2 + i] for f in fiice) for i in range(4)]
            out.append([sint, SINTETICE[sint]] + [_ro(x) for x in _valori(*sume, forma)])
        vals = _valori(*v, forma)
        tot = [a + b for a, b in zip(tot, vals)]
        clasa = [a + b for a, b in zip(clasa, vals)]
        out.append([cont, den] + [_ro(x) for x in vals])
    out.append(["Total clasa %s" % cl, ""] + [_ro(x) for x in clasa])
    out.append(["TOTAL GENERAL", ""] + [_ro(x) for x in tot])
    return out


def fisier(forma="rulaje_precedente", rr=None):
    """Octeții CSV-ului în Windows-1250 (codarea exportului SAGA; ș / ț numai cu sedilă)."""
    text = "\n".join(";".join(str(c) for c in r) for r in (rr if rr is not None else randuri(forma)))
    return text.translate(str.maketrans("șțȘȚ", "şţŞŢ")).encode("cp1250")


def _pe_cont(d):
    return {r["cont"]: r for r in d["randuri"]}


def _sume(mesaj):
    return re.findall(r"(-?\d{1,3}(?:\.\d{3})*,\d{2}) lei", str(mesaj))


# ── fixtura însăși ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_fixtura_echilibrata_pe_fiecare_pereche_si_cu_sold_initial():
    """Fiecare pereche are debit = credit (OMFP 2634/2015 anexa 1 pct.52: balanța verifică înregistrările, debit = credit), iar soldul
    inițial e nenul pe 13 conturi — altfel proba n-ar atinge defectul (o balanță fără sold inițial trece pe orice formă)."""
    for forma in FORME:
        tot = [float(it.valoare(r, j) if isinstance(r[j], (int, float)) else solduri_api._numar(r[j])) for r in [randuri(forma)[-1]]
               for j in range(2, len(r))]
        assert all(abs(tot[i] - tot[i + 1]) < 0.005 for i in range(0, len(tot), 2)), (forma, tot)
    assert sum(1 for f in FRUNZE if f[2] or f[3]) == 13


# ── 439: citirea ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("forma", sorted(FORME))
def test_def_439_balanta_saga_cu_sold_initial_intra_pe_fiecare_forma(forma):
    """ROȘU înainte (forma „rulaje precedente”, a lui Costin): „Rândul 7 (contul 1012): sumele precedente plus rulajele lunii … nu dau
    totalul sumelor …” — egalitatea fără soldul inițial al anului. VERDE: toate formele dau ACELEAȘI solduri inițiale, rulaje și solduri
    finale, pe toate cele 21 de conturi (sinteticele 401 / 4111 / 5121 înlocuite de analiticele lor)."""
    d = solduri_api.extrage_balanta_detaliat(fisier(forma), "balanta_saga_%s.csv" % forma)
    pc = _pe_cont(d)
    assert d["rulaje"] is True and set(pc) == {f[0] for f in FRUNZE} and sorted(d["sintetice_inlocuite"]) == ["401", "4111", "5121"]
    for cont, _den, si_d, si_c, r_d, r_c in FRUNZE:
        r = pc[cont]
        # OMFP 2634/2015 anexa 1 pct.52: soldul final din rulaje „ținându-se seama de soldul de la începutul anului”
        assert (r["si_debit"], r["si_credit"], r["rulaj_debit"], r["rulaj_credit"]) == (si_d, si_c, r_d, r_c), (forma, cont, r)
        assert (r["debit"], r["credit"]) == _sf(si_d, si_c, r_d, r_c), (forma, cont, r)
    # 5121.1: sold inițial 5.000 + 45.000 − 41.200 = 8.800 debitor; 707: cifra de afaceri 50.000, sold final 0
    assert (pc["5121.1"]["debit"], pc["707"]["rulaj_credit"], pc["707"]["debit"], pc["707"]["credit"]) == (8800.0, 50000.0, 0.0, 0.0)


def test_def_439_forma_citita_e_spusa_cu_soldul_initial():
    """Ecranul spune ce s-a citit și cum: „rulajele precedente” (fără soldul inițial) vs. „sumele precedente” (cu el)."""
    d = solduri_api.extrage_balanta_detaliat(fisier("rulaje_precedente"), "b.csv")
    assert d["perechi"] == {"si": ["Solduri iniţiale an Debit", "Solduri iniţiale an Credit"],
                            "rp": ["Rulaje precedente Debit", "Rulaje precedente Credit"],
                            "rl": ["Rulaje lună Debit", "Rulaje lună Credit"], "ts": ["Total sume Debit", "Total sume Credit"]}
    assert d["forma_rulaje"] == {"rp": False, "ts": True}      # True = coloana cuprinde soldul inițial al anului


def test_def_439_antetul_care_minte_decide_datele():
    """„Sume precedente” în antet, dar valorile sunt rulajele FĂRĂ soldul inițial (alt program, aceeași etichetă): datele decid, nu
    eticheta — rulajele ies aceleași. MUTAȚIA: numai forma din antet -> refuz -> pică."""
    rr = randuri("rulaje_precedente")
    rr[3] = [c.replace("Rulaje precedente", "Sume precedente") for c in rr[3]]
    pc = _pe_cont(solduri_api.extrage_balanta_detaliat(fisier(rr=rr), "b.csv"))
    assert (pc["1012"]["si_credit"], pc["1012"]["rulaj_credit"], pc["5121.1"]["rulaj_debit"]) == (16800.0, 0.0, 45000.0)


# ── 439: refuzurile rămân, cu motivul numit ──────────────────────────────────────────────────────────────────────────────────
def _schimba(rr, cont, j, delta):
    for r in rr:
        if r[0] == cont:
            r[j] = _ro(solduri_api._numar(r[j]) + delta)
    return rr


def test_def_439_coloana_dezechilibrata_se_refuza_numita():
    """707: 100 lei în plus pe „Rulaje lună Credit”, „Total sume Credit” și soldul final creditor; 1012: 100 lei pe „Rulaje precedente
    Debit” și „Total sume Debit”, soldul final creditor cu 100 mai mic. Fiecare rând se închide (sold inițial + rulaje = sold final),
    soldurile inițiale, totalul sumelor și soldurile finale rămân egale, rulajele anului la fel — numai coloanele „Rulaje precedente” și
    „Rulaje lună” nu se mai echilibrează. Refuz cu prima pereche numită și cele două totaluri. OMFP 2634/2015 anexa 1 pct.52 (fiecare
    înregistrare are debit = credit, deci fiecare coloană). MUTAȚIA: verificarea coloanelor scoasă -> nimic altceva n-o prinde -> pică."""
    rr = randuri("rulaje_precedente")
    for j in (7, 9, 11):                 # 707: rulaje lună C, total sume C, sold final C
        _schimba(rr, "707", j, 100)
    _schimba(rr, "1012", 4, 100)         # 1012: rulaje precedente D
    _schimba(rr, "1012", 8, 100)         #       total sume D
    _schimba(rr, "1012", 11, -100)       #       sold final C
    with pytest.raises(ValueError) as e:
        solduri_api.extrage_balanta_detaliat(fisier(rr=rr), "b.csv")
    m = str(e.value)
    assert m.startswith("Coloanele „Rulaje precedente Debit” / „Rulaje precedente Credit” nu se echilibrează"), m
    assert _sume(m)[:3] == ["276.340,00", "276.240,00", "100,00"], m


def test_def_439_contul_care_nu_se_inchide_se_refuza_numit():
    """Soldul final al casei (5311) schimbat (2.400 -> 1.600), 1012 la fel cu −800, deci coloanele rămân echilibrate: niciuna din formele
    încercate nu verifică toate conturile -> refuz pe rândul și contul numite, cu cele două cifre (sold inițial + rulaje vs. sold final)."""
    rr = randuri("rulaje_precedente")
    _schimba(rr, "5311", 10, -800)
    _schimba(rr, "1012", 11, -800)
    with pytest.raises(ValueError) as e:
        solduri_api.extrage_balanta_detaliat(fisier(rr=rr), "b.csv")
    m = re.match(r"Rândul (\d+) \(contul ([\w.]+)\): ", str(e.value))
    assert m and m.group(2) == "1012" and _sume(e.value)[:2] == ["-16.800,00", "-16.000,00"], str(e.value)


def test_def_439_randul_care_se_contrazice_spune_ecuatia_cu_soldul_initial():
    """Total sume schimbat pe un singur cont (5311: +50 pe debit, sold final neschimbat): pe forma din antet, „soldul inițial al anului
    plus rulajele precedente plus rulajele lunii” nu dau totalul sumelor — mesajul numește soldul inițial (egalitatea veche îl omitea)."""
    rr = randuri("rulaje_precedente")
    _schimba(rr, "5311", 8, 50)
    _schimba(rr, "1012", 9, 50)          # coloana „Total sume” rămâne echilibrată
    with pytest.raises(ValueError) as e:
        solduri_api.extrage_balanta_detaliat(fisier(rr=rr), "b.csv")
    m = str(e.value)
    assert re.match(r"Rândul \d+ \(contul 1012\): soldul inițial al anului plus rulajele precedente plus rulajele lunii ", m), m


# ── 439 + 426: scrierea și al doilea import, pe schemă efemeră (tranzacție anulată) ─────────────────────────────────────────────
SCHEMA = "ztest_lot11_m_balanta"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import tenant_provisioning as _tp
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % SCHEMA)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, metoda_stoc) VALUES (1, 'FIRMĂ PROBĂ MIGRARE SRL', '14399840', "
                            "'cantitativ_valoric')")
            yield c
        finally:
            c.rollback()


def _uc(monkeypatch, c):
    from core import uc_tenants, uc_comun

    @contextlib.contextmanager
    def _gc(schema=None):
        yield c
    monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: SCHEMA)
    return uc_tenants


def _json(r):
    import json
    return json.loads(r.body) if hasattr(r, "body") else r


def _corp(d, data, inlocuieste=False):
    import main
    return main.SolduriIn(randuri=[main.SoldRand(**{k: v for k, v in r.items() if k in main.SoldRand.model_fields}) for r in d["randuri"]],
                          data_referinta=data, inlocuieste=inlocuieste,
                          analitic_117="1171")   # [527.1] balanța de probă are 117 fără analitic: alegerea e a contabilului


def test_def_439_426_balanta_saga_se_salveaza_si_a_doua_cere_confirmare(conn, monkeypatch):
    """Drumul ecranului: încărcarea (`solduri_incarca`) -> salvarea (`solduri_salveaza`) -> a doua balanță (altă formă, aceleași
    cifre) -> previzualizarea spune că există deja una -> salvarea fără confirmare = 409, nimic schimbat -> cu confirmare, înlocuită.
    ROȘU înainte: încărcarea întorcea 400 cu „sumele precedente plus rulajele lunii … nu dau totalul sumelor”."""
    from core import erori
    uc = _uc(monkeypatch, conn)
    p = _json(uc.solduri_incarca(1, fisier("rulaje_precedente"), "balanta_saga.csv", {"uid": 7}))
    assert p["valida"] and p["rulaje"] and len(p["randuri"]) == 21 and p["existenta"] is None, p.get("motiv")
    assert p["forma_rulaje"] == {"rp": False, "ts": True}     # ecranul spune cum s-au citit precedentele și totalul
    rez = uc.solduri_salveaza(1, _corp(p, "2026-09-30"), {"uid": 7})
    assert (rez["randuri"], rez["rulaje"]) == (21, True), rez
    with conn.cursor() as cur:
        cur.execute("SELECT si_an_debit, rulaj_an_debit, rulaj_an_credit, sold_debitor FROM solduri_initiale WHERE cont = '5121.1'")
        assert [float(x) for x in cur.fetchone()] == [5000.0, 45000.0, 41200.0, 8800.0]
    # 426: al doilea import
    p2 = _json(uc.solduri_incarca(1, fisier("total_rulaje"), "balanta_saga_2.csv", {"uid": 7}))
    assert p2["existenta"]["randuri"] == 21 and p2["avertisment_inlocuire"].startswith("Firma are deja o balanță de deschidere"), p2
    with pytest.raises(erori.Conflict):
        uc.solduri_salveaza(1, _corp(p2, "2026-09-30"), {"uid": 7})
    rez2 = uc.solduri_salveaza(1, _corp(p2, "2026-09-30", inlocuieste=True), {"uid": 7})
    assert rez2["randuri"] == 21 and rez2.get("inlocuita"), rez2
