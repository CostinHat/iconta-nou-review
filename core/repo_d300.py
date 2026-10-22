# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d300.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d300.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

from core.nomenclator_status_factura import clauza_tip_document as _doc_fiscal
from core.facturi import clauza_nu_din_bon as _nu_din_bon   # [decizia A 02.10] definiția unică


def select_inregistrari(cur, _STATUS_FINAL, inceput, sfarsit):
    # [lotul 10, 428, decizia „Construiesc acum”] decontarea facturii = și compensarea ei (HG 1/2016 pct.26 alin.(9): „se consideră că
    # furnizorul/prestatorul a încasat, respectiv beneficiarul a plătit [...] la data la care se sting total sau parțial datoriile”);
    # nota compensării (401 = 4111) stinge ambele facturi — legătura e `compensari_api.legaturi`, sursa unică, nu `i.factura_id`
    from core import compensari_api as _cz
    cur.execute("SELECT lg.factura_id AS fid, f.directie AS directie, SUM(l.suma) AS settled, "
                # [A2, 17.09.2026] Clasificarea partenerului CALATORESTE cu decontarea: fara ea,
                # `_pull_incasare` intorcea doar {directie, decontari}, iar `calcul_d300` trata orice
                # operatiune la incasare drept RO interna (tara lipsa -> 'RO'). Consecinta: livrarile/
                # achizitiile IC, exportul si serviciile la incasare cadeau la rd.26/rd.9 in loc de
                # rd.1/rd.5/rd.7/rd.14. Cheile sunt PER FACTURA (GROUP BY pe factura le pastreaza unice).
                "COALESCE(f.tert_tara, 'RO') AS tert_tara, f.tert_cui AS cui, "
                "f.axa_ic AS axa_ic, f.categorie_331 AS categorie_331, "
                # [lotul 10, 428] furnizorul in sistem (art.297 alin.(2)) desparte in D394 tvaDedAI de tvaDed
                "COALESCE(f.furnizor_tva_incasare, false) AS furnizor_tva_incasare "
                "FROM inregistrari i JOIN " + _cz.legaturi() + " lg ON lg.inregistrare_id = i.id "
                "JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                "JOIN facturi f ON f.id = lg.factura_id "
                "WHERE i.status = 'validata' "
                "AND COALESCE(f.taxare_inversa, false) = false "  # art.282(6)/297(3): taxare inversa = regim general, nu la incasare
                "AND " + _STATUS_FINAL + " "  # [B1] doar facturi contabilizabile
                "AND " + _doc_fiscal("f") + " "   # [DECIZII 46] proforma/avizul nu sunt documente fiscale
                "AND " + _nu_din_bon("f") + " "   # [decizia A 02.10] factura din bon: vânzarea e în raportul Z
                "AND i.data >= %s AND i.data < %s "
                "AND ((f.directie = 'emisa' AND l.cont_credit = '4111') "
                "  OR (f.directie = 'primita' AND l.cont_debit = '401')) "
                "GROUP BY lg.factura_id, f.directie, f.tert_tara, f.tert_cui, f.axa_ic, f.categorie_331, f.furnizor_tva_incasare",
                (inceput, sfarsit))
    return cur.fetchall()


def select_facturi(cur, fids):
    cur.execute("SELECT f.id AS fid, f.total, f.tva, l.cantitate, l.pret_unitar, l.cota_tva, "
                "l.valoare_neta "   # [lotul 11, C82] BT-131 de pe factura importată: baza liniei la alocarea decontării pe cote
                "FROM facturi f LEFT JOIN factura_linii l ON l.factura_id = f.id "
                "WHERE f.id = ANY(%s)", (fids,))


def select_rapoarte_z(cur, surse, inceput, sfarsit):
    """[lot 19 pct.4b] Rapoartele Z VALIDATE din fereastra, cu defalcarea lor pe cote. LEFT JOIN: un raport fără
    defalcare iese cu cota NULL — apelantul îl numește (nu îl sare tăcut)."""
    cur.execute("SELECT i.id AS id, i.numar AS numar, i.data AS data, z.cota AS cota, z.baza AS baza, z.tva AS tva "
                "FROM inregistrari i LEFT JOIN rapoarte_z_cote z ON z.inregistrare_id = i.id "
                "WHERE i.status = 'validata' AND i.sursa = ANY(%s) AND i.data >= %s AND i.data < %s "
                "ORDER BY i.id, z.cota", (list(surse), inceput, sfarsit))
    return cur.fetchall()


def select_chitante_cu_cota(cur, inceput, sfarsit):
    """[D394 Î2] Chitanțele de VÂNZARE fără factură (cu cotă), neanulate, din fereastră — livrări taxabile pe cotă."""
    cur.execute("SELECT id, serie, numar, data, suma, cota_tva FROM chitante "
                "WHERE factura_id IS NULL AND cota_tva IS NOT NULL AND NOT anulata AND data >= %s AND data < %s "
                "ORDER BY id", (inceput, sfarsit))
    return cur.fetchall()


def select_note_tva_fara_factura(cur, inceput, sfarsit):
    """[lotul 11, C76] Liniile de TVA (4426 / 4427 / 4428, pe debit sau pe credit) ale notelor VALIDATE din fereastră care NU vin dintr-o
    factură (`factura_id` NULL) și nu sunt nota unei compensări (aceea decontează două facturi — `compensari`). Pe ele decide D300 ce
    intră (ajustările de taxă) și ce spune că nu intră. Rândurile: id, data, sursa, descriere, eticheta, debit, credit, suma, din_chitanta
    (nota unei chitanțe de vânzare fără factură — declarată din `chitante`, `select_chitante_cu_cota`)."""
    cur.execute("SELECT i.id AS id, i.data AS data, i.sursa AS sursa, i.descriere AS descriere, eticheta_nota(i.id) AS eticheta, "
                "l.cont_debit AS debit, l.cont_credit AS credit, l.suma AS suma, "
                "EXISTS (SELECT 1 FROM chitante ch WHERE ch.inregistrare_id = i.id AND ch.factura_id IS NULL AND ch.cota_tva IS NOT NULL "
                "        AND NOT ch.anulata) AS din_chitanta "
                "FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                "WHERE i.status = 'validata' AND i.factura_id IS NULL AND i.data >= %s AND i.data < %s "
                "AND NOT EXISTS (SELECT 1 FROM compensari cz WHERE cz.inregistrare_id = i.id) "
                "AND (split_part(l.cont_debit, '.', 1) IN ('4426', '4427', '4428') "
                "  OR split_part(l.cont_credit, '.', 1) IN ('4426', '4427', '4428')) "
                "ORDER BY i.data, i.id, l.id", (inceput, sfarsit))
    return cur.fetchall()


def select_firma_profil(cur):
    cur.execute("SELECT nume, cui, adresa, oras, judet, caen, banca, iban, tip_decont, pro_rata, "
                "COALESCE(tva_la_incasare, false) AS tva_la_incasare, "
                "declarant_nume, declarant_prenume, declarant_functie "
                "FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def select_facturi_4(cur, _STATUS_FINAL, _EXIG_NORMAL, inceput, sfarsit):
    cur.execute("SELECT f.id, f.directie, f.total, f.tva, "
                "f.tip, f.serie, f.numar, f.data_emitere, "   # [258] factura numită în avertismente cum o vede omul, nu prin id
                "f.moneda, f.curs_bnr, f.total_lei, f.tva_lei, "  # [A1] conversia in lei (core.sume_lei)
                "COALESCE(f.taxare_inversa, false) AS taxare_inversa, f.categorie_331, "
                "COALESCE(f.tert_tara, 'RO') AS tert_tara, f.tert_cui, "
                "f.axa_ic, "   # [R186] axa bunuri/servicii, INGHETATA pe document

                # [F125] LUNA de exigibilitate (aceeasi expresie pe care se face fereastra): cheia
                # reclasificarii D390 e per-luna (acelasi partener poate fi reclasificat diferit in luni
                # diferite - trimestru). Fara ea D300 nu poate potrivi factura pe luna corecta.
                + _EXIG_NORMAL + " AS exig, "
                "l.cantitate, l.pret_unitar, l.cota_tva, "
                "l.valoare_neta, "   # [lotul 11, C82] BT-131 de pe factura importată, exact
                "COALESCE(l.destinatie_tva, 'taxabil') AS destinatie_tva, "  # [A12 art.300] per linie
                "l.categorie_tva "   # [274b] categoria liniei cu 0%: rândul din decont (core/categorii_tva)
                "FROM facturi f LEFT JOIN factura_linii l ON l.factura_id = f.id "
                # [B1] fereastra pe EXIGIBILITATE (COALESCE(data_faptului_generator, data_emitere); avans->emitere)
                "WHERE " + _EXIG_NORMAL + " >= %s AND " + _EXIG_NORMAL + " < %s "
                # [B1] doar facturi contabilizabile (exclude ciorna/de_preluat/descarcata/anulata/stornata)
                "AND " + _STATUS_FINAL + " "
                # [lotul 10, 428] deducerea amanata (art.297 alin.2-3) si facturile emise in sistem nu se mai scot aici: regimul e al
                # facturii la data ei, decis in `d300.pull` (`tva_incasare.regim`) — o singura definitie
                # [DECIZII 46, 15.09.2026] Proforma NU e document fiscal: TVA-ul nu e exigibil pe ea.
                # Aici se rupea — filtrul era pe dată și pe status, iar proforma are status declarabil.
                "AND " + _doc_fiscal("f") + " "
                # [decizia A 02.10] factura emisă pe baza bonului fiscal: vânzarea e deja în raportul Z (rd.9/10 din
                # rapoarte_z_cote) — numărată o singură dată; definiția în core.facturi
                "AND " + _nu_din_bon("f") + " "
                "ORDER BY f.id", (inceput, sfarsit))
    return cur.fetchall()


def select_facturi_5(cur, _nsf, _inc, _sf):
    # [DECIZII 46] Si numaratoarea de diagnostic: o proforma nu e un document „de contabilizat".
    cur.execute("SELECT count(*) FROM facturi WHERE data_emitere >= %s AND data_emitere < %s "
                "AND " + _nsf.clauza_sql(None) + " AND " + _doc_fiscal(None) + " AND " + _nu_din_bon(None),
                (_inc.isoformat(), _sf.isoformat()))
    return cur.fetchone()
