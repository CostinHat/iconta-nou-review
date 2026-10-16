// cate(n, singular, plural) — SINGURUL loc din interfață care pune un număr lângă substantivul lui: „1 notă”, „3 note”,
// „20 de note”, „101 note”, „120 de note”, „0 note”. Oglinda lui `core/common.py::cate` (aceeași regulă, aceeași tabelă de valori
// în `core/test_plural_dupa_numar.py`): româna cere „de” când numărul se termină în 00 sau în 20–99. Unde substantivul are un
// adjectiv acordat, se dau formele complete („factură emisă” / „facturi emise”). Comanda Costin 15.10.2026 (261, 263, „1 angajați”);
// gard PLURAL_FIX (`core/test_plural_dupa_numar.py`).
// dupaNumar(n, singular, plural) — numai ce urmează numărului („notă”, „de note”), pentru un număr pus separat (`<b>${n}</b> …`).
// Un număr cu zecimale („12,5 zile”) ia pluralul fără „de” — se citește după ultima cifră; ca în `common.cate`.
export function dupaNumar(n, singular, plural) {
  if (!Number.isInteger(Number(n) || 0)) return plural;
  const k = Math.trunc(Number(n) || 0);
  if (k === 1) return singular;
  const r = ((k % 100) + 100) % 100;   // ca `%` din Python (aceeași regulă și pentru negative)
  return `${k && (r === 0 || r >= 20) ? "de " : ""}${plural}`;
}
export function cate(n, singular, plural) {
  const x = Number(n) || 0;
  return `${Number.isInteger(x) ? x : String(x).replace(".", ",")} ${dupaNumar(n, singular, plural)}`;
}
