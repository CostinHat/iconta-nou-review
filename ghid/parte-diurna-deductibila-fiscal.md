---
title: "Ce parte din diurnă este deductibilă fiscal?"
description: "Cum se împarte diurna de delegare/detașare în parte neimpozabilă și parte impozabilă, conform plafonului din Codul fiscal."
published: 2026-09-26
modified: 2026-09-26
poarta: v1
---

# Ce parte din diurnă este deductibilă fiscal?

Diurna acordată unui salariat aflat în delegare sau detașare nu este integral scutită de impozit. Legea stabilește un plafon zilnic: partea de sub plafon nu e venit impozabil, iar partea care depășește plafonul devine venit salarial obișnuit, supus impozitului și contribuțiilor. Diferența dintre cele două nu ține de bunul-simț al contabilului, ci de o formulă precisă din Codul fiscal.

## Temeiul legal

::: ghid-temei
„k) indemnizația de delegare, indemnizația de detașare, [...] precum și orice alte sume de aceeași natură, altele decât cele acordate pentru acoperirea cheltuielilor de transport și cazare, primite de salariați potrivit legislației în materie, pe perioada desfășurării activității în altă localitate, în țară sau în străinătate, în interesul serviciului, pentru partea care depășește plafonul neimpozabil stabilit astfel: (i) în țară, 2,5 ori nivelul legal stabilit pentru indemnizație, prin hotărâre a Guvernului, pentru personalul autorităților și instituțiilor publice, în limita a 3 salarii de bază corespunzătoare locului de muncă ocupat; [...] (ii) în străinătate, 2,5 ori nivelul legal stabilit pentru diurnă, prin hotărâre a Guvernului, pentru personalul român trimis în străinătate pentru îndeplinirea unor misiuni cu caracter temporar, în limita a 3 salarii de bază corespunzătoare locului de muncă ocupat."
— Codul fiscal, art. 76 alin. (2) lit. k) (sursă: anaf_surse/cod_fiscal_227_2015_consolidat.txt)
:::

Din text rezultă o formulă cu două praguri, se aplică cel mai mic dintre ele:

- **Pragul 1** — 2,5 × nivelul legal al indemnizației/diurnei stabilit prin hotărâre de guvern (23 lei/zi pentru intern, de la 1 aprilie 2023, conform Ordinului MF 1235/2023).
- **Pragul 2** — 3 salarii de bază ale angajatului, raportate la zilele lucrătoare din luna respectivă și înmulțite cu numărul de zile din perioada delegării.
- **Plafonul zilnic neimpozabil** este *minimul* dintre cele două praguri — nu suma lor, nu media lor.
- Tot ce depășește acest plafon zilnic devine **venit salarial impozabil**: se supune impozitului pe venit, CAS și CASS, exact ca un spor de salariu.
- Cheltuielile de transport și cazare, decontate separat pe bază de documente justificative, **nu intră deloc în acest calcul** — plafonul privește doar indemnizația/diurna propriu-zisă.

## Ce se greșește în practică

- Se tratează toată diurna plătită ca fiind automat neimpozabilă, fără a verifica dacă depășește plafonul de 2,5×.
- Se ignoră al doilea prag (3 salarii de bază/zile lucrătoare) — pentru un salariu mic, acesta poate fi sub pragul de 2,5×, deci el devine plafonul efectiv, nu 23 de lei.
- Se calculează plafonul cu diurna bugetară valabilă azi, chiar și pentru deplasări din perioade vechi, când valoarea legală era alta (20 lei până la 31.03.2023).
- Se confundă indemnizația de delegare (art. 76 alin. (2) lit. k) cu alte beneficii neimpozabile plafonate la 33% din salariu (clauza de mobilitate, hrană, abonamente etc.) — sunt categorii diferite, cu formule diferite.

## Ce face iConta.eu

Formula legală de mai sus este implementată corect în motorul de calcul din `core/deconturi.py` (funcția `plafon_diurna`): calculează ambele praguri (2,5× diurnă bugetară și 3×salariu/zile lucrătoare), alege minimul, și întoarce separat suma neimpozabilă și cea impozabilă. Motorul este chiar „period-aware" — recunoaște dacă diurna bugetară aplicabilă e 20 sau 23 lei, în funcție de data la care se raportează calculul.

Există însă o limitare reală, verificată în cod: **acest calcul de plafon nu este accesibil din nicio interfață a aplicației**. Ecranul „Decont deplasare / diurnă" (din „Operațiuni speciale") permite doar înregistrarea unui avans sau a unui decont — nu oferă un buton sau un câmp pentru a vedea plafonul calculat. Mai mult, atunci când se înregistrează un decont propriu-zis, aplicația **postează întreaga sumă de diurnă introdusă drept cheltuială**, fără să verifice automat dacă depășește plafonul. Separarea neimpozabil/impozabil descrisă mai sus există doar ca funcție de calcul brut la nivel de cod (API), nu ca pas automat în fluxul de înregistrare a decontului. Contabilul trebuie, astăzi, să calculeze manual plafonul înainte de a introduce diurna, pentru a decide singur dacă și cât din ea trebuie tratat ca venit salarial suplimentar.

[iConta.eu](/)
