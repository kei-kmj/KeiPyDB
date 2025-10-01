# keiPyDB

`keiPyDB` is a lightweight, Python-based database inspired by Java's `SimpleDB`.
The goal is to create a minimalistic, file-based database system for small-scale applications.

## Getting Started

### Installation
Currently, `keiPyDB` is under development. Clone this repository to begin:

```bash
$ git clone https://github.com/yourusername/keiPyDB.git
$ cd keiPyDB
```

### Usage

#### Interactive SQL Client (Recommended)
Use the embedded SQL client for interactive database operations:

```bash
$ python -m client.keipy_client [database_directory]
```

Example session:
```sql
Database connected

SQL> CREATE TABLE users (id int, name varchar(10))
0 records processed

SQL> INSERT INTO users (id, name) VALUES (1, 'Alice')
1 records processed

SQL> SELECT id, name FROM users
id = 1, name = Alice

SQL> UPDATE users SET name = 'Bob' WHERE id = 1
1 records processed

SQL> DELETE FROM users WHERE id = 1
1 records processed

SQL> exit
Goodbye!
```

#### Programmatic Usage
For advanced usage or testing, you can also run the server directly:

```bash
$ python db/server/start_server.py
```
## ✅ Current Features

### Interactive SQL Client
- Simple command-line interface for database operations
- No setup required - just run and start using SQL commands

### SQL Support
- `CREATE TABLE` - Create tables with multiple columns
- `INSERT` - Insert data into tables
- `SELECT` - Query data with WHERE clauses and multiple columns
- `UPDATE` - Modify existing records
- `DELETE` - Remove records from tables
- `CREATE INDEX` - Create indices for query optimization

### Data Types
- `INT` - Integer values
- `VARCHAR(n)` - Variable-length strings

### Advanced Features
- Indexing support for faster queries
- Transaction support with automatic commit/rollback
- Join operations between tables

## Commands

- `exit` - Exit the client
- All SQL commands are executed immediately (no semicolon required)

