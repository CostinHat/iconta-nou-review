# fix_fir_doar_parinti.py — firul din antet arata DOAR parintii (provenienta);
# pasul curent traieste o singura data: ca titlu (h2) in corp.
# /opt/iconta/venv/bin/python3 fix_fir_doar_parinti.py  (fara restart)
import shutil, os
CALE = os.path.expanduser("~/iconta_nou/static/js/navigator.js")
MARKER = "fir_doar_parinti_v1"
with open(CALE, encoding="utf-8") as f:
    t = f.read()
assert MARKER not in t, "deja aplicat"
V = '''    const titluAcum = sus.titluCurent || sus.titlu || "";
    const drumHtml = drum.map((d) =>
      `<button class="fir-veriga" data-fer="${d.fereastra ?? ''}" data-pas="${d.pas ?? ''}">${String(d.text).replace(/[<>&]/g, "")}</button><span class="fir-sep" aria-hidden="true">›</span>`
    ).join("") + (titluAcum ? `<span class="fir-acum">${String(titluAcum).replace(/[<>&]/g, "")}</span>` : "");'''
N = '''    const drumHtml = drum.map((d, i) =>
      `<button class="fir-veriga" data-fer="${d.fereastra ?? ''}" data-pas="${d.pas ?? ''}">${String(d.text).replace(/[<>&]/g, "")}</button>` +
      (i < drum.length - 1 ? `<span class="fir-sep" aria-hidden="true">›</span>` : "")
    ).join("");  // ''' + MARKER + ''': doar parintii; pasul curent = titlul din corp'''
assert t.count(V) == 1, "ANCORA drum: %d" % t.count(V)
t = t.replace(V, N)
t += "\n// " + MARKER + "\n"
shutil.copy(CALE, CALE + ".bak_" + MARKER)
with open(CALE, "w", encoding="utf-8") as f:
    f.write(t)
print("OK:", MARKER)
