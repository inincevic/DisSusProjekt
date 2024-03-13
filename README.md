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
- Neki actual task :check_mark:

~~## Ideja za posao workera~~
~~Ili nekakve statisticke operacije ili operacije sa datotekama.~~
## Zadan posao workera
Svaki worker ima mogucnost pisanja u datoteku kojoj svi workeri imaju pristup.
Ta datoteka zove se write_file.txt.
Svaki worker koji se pokrene provjerava postoji li vec datoteka, te ako ne postoji, workeri imaju mogucnost kreirati datoteku.

Postoje dvije rute za svrhu rada workera: ruta za pisanje u datoteku i ruta za citanje iz datoteke.
S ovim zadatcima simulira se rad neke kompleksnije aplikacije, i uzima se vrijeme.


## Rad aplikacije
Kako bi postojao smisao load balancera, potrebno je odrediti sto ce workeri aplikacije raditi.
Kako bi se smanjilo kompliciranje i kolicina rada provedenog na workerima, workeri ce, barem za sada biti zauzeti i cekati 20s ~~4.5s~~ prije davanja odgovora i oslobadjanja.
~~Vrijeme cetanja je smanjeno sa 20 sekundi na 4.5 sekunde usljed provlema sa fastAPI timeoutom.~~ Uspjesno rjesen problem sa timeoutom.

Kako bi aplikacija imala nekakve realne primjene, dodane su dvije nove operacije koje workeri mogu raditi: pisanje i citanje iz .txt datoteke.

## Pokretanje load balancera
Unutar ./src/ potrebno je pokreniti slijedece naredbe
> python -m uvicorn balancer:app --reload

## Pokretanje workera
S obzirom na broj worker-a, potrebno je odrediti nekoliko portova na kojima ce se ti workeri pokretati.
Za odredjivanje porta na kojem ce se pokretati worker, koristimo slijedecu naredbu unutar ./src/
> python -m uvicorn worker:app --reload --port X
Gdje je X broj porta.