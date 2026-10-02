# -*- coding: utf-8 -*-
"""core/corpus_continut.py — conținutul unui act din corpus, comparat PE ARTICOL, nu pe octeți.

De ce există (02.10.2026, comanda lui Costin, pct.3): la Pachetul FiscalOS §1 (01.10.2026) 54 de acte
au fost înlocuite cu forma consolidată oficială. La două ordine (OPANAF 2594/2015, OPANAF 878/2022)
portalul legislatie.just.ro publică actul în DOUĂ documente — ordinul (articolele, formularele,
convenția-cadru) și anexa-procedură, consolidată separat — iar înlocuirea a adus numai procedura.
Octeții erau oficiali și amprentați; ce lipsea era CONȚINUTUL: 10/10, respectiv 13/13 articole ale
ordinului. O amprentă SHA dovedește că fișierul e cel descărcat, nu că e actul întreg.

Ce face:
  · `unitati(cale)` — articolele și anexele unui fișier din corpus. HTML-ul portalului marchează
    structura (`S_ART`/`S_ANX`, cu `*_TTL` pentru titlu); textul (.txt) se taie pe rândurile care
    încep cu „Articolul N” / „Art. N”.
  · `clasifica(vechi, noi, text_nou)` — fiecare unitate a formei vechi e PREZENTĂ (≥ 90% din
    ferestrele ei de text apar în textul integral al formei noi — notele de modificare adăugate de
    portal și mutarea între fișierele aceluiași act nu contează), MODIFICATĂ (același titlu există
    în forma nouă și portalul declară schimbarea: „(la ZZ-LL-AAAA …)” / „Abrogat”), sau PIERDUTĂ.
  · `pierderi_act(vechi, [noi…])` — doar cele PIERDUTE, față de reuniunea fișierelor formei noi.

Limita declarată: compară structura pe care portalul o MARCHEAZĂ. Un text dintr-un act nemarcat
(fără `S_ART`, fără „Articolul N” la început de rând) nu are unități, deci nu poate „pierde”
nimic — `unitati()` întoarce lista goală și apelantul trebuie să o trateze ca NEMĂSURABIL, nu ca
„fără pierderi” (gardul o face: un act vechi cu unități și unul nou fără e chiar cazul 2594).
"""
import html
import io
import re
import unicodedata
from html.parser import HTMLParser

# Pragul de acoperire: o unitate veche e PREZENTĂ dacă ≥ 90% din ferestrele ei de text (câte
# FEREASTRA cuvinte) apar în textul integral al formei noi — notele de modificare adăugate de portal
# nu o fac „absentă”, iar mutarea între fișierele aceluiași act nu contează. Calibrat pe cele 54 de
# perechi din _inlocuite_fiscalos_2026-10-01 (core/test_corpus_continut.py).
FEREASTRA = 10
PRAG_ACOPERIRE = 0.90
# Portalul declară o schimbare a articolului în textul lui: „(la 15-12-2023, Articolul 7 ... a fost
# abrogat/modificat ...)" sau corpul „Abrogat.”. Un articol cu același titlu care poartă declarația
# e MODIFICAT (evoluție legislativă), nu pierdut.
_RE_DECLARATIE = re.compile(r"\(la \d{2}-\d{2}-\d{4}|\babrogat")

_TIPURI = {"S_ART": "articol", "S_ANX": "anexa"}
_RE_ART_TXT = re.compile(r"^\s*(Articolul|Art\.)\s*([0-9]+(?:\^[0-9]+)?|[IVXLC]+)\b", re.M)


def _norm(s):
    s = unicodedata.normalize("NFKD", html.unescape(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("ş", "s").replace("ţ", "t")
    return re.sub(r"\s+", " ", s).strip()


def _titlu(s):
    """„Articolul 3” / „Art. 3” / „Anexa nr. 2” -> cheie comparabilă („art 3”, „anexa 2”)."""
    t = _norm(s)
    m = re.match(r"(articolul|art\.?)\s*([0-9]+(?:\^[0-9]+)?|[ivxlc]+)", t)
    if m:
        return "art " + m.group(2)
    m = re.match(r"anexa\s*(nr\.?)?\s*([0-9a-z]+)?", t)
    if m:
        return "anexa " + (m.group(2) or "")
    return t[:40]


class _Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.adanc = 0
        self.deschise = []  # [tip, adancime, titlu_parti, text_parti, in_titlu_la_adancime]
        self.gata = []

    def handle_starttag(self, tag, attrs):
        if tag != "span":
            return
        self.adanc += 1
        cls = dict(attrs).get("class") or ""
        if cls in _TIPURI:
            self.deschise.append({"tip": _TIPURI[cls], "ad": self.adanc, "ttl": [], "txt": [], "ttl_ad": None})
        elif cls in ("S_ART_TTL", "S_ANX_TTL") and self.deschise:
            u = self.deschise[-1]
            if u["ttl_ad"] is None and not u["ttl"]:
                u["ttl_ad"] = self.adanc

    def handle_endtag(self, tag):
        if tag != "span":
            return
        for u in self.deschise:
            if u["ttl_ad"] == self.adanc:
                u["ttl_ad"] = -1
        while self.deschise and self.deschise[-1]["ad"] == self.adanc:
            u = self.deschise.pop()
            self.gata.append(u)
        self.adanc -= 1

    def handle_data(self, data):
        for u in self.deschise:
            u["txt"].append(data)
            if u["ttl_ad"] not in (None, -1):
                u["ttl"].append(data)


def unitati(cale):
    """Lista de unități {tip, titlu, cheie, text} ale fișierului, în ordinea apariției."""
    brut = io.open(cale, "rb").read().decode("utf-8", errors="replace")
    if cale.endswith((".html", ".htm")):
        p = _Parser()
        p.feed(brut)
        p.close()
        out = []
        for u in p.gata:
            ttl = "".join(u["ttl"]).strip()
            txt = _norm(" ".join(u["txt"]))   # spațiu între segmente: „…impozitul</span><span>Articolul 3”
            out.append({"tip": u["tip"], "titlu": ttl, "cheie": _titlu(ttl), "text": txt})
        return out
    poz = [(m.start(), m.group(0)) for m in _RE_ART_TXT.finditer(brut)]
    out = []
    for i, (st, ttl) in enumerate(poz):
        sf = poz[i + 1][0] if i + 1 < len(poz) else len(brut)
        out.append({"tip": "articol", "titlu": ttl.strip(), "cheie": _titlu(ttl), "text": _norm(brut[st:sf])})
    return out


def text_integral(cale):
    """Tot textul fișierului, normalizat (pentru acoperire)."""
    brut = io.open(cale, "rb").read().decode("utf-8", errors="replace")
    if cale.endswith((".html", ".htm")):
        p = _TextParser()
        p.feed(brut)
        p.close()
        brut = " ".join(p.parti)
    return _norm(brut)


class _TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parti = []
        self._sari = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._sari += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._sari:
            self._sari -= 1

    def handle_data(self, data):
        if not self._sari:
            self.parti.append(data)


def _cuvinte(text):
    """Cuvintele alfanumerice (punctuația și spațierea diferă între randări — „12(1)” / „12 (1)”,
    „xvi-xx ,” / „xvi-xx,” — fără să fie diferență de conținut)."""
    return re.findall(r"[0-9^]+|[a-z]+", text)


def _ferestre(text):
    cuv = _cuvinte(text)
    if len(cuv) <= FEREASTRA:
        return [" ".join(cuv)] if cuv else []
    return [" ".join(cuv[i:i + FEREASTRA]) for i in range(0, len(cuv) - FEREASTRA + 1, FEREASTRA)]


class Text:
    """Textul formei noi, indexat O DATĂ: toate ferestrele de FEREASTRA cuvinte, la orice decalaj. O căutare de
    subșir pe tot textul pentru fiecare unitate a Codului fiscal costa minute; un set costă secunde."""

    def __init__(self, text):
        cuv = _cuvinte(text)
        self.plan = " " + " ".join(cuv) + " "
        self.ngr = {" ".join(cuv[i:i + FEREASTRA]) for i in range(max(len(cuv) - FEREASTRA + 1, 0))}

    def contine(self, fereastra):
        if fereastra.count(" ") + 1 == FEREASTRA:
            return fereastra in self.ngr
        return " " + fereastra + " " in self.plan      # unitate scurtă (< FEREASTRA cuvinte)


def acoperire(unitate, text_nou):
    """Fracțiunea din ferestrele de text ale unității care apar în `text_nou` (șir sau `Text`)."""
    f = _ferestre(unitate["text"])
    if not f:
        return 1.0
    t = text_nou if isinstance(text_nou, Text) else Text(text_nou)
    return sum(1 for x in f if t.contine(x)) / len(f)


def clasifica(vechi, noi, text_nou):
    """Pentru fiecare unitate din `vechi`: (unitate, stare, acoperire), stare ∈
    PREZENT (conținutul e în forma nouă) · MODIFICAT (același titlu există în forma nouă și portalul
    declară schimbarea: notă „(la ZZ-LL-AAAA …)” sau „Abrogat”) · PIERDUT (niciuna)."""
    text_nou = text_nou if isinstance(text_nou, Text) else Text(text_nou)
    pe_cheie = {}
    for u in noi:
        pe_cheie.setdefault((u["tip"], u["cheie"]), []).append(u)
    out = []
    for u in vechi:
        a = acoperire(u, text_nou)
        if a >= PRAG_ACOPERIRE:
            out.append((u, "PREZENT", a))
            continue
        frati = pe_cheie.get((u["tip"], u["cheie"]), [])
        if any(_RE_DECLARATIE.search(x["text"]) for x in frati):
            out.append((u, "MODIFICAT", a))
        else:
            out.append((u, "PIERDUT", a))
    return out


def pierderi_act(vechi_cale, noi_cai):
    """Unitățile PIERDUTE ale formei vechi față de reuniunea fișierelor formei noi a actului."""
    noi, text = [], []
    for c in noi_cai:
        noi += unitati(c)
        text.append(text_integral(c))
    return [(u, a) for u, st, a in clasifica(unitati(vechi_cale), noi, "\n".join(text)) if st == "PIERDUT"]
