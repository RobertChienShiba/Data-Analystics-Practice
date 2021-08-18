import mysql.connector


db_settings = {
"host": "127.0.0.1",
"port": 3306,
"user": "root",
"password": "root123",
"charset": "utf8"
}
cnx = mysql.connector.connect(**db_settings, database='pchome')
cursor = cnx.cursor(dictionary=True)

query = ("SELECT * FROM products "
         "WHERE name LIKE '%三星%';"
           # "SELECT * FROM products "
           # "WHERE name LIKE '%Kingston%';"
        )


cursor.execute(query)

            
# for row in cursor.execute(query,multi=True):
#     print(row) ##MySQLCursorDict
#     print('=============================================')
#     if row.with_rows:
#         print("Rows produced by statement '{}':".format(row.statement))
#         print(row.fetchall())
#     print(cursor.rowcount)



for row in cursor:
      print(row)
      #print(row['name'])


# while cursor.fetchone() is not None:
#   if cursor.with_rows:
#     print("Rows produced by statement '{}':".format( cursor.statement))
#     print( cursor.fetchmany(7))
# else:
#     print("Number of rows affected by statement '{}': {}".format(
#       cursor.statement,  cursor.rowcount))
    

# head_rows = cursor.fetchmany(size=2)
# remaining_rows = cursor.fetchall()
# print(head_rows)
# print("==============================")
# print(remaining_rows)


cursor.close()
cnx.close()