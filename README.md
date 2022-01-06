# Tap LinkedIn Sales Navigator

[Singer](https://www.singer.io/) tap that extracts data from [LinkedIn Sales Navigator](https://www.airtable.com/) and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md).

To make this Tap work with a Target, clone both projects and follow this instructions:

## Usage

This section dives into basic usage of `tap-airtable` by walking through extracting
data from a table. It assumes that you have access to the Airtable API.

### Install

```bash
python3 -m venv ~/.virtualenvs/tap-linkedin
source ~/.virtualenvs/tap-linkedin/bin/activate
pip install -e .
```


### Create the configuration file


| Configuration Key   | Description                                                                                              |
|---------------------|----------------------------------------------------------------------------------------------------------|
| token               | Airtable Token                                                                                           |
| base_id             | Airtable base ID to export                                                                               |
| selected_by_default | Default for every table in the base. If set to true, all of the tables in the schema will be syncronized |



#### Configuration file example


```json
{
    "token":"airtable_token",
    "base_id": "airtable_base_id",
    "selected_by_default": true,
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

Complete the config.json 

```
{
    "token":"airtable-api-key",
    "base_id": "base-id",
    "selected_by_default": true
}
```

From the home directory of the project 

```shell
tap-linkedin -c config.json --catalog catalog.json | ~/.virtualenvs/target-postgres/bin/target-postgres 
```
