import sqlite3

if __name__ == '__main__':
    sql = 'SELECT COUNT(*) FROM PERSONA'

    connection = sqlite3.connect('tasks.db')

    cursor = connection.cursor()

    connection.commit()
    cursor.execute(sql)

    count = cursor.fetchall()[0][0]

    sql = 'SELECT * FROM PERSONA'
    cursor.execute(sql)

    for i in range(count):
        result = cursor.fetchone()
        for value in result:
            print(value, end='\t')
        print()

    cursor.close()
    connection.close()
