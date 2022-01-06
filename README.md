# Tap LinkedIn Sales Navigator

[Singer](https://www.singer.io/) tap that extracts data from [LinkedIn Sales Navigator](https://www.linkedin.com/sales) and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md).

To make this Tap work with a Target, clone both projects and follow these instructions:

## Usage

This section dives into basic usage of `tap-linkedin` by walking through extracting
data from a table. It assumes that you have access to LinkedIn Sales Navigator.

### Install

```bash
python3 -m venv ~/.virtualenvs/tap-linkedin
source ~/.virtualenvs/tap-linkedin/bin/activate
pip install -e .
```

### Create the configuration file


### Create the configuration file

| Configuration Key   | Description                                                                                              |
|---------------------|----------------------------------------------------------------------------------------------------------|
| keyword             | The keyword to search for in Sales Navigator.                                                            |
| cookie              | Your LinkedIn cookie                                                                                     |
| x_li_identity       | Your LinkedIn x-li-identity                                                                              |
| csrf_token          | Your LinkedIn csrf-token                                                                                 |



#### Configuration file example


```json
{
    "keyword": "keywork",
    "cookie": "cookie",
    "x_li_identity": "x_li_identity",
    "csrf_token": "csrf_token"
}
```


### Discovery mode

The tap can be invoked in discovery mode to find the available tables and
columns in the database:

```bash
$ tap-linkedin --config config.json --discover >> catalog.json

```

A discovered catalog is output, with a JSON-schema description of each table. A
source table directly corresponds to a Singer stream.

The `selected-by-default` fields is used to enable the sync of the tables. If set to 'true', all of the tables will be 
selected in the `catalog.json` 

### Saving State


## Target project (Example: target-postgres) 

### Clone target-postgres project

```shell
 git clone https://github.com/datamill-co/target-postgres
 cd target-postgres
```

### To install dependencies on target project run the commands

```shell
 python3 -m venv ~/.virtualenvs/target-postgres
 source ~/.virtualenvs/target-postgres/bin/activate
 pip install target-postgres
```

### To run full tap and target action run for a particular Base

From the home directory of the project 

```shell
tap-linkedin -c config.json --catalog catalog.json | ~/.virtualenvs/target-postgres/bin/target-postgres 
```
