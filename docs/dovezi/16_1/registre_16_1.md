# Registre 16.1 (lot de unelte) — în locul DECIZII.md / PREDARE_LANT.md

Perimetrul comenzii 16.1 (punctul 0) exclude orice fișier din afara scripts/, conftest.py, CLAUDE.md și docs/dovezi/16_1/ („orice alt fișier în diff = nerezolvat, nepublicat”). DECIZII.md, DEFICIENTE.md și PREDARE_LANT.md
(registre obligatorii la fiecare lot, CLAUDE.md §8) rămân deci neatinse în acest lot; conținutul lor se consemnează aici și se mută în ele de lotul următor.

## DECIZII (adăugare)
- 04.11.2026, 16.1: poarta de publicare = scripts/poarta_rulare.py (rulare completă finală + reluare), baza = docs/dovezi/16_1/baza.json (produsă din primul commit, d763f788, pe un worktree curat al lui f2e64c1b).
- Selecția veche după fișiere atinse rămâne numai ca POARTA_DIAGNOSTIC=1 și scrie DIAGNOSTIC_VERDE / DIAGNOSTIC_ROSU, pe care garda de pe main nu le primește.
- Publicarea = numai scripts/publica_lot.sh; reference-transaction, pre-push și restartul din post-commit cer PASS pe lângă VERDE.
- Jurnalul lotului: ~/iconta_nou/.lot_jurnal.log (ignorat prin `*.log`), scris de scripts/jurnal_lot.py.

## PREDARE_LANT (stare curentă)
- 16.1 gata pe ramura lucru/lot16-1 (worktree ~/iconta_lot16_1), unelte; aplicația nu s-a schimbat. Următoarea comandă: 16.2 (primul lot cu scenariul pilotului; auditul extern cerut de Costin la 04.11 16:59).
- Pentru lotul următor: producerea bazei (`sh scripts/poarta_lot.sh --baza`) din primul commit, exceptii_<lot>.txt scris de arhitect numai dacă apare reluare.
