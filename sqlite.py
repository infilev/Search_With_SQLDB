import sqlite3

## Connection to sqlite

connection = sqlite3.connect("students.db")

## Cursor object creation for insertion of record and create table

cursor = connection.cursor()


## create a table

table_info = """

create table STUDENT(
        NAME VARCHAR(25),
        CLASS VARCHAR(25),
        SECTION VARCHAR(25),
        MARKS INT
          )
"""

cursor.execute(table_info)

## Insert some more records

cursor.execute('''Insert into STUDENT values('Anubhav', 'Data Science', 'A', 90)''')
cursor.execute('''Insert into STUDENT values('John', 'Data Science', 'B', 100)''')
cursor.execute('''Insert into STUDENT values('Mukesh', 'Data Science', 'A', 86)''')
cursor.execute('''Insert into STUDENT values('Jacob', 'Data Science', 'A', 50)''')
cursor.execute('''Insert into STUDENT values('Dipesh', 'Data Science', 'A', 35)''')

## Display all the results

print("The inserted records are")
data = cursor.execute('''SELECT * FROM STUDENT''')
for row in data:
    print(row)

## Commit the changes in databases 

connection.commit()
connection.close()    

## cd LangChain_Projects  cd Search_with_SQLDB