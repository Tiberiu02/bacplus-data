import sys, os
#from subprocess import Popen, PIPE
from subprocess import run as system
import json

BUFSIZE = 32 * 1024 # 32Kb output buffer

SELECTED_FIELDS = [
  'name',   # cod
  'school', # scoala

  # romana
  'ri',
  'ra',
  'rf',

  # matematica
  'mi', 
  'ma',
  'mf',

  # limba materna
  'lmp',
  'lmi',
  'lma',
  'lmf',

  'mev' # media finala
]

def usage():
  print( "Usage: python %s <year> <output file>" % (sys.argv[0]) )
  print( "  crawls year <year> and puts output in <output file>" )
  sys.exit( 1 )

def main( argv ):
  if( len(argv) < 3 ):
    usage()

  year = argv[1]
  fout_name = argv[2]

  fjud = open( "meta/coduri-judete.txt", "r" )
  coduri = [line.split(',')[0] for line in fjud.readlines()]
  fjud.close()

  system( ['rm', '-rf', 'tmp'] ) # to not interfere with previous runs
  system( ['mkdir', 'tmp'] )

  rezarr = []
  for cod in coduri:
    system( ['wget', '-q', '--show-progress', '-O', 'tmp/%s_%s.json' % (cod, year), 'evaluare.edu.ro/%s/rezultate/%s/data/candidate.json' % (year, cod)] )
    with open( 'tmp/%s_%s.json' % (cod, year), 'r' ) as fjson:
      rezarr_jud = json.load( fjson )
      rezarr += rezarr_jud
    system( ['rm', 'tmp/%s_%s.json' % (cod, year)] )

  system( ['rmdir', 'tmp'] )

  # now we have to turn the json array into the output CSV file

  fout = open( fout_name, 'w', buffering = BUFSIZE )

  for entry in rezarr:
    fout.write( '\t'.join(
      map( lambda i : ('-' if entry[i] == None else str(entry[i])), SELECTED_FIELDS )
    ) + '\n' )

  fout.close()

if __name__ == '__main__':
  main( sys.argv )
