# ud_fullstack_p3
# project 3

### To run my project:

1. You need to run code from `tournament.sql`, it will create database `tournament` and also create table `players` in it. You can do it either from `psql` shell or using command `\i tournament.sql` to import whole file.
2. My `tournament.py` script contains only one module not from standart library - `psycopg2`. In order to install it you should execute `sudo apt-get install python-psycopg2` on Debian or if you're using Mac or Windows please check this official install guide out http://initd.org/psycopg/docs/install.html
3. `python tournament.py`

### Description of tournament.py script:

1. After installing psycopg2 and creating database with table you are ready to run `python tournament.py`. Function `main()` will be called. First of all you will be asked if you wish to erase the table and if you wish to add some players to the table. Then you'll specify names of the players, that names would be fetched to the `players` table.
2. Next, `main()` will hold the tournament, will print initial standings of the players, results after each round and pairs for each round.
3. Also I have `gen_and_run_html.py` script. `main()` function from `tournament.py` will give current data for each round to the `gen_and_run_html.py`. And this script will draw names and winner's or looser's lines using html.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; So, to begin `python tournament.py`.

In order to create db or connect to existing please specify your postgres username, password and db name in special file, that i've created in the root folder of the project - `db.cfg`. Please full it like this, without any quotes os whitespaces:
![example db.cfg](https://cloud.githubusercontent.com/assets/5002732/9095807/056c37f4-3bc2-11e5-9d53-886951efadee.png)
