# -*- coding: utf-8 -*-
"""Parcursul lotului 17.5-S (poziții Pilot deschise pe ecran), cu contul administratorului (dovada.71507), la 1366×768, ceas înghețat 03.11.2026:
pagina principală (implicit), «De validat», Parteneri › fișa partenerului, clopoțelul, Facturi › Scadențar, Salariați › stat de plată (F5), Stocuri › «Mișcări, fișe de magazie»,
Control fiscal pe F2 (semnalul D205) și Emite factură pe F1 și pe FISCALOS ICONTA. Pe fiecare pas se judecă texte. Nu salvează, nu depune și nu adaugă nimic.
Un clic sau o așteptare care eșuează ridică eroarea și oprește parcursul (pe commitul de bază elementele există, iar aserțiunile a. pică). Importă numai biblioteca standard și verifica_pas."""
import os
import subprocess
import sys

import verifica_pas as VP

TOP = ".fereastra-overlay:not(.fundal) "
F1, F2, F5, FISCALOS = "F1 Comert Stoc", "F2 Profit Amortizare", "F5", "FISCALOS"


# ---- martorii (aceiași ca în e2e_pilot_17_5_S.py): baza restaurată n-are nicio notă în coada de validare (a.1, a.4 n-ar avea ce arăta), iar FISCALOS n-a emis
# niciodată și «Emite factură» îi deschide «Configurare emitere» în loc de formular (a.10, a.11 n-ar ajunge la card). Se pun înaintea pașilor și se scot în `finally`.
# Parcursul importă numai biblioteca standard: scrierea în baza de TEST se face într-un proces fiu (python-ul lansatorului, cu mediul din ~/.iconta/test.env).
_MARTORI = r"""
import json, os, sys
sys.path.insert(0, os.environ["ICONTA_RAD"])
from core import coada_api, db
db.init_pool()
ASISTENT, SCHEMA, FISCALOS, SERIE, DESC = "dovada.71508@sesiuneab.test", "tenant_9049", "FISCALOS", "MARTOR17S-", "Martor 17.5-S: nota pregătită de asistent"
def sql(q, p=()):
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute(q, p)
        r = cur.fetchall() if cur.description else None
        c.commit()
    return r
def schema_fiscalos():
    return sql("SELECT schema_name FROM public.tenants WHERE nume ILIKE %s ORDER BY id LIMIT 1", (FISCALOS + "%",))[0][0]
def scoate(peste):
    if peste:
        sql("DELETE FROM public.declaratii_coada WHERE id > %s AND fel = 'nota' AND creat_de = (SELECT id::text FROM public.users WHERE email = %s)", (int(peste), ASISTENT))
    for (nid,) in sql("SELECT id FROM %s.inregistrari WHERE descriere = %%s" % SCHEMA, (DESC,)) or []:
        sql("DELETE FROM public.declaratii_coada WHERE fel = 'nota' AND perioada = %s", ("nota-%d" % nid,))
        sql("DELETE FROM %s.inregistrari WHERE id = %%s" % SCHEMA, (nid,))
    sql('UPDATE "%s".firma_profil SET serie_factura = NULL, urmator_numar_factura = 1, numerotare_configurata = false WHERE serie_factura = %%s' % schema_fiscalos(), (SERIE,))
if sys.argv[1] == "pune":
    scoate(None)
    uid = sql("SELECT id FROM public.users WHERE email = %s", (ASISTENT,))[0][0]
    tid, cab = sql("SELECT id, accounting_firm_id FROM public.tenants WHERE schema_name = %s", (SCHEMA,))[0]
    peste = sql("SELECT COALESCE(max(id), 0) FROM public.declaratii_coada")[0][0]
    nid = sql("INSERT INTO %s.inregistrari (data, descriere, sursa, status, creat_de_id) VALUES ('2026-11-02', %%s, 'manual', 'ciorna', %%s) RETURNING id" % SCHEMA, (DESC, uid))[0][0]
    sql("INSERT INTO %s.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, '5311', '7588', 10.00)" % SCHEMA, (nid,))
    with db.get_conn(SCHEMA) as c:
        coada_api.pune_notele_in_coada(c, cab, tid, uid)
        c.commit()
    assert sql("SELECT 1 FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' AND stare = 'la_senior' AND perioada = %s", (tid, "nota-%d" % nid)), "martorul nu a intrat în coadă"
    sql('UPDATE "%s".firma_profil SET serie_factura = %%s, urmator_numar_factura = 1, numerotare_configurata = true WHERE COALESCE(serie_factura, %%s) = %%s AND numerotare_configurata = false' % schema_fiscalos(), (SERIE, '', ''))
    assert sql('SELECT 1 FROM "%s".firma_profil WHERE serie_factura = %%s' % schema_fiscalos(), (SERIE,)), "FISCALOS nu e în starea așteptată (numerotare neconfigurată)"
    print(peste)
else:
    scoate(sys.argv[2] if len(sys.argv) > 2 else None)
"""


def _mediu_test():
    env = dict(os.environ)
    for ln in open(os.path.expanduser("~/.iconta/test.env"), encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1)
            env[k] = v.strip().strip("'\"")
    env.setdefault("ICONTA_RAD", os.getcwd())
    return env


def _martori(*argumente):
    r = subprocess.run([sys.executable, "-c", _MARTORI, *argumente], env=_mediu_test(), capture_output=True, text=True, cwd=os.environ.get("ICONTA_RAD") or os.getcwd())
    if r.returncode:
        raise RuntimeError("martorii: " + (r.stdout + r.stderr)[-400:])
    return r.stdout.strip()


def card(cheie):
    return "button.cab-card:has([data-cheie='%s'])" % cheie


def acasa(pg):
    """Pagina principală proaspătă (goto): memoria ferestrei deschise se șterge întâi; se așteaptă cardurile și sintezele lor."""
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(pg.evaluate("location.origin") + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
    try:
        pg.wait_for_function("() => ![...document.querySelectorAll('.cab-card-sinteza')].some((e) => e.textContent.includes('se încarcă'))", timeout=20000)
    except Exception:   # noqa: BLE001 — contoarele întârzie: pasul se judecă pe ce s-a desenat
        pass
    pg.wait_for_timeout(800)


def firma(pg, nume):
    """Pagina principală › Firme › Firme existente › firma al cărei nume conține `nume`, cu grupurile ferestrei ei deschise."""
    acasa(pg)
    pg.click(card("firme"), timeout=10000)
    pg.wait_for_selector("#opt-existente", timeout=20000)
    pg.click("#opt-existente")
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)
    pg.locator("#firme-lista button.firme-rand", has_text=nume).first.click()
    pg.wait_for_selector("#fa-facturi", timeout=20000)
    pg.evaluate("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .firme-grup-btn[aria-expanded=\"false\"]').forEach((b) => b.click())")
    pg.wait_for_timeout(400)


def intra(pg, id_card, asteapta):
    """Clic pe cardul `id_card` din fereastra firmei și așteptarea ecranului (dacă nu apare, parcursul se oprește)."""
    pg.click(TOP + "#" + id_card, timeout=10000)
    pg.wait_for_selector(asteapta, state="attached", timeout=60000)
    pg.wait_for_timeout(800)


def la_semnale(pg):
    """v2: aduce în ecran semnalele declarațiilor «nu se poate verifica» (rândurile cu D205) din Control fiscal."""
    pg.evaluate("() => { const e = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .cf-decl')].find((x) => x.textContent.includes('D205')); if (e) e.scrollIntoView({block: 'center'}); }")
    pg.wait_for_timeout(500)


def ruleaza(pagina, ctx):
    peste = _martori("pune")
    try:
        _pasi(pagina, ctx)
    finally:
        _martori("scoate", peste)


def _pasi(pagina, ctx):
    pg = pagina

    def pas(nume):
        pg.wait_for_timeout(700)
        rez, v = VP.verifica_pagina(pg, ctx.lot, nume, ctx.parcurgere, ctx.verificator, ctx.pasi_json, ctx.csv)
        print("[parcurs] pasul %s: %s %s" % (nume, v, rez))

    acasa(pg)
    pas("implicit")                 # f.1: cardul «Control fiscal»

    # S01 (X04): De validat
    pg.click(card("validat"), timeout=10000)
    pg.wait_for_selector("#val-note", state="attached", timeout=40000)
    pas("validat")                  # f.2 (tabelul de note), a.1 («Pregătit de»)

    # S03 (640.1): Parteneri › fișa partenerului DANTE
    firma(pg, F1)
    intra(pg, "fa-parteneri", "#pt-rezumat")
    pas("parteneri")                # f.3
    pg.locator(TOP + "tr", has_text="DANTE").locator(".pt-deschide").first.click(timeout=10000)
    pg.wait_for_timeout(2500)
    pas("fisa")                     # a.2, a.3

    # S04 (563): clopoțelul
    acasa(pg)
    pg.click("#nav-clopot", timeout=10000)
    pg.wait_for_selector("#nav-clopot-panou", timeout=10000)
    pg.wait_for_timeout(1500)
    pas("clopot")                   # a.4

    # S05 (738): Facturi › Scadențar
    firma(pg, F1)
    intra(pg, "fa-facturi", "#fac-scadentar")
    pg.click(TOP + "#fac-scadentar", timeout=10000)
    pg.wait_for_selector("#sc-lista", state="attached", timeout=30000)
    pg.wait_for_timeout(1500)
    pas("scadentar")                # f.4, a.5

    # S06 (752): Salariați › stat de plată, F5, luna cu excedentul de diurnă (10/2026)
    firma(pg, F5)
    intra(pg, "fa-salariati", "#sp-tabel")
    for _ in range(4):
        if any(v in pg.inner_text(TOP + "#sp-tabel") for v in ("885,00", "4.815,34", "5.700,34")):
            break
        pg.click(TOP + "#sp-prev", timeout=10000)
        pg.wait_for_timeout(1500)
    pas("stat")                     # f.5, a.6, a.7

    # S02 (Mișcări, fișe de magazie)
    firma(pg, F1)
    intra(pg, "fa-stocuri", "#cv-toggle")
    pg.click(TOP + "#cv-toggle", timeout=10000)
    pg.wait_for_timeout(2500)
    pas("miscari")                  # a.8

    # S09 (749): Control fiscal pe F2
    firma(pg, F2)
    intra(pg, "fa-control", "#cf-incrucisat")
    pg.wait_for_timeout(2500)
    la_semnale(pg)
    pas("control")                  # f.6, a.9

    # S13: Emite factură pe FISCALOS ICONTA (firmă nouă)
    firma(pg, FISCALOS)
    intra(pg, "fa-facturi", "#fac-emite")
    pg.click(TOP + "#fac-emite", timeout=10000)
    pg.wait_for_selector("#em-cui", state="attached", timeout=30000)
    pg.wait_for_timeout(1500)
    pas("emitere")                  # f.7, a.10

    # S13 (b): Date firmă deschisă din cardul de emitere
    pg.locator(TOP + "button", has_text="Deschide Date firmă").first.click(timeout=10000)
    pg.wait_for_timeout(2500)
    pg.click(TOP + "button[data-fila='tva']", timeout=10000)   # v2: fila «TVA și declarații», cu câmpul «Regim fiscal»
    pg.wait_for_timeout(1000)
    pas("datefirma")                # a.11
