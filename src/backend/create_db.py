from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

def main():
	with  mysql.connector.connect(
		host="localhost",
		user="admin",
		password=os.environ["DB_PASSWORD"],
		database="internship_project"
	) as connection:
		
		cursor = connection.cursor()
		for file in os.listdir("./data"):
			path = os.path.join("./data", file);

			with open(path, 'r') as source:
				content = source.read()

			with open(path, 'r') as source:
				name = source.readline()[7:].strip()
				try:
					stockID = int(source.readline()[4:].strip())
				except ValueError:
					continue

			TYPE_IDS = {"KEY STATS": 1, "BALANCE SHEET": 2, "INCOME STATEMENT": 3, "CASH FLOW": 4}
			for type in TYPE_IDS.keys():
				if type in file:
					typeID = TYPE_IDS[type]
			
			assert typeID != ""

			INSERT = f"INSERT IGNORE INTO documents VALUES({stockID}, {typeID}, \"{content}\", \"{name}\");"
			cursor.execute(INSERT)

		cursor.close()
		connection.commit()

if __name__ == "__main__":
	main()