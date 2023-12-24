# elvanto
Elvanto API parsing for C3 projects + associated scripts

### elvanto
* `main`: ElvantoQuery base class for all Elvanto-connected objects
* `groups`: Group object interfacing Elvanto Groups API
* `people`: People object interfacing Elvanto People API
* `services`: Services object interfacing Elvanto Services API
* `coach`: Coach object related to Coaching Roster parsing

### elvanto.utils
* `coachutils`: contains simple utility functions related to coaching roster and discipleship form automation

### scripts
* `get_groups`: fetches and parses all existing groups. Will create a database that is saved under `db/groups.csv`
* `get_people`: fetches and parses all existing people in Elvanto directory. Will create a database that is saved under `db/people.json`
* `get_services`: fetches and parses all existing groups. Will create a database of services that is saved under `db/services.json`, `db/services.csv`
* `get_cg_join_counts.py`: aggregates daily count of connect group sign-ups
* `get_team_stats.py`: aggregates weekly team member involvement, per team. This script could use a LOT of optimization. (1st, move functions out to elvanto.utils)
* `get_coaches.py`: fetches and parses coaching roster from Google Sheets. Creates a database under `db/coaches.json`, `db/coaches.csv`
* `build_coach_tree.py`: recursively searches coaches tree, to find all of their children/leaves
* `get_discipleship_forms.py`: builds spreadsheet of all coaches' children's forms
