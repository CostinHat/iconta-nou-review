# -*- coding: utf-8 -*-
"""core/setari_platforma.py — comutatoarele platformei, schimbate de superadmin din Panou Admin, fără publicare (comanda Costin
15.10.2026, „Lotul 4” pct.6, verbatim în DECIZII: „Comutator în Panou Admin: «Înregistrare: liberă, cu confirmarea emailului / numai
prin invitație», ca să o pot schimba eu fără publicare.”).

Tabela `public.setari_platforma` (core/migrare_inregistrare_libera.py). Primul comutator: `inregistrare`.
FAIL-CLOSED: un rând lipsă, o valoare necunoscută sau o tabelă lipsă se citesc „numai prin invitație”.
Pct.1 din aceeași comandă („fără email funcțional nu se deschide înregistrarea”) stă tot aici, mecanic: înregistrarea liberă e
DESCHISĂ numai dacă modul e `libera` ȘI emailul poate pleca (`email_functional`).
"""
import os

from core import afirmatii as _af

LIBERA = "libera"
INVITATIE = "invitatie"
MODURI = (LIBERA, INVITATIE)
ETICHETE = {LIBERA: "liberă, cu confirmarea emailului", INVITATIE: "numai prin invitație"}

MESAJ_NUMAI_INVITATIE = ("Acum, conturile noi de cabinet se creează numai prin invitație. Dacă vrei să folosești iConta.eu, scrie-ne "
                         "la contact@iconta.eu și îți trimitem invitația.")
MESAJ_FARA_EMAIL = ("Înregistrarea nu e disponibilă acum: emailul de confirmare nu poate pleca. Încearcă din nou mai târziu sau "
                    "scrie-ne la contact@iconta.eu.")


def email_functional():
    """Poate pleca un email? Cheia Brevo în mediu — sau, NUMAI pe instanța de probă, cutia poștală de test (`ICONTA_EMAIL_CUTIE`,
    `core/observare.py`), din care probele își iau linkul."""
    return bool(os.environ.get("BREVO_API_KEY") or os.environ.get("ICONTA_EMAIL_CUTIE"))


def mod_inregistrare(cur):
    """`{mod, eticheta, modificat_de, modificat_la}`; fără rând / tabelă / valoare cunoscută -> `invitatie`."""
    cur.execute("SELECT to_regclass('public.setari_platforma') IS NOT NULL")
    if not cur.fetchone()[0]:
        return {"mod": INVITATIE, "eticheta": ETICHETE[INVITATIE], "modificat_de": None, "modificat_la": None}
    cur.execute("SELECT s.valoare, s.modificat_la, u.email FROM public.setari_platforma s LEFT JOIN public.users u "
                "ON u.id = s.modificat_de WHERE s.cheie = 'inregistrare'")
    r = cur.fetchone()
    mod = r[0] if r and r[0] in MODURI else INVITATIE
    return {"mod": mod, "eticheta": ETICHETE[mod], "modificat_de": r[2] if r else None,
            "modificat_la": r[1].isoformat() if r and r[1] else None}


def seteaza_mod_inregistrare(cur, mod, uid):
    # upsert-ok: comutatorul are o singură valoare pe cheia naturală `inregistrare`; schimbarea ei de către superadmin E suprascrierea
    # cerută (cine și când rămân scrise în același rând) — nu e un „adaugă” al unui utilizator care ar înlocui tacit altceva
    if mod not in MODURI:
        raise ValueError("Modul de înregistrare e „%s” sau „%s”." % (ETICHETE[LIBERA], ETICHETE[INVITATIE]))
    cur.execute("INSERT INTO public.setari_platforma (cheie, valoare, modificat_de, modificat_la) VALUES ('inregistrare', %s, %s, now()) "
                "ON CONFLICT (cheie) DO UPDATE SET valoare = EXCLUDED.valoare, modificat_de = EXCLUDED.modificat_de, "
                "modificat_la = now()", (mod, uid))


REGULA = ("Înregistrarea liberă e deschisă numai cu comutatorul pe „%s” (Panou Admin -> Înregistrare) și numai dacă emailul de "
          "confirmare poate pleca." % ETICHETE[LIBERA])


def _inchisa(cod, motiv):
    return _af.afirmatie("neconformitate", "inregistrare_inchisa", motiv, unde="înregistrarea unui cabinet nou", regula=REGULA, cod=cod)


def inregistrare_libera(cur):
    """`{deschisa, mod, refuz}` — ce vede vizitatorul la „Client nou” (fără invitație); `refuz` = afirmația tipată `neconformitate`
    (cod NUMAI_INVITATIE / FARA_EMAIL), sau None când e deschisă."""
    m = mod_inregistrare(cur)["mod"]
    if m != LIBERA:
        return {"deschisa": False, "mod": m, "refuz": _inchisa("NUMAI_INVITATIE", MESAJ_NUMAI_INVITATIE)}
    if not email_functional():
        return {"deschisa": False, "mod": m, "refuz": _inchisa("FARA_EMAIL", MESAJ_FARA_EMAIL)}
    return {"deschisa": True, "mod": m, "refuz": None}
