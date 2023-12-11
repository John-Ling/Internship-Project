from dotenv import load_dotenv
import mysql.connector
import os
import hashlib

load_dotenv()

def main():
	with  mysql.connector.connect(
		host=os.environ["DB_ADDRESS"],
		user=os.environ["DB_USER"],
		password=os.environ["DB_PASSWORD"],
		database=os.environ["DB_NAME"]
	) as connection:
		cursor = connection.cursor()

		cursor.execute("CREATE TABLE IF NOT EXISTS documents(id varchar(60) NOT NULL PRIMARY KEY, stock_id INT NOT NULL, type_id INT NOT NULL, content VARCHAR(8000), name VARCHAR(50));");
		connection.commit()
		
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

			id = hashlib.md5(f"{name.lower()}{typeID}".encode()).hexdigest()
			INSERT = f"INSERT INTO documents VALUES(\"{id}\", {stockID}, {typeID}, \"{content}\", \"{name}\");"
			cursor.execute(INSERT)

		cursor.close()
		connection.commit()

if __name__ == "__main__":
	main()