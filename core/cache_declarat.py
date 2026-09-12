# -*- coding: utf-8 -*-
"""P6 valul 2 — forma unei DECLARAȚII de cache local.

CE CERE TEXTUL CANONIC (`PLAN_HARDENING.md:704-707`, citat): *«Cache local admis, dar numai
DECLARAT»*, cu cinci lucruri scrise lângă el — **rol** (ce accelerează) · **sursa autoritativă**
(de unde se poate reface) · **motiv** (de ce e în memorie) · **invalidare** (când și cum) ·
**dovadă de reconstrucție identică** (o probă care golește cache-ul și arată că răspunsul e același).

DE CE E O STRUCTURĂ ȘI NU UN COMENTARIU. Un comentariu cu cinci rânduri ar fi „declarat" pentru un
om și invizibil pentru o gardă, iar casa cere ca o gardă să asereze pe STRUCTURĂ, nu pe text
(clichet 50). Cu un `namedtuple`, întrebarea „are cache-ul ăsta cele cinci lucruri?" se pune pe
câmpuri, nu pe o expresie regulată care caută cuvinte într-un docstring. Iar `dovada` nu e o
promisiune: garda cere ca testul numit acolo să EXISTE cu adevărat — o declarație care trimite la o
probă inexistentă e mai rea decât lipsa ei, fiindcă se citește ca verificată.

CONVENȚIA DE NUME, mecanică: pentru un cache numit `X`, declarația e `X_DECLARATIE`, în ACELAȘI
modul. Lângă el, nu într-un registru central — fiindcă un registru central se depărtează de cod și
îmbătrânește, iar aici toată ideea e ca declarația să moară odată cu cache-ul pe care îl descrie.

CE NU FACE modulul ăsta: nu ține cache-uri, nu invalidează nimic, nu știe despre niciunul dintre
ele. E doar FORMA. Verificarea că fiecare cache o poartă e în `core/test_cache_declarat.py`.
"""
import collections

#: Cele cinci lucruri, în ordinea din textul canonic. Toate sunt șiruri, toate obligatorii.
#: `dovada` poartă numele unei funcții de test care CHIAR golește cache-ul și compară răspunsul.
Declaratie = collections.namedtuple("Declaratie", "rol sursa motiv invalidare dovada")

#: Sufixul după care se găsește declarația unui cache. Scris o dată, folosit și de gardă.
SUFIX = "_DECLARATIE"


def numele_declaratiei(nume_cache):
    """`_CACHE` -> `_CACHE_DECLARATIE`. O singură regulă, într-un singur loc."""
    return nume_cache + SUFIX
