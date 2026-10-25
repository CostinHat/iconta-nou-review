# -*- coding: utf-8 -*-
"""core/factura_primita_dublura.py — CHEIA unei facturi de furnizor și refuzul celei de-a doua introduceri (lotul 12, C73.1). PUR, LEAF.

Comanda Costin 12.2 pct.6, verbatim (DECIZII „Comanda 12.2”): „C73.1 (grav) — Aceeași factură de furnizor (CUI 14399840, nr. LIC-73,
1.000 + 210) introdusă de două ori la «Achiziție necorporală» pe F1 a generat două note 205 = 404 / 4426 = 404, fără niciun avertisment:
imobilizarea și TVA-ul deductibil se dublează. Dublura (același furnizor + același număr de factură) se oprește pe toate căile prin care
intră o factură de furnizor.”

CHEIA (o factură de furnizor e una singură): furnizorul + numărul ei.
  * furnizorul = codul fiscal în forma păstrată (`cui_forma.stocare`: fără spații, fără „RO” în fața cifrelor — XML-ul aduce
    „RO14399840”, fișa „14399840”); fără cod fiscal, denumirea (literele și cifrele, fără spații și semne);
  * numărul = seria lipită de număr, numai litere și cifre, majuscule, fără zerourile din fața unui grup de cifre: „LIC-73”, „LIC 73”,
    „lic/073” și seria „LIC” + numărul „73” (factura de mână, cu seria separat) sunt aceeași factură; XML-ul n-are seria separat (BT-1 o
    cuprinde). Data NU intră în cheie: aceeași factură introdusă cu altă dată tot aceeași factură e (cheia veche a facturii de mână,
    `repo_main.select_facturi_3`, cerea și data — o a doua introducere cu altă zi trecea).

CE RĂMÂNE PERMIS (cazurile legitime): furnizori diferiți cu același număr (cheia cuprinde furnizorul); stornarea (factura cu semnul minus
nu se ciocnește de cea pozitivă — semnul intră în comparație); borderoul și avizul (au cheia lor, `facturi_borderou_numar_an_uniq`);
documentul anulat (nu mai e în evidență). Factura deschisă PRELUATĂ la migrare (`tip = 'preluata'`) INTRĂ în comparație: soldul ei e deja
în balanța de deschidere, deci aceeași factură introdusă din nou ar dubla datoria.

UN SINGUR PUNCT: `repo_facturi.primite_cu_aceeasi_cheie` (citirea, sub lacătul tranzacției pe cheie, ca două salvări simultane să nu
treacă amândouă), chemat de cele trei căi prin care se naște o factură (`core/scan_cai_factura.py`): `facturi_api.creeaza_factura`
(Operațiuni — necorporală, taxare inversă, intracomunitară —, `POST /facturi`), `uc_comun._factura_din_parsat` (XML / SPV, factura de
mână, importul de fișiere) și `solduri_parteneri_api._scrie_documente` (preluarea soldurilor). Garda:
`core/test_lot12_fact2_c73_dublura.py::test_cele_trei_cai_cheama_verificarea`.

Temei: OMFP 2634/2015 anexa 1 pct.58 lit.c — „fiecare dată înregistrată în contabilitate trebuie să se regăsească în conținutul unui
document”; un document înregistrat de două ori dă de două ori cheltuiala / imobilizarea și TVA-ul de dedus, pe un singur document.
"""
import re

from core import cui_forma as _cf

#: tot ce nu e literă sau cifră ASCII (aceeași clasă în Python și în SQL: interval pe puncte de cod, nu pe colaționare)
_NEALFANUMERIC = re.compile(r"[^A-Za-z0-9]")
#: zerourile din fața unui grup de cifre („073” -> „73”; „0” singur rămâne)
_ZEROURI = re.compile(r"(^|[^0-9])0+([0-9])")

#: aceeași normalizare a NUMĂRULUI, în SQL (`{serie}`, `{numar}` = coloanele)
SQL_NUMAR = ("regexp_replace(upper(regexp_replace(COALESCE({serie}, '') || COALESCE({numar}, ''), '[^A-Za-z0-9]', '', 'g')), "
             "'(^|[^0-9])0+([0-9])', '\\1\\2', 'g')")
#: aceeași normalizare a DENUMIRII furnizorului fără cod fiscal, în SQL
SQL_NUME = "upper(regexp_replace(COALESCE({nume}, ''), '[^A-Za-z0-9]', '', 'g'))"
#: codul fiscal, în forma păstrată (`cui_forma.SQL`)
SQL_CUI = _cf.SQL



def expresii_facturi():
    """(codul fiscal, denumirea, numărul) în forma cheii, ca expresii SQL pe coloanele tabelei `facturi` (`tert_cui`, `tert_nume`, `serie`,
    `numar`) — pentru citirile din `repo_facturi` (o funcție pură, fără cursor, deci locul ei e aici, lângă formele SQL)."""
    return SQL_CUI.format(c="tert_cui"), SQL_NUME.format(nume="tert_nume"), SQL_NUMAR.format(serie="serie", numar="numar")


#: tipurile de document care sunt FACTURI de furnizor în comparație (borderoul și avizul au cheia lor)
TIPURI = ("factura", "preluata")


def numar(serie, nr):
    """Numărul facturii în forma cheii: „LIC” + „73” -> „LIC73”; „lic-073” -> „LIC73”; gol -> ""."""
    t = _NEALFANUMERIC.sub("", "%s%s" % (serie or "", nr if nr is not None else "")).upper()
    return _ZEROURI.sub(r"\1\2", t)


def furnizor(cui, nume):
    """(este_cod_fiscal, cheia furnizorului): codul fiscal în forma păstrată; fără el, denumirea normalizată; ("", "") fără niciunul."""
    c = _cf.stocare(cui)
    if c:
        return True, c
    return False, _NEALFANUMERIC.sub("", str(nume or "")).upper()


def _una(x):
    from core.pdf_util import bani, data_ro, serie_nr
    t = "factura %s din %s, %s" % (serie_nr(x.get("serie"), x.get("numar")), data_ro(x.get("data_emitere")),
                                   bani(x.get("total"), (x.get("moneda") or "RON").replace("RON", "lei")))
    if x.get("tip") == "preluata":
        t += " (factură deschisă preluată la migrare, cu soldurile inițiale)"
    return t


def mesaj(existente, sfat=None):
    """Refuzul pentru contabil: factura existentă (toate, dacă sunt deja mai multe), numită ca în „Istoric facturi”."""
    from core.pdf_util import serie_nr
    x0 = existente[0]
    cine = (x0.get("tert_nume") or "").strip() or _cf.stocare(x0.get("tert_cui")) or "același furnizor"
    unde = (" de %d ori" % len(existente) if len(existente) > 1 else "") + ": " + "; ".join(_una(x) for x in existente)
    return ("Factura %s de la %s e deja înregistrată%s. O factură de furnizor intră o singură dată în evidență — a doua ar dubla "
            "cheltuiala (sau imobilizarea, marfa) și TVA-ul de dedus. O găsești în „Istoric facturi”; dacă documentul din evidență e "
            "greșit, corectează-l pe acela.%s" % (serie_nr(x0.get("serie"), x0.get("numar")), cine, unde, (" " + sfat) if sfat else ""))


def refuz(existente, sfat=None, camp=None):
    """`chei_unice.CheieDublata` (un `ValueError`: apelanții care traduc `ValueError` în refuz numit îl arată la fel), cu facturile
    existente în `existent` (id-urile lor)."""
    from core import chei_unice as _chei
    return _chei.CheieDublata(mesaj(existente, sfat), valoare=numar(existente[0].get("serie"), existente[0].get("numar")),
                              existent={"facturi": [x.get("id") for x in existente]}, camp=camp)
