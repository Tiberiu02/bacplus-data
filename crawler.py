from math import inf
import sys
from selenium import webdriver
import time

num_pages, output = None, None

js_script_extract = open("js/extract.js", "r").read()
js_script_next = open("js/next.js", "r").read()

browser = webdriver.Firefox()
browser.install_addon('web-extensions/ublock_origin-1.43.0.xpi', temporary=True)

def prev_page():
	browser.execute_script("history.back()")
	while browser.execute_script("return document.readyState") != 'complete':
		time.sleep(0.1)
	time.sleep(0.5)


def next_page():
	success = False
	fails = 0

	while not success:
		browser.execute_script(js_script_next)
		time.sleep(0.2)
		while browser.execute_script("return document.readyState") != 'complete':
			time.sleep(0.1)

		# Page not found?
		tr = None
		while tr == None:
			tr = browser.execute_script("return document.getElementsByClassName('tr1').length")

		if tr == 0:
			print('failed to load next page, going back')
			fails += 1
			prev_page()

			if fails == 10:
				fails = 0
				prev_page()
				next_page()
		else:
			time.sleep(0.1)
			success = True
	
def adjust_page(id):
	while page_id() != id:
		while page_id() < id:
			next_page()
			print('Next page')
		while page_id() > id:
			prev_page()
			print('Prev page')

def extract_data(pid):
	fails = 5
	while fails == 5:
		data = browser.execute_script(js_script_extract)
		fails = 0
		while fails < 5 and pid < num_pages and data != None and data.count('\n') != 10:
			print('Data not fetched correctly, waiting and retrying')
			print(data)
			fails += 1
			time.sleep(1)
			data = browser.execute_script(js_script_extract)
		if fails == 5:
			print('Failed too much, realoading page...')
			if pid != 1:
				prev_page()
			next_page()
			adjust_page(pid)
	return data

def page_id():
	pid = None
	attempts = 0
	while attempts < 10 and type(pid) != int:
		pid = browser.execute_script("let x = Array.from(document.getElementsByClassName('td2')).concat(Array.from(document.getElementsByClassName('tdBac')))[0]; if (x) return Math.floor(parseInt(x.innerHTML.replace(/\D+/g,'')) / 10) + 1")
		attempts += 1
		time.sleep(0.2)
	
	return pid if type(pid) == int else 1e9

def main(argv):
	if len(argv) != 4:
		print("Usage: python %s download_url num_pages output_file" % (argv[0]))
		return

	browser.get(argv[1])
	global num_pages, output
	num_pages = int(argv[2])
	output = open(argv[3], "a", encoding="utf-8")

	for i in range(1, num_pages + 1):
		output.write(extract_data(i))
		print("Loaded page %d/%d" % (i, num_pages))
		if i < num_pages:
			next_page()
			adjust_page(i + 1)

	print("Job done!")
	browser.close()

if __name__ == "__main__":
   main(sys.argv)