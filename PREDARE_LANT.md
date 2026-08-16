Marca de referinta: audit tenant_004, 17.08.2026 (intrare 3777150). Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba - pct.11 poarta verde vizuala) + ARHITECT.md "FORMA COMENZII", apoi acest PREDARE_LANT.md, inainte de a incepe.

# PREDARE LANT — audit vizual tenant_004 (Distributie Profit IC SRL); verdict control fiscal REPARAT (diacritice + nume intern)

## REPORNIRE (comanda exacta, gata de dat)
Continua auditul vizual tenant_004 de la marca HEAD_IESIRE (vezi FOUR-WAY), traseu cap-coada cu Playwright (captura privita), REPARAND ce gasesti. Punctul la care am ramas: parcurs pana la Control fiscal INCLUSIV (reparat). RAMASE, NEATINSE pe traseu:
- Declaratii pana la XML + DUK PER declaratie din UI: cifrele D300/D390 mai verificate la SURSA, dar NU generat XML + rulat DUK prin ecran; D394/D100/D101/D406 neparcurse deloc.
- Operare: Facturi (firma are 9), Banca/Casa/Salariati (0 - de confirmat pe ecran ca stare goala canonica, nu fundatura).
- Provocarea deliberata a blocajelor: fisiere stricate pe straturile de import (preview, nu salvare), reg_com lipsa -> generare Bilant S1005 (mesajul e pe Date firma; de dus pana la refuzul real), campuri obligatorii goale.
- Straturile de migrare: import->preview->salvare->confirmare->ecranul unde apar datele (parcurs doar meniul; straturile individuale neparcurse).

## FOUR-WAY (ultima executie, 17.08.2026)
HEAD = origin/main = backup/lant-2026-08-17 = RUNNING = HEAD_IESIRE (SHA exact in raportul turei §11).

## LIVRAT ACEASTA TURA
Defect de COD gasit pe ecranul Control fiscal al tenant_004 (Regula 13: defect de cod, nu de firma): 13 mesaje de verdict in control_fiscal_api.py (D300/D394/D406/D100/D101/D390 necompletat + 2x "necunoscut declarat") erau proza romaneasca FARA diacritice; unul scurgea numele coloanei din baza (platitor_tva_anaf_inceput) contabilului. Reparat toate 13 la diacritice complete + inlocuit numele intern cu label-ul UI real "Data inregistrarii in scopuri de TVA". Gard nou core/test_control_fiscal_diacritice.py (RED 13 mesaje + 1 scurgere -> GREEN). DS cap.20 extins. Cele 4 registre actualizate.

## FRONT DESCHIS PRINCIPAL (nou, din aceasta tura) - clasa "erori generare declaratii fara diacritice"
Scan AST core/ (raise-inline + append la liste-mesaj) = ~218 candidati; clasa REALA (afisata contabilului) = erorile de generare dXXX (d100/d101/d112/d205/d119/bilant_api): "corecteaza in fisa", "declaratia ar fi respinsa de validator", nume XSD interne scurse "(cifR)"/"(den1)". NEreparata: distinctia user-facing-pe-ecran vs eroare-developer (legitim ASCII) NU e mecanica -> un fix fara gard ar incalca Regula 6. De facut: gard care distinge (doar modulele de generare dXXX, mesaje prefixate "Dxxx:") + diacriticizare + inlocuit nume XSD interne cu descriere umana. Detaliu: GARZI + raport 17.08 §5.

## FRONT DESCHIS - C3 (ramas din tura dd25c3e, NEATINS)
Badge stare per strat in meniuMigrarePerFirma (migrare.js) - confirmat vizual absent pe tenant_004 (randurile .mig-frand nu arata ce strat are deja date) + flag plan_conturi.sursa. Decizia lui Costin DATA: adaugi flagul. Schimbare de schema pe 28 tenanturi - test_audit_schema PICA daca template diverge -> template + migrare + rulare pe 28 scheme intr-un singur cluster. Scop complet (6 puncte) in git show dd25c3e:PREDARE_LANT.md.

## BACKLOG (din PREDARE anterior, tot deschis)
Q9 coerenta blocanta parteneri · Q18 XSD auto-select · Q7 mesaj confirmare · Q8 badge per-strat (blocat: semnal prezenta plan_conturi = flagul C3) · Q12 avertisment pe rand accesibil · Q14 CSV model x5. Constatari infra vizuala 17.08 (contrast chrome comun, title-extra motiv blocare, tinte <44px) - Costin da ordinea repararii.
