# How can we lock in Galera?

**Case: multi-master Galera with simultaneous lock on different nodes.**

There is a nearly one good way to lock with waiting for new data - `select ... for update`.

So, main possible cases, deadlock is the only way to get working locks (otherwise locks don't work):

| 1tx on 1st one                     | 2tx on 2nd node   | deadlocks |
| ---------------------------------- | ----------------- | --------- |
| select for update                  |                   |           |
|                                    | select for update |           |
| commit                             | commit            | -         |
|                                    |                   |           |
| select for update                  |                   |           |
|                                    | select for update |           |
| update selected raw                |                   |           |
|                                    | select for update |           |
| commit                             | commit            | DEADLOCK  |
|                                    |                   |           |
| select for update                  |                   |           |
|                                    | select for update |           |
| update selected raw with same data |                   |           |
|                                    | select for update |           |
| commit                             | commit            | -         |
|                                    |                   |           |
| select for update                  |                   |           |
|                                    | select for update |           |
| update different table             |                   |           |
|                                    | select for update |           |
| commit                             | commit            | -         |
|                                    |                   |           |
| select for update                  |                   |           |
|                                    | select for update |           |
| update different raw in same table |                   |           |
|                                    | select for update |           |
| commit                             | commit            | -         |

(tested by `test_locks.py`)

Other limitations - https://mariadb.com/kb/en/mariadb-galera-cluster-known-limitations/

### Run tests on master-master Galera
```
pip install requirements.txt
mysql -u root -p < create_db_and_user.sql
./tests_locks.py IP1 IP2 IP3
```
