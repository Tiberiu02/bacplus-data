from math import inf
import sys, getopt
import os
from selenium import webdriver
import time

NUM_ROWS_PAGE = 25
MIN_PAGES_IN_REAL_WORLD = 10

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
  if 'browser' not in globals():
    browser = webdriver.Firefox()
    browser.install_addon('web-extensions/ublock_origin-1.43.0.xpi', temporary=True)

def del_browser():
  global browser
  if 'browser' in globals():
    browser.close()

def wait4load():
  while browser.execute_script("return document.readyState") != 'complete':
    time.sleep(0.1)

def extract_data():
  wait4load()
  return browser.execute_script(js_script_extract)

# automatic page number detection
def _get_num_pages():
  wait4load()

  num_rows = int( browser.execute_script( "return document.getElementById('dynatable-record-count-candidate-list').innerText.split('/ ')[1]" ) )
  num_pages = int( num_rows / NUM_ROWS_PAGE )

  return num_pages

def get_num_pages():
  retval = _get_num_pages()
  while retval < MIN_PAGES_IN_REAL_WORLD:
    retval = _get_num_pages()

  return retval

def usage( argv0 ):
  print("Usage: python %s [-h|--help] [-v] -o|--output <output_file> <download_url>" % (argv0))
  if 'browser' in globals():
    global browser
    browser.close()
  sys.exit( 1 )

def test_browser( url1, url2 ):
  init_browser()
  browser.get( url1 )
  time.sleep( 1 )
  browser.get( url2 )

def main(argv):
  fout = 'out.csv'
  url = ''
  extra = ''
  global verbose
  verbose = False

  try:
    opts, args = getopt.getopt( argv[1:], "hvo:", ["help", "output="] )
  except getopt.GetoptError:
    usage( argv[0] )

  if len( args ) == 0:
    usage( argv[0] )

  url = args[0]
  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage( argv[0] )
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

if __name__ == "__main__":
   main(sys.argv)
   del_browser()