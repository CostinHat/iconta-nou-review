# -*- coding: utf-8 -*-
"""scripts/verifica_duk_publicat.py — validatoarele DUK instalate sunt cele PUBLICATE de ANAF?

[comanda Costin 07.10.2026, C3] „Verifică întâi dacă validatorul D112 instalat e ultima versiune publicată de ANAF.” Măsurat:
D112 instalat = J27.0.1 (08.08.2026), publicat = J27.0.6 (14.09.2026); diferența era chiar regula salariului minim (J27.0.2,
„corectie regula salmin”), iar validatorul vechi semnala drept atenționare un D112 corect. Încă 4 validatoare erau în urmă
(D100, D101, D710, B230). Validatorul e judecătorul final (CLAUDE.md) — un judecător vechi judecă după altă lege.

CE FACE:
  ./venv/bin/python scripts/verifica_duk_publicat.py            # descarcă versiuni.xml de la ANAF, compară cu manifestul
                                                                 # (anaf_surse/duk_instalat.json); exit 1 dacă vreunul e în urmă
  ./venv/bin/python scripts/verifica_duk_publicat.py --zilnic   # NUMAI CITIRE în depozit și în ~/duk: compară cu ANAF și scrie
                                                                 # starea comparației în fișierul local `cale_stare()`; dacă un
                                                                 # validator e în urmă, alertează administratorul (observare.alerteaza)
  ./venv/bin/python scripts/verifica_duk_publicat.py --scrie    # DUPĂ instalare: scrie anaf_surse/versiuni.xml (copia oficială)
                                                                 # și manifestul (versiunea publicată + sha256 al jarului instalat)
Garda din poartă (`core/test_duk_instalat.py`) nu are rețea: cere ca jarurile instalate să fie cele din manifest, manifestul să
spună aceleași versiuni ca `anaf_surse/versiuni.xml`, iar comparația cu ANAF (cea mai nouă dintre manifest și starea zilnică) să nu
fie mai veche de ZILE_MAX și să nu fi găsit un validator în urmă.

[deficiența 494, lotul 12, 23.10.2026] Costin: „manifestul DUKIntegrator expiră pe 07.11.2026 — după acea dată declarațiile nu se mai
validează”. Validatoarele nu expiră; expira COMPARAȚIA: singura ei dată era `verificat_la` din manifest, scris numai de `--scrie`, adică
numai la o instalare. Între instalări nimic nu mai întreba ANAF, iar poarta pica la 30 de zile fără să spună dacă ceva chiar e în urmă.
`--zilnic` (din crontab) ține comparația proaspătă fără să scrie în depozit, iar un validator rămas în urmă se află a doua zi, prin
alertă, și oprește poarta numind validatorul și pașii — nu peste o lună, printr-o dată expirată.
"""
import datetime
import hashlib
import io
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL_VERSIUNI = "https://static.anaf.ro/static/10/Anaf/update5/versiuni.xml"   # = urlVersiuni din ~/duk/dist/config/config.properties
LIB = os.path.expanduser("~/duk/dist/lib")
VERSIUNI_LOCAL = os.path.join(RAD, "anaf_surse", "versiuni.xml")
MANIFEST = os.path.join(RAD, "anaf_surse", "duk_instalat.json")
#: Cât de veche poate fi ultima comparație cu ANAF până când poarta o cere din nou. Nu e o valoare fiscală, e o CADENȚĂ: ANAF a
#: publicat D112 de patru ori în august 2026; 30 de zile înseamnă că un validator nu poate rămâne în urmă mai mult de o lună.
ZILE_MAX = 30
#: Starea comparației zilnice: în AFARA depozitului (jobul zilnic nu scrie în arborele publicat), pe calea din variabila de mediu,
#: citită la apel. Aceeași cale o citește garda din poartă.
ENV_STARE = "ICONTA_DUK_STARE"
STARE_IMPLICITA = "~/.cache/iconta_duk/verificare_anaf.json"
#: Numele jobului în heartbeat (`core/cron.RITMURI`) când `--zilnic` e legat de crontab.
NUME_JOB = "verificare_duk"


def versiuni(xml_text):
    """{declaratie: (versiuneJ, jar, url_jar)} din versiuni.xml."""
    out = {}
    for m in re.finditer(r"<(\w+)>\s*<versiuneJ>([^<]*)</versiuneJ>.*?<JURL>([^<]*)</JURL>", xml_text, re.S):
        url = m.group(3).strip()
        out[m.group(1)] = (m.group(2).strip(), url.rsplit("/", 1)[-1], url)
    return out


def versiuni_noi_pe_jar_vechi(vechi, nou):
    """[lotul 12, C106] PURĂ. `[(tip, versiune_veche, versiune_nouă)]` pentru validatoarele cărora manifestul nou le dă altă versiune
    decât cel vechi, deși jarul instalat are același sha256 — adică jarul publicat nu s-a instalat."""
    out = []
    for tip, v in sorted(nou.get("validatoare", {}).items()):
        w = vechi.get("validatoare", {}).get(tip)
        if w and w.get("versiuneJ") != v["versiuneJ"] and w.get("sha256") == v["sha256"]:
            out.append((tip, w.get("versiuneJ"), v["versiuneJ"]))
    return out


def sha(cale):
    return hashlib.sha256(open(cale, "rb").read()).hexdigest()


def instalate(lib=None):
    return sorted(f for f in os.listdir(lib or LIB) if f.endswith("Validator.jar") and f != "Validator.jar")


def descarca():
    """versiuni.xml publicat de ANAF. Prin `requests`: o rețea căzută (Timeout / ConnectionError) e recunoscută de
    `cron.tranzitoriu` și nu alertează (deficiența 296); un răspuns HTTP de eroare (adresa mutată) alertează."""
    import requests
    r = requests.get(URL_VERSIUNI, timeout=60)
    r.raise_for_status()
    return r.content.decode("utf-8", "replace")


def in_urma(man, pv):
    """[(tip, instalat, publicat)] — validatoarele din manifest a căror versiune publicată e alta."""
    return [(tip, v["versiuneJ"], pv.get(tip, ("?",))[0]) for tip, v in sorted(man["validatoare"].items())
            if pv.get(tip, (v["versiuneJ"],))[0] != v["versiuneJ"]]


def cale_stare():
    return os.path.expanduser(os.environ.get(ENV_STARE) or STARE_IMPLICITA)


def citeste_stare(cale=None):
    """Starea comparației zilnice, sau None dacă jobul n-a rulat încă. Un fișier stricat NU se ignoră: aruncă (o stare
    necitibilă tratată ca „nicio stare” ar ascunde exact un validator găsit în urmă)."""
    cale = cale or cale_stare()
    if not os.path.exists(cale):
        return None
    return json.load(io.open(cale, encoding="utf-8"))


def _scrie_atomic(cale, date):
    os.makedirs(os.path.dirname(cale), exist_ok=True)
    tmp = cale + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        json.dump(date, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, cale)


def comparatia_curenta(man, stare):
    """(data ultimei comparații cu ANAF, validatoarele găsite în urmă care sunt ÎNCĂ în urmă).

    Data = cea mai nouă dintre `verificat_la` din manifest (scris de `--scrie`) și din starea zilnică. O intrare din stare contează
    numai cât timp manifestul spune încă versiunea pe care jobul a găsit-o instalată: după instalare + `--scrie`, manifestul spune
    versiunea publicată, iar intrarea veche nu mai oprește poarta până la rularea zilnică următoare."""
    data = datetime.date.fromisoformat(man["verificat_la"])
    if not stare:
        return data, []
    data = max(data, datetime.date.fromisoformat(stare["verificat_la"]))
    valabile = [e for e in stare["in_urma"]
                if man["validatoare"].get(e["tip"], {}).get("versiuneJ") == e["instalat"]]
    return data, valabile


def mesaj_in_urma(intrari):
    """Textul pentru administrator și pentru poartă: ce validator, ce versiune, de unde se ia, ce comenzi repară."""
    randuri = ["  - %s: instalat %s, publicat de ANAF %s (%s)" % (e["tip"], e["instalat"], e["publicat"], e.get("url") or "?")
               for e in intrari]
    return ("Validatoare DUK în urmă față de ANAF (declarațiile de mai jos se validează după o versiune veche):\n%s\n\n"
            "Ce repară:\n"
            "  1. descarcă jarul publicat (adresa de mai sus) în %s, peste cel vechi;\n"
            "  2. cd %s && ./venv/bin/python scripts/verifica_duk_publicat.py --scrie   (copia oficială + manifestul);\n"
            "  3. rulează probele DUK ale declarațiilor atinse (core/test_d<nr>.py) și comite anaf_surse/."
            % ("\n".join(randuri), LIB, RAD))


def zilnic(publicat=None, manifest=None, lib=None, cale=None, alerta=None, azi=None):
    """Comparația zilnică cu ANAF. Nu scrie nimic în depozit și nimic în `lib`; scrie numai starea, la `cale_stare()`.

    Întoarce starea scrisă. Rețea căzută sau un versiuni.xml fără niciun validator -> aruncă, iar starea veche rămâne (data ei
    îmbătrânește, iar poarta o cere la ZILE_MAX)."""
    publicat = descarca() if publicat is None else publicat
    pv = versiuni(publicat)
    if not pv:
        raise RuntimeError("versiuni.xml de la %s nu conține niciun validator — comparația nu se poate face (pagina s-a schimbat?)"
                           % URL_VERSIUNI)
    lib = lib or LIB
    cale = cale or cale_stare()
    man = json.load(io.open(manifest or MANIFEST, encoding="utf-8"))
    pe_disc = set(instalate(lib))
    intrari = [{"tip": tip, "jar": man["validatoare"][tip]["jar"], "instalat": inst, "publicat": publ,
                "url": pv.get(tip, (None, None, None))[2]}
               for tip, inst, publ in in_urma(man, pv)]
    # un jar înlocuit fără `--scrie`: versiunea din manifest nu mai e dovedită pentru el
    schimbate = sorted(tip for tip, v in man["validatoare"].items()
                       if v["jar"] in pe_disc and sha(os.path.join(lib, v["jar"])) != v["sha256"])
    stare = {"verificat_la": (azi or datetime.date.today()).isoformat(), "sursa": URL_VERSIUNI,
             "manifest_verificat_la": man["verificat_la"],
             "publicate": {tip: t[0] for tip, t in sorted(pv.items())},
             "in_urma": intrari, "jaruri_schimbate": schimbate}
    _scrie_atomic(cale, stare)
    print("comparate %d · în urmă %d · jaruri schimbate fără --scrie %d · stare: %s"
          % (len(man["validatoare"]), len(intrari), len(schimbate), cale), flush=True)
    if intrari or schimbate:
        if alerta is None:
            sys.path.insert(0, RAD)
            from core import observare
            alerta = observare.alerteaza
        corp = mesaj_in_urma(intrari) if intrari else ""
        if schimbate:
            corp += ("\n\nJaruri din %s diferite de manifest (instalate fără --scrie?): %s — versiunea lor nu e cunoscută."
                     % (lib, ", ".join(schimbate)))
        subiect = "Validatoare DUK în urmă față de ANAF: %s" % ", ".join([e["tip"] for e in intrari] + schimbate)
        if not alerta("duk_in_urma", subiect, corp.strip()):
            print("ALERTĂ NETRIMISĂ: %s" % subiect, flush=True)
    return stare


def ruleaza_zilnic():
    """Intrarea jobului din crontab: prin `cron.ruleaza` (eșec -> alertă, rețea căzută -> fără alertă; reușită -> bătaia
    `NUME_JOB` în heartbeat). Semnalul unui validator în urmă e alerta, nu codul de ieșire."""
    sys.path.insert(0, RAD)
    from core import cron
    cron.ruleaza(NUME_JOB, zilnic)
    return 0


def main():
    if "--zilnic" in sys.argv:
        return ruleaza_zilnic()
    publicat = descarca()
    pv = versiuni(publicat)
    if "--scrie" in sys.argv:
        vechi = json.load(io.open(MANIFEST, encoding="utf-8")) if os.path.isfile(MANIFEST) else {"validatoare": {}}
        man = {"verificat_la": datetime.date.today().isoformat(), "sursa": URL_VERSIUNI, "validatoare": {}}
        for tip, (ver, jar, _url) in sorted(pv.items()):
            if jar in instalate():
                man["validatoare"][tip] = {"jar": jar, "versiuneJ": ver, "sha256": sha(os.path.join(LIB, jar))}
        neinlocuite = versiuni_noi_pe_jar_vechi(vechi, man)
        if neinlocuite:
            # [lotul 12, C106] jarul nu-și spune versiunea (MANIFEST.MF n-o are): manifestul o ia din versiuni.xml. O versiune nouă pe un
            # jar cu ACELAȘI sha256 ca în manifestul vechi înseamnă că jarul publicat nu s-a instalat — manifestul ar minti.
            for tip, v0, v1 in neinlocuite:
                print("REFUZ: %s — ANAF publică %s, manifestul spune %s, dar jarul instalat e tot cel vechi (același sha256). Instalează "
                      "întâi jarul publicat în %s, apoi rulează din nou --scrie." % (tip, v1, v0, LIB))
            return 1
        io.open(VERSIUNI_LOCAL, "w", encoding="utf-8").write(publicat)
        json.dump(man, io.open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
        print("scris: %d validatoare, verificat_la %s" % (len(man["validatoare"]), man["verificat_la"]))
        return 0
    man = json.load(io.open(MANIFEST, encoding="utf-8"))
    rez = in_urma(man, pv)
    for t in rez:
        print("ÎN URMĂ: %s instalat %s, publicat %s" % t)
    print("comparate %d · în urmă %d" % (len(man["validatoare"]), len(rez)))
    return 1 if rez else 0


if __name__ == "__main__":
    sys.exit(main())
