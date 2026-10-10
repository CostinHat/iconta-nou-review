# -*- coding: utf-8 -*-
"""GARD — regulile de fond a, c, d, e, f în BAZĂ (comanda Costin 09.10.2026, „Retestul plasei” pct.6, verbatim în DECIZII;
`core/migrare_reguli_fond_2.py`). Ca `core/test_reguli_fond.py`: schema EFEMERĂ din `tenant_template.sql` (deci și oglinda e
probată), direct în SQL — regula ține oricare ar fi drumul. Contraproba lângă fiecare refuz. Perioade în 2099."""
import io

from core import migrare_reguli_fond_2 as rf2
from core.test_reguli_fond import _merge, _refuz, cur   # noqa: F401 — fixtura schemei efemere

TID = 990899   # tenant sintetic pentru tabelul comun al declarațiilor
#: începutul exact al refuzului R6 (temeiul inclus: CF art.330 alin.(1))
R6 = "REGULA_CONTABILA: Factura %s e emisă, deci nu se șterge: se corectează prin factură de stornare (CF art.330 alin.(1))."


def _factura(cur, status="emisa", tip="factura", directie="emisa", numar="R6-1", data="2099-10-05"):
    return _merge(cur, "INSERT INTO facturi (numar, serie, data_emitere, total, tva, directie, status, tip) "
                       "VALUES (%s, 'PR', %s, 121, 21, %s, %s, %s) RETURNING id", (numar, data, directie, status, tip))


def test_oglinda_din_sablon_e_cea_generata_de_migrare():
    """MUTAȚIE: o regulă schimbată numai în migrare -> pică."""
    t = io.open("tenant_template.sql", encoding="utf-8").read()
    i, j = t.index(rf2.MARCAJ_INCEPUT), t.index(rf2.MARCAJ_SFARSIT) + len(rf2.MARCAJ_SFARSIT)
    assert t[i:j] == rf2.sql("TENANT_PLACEHOLDER")


def test_r6_factura_emisa_nu_se_sterge(cur):
    """(a) CF art.330 alin.(1) lit.a)–b): „Corectarea informațiilor înscrise în facturi […] a) în cazul în care factura nu a fost
    transmisă către beneficiar, aceasta se anulează și se emite o nouă factură; b) […] se emite o nouă factură […] cu valorile cu
    semnul minus” — factura nu dispare. MUTAȚIE: triggerul scos -> ștergerea trece -> pică."""
    f = _factura(cur)
    cur.connection.commit()
    _refuz(cur, "DELETE FROM facturi WHERE id = %s", (f,), incepe=R6 % "PRR6-1")
    # orice stare a nomenclatorului în afară de ciornă e un document emis — și `de_preluat`, starea în care `emite_factura` produce
    # factura emisă din aplicație (prima formă a regulii o excepta, crezând-o importul nerecunoscut: greșit, prins de
    # `test_status_factura_un_loc`). MUTAȚIE: `de_preluat` adăugat în STERGIBILE -> ștergerea trece -> pică.
    from core.nomenclator_status_factura import STARI, STERGIBILE
    for k, status in enumerate(sorted(set(STARI) - set(STERGIBILE))):
        x = _factura(cur, status, "factura", "emisa", "R6-S%d" % k)
        cur.connection.commit()
        _refuz(cur, "DELETE FROM facturi WHERE id = %s", (x,), incepe=R6 % ("PRR6-S%d" % k))
    for status, tip, directie, nr in (("ciorna", "factura", "emisa", "R6-2"), ("emisa", "proforma", "emisa", "R6-4"),
                                      ("emisa", "factura", "primita", "R6-5")):
        x = _factura(cur, status, tip, directie, nr)
        _merge(cur, "DELETE FROM facturi WHERE id = %s", (x,))   # contraproba: ciorna, proforma, primita


def test_r7_declaratia_depusa_nu_se_modifica_nici_nu_se_sterge(cur):
    """(c) Declarația depusă prin iConta.eu: o corectură e o depunere nouă. Marcările (extern / contabil anterior) rămân modificabile.
    MUTAȚIE: verificarea UPDATE scoasă -> modificarea trece -> pică."""
    cur.execute(rf2.SQL_DECLARATII)   # tabelul comun: triggerul se pune în tranzacția probei și pleacă odată cu ea (ROLLBACK)
    cur.execute("SET LOCAL iconta.regula_declaratii = 'activa'")
    _merge(cur, "INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, sursa, xml) VALUES (%s, 2099, 10, 'd300', 'iconta', '<x/>')",
           (TID,))
    _merge(cur, "INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, sursa) VALUES (%s, 2099, 10, 'd112', 'extern')", (TID,))
    _refuz(cur, "UPDATE public.declaratii_depuse SET xml = '<y/>' WHERE tenant_id = %s AND tip = 'd300'", (TID,),
           incepe="REGULA_CONTABILA: Declarația D300 pe 10/2099 e depusă prin iConta.eu, deci nu se modifică: o corectură e o depunere nouă")
    _refuz(cur, "DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 'd300'", (TID,),
           incepe="REGULA_CONTABILA: Declarația D300 pe 10/2099 e depusă prin iConta.eu, deci nu se șterge: o corectură e o depunere nouă")
    _merge(cur, "UPDATE public.declaratii_depuse SET recipisa = 'R-1' WHERE tenant_id = %s AND tip = 'd300'", (TID,))   # recipisa: da
    _merge(cur, "UPDATE public.declaratii_depuse SET recipisa = 'X' WHERE tenant_id = %s AND tip = 'd112'", (TID,))
    _merge(cur, "DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND tip = 'd112'", (TID,))   # marcarea se anulează


def test_r8_stocul_nu_devine_negativ(cur):
    """(d) O ieșire nu scoate mai mult decât e în stoc; stornarea/ștergerea unei intrări nu lasă stocul negativ. MUTAȚIE: verificarea
    scoasă -> ieșirea de 15 din 10 trece -> pică."""
    a = _merge(cur, "INSERT INTO articole (denumire, um) VALUES ('Marfă R8', 'buc') RETURNING id")
    intr = _merge(cur, "INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, valoare, document) VALUES (%s, '2099-10-01', 'intrare', 10, 100, 'NIR R8') "
                       "RETURNING id", (a,))
    from core.stocuri_anulare import MARCAJ_STOC_NEGATIV                  # stornarea la respingere recunoaște refuzul după el
    _refuz(cur, "INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, valoare, document) VALUES (%s, '2099-10-02', 'iesire', 15, 150, 'FCT R8')",
           (a,), incepe="%s #%d ar deveni negativ (-5.000 după mișcarea „FCT R8”)" % (MARCAJ_STOC_NEGATIV, a))
    _merge(cur, "INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, valoare, document) VALUES (%s, '2099-10-02', 'iesire', 10, 100, 'FCT R8b')",
           (a,))                                                             # contraproba: exact cât e în stoc
    _refuz(cur, "DELETE FROM miscari_stoc WHERE id = %s", (intr,),                                 # intrarea care a fost vândută
           incepe="%s #%d ar deveni negativ (-10.000 după mișcarea „NIR R8”)" % (MARCAJ_STOC_NEGATIV, a))


def test_r9_luna_blocata_nu_primeste_facturi_stoc_casa_chitante(cur):
    """(e) Luna blocată se extinde la facturi, mișcări de stoc, casă și chitanțe. MUTAȚIE: triggerul facturilor scos -> pică."""
    a = _merge(cur, "INSERT INTO articole (denumire, um) VALUES ('Marfă R9', 'buc') RETURNING id")
    _merge(cur, "INSERT INTO perioade_blocate (an, luna) VALUES (2099, 9)")
    for sql_, args in (("INSERT INTO facturi (numar, serie, data_emitere, total, tva, directie) VALUES ('R9', 'PR', '2099-09-10', 1, 0, 'emisa')", ()),
                       ("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, valoare) VALUES (%s, '2099-09-10', 'intrare', 1, 1)", (a,)),
                       ("INSERT INTO casa_operatiuni (data, tip, categorie, suma) VALUES ('2099-09-10', 'incasare', 'alte', 1)", ()),
                       ("INSERT INTO chitante (serie, numar, data, suma) VALUES ('CH', 1, '2099-09-10', 1)", ())):
        assert _refuz(cur, sql_, args, incepe="PERIOADA_BLOCATA: luna 09/2099")
    _merge(cur, "INSERT INTO facturi (numar, serie, data_emitere, total, tva, directie) VALUES ('R9b', 'PR', '2099-10-10', 1, 0, 'emisa')")   # luna deschisă


def test_r10_chitanta_nu_se_sterge(cur):
    """(f) OMFP 2634/2015, Anexa 1 pct.15: „documentul întocmit greşit se anulează şi se păstrează sau rămâne în carnetul respectiv”.
    MUTAȚIE: triggerul scos -> ștergerea trece -> pică."""
    c = _merge(cur, "INSERT INTO chitante (serie, numar, data, suma) VALUES ('CH', 7, '2099-10-05', 50) RETURNING id")
    _refuz(cur, "DELETE FROM chitante WHERE id = %s", (c,), incepe="REGULA_CONTABILA: Chitanța CH nr. 7 e emisă, deci nu se șterge: se "
           "anulează și se păstrează (OMFP 2634/2015, Anexa 1 pct.15).")
    _merge(cur, "UPDATE chitante SET anulata = true WHERE id = %s", (c,))   # contraproba: anularea
