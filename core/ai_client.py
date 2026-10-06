"""
core/ai_client.py — wrapper subtire peste API-ul Claude (Anthropic).
Refolosibil: pachete lunare (narativ), si ulterior stratul 5 Raportari.
Citeste ANTHROPIC_API_KEY din mediu. Daca lipseste -> intoarce disponibil()=False,
ca apelantul sa ofere fallback manual (nu crapa aplicatia).
"""
import os

_MODEL = "claude-sonnet-4-6"  # echilibru calitate/cost pentru narativ


import re as _re

# [lot 06.10 pct.14, comanda Costin 06.10.2026] Textul generat de model ajunge pe ecrane și în emailuri ca TEXT SIMPLU (esc +
# rânduri păstrate), nu ca markdown — deci marcajele lui de formatare (`**`, `__`, `*cuvânt*`, `# titlu`) apar brute.
# `text_simplu` le scoate; e SURSA UNICĂ a regulii pentru orice text AI afișat (povestea lunii, analiza tiparelor, răspunsul
# la o raportare). Un asterisc care nu e marcaj (`2 * 3`, `4*5`) rămâne.
_MARCAJ_DUBLU = _re.compile(r"\*\*|__")
_MARCAJ_SIMPLU = _re.compile(r"(?<![\w*])\*(?=\S)([^*\n]+?)(?<=\S)\*(?![\w*])")
_TITLU_MD = _re.compile(r"^[ \t]{0,3}#{1,6}[ \t]+", _re.M)


def text_simplu(text):
    if not text:
        return text
    return _MARCAJ_DUBLU.sub("", _MARCAJ_SIMPLU.sub(r"\1", _TITLU_MD.sub("", text)))


def disponibil():
    """True daca exista cheie configurata."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def genereaza_text(prompt, sistem=None, max_tokens=1200, temperatura=0.7, model=None):
    """Trimite un prompt la Claude, intoarce textul raspunsului.
    Ridica RuntimeError daca nu e disponibil sau apelul esueaza (apelantul prinde)."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY lipseste")
    try:
        from anthropic import Anthropic
    except Exception as e:
        raise RuntimeError("libraria anthropic indisponibila: %s" % e)

    client = Anthropic(api_key=key)
    kwargs = {
        "model": model or _MODEL,
        "max_tokens": int(max_tokens),
        "temperature": float(temperatura),
        "messages": [{"role": "user", "content": prompt}],
    }
    if sistem:
        kwargs["system"] = sistem
    resp = client.messages.create(**kwargs)
    # raspunsul e o lista de blocuri; concatenam textul
    parti = []
    for bloc in (resp.content or []):
        t = getattr(bloc, "text", None)
        if t:
            parti.append(t)
    return "".join(parti).strip()


def citeste_imagini(lista_imagini, prompt, max_tokens=800):
    """lista_imagini = [(bytes, media_type), ...] — mai multe poze, un raspuns."""
    import base64, anthropic, os
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    continut = [{"type": "image",
                 "source": {"type": "base64", "media_type": mt,
                            "data": base64.standard_b64encode(b).decode()}}
                for b, mt in lista_imagini]
    continut.append({"type": "text", "text": prompt})
    r = client.messages.create(model="claude-sonnet-4-6", max_tokens=max_tokens,
                               messages=[{"role": "user", "content": continut}])
    return "".join(bl.text for bl in r.content if bl.type == "text")
