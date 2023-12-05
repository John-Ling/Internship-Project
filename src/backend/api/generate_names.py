import os

def main():
	out = open("names.py", 'w')
	out.write('NAMES = [')
	for file in os.listdir("../data"):
		with open(os.path.join("../data", file)) as source:
			title = source.readline()[7:]
			out.write(f"\"{title.strip().lower()}\",")
	out.write(']')
	out.close()

if __name__ == "__main__":
	main()