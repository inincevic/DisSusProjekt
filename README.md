# DisSusProjekt
Repozitorij u kojemu ce biti moj projekt za kolegij Raspodijeljeni sustavi


## Rad aplikacije
Kako bi postojao smisao load balancera, potrebno je odrediti sto ce workeri aplikacije raditi.
Kako bi se smanjilo kompliciranje i kolicina rada provedenog na workerima, workeri ce, barem za sada biti zauzeti i cekati 20s prije davanja odgovora i oslobadjanja.

## Pokretanje load balancera
Unutar ./src/ potrebno je pokreniti slijedecu naredbu
> python -m uvicorn balancer:app --reload