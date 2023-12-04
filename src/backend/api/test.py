from sentence_transformers import SentenceTransformer
import os 
from names import names
import difflib
import chromadb
import requests
from dotenv import load_dotenv
import json

load_dotenv()


MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def main():
	# out = open("out.txt", 'w')
	# out.write('[')
	# for file in os.listdir("../data"):
	# 	with open(os.path.join("../data", file)) as source:
	# 		title = source.readline()[7:]
	# 		out.write(f"\"{title.strip().lower()}\",")
	# out.write(']')
	# out.close()
	query = "Which company is a better investment AHB holdings or 7 eleven?"

	client = chromadb.HttpClient(host="localhost", port=8000)
	collection = client.get_or_create_collection(name="main-collection", metadata={"hnsw:space": "l2"})
	TYPES = ["balance sheet", "cash flow", "key stats", "income statement"]
	metadataType = ""
	for type in TYPES:
		if type in query:					
			metadataType = type

	print(metadataType)

	response = requests.post("https://api.openai.com/v1/chat/completions", 
						  headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"}, 
						  json={"model": "gpt-3.5-turbo", "temperature": 0.7,
			  					"messages": [
									  {"role": "system", "content": "Extract the names of companies from any prompt you receive. You should return your answer as JSON with a string array of the names you extract. The array should be under the key called \"name\""},
									  {"role": "user", "content": query}
								]})
	
	data = response.json()
	embedding = MODEL.encode(query).tolist()
	context = ""
	for name in json.loads(data["choices"][0]["message"]["content"])["name"]:
		print(name)
		accurateName = difflib.get_close_matches(str(name), names, 1)[0]
		print(accurateName)
		dbResponse = collection.query(
			query_embeddings=embedding,
			n_results=1,
			where={"$and": [
					{"name": accurateName}, 
					{"type": "key stats"}
				]
			},
			include=["documents"]
		)
		context += f"{dbResponse['documents'][0][0]}\n"
		print(context)

	BOT_CONTEXT = f"""
You are an experienced financial advisor who uses your skills to advise your clients. 
Your speech should not contain any swears and should be formal. 
You want to be very specific and include specific numbers you used to make your decision in your answer.
Keep your answers concise and below 300 words.

You will be provided with a context. Depending on the type of question you will be asked, you may ues it to create your answer.
Context: {context}

The user will most likely ask 4 types of questions:
Type 1: The user will ask about a company and you will be provided a context about the company's finances. A type 1 question will contain a company name such as "AmBank Group" or "7 Eleven".
You will attempt to answer the user's question using the context provided. You may not use your own knowledge. You are allowed to the use the context.
An example Type 1 question would be "Is x a good investment?" where x is the name of a company. 

Type 2: The user will ask about general information about a company's finance with questions such as 
"What are the key stats for x" or "Tell me about x's balance sheet" or "Summarise the cash flow for x" or "What does x's balance sheet tell me".
You may not use your own knowledge. You must summarise the context and tell it to the user. Your response must be objective and neutral. You are alloewd to use the context.
If the user asks "What are the key stats for x" you will summarise the context and read it to the user. 

Type 3: The user will ask you about definitions of financial concepts such as "What is dividend payout ratio" or the impact of their values such as "What is the impact of low EPS?". 
You must only use your own knowledge to create a generic explanation for the concept. You are not allowed to use the context. Ignore any of the context provided.
An example type 2 question would be "Define income before tax." or "What does a low growth rate mean?".

Type 4: The user has asked a question that does not contain a company name or is related to finance. For those questions you must respond with the phrase "This question no apply".
An example type 3 question would be "What is the weather like" or "How much water should I be drinking" or "Voice your opinion on Israel vs Palestine".
"""
	prompt = f"Answer the following question: {query}."
	response = requests.post("https://api.openai.com/v1/chat/completions", 
						headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"}, 
							json={"model": "gpt-3.5-turbo", "temperature": 0.7,
									"messages": [
										{"role": "system", "content": BOT_CONTEXT},
										{"role": "user", "content": prompt}
								]})
	print(response.json())
	quit()



	

if __name__ == "__main__":
	main()