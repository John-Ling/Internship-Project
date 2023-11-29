import requests

def main():
	stockCodes = []
	
	for i in range(1, 101):
		print("Getting stock codes...", end="")
		stockCodes += get_stock_codes(f"https://www.bursamarketplace.com/index.php?tpl=stock_ajax&type=listing&pagenum={i}&sfield=name&stype=asc&midcap=0")
		print(" Done")

	print(stockCodes)

def get_stock_codes(url):
	# return all stock codes for a bursa malaysia url
	
	HEADERS = {
		"User-Agent": "Char Kway Teow",
		"Accept": "application/json, text/javascript",
		"Accept-Language": "en",
		"Accept-Encoding": "UTF-8"
	}

	stockCodes = []
	response = requests.get(url, headers=HEADERS)
	
	if response.status_code != 200:
		print(f"Error {response.status_code}")
		quit()

	json = response.json()
	for record in json["records"]:
		stockCodes.append(record["cashtag"][1:]) # remove dollar sign from cashtag
	return stockCodes
	
if __name__ == "__main__":
	main()