## PyDao ##

*A DAO (Data Access Object) library for Python*

### What's New ###

> Version: 0.1.0

> Release Date: 2023-08-26

> Last Update: 2023-08-26

### Requirements ###
* Python 3 and its libs (Yes, that's all! ;P )

### Licensing ###
This Python DAO library is an OPEN SOURCE software under the MIT license

Thus, it is free and open source and is intended to always be. You can use and modify it as you wish, respecting just a few rules defined by the MIT open source license bellow:

MIT License
Copyright (c) 2023 LighterTools Community

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## What is a DAO? ##
*DAO* is an acronym for "Data Access Object" and its purpose is to provide tools for handling database operations, acting as a facilitator.

### It is not an ORM ###
An ORM (Object Relationship Mapper), as its name says, maps the relationship between database entities(tables) using object of data classes to represent them, so the user operates only using these classes and the ORM handles all the database SQL querying (supposedly).

A DAO is a much lighter tool, which does not intend to abstract the database SQL querying, - thus, removing all the advantages and controls that the RDBMS and SQL languages provide - but, instead, provides a great set of facilitators to work with it. To implement a DAO you don't have to write all those data classes, for representing the database entities. Instead of writing an entire data class for each table in your db, all you need to provide is the db credentials (aka: host, user, password, etc.) and it is ready to go, thus making it a tool much easier and faster to setup. It is also much easier to learn, because all you need to know is a bunch of methods, with obvious names like: "update()", "insert()", etc.. And, for the sake of infra, it is much lighter than any ORM, for it does not store tons of data class objects in the memory.

### Ok, but what does this provide? ###
* Database connections handling, making sure that none is left open
* Database cursors handling, also making sure that none is left open
* Data persistence in memory, thus avoiding unnecessary SQL executions
* An interface to all database operations, so you don't have to write basic queries
* A set of tools to facilitate when you have to write more complex queries
* Handles the results, returning lists and dictionaries with the data, right to your hand
* Filtering methods, which construct your query conditions and avoid SQL injections

... and so on. Basically you don't have to worry with all those annoying side-things you would have, when working with databases, then can focus on the application itself, that you're building.

---

## Get Started ##
It just came out of the oven, so I didn't have enough time to place it on `pip`. I'll do it later.

For now, you can download it and place it in your project as a normal person. xD

### Basic Usage (CRUD) ###

* **How to insert data into the database?(C)**

```python 
from pydao.mysql import GetDao

data = {
  'field1': 'foo'
  'field2': 'bar'
  'numeric': 12
}

newlyInsertedObj = GetDao('some_table').insert(data)
```
The code above inserts the *data* into the database and returns a dictionary containing the inserted register, including the auto increment primary key.

* **How do I read data from the database?(R)**

```python 
from pydao.mysql import GetDao

result = GetDao('some_table').find()
```
The code above retrieves a list of dictionaries, containing, each, a row of the table "some_table".


* **How to update data?(U)**

```python 
from pydao.mysql import GetDao

data = {
  'field1': 'foo2'
  'field2': 'bar2'
  'numeric': 7
}

numAffectedRows = GetDao('some_table').update(data)
```
The code above updates rows in the database, with the *data*, then returns an integer of how many rows were updated.

* **How to delete data from the database?(D)**

```python 
from pydao.mysql import GetDao

numAffectedRows = GetDao('some_table').delete()
```
The code above deletes data from the database, then returns an integer of how many rows were deleted.

### Connecting to the Database ###
By default, it tries to get the database credentials from the environment variables, as follows:
* DBHOST = "your database's host address"
* DBPORT = "your database's port number"
* DBNAME = "your database's name"
* DBUSER = "your database's user name"
* DBPASS = "your database's user password"

You can also provide connections to it, in case you want to connect to multiple hosts and/or databases:

```python
from pydao.mysql import Cnn
from pydao.mysql import GetDao

customConnection = Cnn(
  host="your database's host address",
  port=3306,
  database="your database's name",
  user="your database's user name",
  password="your database's user password"
)

GetDao('table_name', customConnection).find()
```

---

---

### Authors ###
* Gabriel Valentoni Guelfi(first author and founder)
  > Email: gabriel.valguelfi@gmail.com

  > Linkedin: [Gabriel Guelfi](https://www.linkedin.com/in/gabriel-valentoni-guelfi/)

---

### Acknowledgments ###
* [João Paulo Varandas](https://www.linkedin.com/in/joaovarandas/), my former boss and the author of **[inPaaS](https://www.inpaas.com/)**, a Low-code platform written in Java. Much of the coding interface of **PyDao** is similar to **inPaaS**. Thank you for the huge amount of knowledge.
* [João Ricardo Escribano](https://www.linkedin.com/in/joaoescribano/) my friend and another technology monster who taught me and encouraged me much. Thank you for your patience and for have showed me the world of software engineering.
* [Thiago Valentoni Guelfi](https://www.linkedin.com/in/thiago-valentoni-guelfi-198a4174/) my brother who began much earlier than myself and opened up the software engineering door in my household
* [Ronny Amarante](https://www.linkedin.com/in/ronnyamarante/) tech leader of **inPaaS** team, also have taught me much of what I know today. Thank you!
* [Fulvius Titanero Guelfi](https://www.linkedin.com/in/fulviusguelfi/) my uncle who opened my mind many times to new programming and technology paradigms. Thank you!
* To the wide community of devs around the world who posted unaccountable amounts of knowledge for free throughout the entire network, many thanks.

---