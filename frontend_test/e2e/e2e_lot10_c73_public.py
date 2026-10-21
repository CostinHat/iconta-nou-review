# -*- coding: utf-8 -*-
"""Lotul 10, deficiența C73 pe schema `public` (U3): cheia unică a platformei dublată ajunge la contabil ca refuz numit, nu ca 500.

Drumul vizibil fără cursă: „Setări cont” -> „Date cabinet”, CUI-ul unui ALT cabinet înregistrat pe iConta.eu (`accounting_firms_cui_key`,
unic pe toată platforma). Înainte: 500 al bazei („Eroare la salvare.”). După: „CUI-ul … e deja înregistrat pe iConta.eu pentru alt cabinet.
Verifică cifrele.”, lângă câmpul CUI, fără numele cabinetului care îl are (schema `public` e a tuturor cabinetelor).
Celelalte drumuri ale clasei (adresa de email luată la cursă, numărul depunerii, așteptarea declarației, anunțurile automate) sunt curse:
nu se pot reface din browser — le probează `core/test_lot10_c73_chei_unice.py` pe Postgres.
CUI-ul celuilalt cabinet: 99907310 — sintetic, cifra de control verificată cu algoritmul din CLAUDE.md."""
from conftest import sql
from e2e_lot72_cont import deschide_setari_panou

CUI_ALT_CABINET = "99907310"
NUME_ALT_CABINET = "Cabinet Strain E2E C73"


def test_def_c73_cui_cabinet_al_altuia_refuzat_numit(patron):
    """C73 (U3). Pașii: un alt cabinet are CUI-ul 99907310 -> Setări cont -> Date cabinet -> CUI 99907310 -> „Salvează datele cabinetului”:
    refuzul numit lângă câmp, fără numele celuilalt cabinet; CUI-ul cabinetului rămâne cel de dinainte. Garda fixturii prinde orice 5xx.
    MUTAȚIA: `refuza_dublura` scos din `auth_api.actualizeaza_cabinet` -> ROȘU (500)."""
    [(firm_id, cui_vechi)] = sql("SELECT accounting_firm_id, (SELECT cui FROM public.accounting_firms a WHERE a.id = u.accounting_firm_id) "
                                 "FROM public.users u WHERE email = 'patron@prisma-cont.test'")
    sql("DELETE FROM public.accounting_firms WHERE nume = %s AND NOT EXISTS (SELECT 1 FROM public.users WHERE accounting_firm_id = "
        "accounting_firms.id)", (NUME_ALT_CABINET,))
    sql("INSERT INTO public.accounting_firms (nume, cui) VALUES (%s, %s)", (NUME_ALT_CABINET, CUI_ALT_CABINET))
    try:
        deschide_setari_panou(patron, "Date cabinet", "#set-cab-cui")
        pg = patron.pg
        pg.fill(".fereastra:last-of-type #set-cab-cui", CUI_ALT_CABINET)
        pg.click(".fereastra:last-of-type #set-salveaza-cabinet")
        pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #set-msg-cabinet') || {}).innerText "
                             "&& !document.querySelector('.fereastra:last-of-type #set-msg-cabinet').innerText.includes('Se salvează')",
                             timeout=20000)
        patron.captura()
        text = patron.fereastra()
        # ce citește contabilul: CUI-ul refuzat, numit, și ce are de făcut
        assert "CUI-ul 99907310 e deja înregistrat pe iConta.eu pentru alt cabinet. Verifică cifrele." in text, text
        assert NUME_ALT_CABINET not in text and "accounting_firms" not in text and "duplicate key" not in text, text
        assert "Date cabinet salvate." not in text, text
        assert sql("SELECT cui FROM public.accounting_firms WHERE id = %s", (firm_id,)) == [(cui_vechi,)]
    finally:
        sql("DELETE FROM public.accounting_firms WHERE nume = %s AND cui = %s", (NUME_ALT_CABINET, CUI_ALT_CABINET))
        sql("UPDATE public.accounting_firms SET cui = %s WHERE id = %s", (cui_vechi, firm_id))
