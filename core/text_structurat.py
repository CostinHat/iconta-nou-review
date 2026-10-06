# -*- coding: utf-8 -*-
"""core/text_structurat.py — baza subclaselor de `str` care poartă STRUCTURĂ (`Temei`, `Unde`).

[comanda Costin 07.10.2026, C1] D390 nu intra în coadă: `POST /coada` = 500. `coada_api.randuri_din_res` face
`dataclasses.asdict(res)`, care COPIAZĂ fiecare câmp; copierea unui `str` cu constructor propriu trece prin
`cls.__new__(cls, <textul>)` (protocolul implicit `__getnewargs__` al lui `str`), iar `Unde.__new__(fel, id, detaliu)` primea
textul „factura 95141537 — Comert Micro TVA SRL” drept `fel` și îl refuza. `Temei` avea același mecanism; copia ieșea corectă
doar fiindcă textul refăcut coincidea cu cel original.

REPARAȚIA, pe clasă: copierea (copy / deepcopy / pickle / `dataclasses.asdict`) reface obiectul din TEXTUL EXACT și din
ATRIBUTELE lui, fără să mai treacă prin constructorul care validează — ce s-a validat o dată nu se revalidează din altă formă.
Gard: `core/test_text_structurat.py` (orice subclasă de `str` din `core/` cu `__new__` propriu moștenește de aici și
supraviețuiește celor patru căi de copiere).
"""


def _reface(cls, text, stare):
    o = str.__new__(cls, text)
    o.__dict__.update(stare)
    return o


class TextStructurat(str):
    """Un `str` cu atribute: se compară și se afișează ca textul lui, se copiază cu tot cu atribute."""

    def __reduce__(self):
        return (_reface, (type(self), str(self), dict(self.__dict__)))

    def __reduce_ex__(self, protocol):
        return self.__reduce__()
