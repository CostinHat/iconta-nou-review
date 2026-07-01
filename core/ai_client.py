"""
core/ai_client.py — wrapper subtire peste API-ul Claude (Anthropic).
Refolosibil: pachete lunare (narativ), si ulterior stratul 5 Raportari.
Citeste ANTHROPIC_API_KEY din mediu. Daca lipseste -> intoarce disponibil()=False,
ca apelantul sa ofere fallback manual (nu crapa aplicatia).
"""
import os

_MODEL = "claude-sonnet-4-6"  # echilibru calitate/cost pentru narativ


def disponibil():
    """True daca exista cheie configurata."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def genereaza_text(prompt, sistem=None, max_tokens=1200, temperatura=0.7):
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
        "model": _MODEL,
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
