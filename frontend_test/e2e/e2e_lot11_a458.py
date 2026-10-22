# -*- coding: utf-8 -*-
"""Lotul 11, comanda Costin 11.3 pct.6 (verbatim în DECIZII), subagentul A458 — deficiența 458: „în Erori — echipa: text suprapus peste
nume; regenerările automate ale aplicației apar ca greșeli ale administratorului; numerele de respingeri nu se adună cu rândurile.”

Pașii contabilului, pe aplicația din index, pe baza de TEST, pe firma nouă a fișierului (`firma_e2e`):
  1. contabilul-șef emite o factură, îi validează nota și trimite D300 pe luna încheiată în coadă; apoi „Generează din nou” de DOUĂ ori
     (ruta butonului `.val-regenereaza`, `POST /coada/{id}/regenereaza`) — două înlocuiri ale declarației lui;
  2. îi dă asistentei firma (ruta ecranului Asistenți, `POST /asistenti/{uid}/firme/{tid}`); asistenta („Poate pregăti”) scrie o notă în
     Registrul jurnal (`POST /tenants/{tid}/jurnal`) — intră singură în coadă; contabilul-șef o respinge cu motiv (`POST /coada/{id}/respinge`,
     ruta butonului „Respinge” din De validat);
  3. pagina principală -> Asistenți -> „Vezi erorile” -> fereastra „Erori — echipa”:
     * nicio rubrică „Înlocuită de declarația generată din nou” (generarea din nou nu e o greșeală a nimănui);
     * pe fiecare card, numărul de lângă nume („N respinse”) = Σ numerelor rândurilor lui („k×”);
     * motivul asistentei apare pe cardul ei;
     * niciun text nu se suprapune peste alt text, la 1280×720, 1366×768 și pe telefon (390×844); bulina n-are text în ea.
Date de pornire fără ecran: niciuna (tot pe rutele ecranelor). Temei: N/A — indicator intern al cabinetului (regulă de UI: DS cap.8).
"""
import re

from conftest import sql
from e2e_bloc_a import AZI, _api, _ok, emite_api, pregateste_firma
from e2e_lot72_declaratii import ZI, _curata, _in_coada, _peste, _valideaza_notele

MOTIV = "Lipsește documentul justificativ (E2E 458)"
INLOCUIRE = "Înlocuită de declarația generată din nou"

CARDURI = """() => {
  const f = [...document.querySelectorAll('.fereastra')].pop();
  return [...f.querySelectorAll('.val-card')].map((c) => ({
    nume: (c.querySelector(':scope > div:first-child > b') || {}).innerText,
    // [458] antetul are două `.tip-desc`: eticheta semaforului (înaintea numelui) și cifra respingerilor (după nume)
    semafor: (c.querySelector(':scope > div:first-child > .asi-sem + .tip-desc') || {}).innerText,
    antet: (c.querySelector(':scope > div:first-child > b + .tip-desc') || {}).innerText,
    randuri: [...c.querySelectorAll('.asi-cal-motiv')].map((r) => ({motiv: r.firstElementChild.innerText,
                                                                    nr: (r.querySelector('b') || {}).innerText}))}));
}"""


def _deschide_erori(patron):
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='asistenti'])")
    pg.wait_for_selector("#asi-vezi-erori", timeout=30000)
    pg.click("#asi-vezi-erori")
    pg.wait_for_selector(".fereastra:last-of-type .val-card .asi-cal-motiv", timeout=30000)
    pg.wait_for_timeout(300)


def test_def_458_erori_echipa_fara_regenerari_totalul_e_suma_randurilor_fara_text_suprapus(patron, asistent, firma_e2e):
    """ROȘU înainte: cardul contabilului-șef avea „Înlocuită de declarația generată din nou … 2× sistematic”; numărul de lângă nume nu
    era Σ rândurilor (rândurile numărau rânduri de coadă); „probleme” / „de urmărit” se suprapuneau peste nume. MUTAȚII:
    `mut_lot11_a458.json`."""
    from core.test_lot11_a458_erori_ecran import MASOARA, _selector_bulina
    pregateste_firma(patron, firma_e2e)
    tid = firma_e2e["tenant_id"]
    uid_a = sql("SELECT id FROM public.users WHERE email = 'asistent@prisma-cont.test'")[0][0]
    peste = _peste()
    # contul comun de asistent pornește rularea cu drepturile lui de bază (`conftest._drepturi_initiale`: pe baza de test, și „Poate
    # valida”); nota unui validator NU intră în coadă (`uc_coada.note_in_coada`), deci pasul 2 cere asistenta numai cu „Poate pregăti”
    # — ca la 279 (e2e_lot6), dreptul se comută pe durata testului și se pune la loc
    era_valida = sql("SELECT poate_valida FROM public.users WHERE id = %s", (uid_a,))[0][0]
    sql("UPDATE public.users SET poate_valida = false WHERE id = %s", (uid_a,))
    try:
        # 1. D300 în coadă, apoi „Generează din nou” de două ori (ruta butonului)
        f1 = emite_api(patron, firma_e2e, data_emitere=ZI)
        _valideaza_notele(patron, firma_e2e, f1["factura_id"])
        r = _in_coada(patron, firma_e2e)
        assert r["status"] == 200, r
        cid = r["json"]["coada_id"]
        for _ in range(2):
            cid = _ok(_api(patron, "POST", "/coada/%d/regenereaza" % cid, {}), "Generează din nou")["coada_id"]
        inlocuite = sql("SELECT count(*) FROM public.declaratii_coada WHERE tenant_id = %s AND id > %s AND stare = 'respinsa' "
                        "AND motiv_respingere LIKE %s", (tid, peste, INLOCUIRE + "%"))[0][0]
        assert inlocuite == 2, inlocuite                                   # cele două ieșiri din coadă, pe drumul aplicației
        # 2. firma dată asistentei; nota ei intră în coadă; contabilul-șef o respinge cu motiv
        _ok(_api(patron, "POST", "/asistenti/%d/firme/%d" % (uid_a, tid), {}), "alocarea firmei")
        nota = _ok(_api(asistent, "POST", "/tenants/%d/jurnal" % tid, {
            "descriere": "Ridicare numerar 458", "data": AZI.replace(day=2).isoformat(), "document_ref": "CEC 458",
            "linii": [{"debit": "5311", "credit": "5121", "suma": "10.00"}]}), "nota asistentei")
        cn = sql("SELECT id FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' AND stare = 'la_senior' AND perioada = %s",
                 (tid, "nota-%d" % nota["id"]))
        assert cn, "nota asistentei n-a intrat în coadă"
        _ok(_api(patron, "POST", "/coada/%d/respinge" % cn[0][0], {"motiv": MOTIV}), "respingerea")
        # 3. Asistenți -> „Vezi erorile”
        _deschide_erori(patron)
        pg = patron.pg
        carduri = pg.evaluate(CARDURI)
        patron.captura("erori_echipa")
        assert carduri, carduri
        assert not [c for c in carduri for x in c["randuri"] if x["motiv"].startswith(INLOCUIRE)], carduri   # nu e greșeala nimănui
        for c in carduri:
            m = re.match(r"(\d+) respins[ăe] · \d+%", c["antet"] or "")
            assert m, c
            assert int(m.group(1)) == sum(int(x["nr"].rstrip("×")) for x in c["randuri"]), c   # „nu se adună cu rândurile”
        ale_ei = [c for c in carduri if any(x["motiv"] == MOTIV for x in c["randuri"])]
        assert len(ale_ei) == 1 and "Asistent" in (ale_ei[0]["nume"] or ""), carduri
        sel = _selector_bulina()
        for lat, inalt in ((1280, 720), (1366, 768), (390, 844)):
            pg.set_viewport_size({"width": lat, "height": inalt})
            pg.wait_for_timeout(300)
            o = pg.evaluate(MASOARA, sel)
            patron.captura("erori_echipa_%dx%d" % (lat, inalt))
            assert not o["supr"], (lat, o["supr"])                        # „text suprapus peste nume”
            assert not o["bulineCuText"], (lat, o["bulineCuText"])
            assert o["cozi_rupte"] == 0 and not o["lateral"] and not o["pagina_lat"], (lat, o)
    finally:
        _curata(firma_e2e, peste)
        sql("DELETE FROM public.user_tenants WHERE user_id = %s AND tenant_id = %s", (uid_a, tid))
        sql("UPDATE public.users SET poate_valida = %s WHERE id = %s", (era_valida, uid_a))
