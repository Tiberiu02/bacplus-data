from math import inf
import sys, getopt
import os
from selenium import webdriver
import time

NUM_ROWS = 20

num_pages, output = None, None
verbose = False

os.environ['PATH'] = os.environ['PATH'] + ":."

js_script_extract = open("js/extract_EN.js", "r").read()
js_script_next = open("js/next.js", "r").read()
js_script_last = open("js/last.js", "r").read()
js_script_first = open("js/first.js", "r").read()

coduri_judete = {}
for line in open("meta/coduri-judete.txt", "r").read().split('\n'):
  v = line.split(',')
  if len(v) == 2:
    coduri_judete[v[0]] = v[1]

def init_browser():
  global browser
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
      if verbose:
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
      if verbose:
        print('Next page')
    while page_id() > id:
      prev_page()
      if verbose:
        print('Prev page')

def extract_data(pid):
  fails = 5
  while fails == 5:
    data = browser.execute_script(js_script_extract)
    fails = 0
    while fails < 5 and pid < num_pages and data != None and data.count('\n') < NUM_ROWS:
      if verbose:
        print('Data not fetched correctly, waiting and retrying')
        print(data)
      fails += 1
      time.sleep(1)
      data = browser.execute_script(js_script_extract)
    if fails == 5:
      if verbose:
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
    pid = browser.execute_script("let x = Array.from(document.getElementsByClassName('tdnr'))[0]; if(x) return Math.floor(parseInt(x.innerHTML.replace(/\D+/g,'')) / " + str(NUM_ROWS) + ") + 1")
    attempts += 1
    time.sleep(0.2)
  
  return pid if type(pid) == int else 1e9

# automatic page number detection
def get_num_pages():
  #wait for page to load
  time.sleep(0.2)
  while browser.execute_script("return document.readyState") != 'complete':
    time.sleep(0.1)

  browser.execute_script(js_script_last)

  time.sleep(0.2)
  while browser.execute_script("return document.readyState") != 'complete':
    time.sleep(0.1)

  retval = page_id()

  browser.execute_script(js_script_first)

  return retval

def usage():
  print("Usage: python %s [-h|--help] [-v] -o|--output <output_file> <download_url>" % (sys.argv[0]))
  if 'browser' in globals():
    global browser
    browser.close()
  sys.exit( 1 )

def main(argv):
  fout = 'out.csv'
  url = ''
  extra = ''
  global verbose
  verbose = False

  try:
    opts, args = getopt.getopt( argv[1:], "hvo:", ["help", "output="] )
  except getopt.GetoptError:
    usage()

  if len( args ) == 0:
    usage()

  url = args[0]
  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage()
    elif opt == '-v':
      verbose = True
    elif opt in ('-o', '--output'):
      fout = arg

  init_browser()
  browser.get( url )
  global num_pages, output

  num_pages = get_num_pages()

  output = open(fout, "a", encoding="utf-8")

  for i in range(1, num_pages + 1):
    data = extract_data( i )
    output.write( data )

    if data[:2] in coduri_judete.keys():
      judet = coduri_judete[data[:2]]
    elif data[0] in coduri_judete.keys():
      judet = coduri_judete[data[0]]
    else:
      judet = '??'

    print("Loaded page %d/%d (%s)   " % (i, num_pages, judet), end = ("\n" if verbose else "\r"))
    if i < num_pages:
      next_page()
      adjust_page(i + 1)

  print("Job done!" if verbose else "")
  output.close()
  browser.close()

if __name__ == "__main__":
   main(sys.argv)