from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv
import requests
import chromadb
import os

load_dotenv()

print("Setting up embedding model")
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

print("Connecting to database")
CLIENT = chromadb.HttpClient(host="localhost", port=8000)

print("Getting collection")
COLLECTION = CLIENT.get_or_create_collection(name="main-collection")

print("Starting Flask")
app = Flask(__name__)

ORIGIN = "*" # pls change this later

@app.route("/search", methods=["POST", "OPTIONS"])
def search():
	if request.method == "OPTIONS":
		response = Response()
		response.headers["access-control-allow-origin"] = ORIGIN
		response.headers["access-control-allow-headers"] = ORIGIN
		response.headers["access-control-allow-methods"] = ORIGIN
		return response

	body = request.get_json()
	query = body["query"]
	embedding = MODEL.encode(query).tolist()
	dbResponse = COLLECTION.query(
		query_embeddings=[embedding],
		n_results=5,
		include=["distances", "embeddings", "documents"]
	)

	response = jsonify(dbResponse)
	response.headers.add("access-control-allow-origin", ORIGIN)
	return response

def load_data(path):
	content, ids = [], []
	for index, file in enumerate(os.listdir(path)):
		with open(os.path.join(path, file), 'r') as f:
			content.append(f.read())
			ids.append(f"id{index+1}")
	return (content, ids)

@app.route("/query", methods=["POST", "OPTIONS"])
def query():
	if request.method == "OPTIONS":
		response = Response()
		response.headers["access-control-allow-origin"] = ORIGIN
		response.headers["access-control-allow-headers"] = ORIGIN
		response.headers["access-control-allow-methods"] = ORIGIN
		return response

	body = request.get_json()
	query = body["query"]
	context = body["context"]

	response = jsonify(query_llm(query, context))
	response.headers.add("access-control-allow-origin", ORIGIN)
	return response

def query_llm(query, context):
	# for now I use OpenAI API but want to change to self hosted for costs
	BOT_CONTEXT = "You are a financial advisor who uses your skills to advise your clients. You will maintain a professional but concise manner of speech."
	prompt = f"Context: {context}\n Using the provided context answer the following question: {query}"
	
	response = requests.post("https://api.openai.com/v1/chat/completions", 
						  headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"}, 
						  json={"model": "gpt-3.5-turbo", "temperature": 0.7,
			  					"messages": [
									  {"role": "system", "content": BOT_CONTEXT},
									  {"role": "user", "content": prompt}
								]})
	
	return response.json()

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080)