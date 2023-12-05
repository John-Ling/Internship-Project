import mysql.connector

def main():
	db = mysql.connector.connect(
		host="localhost",
		user="root",
		password="Bonz1Buddi"
	)
	cursor = db.cursor()
	cursor.execute("USE test;")
	cursor.execute("SELECT * FROM users;");

	results = cursor.fetchall()
	for x in results:
		print(x)

if __name__ == "__main__":
	main()