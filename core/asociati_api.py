"""
core/asociati_api.py — asociații firmei și cotele lor, în Date firmă (deficiența 431, lotul 10, comanda Costin 10.1).

[lotul 10, deficiența 431] „Fluxul e unul singur: asociații și cotele (cu istoricul cesiunilor) în datele firmei; nota de dividende
împarte automat pe asociați; D205 preia din notele validate; mesajul de refuz trimite la ce lipsește.” Partea de aici: asociații și
cotele, cu istoricul cesiunilor, în Date firmă. Până azi tabelele (`asociati`, `asociati_istoric`) se umpleau numai din importul CSV.

O SINGURĂ LOGICĂ, CU IMPORTUL. Verificarea rândurilor (CNP/CUI cu cifra de control, cota între 0 și 100, fără dubluri, suma 100%,
CUI-ul juridic confruntat cu ANAF) e `asociati_import_api.verifica_randuri`; scrierea (DELETE + INSERT) și arhivarea structurii la o
cesiune sunt `asociati_import_api.importa` / `arhiveaza_pentru_cesiune`. Aici: citirea pentru ecran (structura curentă + istoricul,
cu intervalul de valabilitate al fiecărei structuri) și structura valabilă la o dată.

TEMEIUL:
- Legea 31/1990 art.7 lit.d): actul constitutiv cuprinde „capitalul social subscris, cu menționarea aportului fiecărui asociat […];
  la societățile cu răspundere limitată se vor preciza numărul și valoarea nominală a părților sociale, precum și numărul părților
  sociale atribuite fiecărui asociat pentru aportul său”; art.11 alin.(1): „Capitalul social al unei societăți cu răspundere limitată
  se divide în părți sociale egale.” — INTERPRETARE CU TEMEI: capitalul e împărțit în întregime între asociați, deci cotele lor
  însumează 100% (invariant aritmetic; legea nu scrie „100%”).
- Legea 31/1990 art.202 alin.(1): „Părțile sociale pot fi transmise între asociați.” — cesiunea schimbă structura de la o dată.
- Legea 31/1990 art.67 alin.(2): „Dividendele se distribuie asociaților proporțional cu cota de participare la capitalul social
  vărsat”; alin.(6): „Dividendele care se cuvin după data transmiterii acțiunilor aparțin cesionarului, în afară de cazul în care
  părțile au convenit altfel.” — de aceea structura veche rămâne, cu data până la care a fost valabilă.

Conexiunea / cursorul vin pe schema firmei; nimic de aici nu comite.
"""
from __future__ import annotations

import datetime as _dt
from decimal import Decimal

from core import cui_forma as _forma_cui

MODUL = "asociati_api"


def _rand(r):
    return list(r.values()) if isinstance(r, dict) else list(r)


def _tip(cod):
    cod = str(cod or "").strip()
    return "fizica" if (len(cod) == 13 and cod.isdigit()) else ("juridica" if cod else "")


def curenta(cur):
    """Structura curentă: [{id, nume, cnp, cota (text, fără zerouri inutile), tip}], cota descrescător."""
    cur.execute("SELECT id, nume, cnp, cota FROM asociati ORDER BY cota DESC, nume, id")
    out = []
    for i, nume, cnp, cota in (_rand(r) for r in cur.fetchall()):
        out.append({"id": i, "nume": nume or "", "cnp": cnp or "", "cota": _cota_text(cota), "tip": _tip(cnp)})
    return out


def _cota_text(c):
    """Cota ca text, fără zerouri inutile („50”, „33.33”) — pentru ecran și pentru câmpul de editare."""
    d = Decimal(str(c if c is not None else 0)).normalize()
    return format(d, "f")


def istoric(cur):
    """Structurile ANTERIOARE, cea mai nouă prima: [{de_la (ISO|None = de la început), pana_la (ISO), asociati: [{nume, cnp, cota}]}].
    `de_la` = ziua de după structura precedentă (garanția „fără goluri”, `asociati_import_api.arhiveaza_pentru_cesiune`)."""
    cur.execute("SELECT valabil_pana_la, cnp, nume, cota FROM asociati_istoric ORDER BY valabil_pana_la, cota DESC, cnp")
    grupe = {}
    for pana, cnp, nume, cota in (_rand(r) for r in cur.fetchall()):
        grupe.setdefault(pana, []).append({"nume": nume or "", "cnp": cnp or "", "cota": _cota_text(cota)})
    out, precedenta = [], None
    for pana in sorted(grupe):
        out.append({"de_la": (precedenta + _dt.timedelta(days=1)).isoformat() if precedenta else None,
                    "pana_la": pana.isoformat(), "asociati": grupe[pana]})
        precedenta = pana
    return list(reversed(out))


def valabila_de_la(cur):
    """Data de la care e valabilă structura curentă (ziua de după ultima cesiune) sau None (de la început)."""
    cur.execute("SELECT max(valabil_pana_la) FROM asociati_istoric")
    r = _rand(cur.fetchone())[0]
    return (r + _dt.timedelta(days=1)) if r else None


def structura_la(cur, data):
    """Structura asociaților valabilă la `data` (date sau 'AAAA-LL-ZZ'): [(cnp, nume, cota Decimal)] — pentru nota de dividende și
    D205 (Legea 31/1990 art.67 alin.(2) și (6)). Aceeași regulă ca `dividende_curs.structura_la` (o refolosește): la data d, cea mai
    veche structură arhivată cu valabil_pana_la >= d; altfel cea curentă."""
    from core import dividende_curs as _dc
    d = data if isinstance(data, _dt.date) else _dt.date.fromisoformat(str(data)[:10])
    cur.execute("SELECT nume, cnp, cota FROM asociati")
    cur_ = [tuple(_rand(r)) for r in cur.fetchall()]
    cur.execute("SELECT cnp, nume, cota, valabil_pana_la FROM asociati_istoric")
    ist = [tuple(_rand(r)) for r in cur.fetchall()]
    return _dc.structura_la(cur_, ist)(d)


def citeste(cur):
    """Tot ce arată secțiunea „Asociați” din Date firmă."""
    c = curenta(cur)
    total = sum((Decimal(x["cota"]) for x in c), Decimal(0))
    de_la = valabila_de_la(cur)
    return {"asociati": c, "total_cota": _cota_text(total), "valabila_de_la": de_la.isoformat() if de_la else None,
            "istoric": istoric(cur)}


#: regula respingerii (asociati_import_api.verifica_randuri) -> coloana din tabelul ecranului; fără coloană = refuz pe set
_COLOANA = {"denumire_lipsa": "nume", "nume_diferit_anaf": "nume", "cnp_invalid": "cnp", "cui_invalid": "cnp",
            "cui_negasit_anaf": "cnp", "identificator_dublat": "cnp", "identificator_lipsa": "cnp", "cota_invalida": "cota"}


def _cota(x):
    """Cota scrisă pe ecran („50”, „33,33”, „25%”) -> float; gol -> None; altceva -> textul (verificarea comună îl respinge numit:
    „cota abc% nu e o cotă de participare”). Nu `numere.numar`: acolo „abc” devine 0, adică o cotă inventată."""
    t = str(x if x is not None else "").strip().rstrip("%").strip().replace(",", ".")
    if not t:
        return None
    try:
        return float(Decimal(t))
    except Exception:  # noqa: BLE001 — InvalidOperation: textul merge mai departe, la refuzul numit
        return str(x).strip()


def randuri_din_corp(randuri):
    """Rândurile trimise de ecran -> forma verificării comune: {nume, cnp, cota, rand_fisier = poziția pe ecran, de la 1}.

    `cnp` e identificatorul asociatului: CNP-ul persoanei fizice sau CUI-ul persoanei juridice, în forma păstrată (`cui_forma.stocare`,
    decizia Costin 10.3 pct.4, aceeași ca la import, `asociati_import_api.extrage`). Un CNP n-are „RO”: rămâne cum e (fără spații);
    „RO” se scoate numai din fața CUI-ului din cifre. [lotul 11, clasa „normalizare locală a CUI”] Înainte, `.replace("RO", "")` scotea
    „RO” de oriunde din text, nu numai prefixul."""
    out = []
    for i, r in enumerate(randuri or [], start=1):
        cod = _forma_cui.stocare(r.get("cnp")) or ""
        out.append({"nume": str(r.get("nume") or "").strip(), "cnp": cod, "cota": _cota(r.get("cota")), "rand_fisier": i})
    return out


def erori_cota_lipsa(randuri):
    """PURĂ. Rândurile fără cotă: [{camp, mesaj}]. Verificarea comună ar citi golul ca 0% (o cotă pe care omul n-a scris-o)."""
    return [{"camp": "as-%d-cota" % r["rand_fisier"],
             "mesaj": "%s: scrie cota de participare (procent din capitalul social)." % (r["nume"] or "asociatul de pe rândul %d"
                                                                                       % r["rand_fisier"])}
            for r in randuri if r.get("cota") is None]


def erori_ecran(randuri, erori):
    """PURĂ. [lotul 13, deficiența 526] Respingerile verificării comune, așa cum le citește formularul din Date firmă.

    Comanda 13.1, verbatim: „Cu CNP invalid pe rânduri (verificarea CNP corectă), lângă buton scrie «Total cote: 100%», iar mesajul roșu
    spune «cotele însumează 0%, nu 100%». Mesajul de total nu apare când singura problemă e CNP-ul.” Verificarea comună adună cotele numai
    pe rândurile care INTRĂ (`coerenta_cote`, deficiența 384: la IMPORT, rândurile respinse se lasă deoparte și restul se importă). În Date
    firmă nu intră nimic cât timp un rând e respins (refuzul e al întregului tabel, `uc_asociati._verifica`), deci totalul pe care îl
    judecă omul e cel scris pe ecran, pe TOATE rândurile — exact „Total cote” de lângă „+ Asociat”. Aici: refuzul de total se păstrează
    numai dacă cotele scrise, toate, nu dau 100%, și spune suma lor; altfel (singura problemă e un CNP, un nume…) iese."""
    from decimal import Decimal as _D
    total = sum((_D(str(r["cota"])) for r in randuri or [] if isinstance(r.get("cota"), (int, float))), _D(0))
    out = []
    for e in erori or []:
        if e.get("regula") == "cote_nu_dau_suta":
            if total == 100:
                continue
            e = dict(e, mesaj="cotele asociaților însumează %s%%, nu 100%%" % _cota_text(total).replace(".", ","))
        out.append(e)
    return out


def erori_pe_campuri(erori):
    """Respingerile verificării comune -> [{camp: 'as-<rand>-<coloana>' | None, mesaj}] (DS cap.24: `{prefix}{i}-{camp}`) pentru ecran (refuzul lângă câmp)."""
    out = []
    for e in erori or []:
        col = _COLOANA.get(e.get("regula"))
        rand = e.get("rand")
        camp = ("as-%d-%s" % (rand, col)) if (col and isinstance(rand, int)) else ("as-total" if e.get("regula") == "cote_nu_dau_suta" else None)
        out.append({"camp": camp, "mesaj": e.get("mesaj") or ""})
    return out
