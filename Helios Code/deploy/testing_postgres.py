import psycopg2

connection = psycopg2.connect(
    host="localhost",  # Connect to localhost since you're forwarding the service locally
    port="5433",       # Use the local port that you forwarded to (5433)
    database="postgresdb",
    user="postgresadmin",
    password="admin123"
)
test="test"
c1_string = "value1"
c2_string = "value2"
r1_string = "value3"

cursor = connection.cursor()

cursor.execute("INSERT INTO user_face_shares (email_hash, file1, file2, file3) VALUES (%s, %s, %s, %s)",
                   (test,c1_string, c2_string, r1_string))
connection.commit()
cursor.close()
connection.close()