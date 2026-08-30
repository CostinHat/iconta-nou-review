# -*- coding: utf-8 -*-
"""Unealta de aducere din legislatie.just.ro (Portalul Legislativ).

  portal.py cauta <TIP> <NUMAR> <AN>          -> lista de forme, cu id-uri
  portal.py cauta-titlu "<text>" [an_de an_pana]  -> cand actul e numit prin trimitere, nu prin numar
  portal.py adu <ID> <nume_fisier_fara_ext>   -> salveaza .html + .html.sha256 + .txt in anaf_surse/

De ce o unealta si nu un script de unica folosinta: pasul 1 din Partea 0 („nu-l am -> il aduc") se va
repeta. Un act adus manual, o data, nu lasa in urma nici metoda, nici amprenta.
"""
import hashlib
import html as _html
import http.cookiejar
import io
import os
import re
import sys
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")
BAZA = "https://legislatie.just.ro"
DIR = os.path.expanduser("~/iconta_nou/anaf_surse")

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", UA), ("Accept", "text/html,application/xhtml+xml"),
                 ("Accept-Language", "ro,en;q=0.8")]


def get(url):
    with op.open(url, timeout=60) as r:
        return r.read()


def text(brut):
    h = brut.decode("utf-8", "replace")
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", h)
    h = re.sub(r"<[^>]+>", " ", h)
    h = _html.unescape(h)
    h = re.sub(r"[ \t\xa0]+", " ", h)
    return re.sub(r"\n\s*\n+", "\n\n", h).strip()


def cauta(tip, numar, an):
    h = get(BAZA + "/").decode("utf-8", "replace")
    tok = re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"', h).group(1)
    sel = re.search(r'<select[^>]*id="DocumentType".*?</select>', h, re.S).group(0)
    val = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)</option>', sel)
    # Portalul livreaza etichetele HTML-ESCAPATE: „HOTAR&#194;RE" pentru HOTARARE. Comparate asa
    # cum vin, tipurile cu diacritice codate ca entitati sunt DE NEATINS - masurat 23.08.2026:
    # HG-urile din registrul de cote (HG 146/2026, 1506/2024, 276/2013) nu se puteau cauta deloc,
    # iar mesajul de eroare arata o lista in care „HOTARARE" chiar lipsea. Se deschid intai.
    def _et(x):
        return _html.unescape(x).strip().upper()

    cod = [v for v, t in val if _et(t).startswith(tip.upper())]
    if not cod:
        sys.exit("tip de document necunoscut: %r (optiuni: %s)"
                 % (tip, [t.strip() for _v, t in val][:20]))
    date = {"__RequestVerificationToken": tok, "TitleText": "", "ContentText_First": "",
            "ContentText_Second": "", "ContentText_Third": "", "ContentText_Fourth": "",
            "DocumentType": cod[0], "DocumentNumber": str(numar),
            "DataSemnariiTextFrom": "%s/01/01" % an, "DataSemnariiTextTo": "%s/12/31" % an,
            "PublishedInName": "", "PublishedInNumber": "", "DataPublicariiTextFrom": "",
            "DataPublicariiTextTo": "", "ActInForceOnDateTextFrom": "", "EmitentAct": "",
            "actiontype": "Căutare"}
    req = urllib.request.Request(BAZA + "/", data=urllib.parse.urlencode(date).encode(),
                                 headers={"Content-Type": "application/x-www-form-urlencoded",
                                          "Referer": BAZA + "/"})
    with op.open(req, timeout=60) as r:
        h2 = r.read().decode("utf-8", "replace")
    vazut = set()
    for m in re.finditer(r'<a[^>]+href="/Public/DetaliiDocument/(\d+)"[^>]*>(.*?)</a>', h2, re.S):
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        if t and t.lower() != "vizualizeaza" and m.group(1) not in vazut:
            vazut.add(m.group(1))
            print("   id=%-8s %s" % (m.group(1), t[:110]))
    if not vazut:
        print("   <niciun rezultat>")


def cauta_titlu(text_titlu, an_de=None, an_pana=None):
    """Cauta dupa TITLU, fara sa ceara tipul si numarul actului.

    Portalul accepta `TitleText` in acelasi formular ca restul cautarii — campul exista de la
    inceput, dar `cauta` il trimitea gol, fiindca a fost scris pentru cazul „stiu ce act vreau".
    Cazul asta e celalalt: actul e numit printr-o TRIMITERE (art.68 alin.(9) CF: „modelul si
    continutul se aproba prin ordin al ministrului finantelor publice"), deci numarul lui e chiar
    ce cauti.

    Anii sunt optionali: fara ei, portalul cauta pe tot intervalul.
    """
    h = get(BAZA + "/").decode("utf-8", "replace")
    tok = re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"', h).group(1)
    date = {"__RequestVerificationToken": tok, "TitleText": text_titlu,
            "ContentText_First": "", "ContentText_Second": "", "ContentText_Third": "",
            "ContentText_Fourth": "", "DocumentType": "", "DocumentNumber": "",
            "DataSemnariiTextFrom": ("%s/01/01" % an_de) if an_de else "",
            "DataSemnariiTextTo": ("%s/12/31" % an_pana) if an_pana else "",
            "PublishedInName": "", "PublishedInNumber": "", "DataPublicariiTextFrom": "",
            "DataPublicariiTextTo": "", "ActInForceOnDateTextFrom": "", "EmitentAct": "",
            "actiontype": "Căutare"}
    req = urllib.request.Request(BAZA + "/", data=urllib.parse.urlencode(date).encode(),
                                 headers={"Content-Type": "application/x-www-form-urlencoded",
                                          "Referer": BAZA + "/"})
    with op.open(req, timeout=60) as r:
        h2 = r.read().decode("utf-8", "replace")
    vazut = set()
    for m in re.finditer(r'<a[^>]+href="/Public/DetaliiDocument/(\d+)"[^>]*>(.*?)</a>', h2, re.S):
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        if t and t.lower() != "vizualizeaza" and m.group(1) not in vazut:
            vazut.add(m.group(1))
            print("   id=%-8s %s" % (m.group(1), t[:150]))
    if not vazut:
        print("   <niciun rezultat>")
    return sorted(vazut)


def _scrie_text(nume, t):
    """Scrie <nume>.txt + <nume>.txt.sha256 si intoarce amprenta pe TEXT.

    SE OPRESTE daca extragerea n-a produs nimic, si nu lasa in urma niciunul din cele doua fisiere.
    Motivul, masurat (R20, CONFORMITATE.md): opt artefacte de un octet au intrat in corpus pe
    13.08.2026 fiindca extragerea a produs gol si n-a spus-o. Un .txt gol e MAI RAU decat unul
    lipsa: pentru orice instrument care se uita la corpus arata ca act PREZENT si TACUT, deci
    produce o absenta falsa in loc de o lipsa vizibila. Pagina (.html + .html.sha256) ramane pe
    disc — ea chiar exista; ce lipseste e textul, si asta se spune, nu se scrie ca gol.

    A DOUA amprenta, pe TEXT. Cea pe pagina raspunde la "e acesta fisierul stocat?"; asta raspunde
    la "s-a schimbat TEXTUL?" — singura care se poate reproduce prin re-descarcare, fiindca
    portalul versioneaza URL-urile de CSS/JS in fiecare pagina.
    """
    if not t or not t.strip():
        raise ValueError(
            "EXTRAGERE GOALA pentru %r: nu scriu %s.txt si nici amprenta lui. Pagina e salvata "
            "(%s.html + .sha256); textul se aduce altfel sau lipsa se declara. Un .txt gol ar "
            "arata ca act prezent si tacut." % (nume, nume, nume))
    io.open(os.path.join(DIR, nume + ".txt"), "w", encoding="utf-8").write(t)
    amp_t = hashlib.sha256(t.encode("utf-8")).hexdigest()
    io.open(os.path.join(DIR, nume + ".txt.sha256"), "w", encoding="utf-8").write(amp_t + "\n")
    return amp_t


def adu(ident, nume):
    brut = get(BAZA + "/Public/DetaliiDocument/%s" % ident)
    amp = hashlib.sha256(brut).hexdigest()
    io.open(os.path.join(DIR, nume + ".html"), "wb").write(brut)
    io.open(os.path.join(DIR, nume + ".html.sha256"), "w", encoding="utf-8").write(amp + "\n")
    t = text(brut)
    amp_t = _scrie_text(nume, t)
    print("ADUS %s (id=%s): %d octeti html, %d caractere text" % (nume, ident, len(brut), len(t)))
    print("AMPRENTA pagina %s" % amp)
    print("AMPRENTA text   %s" % amp_t)
    print("SURSA %s/Public/DetaliiDocument/%s" % (BAZA, ident))


if __name__ == "__main__":
    if sys.argv[1] == "cauta":
        cauta(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "cauta-titlu":
        cauta_titlu(sys.argv[2], *(sys.argv[3:5]))
    elif sys.argv[1] == "adu":
        adu(sys.argv[2], sys.argv[3])
