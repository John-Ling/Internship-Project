from sentence_transformers import SentenceTransformer
from flask import Flask, request
import chromadb
import os

def load_data(path):
	content, ids = [], []
	for index, file in enumerate(os.listdir(path)):
		with open(os.path.join(path, file), 'r') as f:
			content.append(f.read())
			ids.append(f"id{index+1}")
	return (content, ids)

MODEL = SentenceTransformer("all-MiniLM-L6-v2")

print("Connecting to database...")
client = chromadb.HttpClient(host="localhost", port=8000)
print("Getting collection...")
collection = client.get_or_create_collection(name="main-collection")

# automate this when database changes
# data, ids = load_data("../data")
# collection.add(
# 	documents=data,
# 	ids=ids
# )

print("Starting Flask")
app = Flask(__name__)


# todo change this use to body instead of url parameters
@app.route("/query", methods=["POST"])
def query():
	args = request.args
	query = args.get("query")
	embedding = MODEL.encode(query).tolist()
	dbResponse = collection.query(
		query_embeddings=[embedding],
		n_results=5,
		include=["distances", "embeddings", "documents"]
	)

	return dbResponse['documents'][0][0]

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080)