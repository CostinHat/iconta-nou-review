# -*- coding: utf-8 -*-
"""scripts/alerta_whatsapp.py — alertele lanțului de loturi către Costin (comanda 17.2-A, C227).

  python scripts/alerta_whatsapp.py lot <lot> <stare> [<sha> [<motiv>]]   stare = PORNIT | publicat | nepublicat
  python scripts/alerta_whatsapp.py proba                                 o alertă de probă (lotul «PROBA»)
  python scripts/alerta_whatsapp.py fara-secrete <cale>...                REFUZ (ieșire 1) dacă o cale conține o valoare secretă

Lanțul unei alerte, în ordine: șablonul `iconta_alerta_lot`; mesajul text liber (merge numai în fereastra de 24 de ore după ce Costin a scris
numărului); emailul (ca ~/alerta_veghe.sh) — dacă WhatsApp a căzut sau dacă lotul s-a oprit nepublicat. O alertă nu poate opri niciodată un lot:
orice situație în afară de argumente greșite (ieșire 2) iese cu 0. Destinatarul: ALERTA_WA_CATRE din ~/.iconta/api_keys.env. Nimic secret nu se
tipărește și nu se scrie în jurnal (~/alerte_lot.log, sau fișierul din ALERTA_WA_LOG).
"""
import datetime
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import observare  # noqa: E402
from core import whatsapp as wa  # noqa: E402
from core.common import cfg  # noqa: E402

STARI = ("PORNIT", "publicat", "nepublicat")
LOT_RE = re.compile(r"[0-9]+\.[0-9]+(-[A-Z][0-9]*)?")
MOTIV_IMPLICIT = "motiv nescris, vezi raportul lotului"
LUNGIME_PARAMETRU = 160
SECRETE = ("WHATSAPP_TOKEN", "WHATSAPP_PIN", "WHATSAPP_VERIFY_TOKEN", "WHATSAPP_APP_SECRET", "ALERTA_WA_CATRE")
UTILIZARE = ("utilizare: alerta_whatsapp.py lot <lot> <PORNIT|publicat|nepublicat> [<sha> [<motiv>]] | proba | fara-secrete <cale>...")

#: șablonul alertei (UTILITY, fără conținut fiscal); trimis spre aprobare de `scripts/whatsapp_meta.py sabloane --trimite`
SABLOANE_ALERTA = [
    {"name": "iconta_alerta_lot", "language": "ro", "category": "UTILITY",
     "components": [{"type": "BODY", "text": "Lotul {{1}} din iConta.eu: {{2}}. Mesaj automat, fără conținut fiscal.",
                     "example": {"body_text": [["17.2", "PORNIT 10:48"]]}}]},
]


def curata(s):
    """Parametru de șablon Meta: fără linii noi, tab sau spații multiple; cel mult 160 de caractere (159 + «…»)."""
    s = " ".join(str(s).split())
    return s if len(s) <= LUNGIME_PARAMETRU else s[:LUNGIME_PARAMETRU - 1] + "…"


def compune(lot, stare, sha, motiv, acum):
    """PURĂ. -> (variabila 1, variabila 2) a șablonului."""
    ora = acum.strftime("%H:%M")
    if stare == "PORNIT":
        v2 = "PORNIT %s" % ora
    elif stare == "publicat":
        sha = (sha or "").strip()
        v2 = "publicat %s %s" % (sha[:8], ora) if sha and sha != "-" else "publicat %s" % ora
    else:
        v2 = "OPRIT %s: %s" % (ora, curata(motiv or "") or MOTIV_IMPLICIT)
    return curata(lot), curata(v2)


def incarca_mediu():
    """Liniile CHEIE=VALOARE din ALERTA_WA_ENV (implicit ~/.iconta/api_keys.env) și din ~/.iconta/db.env, fără să suprascrie ce e deja setat."""
    acasa = os.path.expanduser("~")
    for cale in (os.environ.get("ALERTA_WA_ENV") or os.path.join(acasa, ".iconta", "api_keys.env"), os.path.join(acasa, ".iconta", "db.env")):
        try:
            linii = open(cale, encoding="utf-8").read().splitlines()
        except OSError:
            continue
        for linie in linii:
            linie = linie.strip()
            if not linie or linie.startswith("#") or "=" not in linie:
                continue
            nume, valoare = linie.split("=", 1)
            nume = nume.strip()
            if nume.startswith("export "):
                nume = nume[7:].strip()
            valoare = valoare.strip()
            if len(valoare) >= 2 and valoare[0] == valoare[-1] and valoare[0] in "\"'":
                valoare = valoare[1:-1]
            if nume and nume not in os.environ:
                os.environ[nume] = valoare


def _valori_secrete(cu_pin=True):
    """[(nume, valoare)] pentru secretele nevide din mediu; la ALERTA_WA_CATRE și forma normalizată."""
    iesire = []
    for nume in SECRETE:
        v = os.environ.get(nume, "")
        if not v or (nume == "WHATSAPP_PIN" and not cu_pin):
            continue
        iesire.append((nume, v))
        if nume == "ALERTA_WA_CATRE":
            n = wa.normalizeaza(v)
            if n and n != v:
                iesire.append((nume, n))
    return iesire


def _ascunde(text):
    """Scoate din text valorile secrete (jurnalul și ecranul nu le conțin; PIN-ul nu apare în răspunsurile Meta)."""
    for _, v in _valori_secrete(cu_pin=False):
        text = text.replace(v, "***")
    return text


def _jurnal(lot, v2, canal, rezultat):
    """Un rând pe încercare în ALERTA_WA_LOG; ecranul primește «[alerta] <canal>: <rezultat>». Nu ridică nimic."""
    rezultat = _ascunde(" ".join(str(rezultat).split()))[:120]
    print("[alerta] %s: %s" % (canal, rezultat), flush=True)
    cale = os.environ.get("ALERTA_WA_LOG") or os.path.join(os.path.expanduser("~"), "alerte_lot.log")
    try:
        ora = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        with open(cale, "a", encoding="utf-8") as f:
            f.write("\t".join(_ascunde(" ".join(str(x).split())) for x in (ora, lot, v2, canal, rezultat)) + "\n")
    except OSError:
        pass


def _corp_comun(dest):
    return {"messaging_product": "whatsapp", "recipient_type": "individual", "to": dest}


def _trimite_sablon(dest, v1, v2):
    corp = _corp_comun(dest)
    corp.update({"type": "template", "template": {"name": SABLOANE_ALERTA[0]["name"], "language": {"code": SABLOANE_ALERTA[0]["language"]},
                                                  "components": [{"type": "body", "parameters": [{"type": "text", "text": v1}, {"type": "text", "text": v2}]}]}})
    return wa._mesaj_id(wa._cere("%s/messages" % wa._pnid(), corp))


def _trimite_text(dest, v1, v2):
    corp = _corp_comun(dest)
    corp.update({"type": "text", "text": {"body": "Lotul %s: %s" % (v1, v2)}})
    return wa._mesaj_id(wa._cere("%s/messages" % wa._pnid(), corp))


def _rezultat_esec(e):
    """Rezultatul scurt al unei încercări căzute: la `wa.Refuzat` începutul mesajului Meta (cod HTTP și cod Meta), altfel tipul excepției."""
    return str(e)[:120] if isinstance(e, wa.Refuzat) else type(e).__name__


def _incercare_wa(canal, trimite, dest, v1, v2):
    """True dacă Meta a primit mesajul (răspuns cu id)."""
    try:
        id_ = trimite(dest, v1, v2)
        if not id_:
            raise ValueError("raspuns fara id de mesaj")
    except Exception as e:  # noqa: BLE001 — orice excepție trece la canalul următor
        _jurnal(v1, v2, canal, _rezultat_esec(e))
        return False
    _jurnal(v1, v2, canal, "ok %s" % id_)
    return True


def _email(v1, v2):
    adresa = cfg("ICONTA_ALERTA_EMAIL")
    if not adresa:
        _jurnal(v1, v2, "email", "netrimis: adresa lipsă")
        return
    try:
        ok = observare.trimite_email_html(adresa, "[iConta.eu] Lotul %s: %s" % (v1, v2),
                                          "<p>Lotul %s: %s</p>" % (html.escape(v1), html.escape(v2)))
    except Exception as e:  # noqa: BLE001
        _jurnal(v1, v2, "email", "netrimis: %s" % type(e).__name__)
        return
    _jurnal(v1, v2, "email", "ok" if ok else "netrimis")


def _lant(v1, v2, stare):
    dest = wa.normalizeaza(cfg("ALERTA_WA_CATRE"))
    trimis = False
    if dest is None:
        _jurnal(v1, v2, "sablon", "destinatar lipsă" if not cfg("ALERTA_WA_CATRE").strip() else "destinatar invalid")
    else:
        trimis = _incercare_wa("sablon", _trimite_sablon, dest, v1, v2) or _incercare_wa("text", _trimite_text, dest, v1, v2)
    if not trimis or stare == "nepublicat":
        _email(v1, v2)


def alerta(lot, stare, sha="", motiv="", acum=None):
    """Alerta unui lot. Nu ridică nimic; un nume de lot în afara formei nu trimite nimic."""
    if not LOT_RE.fullmatch(lot or ""):
        _jurnal(lot, "-", "-", "lot ignorat")
        return
    v1, v2 = compune(lot, stare, sha, motiv, acum or datetime.datetime.now())
    _lant(v1, v2, stare)


def proba(acum=None):
    acum = acum or datetime.datetime.now()
    _lant("PROBA", "proba alertă %s" % acum.strftime("%H:%M"), "PORNIT")


def _fisiere(cai):
    for c in cai:
        if os.path.isdir(c):
            for rad, _, nume in sorted(os.walk(c)):
                for n in sorted(nume):
                    yield os.path.join(rad, n)
        else:
            yield c


def fara_secrete(cai):
    """-> 0 dacă nicio cale nu conține o valoare secretă, altfel 1 (numește calea și variabila, niciodată valoarea)."""
    valori = _valori_secrete()
    verificate, binare = 0, 0
    for f in _fisiere(cai):
        try:
            brut = open(f, "rb").read()
        except OSError:
            print("[fara-secrete] nu verific: %s" % f)
            binare += 1
            continue
        if b"\0" in brut[:8192]:
            print("[fara-secrete] nu verific: %s" % f)
            binare += 1
            continue
        text = brut.decode("utf-8", errors="replace")
        verificate += 1
        for nume, v in valori:
            gasit = re.search(r"(?<![0-9A-Za-z])%s(?![0-9A-Za-z])" % re.escape(v), text) if nume == "WHATSAPP_PIN" else v in text
            if gasit:
                print("[fara-secrete] REFUZ: %s conține valoarea lui %s" % (f, nume))
                return 1
    print("[fara-secrete] VERDE: %d fișiere%s" % (verificate, " (%d binare, nu verific)" % binare if binare else ""))
    return 0


def main(argv):
    cmd = argv[0] if argv else ""
    if cmd == "lot" and 3 <= len(argv) <= 5 and argv[2] in STARI:
        pass
    elif cmd == "proba" and len(argv) == 1:
        pass
    elif cmd == "fara-secrete" and len(argv) >= 2:
        pass
    else:
        print(UTILIZARE)
        return 2
    if cmd != "fara-secrete" and os.environ.get("PYTEST_CURRENT_TEST") and not os.environ.get(wa.CHEIE_SIMULAT):
        print("[alerta] REFUZ: sub pytest nu trimit pe real")
        return 0
    try:
        incarca_mediu()
        if cmd == "fara-secrete":
            return fara_secrete(argv[1:])
        if cmd == "proba":
            proba()
        else:
            alerta(argv[1], argv[2], argv[3] if len(argv) > 3 else "", argv[4] if len(argv) > 4 else "")
    except Exception as e:  # noqa: BLE001 — o alertă nu oprește niciodată un lot
        print("[alerta] căzută: %s" % type(e).__name__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
