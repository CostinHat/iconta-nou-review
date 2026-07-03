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


def citeste_imagine(imagine_bytes, media_type, prompt, max_tokens=800):
    """Trimite o imagine la Claude si intoarce textul raspunsului."""
    import base64, anthropic, os
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    b64 = base64.standard_b64encode(imagine_bytes).decode()
    r = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            {"type": "text", "text": prompt},
        ]}],
    )
    return "".join(b.text for b in r.content if b.type == "text")


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
