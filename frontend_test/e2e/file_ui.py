# -*- coding: utf-8 -*-
"""[lotul 14, 687] Filele ferestrelor, apăsate ca omul: o singură definiție, folosită de conftest-ul e2e și de testele din core/ cu pagină proprie."""


#: [lotul 14, 687] Date firmă, Emite factura, e-Transport și Operațiuni au câmpurile pe FILE (`.rap-tab`): o filă ascunsă are `hidden`. Omul apasă
#: fila; testul care umple / alege / apasă un câmp dintr-o filă ascunsă o apasă la fel, o singură dată, aici — nu în fiecare din cele sute de teste.
_JS_ARATA_FILA = """(sel) => { let e; try { e = document.querySelector(sel); } catch (x) { return false; }
  const f = [...document.querySelectorAll('.fereastra')].pop(); if (!e || !f || !f.contains(e)) return false;
  for (let i = 0; i < 4; i++) { const p = e.closest('[hidden]'); if (!p || !f.contains(p)) return i > 0;
    const k = p.dataset.fila || p.dataset.grup || p.dataset.frecventa || p.dataset.vedere; if (!k) return false;
    const b = f.querySelector('.rap-tab[data-fila="' + k + '"], .rap-tab[data-grup="' + k + '"], [data-vedere-r="' + k + '"]');
    if (!b) return false; b.click(); }
  return true; }"""


def _simplu(sel):
    """Selector simplu (`#id`, `.clasa`, `button[data-op='x']`): îl poate judeca JS-ul de mai sus; `:last-of-type`, `:has-text`, `text=` nu."""
    return isinstance(sel, str) and sel[:1] in "#.[abcdefghijklmnopqrstuvwxyz" and ":" not in sel.split(" ")[0][1:] and "=" not in sel.split("[")[0]


def _cu_filele_aratate(pg):
    """Împachetează `fill` / `select_option` / `check` / `click` / `wait_for_selector` / `set_input_files` ale paginii: câmpul dintr-o filă ascunsă
    își arată întâi fila (clic pe ea, ca omul)."""
    for nume in ("fill", "select_option", "check", "uncheck", "click", "set_input_files", "wait_for_selector", "dispatch_event", "inner_text",
                 "get_attribute", "input_value", "eval_on_selector"):
        orig = getattr(pg, nume)

        def mai(sel, *a, __orig=orig, __nume=nume, **k):
            if __nume == "wait_for_selector" and isinstance(sel, str) and _simplu(sel):
                # câmpul poate apărea (ecranul se randează) după ce a trecut primul gest: se reîncearcă fila până la termen, ca omul care așteaptă
                import time as _t
                termen = _t.time() + k.get("timeout", 30000) / 1000.0
                while True:
                    try:
                        if pg.evaluate(_JS_ARATA_FILA, sel):
                            pg.wait_for_timeout(120)
                    except Exception:  # noqa: BLE001
                        pass
                    try:
                        return __orig(sel, *a, **{**k, "timeout": 500})
                    except Exception:  # noqa: BLE001 — Playwright TimeoutError
                        if _t.time() > termen:
                            return __orig(sel, *a, **{**k, "timeout": 500})
            if isinstance(sel, str) and _simplu(sel):
                try:
                    if pg.evaluate(_JS_ARATA_FILA, sel):
                        pg.wait_for_timeout(120)
                except Exception:  # noqa: BLE001 — selector pe care JS nu-l știe: se lasă Playwright să-l judece
                    pass
            return __orig(sel, *a, **k)
        setattr(pg, nume, mai)
