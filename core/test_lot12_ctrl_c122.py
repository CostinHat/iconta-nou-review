# -*- coding: utf-8 -*-
"""Lotul 12, comanda 12.1, pachetul `ctrl` — deficiența C122 (găsită de pachetul `notif`): emailurile de amintire a scadenței către
clienții firmei (`core/notificari_scadenta.py`) n-aveau diacritice — subiectul și corpul spuneau „Factura X - scade in 3 zile”, „a devenit
restanta”, „restanta de 7 zile” —, data scadenței pleca ISO („2026-10-01”) și suma „1210.00 RON”. Clasa = toate textele emailului din
modul: subiectul (`_subiect`), starea (`_eticheta`), corpul (`_email_corp`). Acum: diacritice, pluralul prin `common.cate`, data și suma în
formatele aplicației (`pdf_util.data_ro` / `pdf_util.bani`, DS cap.4 / cap.7).

Temei: N/A — textul unui email (DS cap.1: diacritice complete în tot ce citește omul)."""
import datetime
import html.parser as html_parser
from decimal import Decimal

import pytest

from core import notificari_scadenta as N

F = {"numar": "F1A3", "data_scadenta": datetime.date(2099, 10, 1), "suma": Decimal("1210"), "moneda": "RON"}


@pytest.mark.parametrize("prag,stare", [(-3, "scade în 3 zile"), (-1, "scade în 1 zi"), (-20, "scade în 20 de zile"), (1, "a devenit restantă"),
                                        (7, "restantă de 7 zile")])
def test_subiectul_si_starea_au_diacritice(prag, stare):
    assert N._eticheta(prag) == stare
    assert N._subiect(F, prag) == "Factura F1A3 — " + stare


class _Corp(html_parser.HTMLParser):
    """Paragrafele emailului (textul fiecărui `<p>`) și valorile scoase în evidență (`<b>`), în ordine."""
    def __init__(self):
        super().__init__()
        self.paragrafe, self.bold, self._in = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            self.paragrafe.append("")
        self._in.append(tag)

    def handle_endtag(self, tag):
        self._in.pop()

    def handle_data(self, data):
        if "p" in self._in:
            self.paragrafe[-1] += data
        if self._in[-1:] == ["b"]:
            self.bold.append(data)


def test_corpul_are_data_si_suma_in_formatul_aplicatiei():
    html = N._email_corp("Probă SRL", F, -3)
    corp = _Corp()
    corp.feed(html)
    # pe structura emailului: valorile din `<b>` sunt câmpurile facturii, în formatele aplicației (DS cap.4 / cap.7)
    # [C158] moneda RON se scrie „lei”, ca pe ecran (`pdf_util.moneda_scrisa`, oglinda `monedaScrisa`)
    assert corp.bold == ["F1A3", "Probă SRL", "1.210,00 lei", "01.10.2099", "Probă SRL"], corp.bold
    assert corp.paragrafe[1] == ("Vă reamintim că factura F1A3 emisă de Probă SRL, în valoare de 1.210,00 lei, cu scadența 01.10.2099, "
                                 "scade în 3 zile."), corp.paragrafe
    assert "2099-10-01" not in html and "1210" not in html
