# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.2 pct.2 (verbatim în DECIZII „Comanda 12.2”), pachetul `fact2` — 443.1.

„Mesajul după emitere scrie numărul lipit de serie: «Factura F62 emisă» (F6), «Factura F1A14 emisă» (F1). Seria și numărul se afișează ca
în Istoric («F1A nr. 14»).” Clasa: orice mesaj care numește o factură. Aici, partea de server: răspunsul stornării poartă seria (ecranul o
afișează cu `numarCuSerie`), refuzurile stornării numesc factura „F1A nr. 8”, refuzul transformării numește factura (nu id-ul ei intern),
emailul facturii spune „Factura F1A nr. 8”. Temei: CF art.319 alin.(20) lit.a — „numărul de ordine, în baza uneia sau a mai multor serii”.
Schemă efemeră din template, în tranzacție anulată (fixtura lui 417)."""
import ast
import io
import os

import pytest

from core import facturi_api
from core.test_417_storno_trimitere import _db_ok, _storno, conn  # noqa: F401 — fixtura

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@DB
def test_def_443_1_stornarea_intoarce_seria_iar_refuzul_numeste_factura_ca_in_istoric(conn):
    """Stornarea întoarce `serie` (ecranul: „Storno creat: F1A nr. 1”); a doua stornare se refuză numind factura „F1A nr. 8” și stornarea
    ei „F1A nr. 1”, nu „F1A8” / „F1A1”. MUTAȚIE: `r["serie"]` scos din `storneaza` -> pică."""
    r, s, _d = _storno(conn)
    assert (s["serie"], s["numar"]) == ("F1A", "F1A1"), s
    with pytest.raises(ValueError) as e:
        facturi_api.storneaza(conn, r["factura_id"])
    assert str(e.value).startswith("Factura F1A nr. 8 e deja stornată integral (prin F1A nr. 1)"), str(e.value)
    with pytest.raises(ValueError) as e:
        facturi_api.storneaza(conn, s["factura_id"])
    assert str(e.value).startswith("Factura F1A nr. 1 e ea însăși o stornare"), str(e.value)


def _id_in_text(fn):
    """F-string-urile funcției care interpolează `r[1]` — `transformat_in_id`, id-ul intern al facturii — direct în text."""
    return [v for n in ast.walk(fn) if isinstance(n, ast.JoinedStr) for v in n.values
            if isinstance(v, ast.FormattedValue) and isinstance(v.value, ast.Subscript) and isinstance(v.value.value, ast.Name)
            and v.value.value.id == "r" and getattr(v.value.slice, "value", None) == 1]


def test_def_443_1_transformarea_nu_numeste_factura_prin_id():
    """Refuzul „documentul a fost deja transformat” numea factura prin id-ul ei intern („factura nr. 57”); acum prin eticheta din Istoric
    (`eticheta_nota.factura`: „Factură F1A nr. 12 din …”). MUTAȚIE: f-string-ul vechi pus la loc -> pică."""
    arb = ast.parse(io.open(os.path.join(RAD, "core", "uc_tenants.py"), encoding="utf-8").read())
    fn = next(n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef) and n.name == "proforma_transforma")
    assert _id_in_text(fn) == []
    apeluri = {c.func.attr for c in ast.walk(fn) if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)}
    assert apeluri >= {"factura"}   # `_et_tr.factura(cur, schema, r[1])`
