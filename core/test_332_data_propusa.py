# -*- coding: utf-8 -*-
"""[deficiența 332, comanda Costin 8.1, 18.10.2026, verbatim în DECIZII „Comanda 8.1”] „Casă: data dispoziției noi vine goală (clasa 68).”
Clasa 68 = data propusă pe formularul nou. Formularele documentelor care consemnează un fapt de AZI (DECIZII S2: „emiterea, încasarea,
registrul au data faptului de azi”) pornesc cu data de azi, pe care omul o schimbă dacă faptul e din altă zi. Căutat 18.10.2026 în tot
`static/js` (`<input type="date"` fără `value=`): cele de mai jos erau goale; rămân goale, cu motiv, numai câmpurile care NU sunt data
unui fapt de azi (perioada concediului, data balanței migrate, data CIM-ului existent, data inventarierii, data depunerii unei
declarații în afara iConta, câmpurile generice ale operațiunilor, expirarea unui anunț)."""
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: (fișier, id) — data faptului, propusă azi
DATA_FAPTULUI = [
    ("static/js/ecrane/firme.js", "c-data"),      # dispoziția de casă (332)
    ("static/js/ecrane/firme.js", "ch-data"),     # chitanța fără factură
    ("static/js/ecrane/firme.js", "z-data"),      # raportul Z
    ("static/js/ecrane/firme.js", "cv-data"),     # documentul de stoc (consum / vânzare / inventar)
    ("static/js/ecrane/firme.js", "tr-data"),     # transferul de stoc
    ("static/js/ecrane/firme.js", "rc-data"),     # reclasificarea de stoc
    ("static/js/ecrane/rip_ecran.js", "r-data"),  # operațiunea din registrul de încasări și plăți
]


def _input(cale, id_):
    t = open(os.path.join(RAD, cale), encoding="utf-8").read()
    m = re.search(r'<input type="date"[^>]*\bid="%s"[^>]*>' % re.escape(id_), t)
    return m.group(0) if m else None


def test_332_formularele_noi_pornesc_cu_data_faptului():
    rele = []
    for cale, id_ in DATA_FAPTULUI:
        seg = _input(cale, id_)
        if seg is None:
            rele.append("%s #%s: câmpul nu mai există (lista gărzii e de actualizat)" % (cale, id_))
        elif not re.search(r'value="\$\{dataIso\(\)\}"', seg):
            rele.append("%s #%s: data nu e propusă (azi)" % (cale, id_))
    assert not rele, rele
