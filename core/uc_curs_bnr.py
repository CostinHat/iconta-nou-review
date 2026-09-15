# -*- coding: utf-8 -*-
"""USE_CASE — ACTUL de a aduce cursul BNR și de a-l pune în cache.

[E2b, 15.09.2026] Cele două funcții de aici trăiau în `core/curs_bnr.py`, adică în modulul
DEPOZITULUI, și își deschideau singure conexiunea — de aceea depozitul apărea cu conexiune proprie.
Mutarea e verbatim: ce fac nu s-a schimbat cu nimic.

**Conexiunea proprie NU e un defect aici, e decizia din 04.09.2026** (`core/p4_clasificare.py`,
`curs_bnr:_descarca`): cache-ul de cursuri trebuie să supraviețuiască eșecului actului care l-a
declanșat, altfel fiecare încercare re-descarcă de la BNR. Un act are voie să-și dețină tranzacția —
asta spune contractul (`PLAN_HARDENING.md:840`); un depozit, nu.

Decizia NU se ia aici: pragul de vechime, alegerea cursului și cele trei refuzuri rămân în
`curs_bnr.curs_pentru`, care primește conexiunea apelantului.
"""
from datetime import date

from core import curs_bnr as _cb


def _salveaza_cache(harta: dict):
    """Salveaza cursurile in cache (idempotent), pe o CONEXIUNE PROPRIE.

    **DE CE NU PE CONEXIUNEA APELANTULUI** (gasit apasand, 04.09.2026). Pana azi primea `conn` si
    facea `conn.commit()` pe el. Apelantul lui e `_cb.curs_pentru`, chemat din mijlocul emiterii unei
    facturi — deci commitul asta comitea FACTURA, in mijlocul actului. Consecinta, probata: un
    refuz de curs (`CURS_PREA_VECHI`) facea `rollback()` care nu mai avea ce anula, iar in baza
    ramanea o factura numerotata si contata, fara curs si fara TVA in lei.

    Cache-ul traieste in `public` si e o preocupare a APLICATIEI, nu a facturii; se scrie separat,
    ca sa se pastreze si cand actul care l-a declansat esueaza — altfel fiecare incercare ar
    re-descarca de la BNR, care blocheaza IP-urile cu trafic repetat."""
    from core import db as _db
    with _db.get_conn() as c2:
        with c2.cursor() as cur:
            for d, cursuri in harta.items():
                for mon, c in cursuri.items():
                    cur.execute(
                        "INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES (%s,%s,%s) "
                        "ON CONFLICT (data, moneda) DO NOTHING",
                        (d, mon, c))
        c2.commit()


def asigura_cursul(moneda: str, data_factura: date, prag_zile: int = _cb.PRAG_VECHIME_ZILE):
    """Aduce de la BNR ce lipseste din cache — FARA conexiunea apelantului. Nu decide nimic.

    [P5 val 3, 11.09.2026] Se cheama INAINTEA tranzactiei care va emite factura. Descarcarea are
    termen de 10 s pe fiecare din cele (pana la) trei adrese, iar forma dinainte o facea din
    mijlocul lui `_cb.curs_pentru`, adica din mijlocul tranzactiei de emitere. Zece cereri de facturare
    in valuta goleau pool-ul pentru toata aplicatia.

    *Nu ia nicio decizie:* pragul de vechime, alegerea cursului si cele trei refuzuri raman in
    `_cb.curs_pentru`, unde erau, si se aplica pe cache-ul de ATUNCI — deci o harta adusa aici nu sare
    peste nicio verificare.
    """
    from core import db
    moneda = moneda.upper()
    if moneda == "RON":
        return
    with db.get_conn() as conn:                      # scurta, doar citirea cache-ului
        c, dc = _cb._din_cache(conn, moneda, data_factura)
    if c is not None and (data_factura - dc).days <= prag_zile:
        return                                       # destul de proaspat: nimic de adus

    urls = []
    azi = date.today()
    if (azi - data_factura).days <= 9:
        urls.append(_cb.URL_10ZILE)
    urls.append(_cb.URL_AN.format(an=data_factura.year))
    if data_factura.year != azi.year:
        urls.append(_cb.URL_10ZILE)  # fallback

    ultima_eroare = None
    cotate = set()          # ce monede a cotat BNR in hartile pe care CHIAR le-am citit
    for url in urls:
        try:
            xml = _cb._descarca(url)                     # FARA nicio conexiune in mana
            harta = _cb.parse_xml(xml)
            if harta:
                # Bucla DOAR aduce si salveaza. Nu intoarce cursul: pana la calibrare o facea, si
                # asa sarea peste pragul de vechime — un prag aplicat pe un singur drum din doua
                # nu e un prag. Decizia se ia intr-un singur loc, in `_cb.curs_pentru`.
                _salveaza_cache(harta)
                for _zi in harta.values():
                    cotate.update(_zi)
                if _cb.curs_din_harta(harta, moneda, data_factura)[0] is not None:
                    break
        except Exception as e:  # retea, timeout, IP blocat, parse
            ultima_eroare = e
            continue
    _cb._preda(moneda, data_factura, ultima_eroare, cotate)
