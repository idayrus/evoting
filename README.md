# E-Voting by Idayrus Studio

## Database

Login to mysql client and create database:

```sql
CREATE DATABASE db_idayrus_evoting CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

To create table, run this command:

```
flask db upgrade
```

## Production Setup

Use nginx, mysql, supervisor, and python to run production.

## Development Setup

You need to install mysql-server and python run development.

#### Create Virtual Environment

- Create venv: `python3 -m venv venv`
- Activate: `source venv/bin/activate`
- Install requirements: `pip3 install -r requirements.txt`
