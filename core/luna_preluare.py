# -*- coding: utf-8 -*-
"""LUNA PRELUĂRII firmei în iConta — de la ea se numără restanțele în Control fiscal (decizia Costin 08.10.2026 U2) — PUR.

[08.10.2026, decizia Costin §6 pct.4, verbatim în DECIZII] „Luna preluării: editabilă în Date firmă, cu valoarea dedusă ca propunere,
dar niciodată după luna primei note. Recalculează propunerea pentru F3 (are note din iunie). Schimbarea se jurnalizează.”

  * DEDUSĂ: ziua de după data soldurilor de preluare (`solduri_initiale.data_referinta` — soldurile sunt „la” acea dată, deci evidența
    în iConta începe a doua zi), iar fără ea luna în care firma a fost adăugată în iConta (`tenants.creat_la`).
    *INTERPRETARE CU TEMEI (de produs, nu fiscală):* cele două date sunt singurele fapte care descriu preluarea.
  * PROPUNEREA = dedusa, dar niciodată după luna PRIMEI NOTE: o notă scrisă în iConta dovedește că evidența era deja aici (F3: adăugată
    în octombrie, note din iunie -> 06/2026). „Prima notă” = cea mai veche notă din jurnal, oricare i-ar fi starea — și ciorna e scrisă
    în iConta.
  * EFECTIVĂ = luna salvată în Date firmă (`firma_profil.luna_preluare`), altfel propunerea — dar NICIODATĂ după luna primei note.
  * Luna salvată nu poate fi după luna primei note (refuz lângă câmp, `eroare`). Jurnalul: `firma_profil_api.CAMPURI_JURNAL`.
  * [lotul 12, deficiența 147: „«Luna preluării» editabilă, cu propunere și limită”] Refuzul de la salvare nu ajunge: o notă mai veche
    scrisă DUPĂ salvare (luna salvată 08/2026, apoi o notă din 06/2026) lăsa luna efectivă după prima notă — Control fiscal număra
    restanțele abia din 08/2026, deși jurnalul arăta evidența în iConta.eu din 06/2026. Limita se aplică și la citire: luna efectivă e cea
    salvată, plafonată la luna primei note (`efectiva`, `de_unde`); luna salvată rămâne în bază cum a scris-o omul, iar Date firmă spune
    că s-a plafonat (`plafonata`).
"""
import datetime

CAMP = "luna_preluare"

# [15.1-E3, 724.2] REGULA ALEASĂ: luna preluării nu poate fi înaintea lunii în care a fost înființată firma (`firma_profil.data_infiintare`, Date firmă) — o firmă
# nu are evidență înainte să existe. Dacă data înființării nu se știe, regula nu se aplică. Data vine din Date firmă (câmpul „Data înființării”), nu din altă parte;
# o notă mai veche decât înființarea (F2: înființată 15.03.2026, o notă din 12/2025) nu mută luna preluării înaintea ei, iar luna salvată mai veche se ridică la
# luna înființării. Exemplul care a arătat defectul: F2, înființată 15.03.2026, intrată în iConta 21.09.2026 — textul spunea 12/2025.


def _luna(d):
    return (d.year, d.month) if d else None


def deduse(creat_la, data_solduri=None):
    """(an, luna) dedusă din soldurile de preluare sau din data adăugării; None dacă nu se știe niciuna."""
    if data_solduri:
        return _luna(data_solduri + datetime.timedelta(days=1))
    return _luna(creat_la)


def _nu_inainte(luna, infiintare):
    """[724.2] `luna` ((an, lună) sau None), ridicată la luna înființării firmei când e mai veche."""
    i = _luna(infiintare)
    return max(luna, i) if luna and i else luna


def propunere(creat_la, data_solduri=None, prima_nota=None, infiintare=None):
    """Dedusa, plafonată la luna primei note, niciodată înaintea lunii înființării."""
    d, p = deduse(creat_la, data_solduri), _luna(prima_nota)
    return _nu_inainte(min(d, p) if d and p else d or p, infiintare)


def plafonata(salvata, prima_nota):
    """[147] Luna salvată e după luna primei note (nota mai veche a fost scrisă după salvare): luna efectivă e a primei note."""
    return bool(_luna(salvata) and _luna(prima_nota) and _luna(salvata) > _luna(prima_nota))


def efectiva(salvata, creat_la, data_solduri=None, prima_nota=None, infiintare=None):
    """Luna salvată în Date firmă, altfel propunerea — niciodată după luna primei note (`plafonata`) și niciodată înaintea lunii înființării (724.2)."""
    if plafonata(salvata, prima_nota):
        return _nu_inainte(_luna(prima_nota), infiintare)
    return _nu_inainte(_luna(salvata), infiintare) or propunere(creat_la, data_solduri, prima_nota, infiintare)


def din_fapte(fapte, creat_la=None):
    """Luna efectivă din faptele preluării (`repo_firma_profil.fapte_preluare`): UN SINGUR apel pentru toate locurile care o socotesc (Control fiscal, termene, SPV,
    portal, bilanț, Date firmă) — regula înființării (724.2) nu se mai poate uita într-unul dintre ele. `creat_la` = data adăugării, dacă faptele n-o au."""
    return efectiva(fapte.get("salvata"), fapte.get("creat_la") or creat_la, fapte.get("data_solduri"), fapte.get("prima_nota"), fapte.get("infiintare"))


def de_unde_fapte(fapte, creat_la=None):
    """Textul „de unde vine luna” pentru aceleași fapte (Control fiscal, Date firmă)."""
    return de_unde(fapte.get("salvata"), fapte.get("creat_la") or creat_la, fapte.get("data_solduri"), fapte.get("prima_nota"), fapte.get("infiintare"))


def eroare(luna, prima_nota, infiintare=None):
    """Mesajul refuzului, sau None: luna preluării nu poate fi după luna primei note și nici înaintea lunii înființării firmei (724.2)."""
    if luna and infiintare and _luna(luna) < _luna(infiintare):
        return ("Luna preluării nu poate fi înaintea lunii înființării firmei (%02d/%d). Alege %02d/%d sau o lună mai nouă." % (
            infiintare.month, infiintare.year, infiintare.month, infiintare.year))
    if luna and prima_nota and _luna(luna) > _luna(prima_nota):
        return ("Luna preluării nu poate fi după luna primei note din jurnal (%02d/%d): nota arată că evidența era deja în iConta.eu. "
                "Alege %02d/%d sau o lună mai veche." % (prima_nota.month, prima_nota.year, prima_nota.month, prima_nota.year))
    return None


def din_text(v):
    """„AAAA-LL” (câmpul lună) -> prima zi a lunii; gol -> None; altfel ValueError."""
    v = str(v or "").strip()
    if not v:
        return None
    try:
        return datetime.date(int(v[:4]), int(v[5:7]), 1) if len(v) == 7 and v[4] == "-" else datetime.date.fromisoformat(v).replace(day=1)
    except ValueError:
        raise ValueError("Luna preluării se scrie ca lună și an (ex. 06/2026).")


def de_unde(salvata, creat_la, data_solduri=None, prima_nota=None, infiintare=None):
    """[deficiența 232, comanda Costin 12.10.2026: „Stabilește din datele firmei care e luna preluării și fă cele două locuri
    consecvente.”] Faptul din care vine luna EFECTIVĂ, ca text pentru ecran — aceeași ordine ca `efectiva` / `propunere`."""
    zi = (lambda d: "%02d.%02d.%d" % (d.day, d.month, d.year))
    inf = _luna(infiintare)
    d0, p0 = deduse(creat_la, data_solduri), _luna(prima_nota)
    brut = min(d0, p0) if d0 and p0 else d0 or p0
    if inf and not _luna(salvata) and brut and brut < inf:   # [724.2] propunerea ar cădea înaintea înființării: luna înființării
        return "luna înființării firmei, %s (data soldurilor sau prima notă din jurnal ar fi înaintea ei)" % zi(infiintare)
    if plafonata(salvata, prima_nota):   # [147] luna aleasă e după prima notă: se socotește luna notei
        return "luna primei note din jurnal, %s (luna aleasă în Date firmă, %02d/%d, e după ea)" % (zi(prima_nota), salvata.month,
                                                                                                    salvata.year)
    if _luna(salvata):
        return "aleasă în Date firmă"
    d, p = deduse(creat_la, data_solduri), _luna(prima_nota)
    if p and (not d or p < d):
        return "luna primei note din jurnal, %s" % zi(prima_nota)
    if data_solduri:
        return "ziua de după soldurile de preluare, %s" % zi(data_solduri)
    if creat_la:
        return "luna adăugării firmei în iConta.eu, %s" % zi(creat_la)
    return None


def inainte(an, luna, preluare):
    """[08.10, decizia Costin U2; lotul 10, deficiența 432] Obligația pe perioada (an, luna) e dinaintea lunii preluării: perioada unei
    declarații trimestriale / anuale e luna ei de ancoră (3/6/9/12; anuala = 12), deci un trimestru care cuprinde luna preluării NU e
    „înainte”. `preluare` = (an, lună) sau None (nu se știe -> nimic nu e „înainte”). Predicatul UNIC — Control fiscal
    (`control_fiscal_api.separa_inainte_de_preluare`) și lista termenelor (`firma_rezumat._termene_una_firma`) îl folosesc pe acesta."""
    return bool(preluare) and (an, luna or 12) < tuple(preluare)


def luna_dinainte(luna):
    """(an, lună) -> luna precedentă: ultima perioadă „înainte de preluare”."""
    return (luna[0] - 1, 12) if luna[1] == 1 else (luna[0], luna[1] - 1)


def stare(fapte):
    """`fapte` = `repo_firma_profil.fapte_preluare` -> {salvata, propunere, efectiva, prima_nota} ca „AAAA-LL” (pentru ecran) și
    `plafonata` (147: luna salvată e după prima notă, deci efectiva e luna primei note)."""
    s, c, d, p, i = fapte.get("salvata"), fapte.get("creat_la"), fapte.get("data_solduri"), fapte.get("prima_nota"), fapte.get("infiintare")
    t = (lambda x: "%04d-%02d" % x if x else None)
    return {"salvata": t(_luna(s)), "propunere": t(propunere(c, d, p, i)), "efectiva": t(efectiva(s, c, d, p, i)),
            "prima_nota": t(_luna(p)), "plafonata": plafonata(s, p), "infiintare": t(_luna(i))}
