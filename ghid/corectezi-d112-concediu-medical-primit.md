---
title: "Cum corectezi D112 pentru un concediu medical primit cu întârziere?"
description: "Ce se întâmplă în D112 când un episod de concediu medical se prelungește peste luna deja declarată — regula introdusă de OUG 89/2025, valabilă din 1 iulie 2026."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Cum corectezi D112 pentru un concediu medical primit cu întârziere?

Un caz frecvent: un salariat are un episod de boală care începe într-o lună și se prelungește în luna următoare cu un nou certificat, iar D112 pentru prima lună a fost deja depusă cu un procent provizoriu, calculat doar pe zilele știute până atunci. Din 1 iulie 2026, legea schimbă modul în care se rezolvă această situație — și nu mai cere o declarație rectificativă.

## Temeiul legal

::: ghid-temei
„Pentru situațiile în care perioada de incapacitate temporară de muncă pentru care s-au eliberat certificatele de concediu medical [...] se prelungește în luna următoare și conduce la depășirea perioadelor prevăzute la lit. a) și b) ale aceluiași alineat, diferențele de indemnizații pentru incapacitate temporară de muncă cauzată de boli obișnuite sau de accidente în afara muncii, rezultate ca urmare a recalculării și aferente lunii anterioare celei în care are loc această operațiune, se includ în veniturile lunii în care sunt determinate și se declară în Declarația privind obligațiile de plată a contribuțiilor sociale, impozitului pe venit și evidența nominală a persoanelor asigurate [...] aferentă aceleiași luni."
— OUG 158/2005, art. 17 alin. (1^2), introdus prin OUG 89/2025 art. VII, în vigoare de la 1 iulie 2026 (sursă: anaf_surse/oug_89_2025.txt)
:::

Mecanismul, explicat pas cu pas:

- Procentul indemnizației de boală obișnuită (55/65/75%) depinde de **numărul total de zile din episod**, nu doar din certificatul unei singure luni — un episod care depășește pragul de 7 sau de 14 zile poate schimba retroactiv procentul aplicat zilelor deja plătite în luna anterioară.
- **Înainte de 1 iulie 2026**, corecția acestei diferențe se făcea prin **declarație rectificativă** pentru luna anterioară.
- **De la 1 iulie 2026**, regula se schimbă: diferența de indemnizație rezultată din recalculare **nu se mai declară printr-o rectificativă a lunii anterioare** — se include direct în veniturile lunii curente (cea în care s-a stabilit diferența) și se declară în D112 aferentă acelei luni, ca sumă suplimentară.
- Regula se aplică doar diferențelor de la boală obișnuită sau accident în afara muncii (codul 01) — nu și celorlalte coduri de indemnizație, care au procente fixe, nedependente de durata cumulată.

## Ce se greșește în practică

- Se continuă să se depună declarație rectificativă pentru luna anterioară, deși evenimentul are loc după 1 iulie 2026, când legea cere includerea diferenței în luna curentă.
- Se aplică regula nouă (fără rectificativă) și pentru episoade recalculate înainte de 1 iulie 2026, deși norma prevede expres că se aplică inclusiv episoadelor începute înainte de această dată, dar doar pentru recalculările efectuate după ea — nu retroactiv pentru rectificative deja depuse.
- Se omite complet recalcularea procentului la primirea certificatului de continuare, plătindu-se zilele din prima lună la procentul inițial, fără ajustare.

## Ce face iConta.eu

Motorul de calcul (`core/salarizare.py`) calculează procentul unui certificat de boală obișnuită pe baza datei episodului inițial, iar contabilul poate transmite numărul de zile deja acumulate din episod, astfel încât un certificat de continuare primește procentul corect al episodului cumulat. Aplicația nu determină însă automat „diferența" de indemnizație de recalculat pentru luna anterioară și nu marchează singură dacă acea diferență trebuie declarată ca rectificativă sau inclusă în luna curentă — regimul aplicabil (pre- sau post-1 iulie 2026, vezi mai sus) trebuie verificat și aplicat manual de contabil la depunerea D112.

[iConta.eu](/)
