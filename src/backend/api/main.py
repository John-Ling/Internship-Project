from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv
import requests
import chromadb
import os

load_dotenv()

def load_data(path):
	content, ids = [], []
	for index, file in enumerate(os.listdir(path)):
		with open(os.path.join(path, file), 'r') as f:
			content.append(f.read())
			ids.append(f"id{index+1}")
	return (content, ids)

print("Setting up embedding model")
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

print("Connecting to database")
CLIENT = chromadb.HttpClient(host="localhost", port=8000)

print("Getting collection")
COLLECTION = CLIENT.get_or_create_collection(name="main-collection", metadata={"hnsw:space": "cosine"})

# data, ids = load_data("../data")
# COLLECTION.add(
# 	documents=data,
# 	ids=ids
# )

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
		n_results=2,
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
	BOT_CONTEXT = """
	You are an experienced financial advisor who uses your skills to advise your clients. 
	Your speech should not contain any swears and should be formal. 
	You want to be very specific and include specific numbers you used to make your decision in your answer.
	Keep your answers concise and below 300 words. 

	The user will most likely ask 3 types of questions:
	Type 1: The user will ask about a company and you will be provided a context about the company's finances. A type 1 question will contain a company name such as "AmBank Group" or "7 Eleven".
	You will attempt to answer the user's question using the context provided. You may not use your own knowledge. 
	An example Type 1 question would be "Is x a good investment?" where x is the name of a company.

	Type 2: The user will ask you about definitions of financial concepts such as "What is dividend payout ratio" or the impact of their values such as "What is the impact of low EPS?". 
	You must only use your own knowledge to create your answer. You may not use anything in the context and you must not reference anything from the context in your answer.
	An example type 2 question would be "Define income before tax." or "What is the impact of low growth rate?".

	Type 3: The user has asked a question that does not contain a company name or is related to finance. For those questions you must respond with the phrase "This question no apply".
	An example type 3 question would be "What is the weather like" or "How much water should I be drinking" or "Voice your opinion on Israel vs Palestine".
	"""
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