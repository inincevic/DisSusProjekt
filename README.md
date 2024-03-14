# DisSusProjekt
Repozitorij u kojemu se nalazi projekt moj projekt za kolegij Raspodijeljeni sustavi.

## Zadatak
Generičan load balancer koji ima failover u slučaju prekida rada load balancera.
Radne stanice, ili serveri, kojima load balancer šalje korisnike sami će se registrirati u load balanceru, te će load balancer provjeravati njihovu dostupnost.

Distribuirani je sustav zato što se radi o više poslužitelja sa raznolikim zadatcima kojima korisnici pristupaju, te su raspoređeni ovisno o zauzeću ostalih poslužitelja.


# Elementi projekta

## Zadan posao workerima
Svaki worker ima mogucnost pisanja u datoteku kojoj svi workeri imaju pristup.
Ta datoteka zove se write_file.txt.
Svaki worker koji se pokrene provjerava postoji li već ta datoteka, te ako ne postoji, workeri imaju mogucnost kreirati tu datoteku.

Postoje dvije rute u svrhu rada workera: ruta za pisanje u datoteku i ruta za čitanje iz datoteke.

Kako bi se moglo simulirati "zagušenje" sustava, te provjeriti kako load balancer šalje zadatke workerima napravljena je dodatna ruta koja ima u sebi jednostavniji zadatak okretanja poruke naopako i čekanja period vremena.

## Rad sustava ~~aplikacije~~
Očekivanje ovog sustava je da je load balancer pokrenut prije ijednog workera.

Prilikom pokretanja, workeri se automatski registriraju na load balanceru tako da load balancer može slati zadatke workerima bez vanjske intervencije.
Kada je neki zadatak poslan load balanceru, load balancer će taj zadatak poslati ili prvom slobodnom workeru ili workeru koji trenutno izvodi najmanje zadataka.

## Failover
Kroz cijelo izvođenje, sustav periodički provodi provjere sam nad sobom, na način da load balancer svaki period provjeri jesu li workeri dostupni, te ako nisu izbacuje ih iz liste dostupnih workera.
Workeri, kroz cijelo izvođenje, provjeravaju dostupnost load balancera i prilikom te provjere prepisuju listu dostupnih workera, te ukoliko load balancer prestane sa izvođenjem, registrirani worker sa najmanjim portom će ponovno pokrenuti load balancer.


# Pokretanje sustava
Kako se sustav sastoji od jednog load balancera i neodređenog broja workera, potrebno je prvo pokrenuti load balancer a potom pokrenuti workere.

## Pokretanje load balancera
Unutar ./src/ potrebno je pokreniti slijedeće naredbe
> python -m uvicorn balancer:app --reload

## Pokretanje workera
S obzirom na broj worker-a, potrebno je odrediti portove na kojima će se ti workeri pokretati.
Port korišten za pokretanje workera nikada ne smije biti 8000, zato što je to predodređeni port na kojemu se pokreće load balancer.
Za pokretanje workera na određenom portu, koristimo slijedecu naredbu unutar ./src/
> python -m uvicorn worker:app --reload --port X
Gdje je X broj porta.