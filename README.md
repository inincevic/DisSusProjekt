# DisSusProjekt
Repozitorij u kojemu ce biti moj projekt za kolegij Raspodijeljeni sustavi

## Zadatak
Generičan load balancer koji ima failover u slučaju prekida rada load balancera.
Radne stanice, ili serveri, kojima load balancer šalje korisnike sami će se registrirati u load balanceru, te će load balancer provjeravati njihovu dostupnost.

Distribuirani je sustav zato što se radi o više poslužitelja sa raznolikim zadatcima kojima korisnici pristupaju, te su raspoređeni ovisno o zauzeću ostalih poslužitelja.

## Progress zadatka
- Workeri se sami registriraju :check_mark:
- Load balancer provjerava njihovu dostupnost :check_mark:
- Failover
- Neki actual task


## Rad aplikacije
Kako bi postojao smisao load balancera, potrebno je odrediti sto ce workeri aplikacije raditi.
Kako bi se smanjilo kompliciranje i kolicina rada provedenog na workerima, workeri ce, barem za sada biti zauzeti i cekati 20s ~~4.5s~~ prije davanja odgovora i oslobadjanja.
~~Vrijeme cetanja je smanjeno sa 20 sekundi na 4.5 sekunde usljed provlema sa fastAPI timeoutom.~~ Uspjesno rjesen problem sa timeoutom.

## Pokretanje load balancera
Unutar ./src/ potrebno je pokreniti slijedecu naredbu
> python -m uvicorn balancer:app --reload

## Pokretanje workera
S obzirom na broj worker-a, potrebno je odrediti nekoliko portova na kojima ce se ti workeri pokretati.
Za odredjivanje porta na kojem ce se pokretati worker, koristimo slijedecu naredbu unutar ./src/
> python -m uvicorn worker:app --reload --port X
Gdje je X broj porta.