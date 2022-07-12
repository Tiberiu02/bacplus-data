from math import inf, ceil
import sys, getopt
import os
from selenium import webdriver
import time

NUM_ROWS_PAGE = 25
MIN_PAGES_IN_REAL_WORLD = 10
BUFSIZE = 32 * 1024 # 32Kb output buffer

num_pages, output = None, None
verbose = False

os.environ['PATH'] = os.environ['PATH'] + ":."

js_script_extract = open("js/extract_EN.js", "r").read()
js_script_next = open("js/next.js", "r").read()

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
    time.sleep( 0.1 )
  time.sleep( 0.1 )

def extract_data( url=None ):
  if url != None:
    browser.get( url )

  wait4load()

  while browser.execute_script( "return document.querySelectorAll( '#candidate-list > tbody > tr' ).lenght" ) == 0:
    time.sleep( 0.1 )

  return browser.execute_script( js_script_extract )

# automatic page number detection
def _get_num_pages():
  wait4load()

  num_rows = int( browser.execute_script( "return document.getElementById('dynatable-record-count-candidate-list').innerText.split('/ ')[1]" ) )
  num_pages = ceil( num_rows / NUM_ROWS_PAGE )

  return num_pages

def get_num_pages():
  retval = _get_num_pages()
  while retval < MIN_PAGES_IN_REAL_WORLD:
    retval = _get_num_pages()

  return retval

def crawl_judet( url, fout_name ):
  fout = open( fout_name, "a", buffering = BUFSIZE )

  init_browser()

  browser.get( url )
  num_pages = get_num_pages()
  for page in range( num_pages ):
    fout.write( extract_data( "%s?page=%d" % (url, 1 + page) ) )

  fout.close()

# ui

def usage():
  print( "Usage: python %s\n  The script listens to stdin\n  each query (line) must be of the format:\n    <url>;<output file>\n" % sys.argv[0] )
  sys.exit( 1 )

def main():
  running = True
  while running:
    try:
      line = input()
      args = line.split( ';' )
      crawl_judet( args[0], args[1] )
    except EOFError:
      running = False

if __name__ == "__main__":
  if len( sys.argv ) > 1:
    usage()

  main()
  del_browser()
