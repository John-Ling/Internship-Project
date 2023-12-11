from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv
import requests
import mysql.connector
import os
import json
import difflib
import hashlib
from names import NAMES

load_dotenv()

def load_data(path):
	content, ids, metadata = [], [], []
	for index, file in enumerate(os.listdir(path)):
		tmp = {}
		with open(os.path.join(path, file), 'r') as f:
			content.append(f.read())

			# determine content type using filename
			TYPES = ["BALANCE SHEET", "CASH FLOW", "KEY STATS", "INCOME STATEMENT"]
			for type in TYPES:
				if type in file:
					tmp["type"] = type.lower()

		with open(os.path.join(path, file), 'r') as f:
			name = f.readline()[7:].strip().lower()
			tmp["name"] = name
		metadata.append(tmp)
		ids.append(f"id{index+1}")
	return content, ids, metadata

CONNECTION = mysql.connector.connect(host=os.environ["DB_ADDRESS"],user=os.environ["DB_USER"],password=os.environ["DB_PASSWORD"],database=os.environ["DB_NAME"])

print("Starting Flask")
app = Flask(__name__)

ORIGIN = "*" # pls change this later

@app.route("/ping", methods=["GET"])
def ping():
	return "Pong"

@app.route("/search", methods=["POST", "OPTIONS"])
def search():
	if request.method == "OPTIONS":
		response = Response()
		response.headers = {
			"access-control-allow-origin": ORIGIN,
			"access-control-allow-headers": ORIGIN,
			"access-control-allow-methods": ORIGIN
		}
		return response

	body = request.get_json()
	query = body["query"]


	TYPES = {"balance sheet": 2, "income statement": 3, "cash flow": 4}
	queryID = 1 # by default we look for 
	for type in TYPES:
		if type in query:
			queryID = TYPES[type]

	CONTEXT = "Extract the names of companies from any prompt you receive. You should return your answer as JSON with a string array of the names you extract. The array should be under the key called \"name\""
	response = requests.post("https://api.openai.com/v1/chat/completions",
						  headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"},
						  json={"model": "gpt-3.5-turbo", "temperature": 0.1,
			  					"messages": [
									  {"role": "system", "content": CONTEXT},
									  {"role": "user", "content": query}
								]})

	data = response.json()
	print(data)
	context = ""

	for name in json.loads(data["choices"][0]["message"]["content"])["name"]:
		name = name.lower()
		dbName = difflib.get_close_matches(str(name), NAMES, 1)[0]
		hash = hashlib.md5(f"{dbName}{queryID}".encode()).hexdigest()
		
		cursor = CONNECTION.cursor()
		cursor.execute(f"SELECT content FROM documents WHERE id = \"{hash}\" AND type_id = {queryID} LIMIT 1;")
		result = cursor.fetchall()

		context += result[0][0]

	response = jsonify({"context": context})
	response.headers.add("access-control-allow-origin", ORIGIN)
	return response

@app.route("/query", methods=["POST", "OPTIONS"])
def query():
	if request.method == "OPTIONS":
		response = Response()
		response.headers = {
			"access-control-allow-origin": ORIGIN, 
			"access-control-allow-headers": ORIGIN,
			"access-control-allow-methods": ORIGIN
		}
		return response

	body = request.get_json()
	query = body["query"]
	context = body["context"]

	response = jsonify(query_llm(query, context))
	response.headers.add("access-control-allow-origin", ORIGIN)
	return response

def load_data(path):
	content, ids = [], []
	for index, file in enumerate(os.listdir(path)):
		with open(os.path.join(path, file), 'r') as f:
			content.append(f.read())
			ids.append(f"id{index+1}")
	return (content, ids)


def query_llm(query, context):
	# for now I use OpenAI API but want to change to self hosted for costs
	BOT_CONTEXT = f"""
	You are an experienced financial advisor who uses your skills to advise your clients.
	Your speech should not contain any swears and should be formal.
	You want to be very specific and include specific numbers you used to make your decision in your answer.
	Keep your answers concise and below 300 words. Speak with conviction and certainty.

	You will be provided with a context. Depending on the type of question you will be asked, you may use it to create your answer.
	Context: {context}

	The user will most likely ask 4 types of questions:
	Type 1: The user will ask about a company and you will be provided a context about the company's finances. A type 1 question will contain a company name such as "AmBank Group" or "7 Eleven".
	You will attempt to answer the user's question using the context provided. You may not use your own knowledge. You are allowed to the use the context.
	An example Type 1 question would be "Is x a good investment?" where x is the name of a company.

	Type 2: The user will ask about general information about a company's finance with questions such as
	"What are the key stats for x" or "Tell me about x's balance sheet" or "Summarise the cash flow for x" or "What does x's balance sheet tell me".
	You may not use your own knowledge. 
	You must summarise the context and tell it to the user. Your response must be objective and neutral. You are alloewd to use the context.
	If the user asks "What are the key stats for x" you will summarise the context and read it to the user.

	Type 3: The user will ask you about definitions of financial concepts such as "What is dividend payout ratio" or the impact of their values such as "What is the impact of low EPS?".
	You must only use your own knowledge to create a generic explanation for the concept. You are not allowed to use the context. Ignore any of the context provided.
	An example type 2 question would be "Define income before tax." or "What does a low growth rate mean?".

	Type 4: The user will ask to compare 2 or more companies. You will be provided with the key stats for each company as context.
	You must analyse each stats sheet to conclude which company has the best statistics. You are only allowed to use the context provided. You may not use your own knowledge.
	An example Type 4 question would be "Which is better x or y" or "Compare x, y and z" or "Is x better then y" where x, y and z are different companies.
	For each company list pros and cons then give your conclusion. 

	Type 5: The user has asked a question that does not contain a company name or is related to finance. For those questions you must respond with the phrase "This question no apply".
	An example type 3 question would be "What is the weather like" or "How much water should I be drinking" or "Voice your opinion on Israel vs Palestine".

	For questions 1 and 4, the user may specify that they want answers for a long term or short term investment. These questions may sound something like 
	"Is x a good long term investment" or "Give me reasons x is a good short term investment" or "Is x a bad long term investment?".
	For questions that explicitly contain the term "long term" or "short term" (the phrase may include a dash instead of a space), you should take it into consideration.
	For long term investments look for patterns of stability while for short term look for patterns of immediate reward. If the user does not specify whether they want a long-term
	or short-term investment then assume they want a long term investment. 
	"""

	prompt = f"Answer the following question: {query}."

	response = requests.post("https://api.openai.com/v1/chat/completions",
						  headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"},

						  json={"model": "gpt-3.5-turbo", "temperature": 0.25,
			  					"messages": [
									  {"role": "system", "content": BOT_CONTEXT},
									  {"role": "user", "content": prompt}
								]})

	return response.json()

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080)