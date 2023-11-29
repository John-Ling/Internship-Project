import pandas as pd
import requests
import xlrd
import os

def main():
	PAGES = 100
	stockCodes = []

	# get stock codes for top 1000 stocks in malaysia
	# for i in range(1, PAGES+1):
	# 	print("Getting stock codes...", end=" ")
	# 	stockCodes += get_stock_codes(f"https://www.bursamarketplace.com/index.php?tpl=stock_ajax&type=listing&pagenum={i}&sfield=name&stype=asc&midcap=0")
	# 	print("Done")

	# # get financial data for those companies
	# for code in stockCodes:
	# 	print("Fetching excel data...", end=" ")
	# 	company_info(code)
	# 	print("Done")
	
	# convert and chunk excel documents
	
	for file in os.listdir("../excel-data"):
		print("Chunking File...", end=" ")
		excel_to_text(os.path.join("../excel-data", file));
		print("Done")
		
	return

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

def company_info(stockCode):
	# downloads the key stats, income statement, balance sheet or cash flow for company using its stock code

	HEADERS = {
		"User-Agent": "Char Kway Teow",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
		"Accept-Language": "en",
		"Accept-Encoding": "gzip, deflate, br"
	}

	ENDPOINTS = [
		f"https://www.bursamarketplace.com/index.php?tpl=financial_export_excel&ric={stockCode}&fin=KEY&per=1&mkt=stock",
		f"https://www.bursamarketplace.com/index.php?tpl=financial_export_excel&ric={stockCode}&fin=INC&per=1&mkt=stock",
		f"https://www.bursamarketplace.com/index.php?tpl=financial_export_excel&ric={stockCode}&fin=BAL&per=1&mkt=stock",
		f"https://www.bursamarketplace.com/index.php?tpl=financial_export_excel&ric={stockCode}&fin=CAS&per=1&mkt=stock"
	]

	for url in ENDPOINTS:
		response = requests.get(url, headers=HEADERS)
		if response.status_code != 200:
			print("Could not download file")
			continue

		filename = response.headers["Content-Disposition"][21:-1]
		open(f"../excel-data/{filename}", "wb").write(response.content)
	
	return

def excel_to_text(path):
	# convert excel file into chunked text files for use in vector db
	workbook = xlrd.open_workbook(path, ignore_workbook_corruption=True)
	dataframe = pd.read_excel(workbook)

	CHUNK_SPLIT = 100 # create chunks of N lines

	# get company info
	columns = dataframe.columns
	title = columns[0]
	bursaID = dataframe.iloc[1,0].split()[1] # change this later
	category = dataframe.iloc[3,0]
	type = dataframe.iloc[5,0]
	chunkNumber = 1
	
	FILE_TEMPLATE = f"../data/{title}_{type}_chunk_{chunkNumber}.txt"

	out = open(FILE_TEMPLATE, 'w')
	out.write(f"Title: {title}\nID: {bursaID}\n{category}\n")
	
	for index, row in dataframe.iloc[5:].iterrows():
		if index % CHUNK_SPLIT == 0: # chunking
			chunkNumber += 1
			out.close()

			out = open(FILE_TEMPLATE, 'w')
			out.write(f"Title: {title}\nID: {bursaID}\n{category}\n")

		buffer = ""
		for data in row:
			if pd.notna(data):
				buffer += f"{data} "

		if buffer != "":
			out.write(f"{buffer}\n")

	out.close()

if __name__ == "__main__":
	main()