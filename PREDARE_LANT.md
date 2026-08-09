Citeste CLAUDE.md §2.2 (structura raportului) si §2.3 (lant, siguranta, limba), si ARHITECT.md "FORMA COMENZII" (forma comenzii primite - 7 puncte), inainte de a incepe.

# PREDARE_LANT — STARE CURENTA

Se SUPRASCRIE la fiecare publicare (al 5-lea pas, CLAUDE.md §2.3 pct.10). NU e jurnal - jurnalul e ISTORIC.md.
Ritual pornire: `ssh iconta 'cd ~/iconta_nou && git log -1 && git status --porcelain'`.

## (a) Four-way de la ultima executie
HEAD = origin/main = backup/lant-2026-08-09 = RUNNING = **d217981** (tura 17: diacritice in mesajele importului de solduri).
Commit 2026-08-09 21:09:52 EEST; serviciu `iconta-nou` pornit 21:15:40 EEST (start > commit); `/tenants` -> 401 local (8010) si public (iconta.eu); tree curat.
(Tura 18, aceasta, e doc-only: introduce PREDARE_LANT ca al 5-lea pas de publicare in CLAUDE.md §2.3 pct.10 + §2.2 pct.11; comportament RUNNING identic, four-way-ul ei e in raportul turei 18.)

## (b) Fronturi deschise (cu blocajul fiecaruia)
1. **Test fir de intrare cabinet nou** — ACTIV. Cabinet de test izolat "CABINET TEST FIR INTRARE SRL" (public.accounting_firms id=4163), cont admin_firma `fir-intrare@prisma-cont.test` (user 6504; parola doar in raportul turei 15, nu in git). 4 firme: ALFA=tenant_013 (8396), BETA=tenant_014 (8397), GAMA=tenant_015 (8398), DELTA=tenant_016 (8399). `seed_profil` aplicat pe toate 4 (vector fiscal corect). Fisierele + ordinea + verdictele asteptate: `~/date_test_cabinet/README.md`; runner seed: `~/date_test_cabinet/aplica.py profil|luna`.
   BLOCAJ: Costin importa prin UI (CSV migrare per firma + XML e-Factura); la "gata XML" se ruleaza `~/iconta_nou/venv/bin/python3 ~/date_test_cabinet/aplica.py luna` (note validate, salarii, dividende, patch facturi). Cabinetul REAL cu 12 firme = neatins.

2. **E3_97 (pensie ocupationala, Legea 1/2020)** — build oprit pe stop point. Emisia corecta cere subsistemul art.76(4^1) (plafon lunar 33% pe suma a-j + ordine), care lipseste din app. Curs+cumul confirmate verbatim (art.78(2)(a) BNR ultima zi a lunii; OUG 8/2026 art.10). Metoda B fixata (app aplica plafonul, contabilul introduce brutul).
   BLOCAJ: decizie de scope Costin (E3_97 izolat vs subsistem complet).

3. **D101 scadenta: lege vs validator INVERS** — validatorul DUK (R17) e exact invers fata de CF art.42; codul urmeaza validatorul.
   BLOCAJ: decizie de produs Costin.

4. **Descoperiri din proba de date de test (de tratat separat, neprogramate)** — D710 nederivabil din date (`_DOAR_API`, doar din corp de cerere); D300 pe achizitii (IC R5 / taxare inversa R12-R27 / deductibil 9-5%) nu se deriva din facturi si n-are stocare importabila -> D300 subevaluat SI auto-declanseaza rosul propriu D390-vs-D300; D406 lunar din dispatcher fara Active/Stocuri/Plati (mijloacele fixe necablate in `d406.genereaza`).

## (c) Ce e in lucru acum
Testarea firului de intrare (front 1): Costin parcurge importul prin UI in cabinetul 4163; eu rulez seed-urile la checkpoint-uri (seed_profil DONE; seed_luna la "gata XML"). Turele recente 13-17 au reparat, parcurgand firul: izolare pe cheie API (gard), cross-check TVA D300 mort (semnatura veche), doua "forme care spun altceva" (balanta straina "echilibrata" + "La zi" cu intarziati), diacritice in mesajele solduri.

## (d) Ce urmeaza
1. Costin: importa CSV migrare (per firma) + XML e-Factura -> anunta "gata XML".
2. Eu: `aplica.py luna`.
3. Costin: deschide Control fiscal + Audit preluare + genereaza declaratiile -> confirma verdictele din README (ALFA/BETA verde; GAMA migrare ROSU parteneri + GRI istoric + ROSU restante D300/D112; DELTA luna ROSU cota19/D300 necontabilizat/D390 + trezorerie negativa + D112 blocat).
4. Reia parcurgerea; orice "forma care spune altceva decat faptul" -> comanda de reparatie, ca turele 16-17.
