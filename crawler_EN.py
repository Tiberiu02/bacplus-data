import sys, os
#from subprocess import Popen, PIPE
import subprocess

NUM_JUD = 42

def usage():
  print( "Usage: python %s <year> <number of browser windows> <output file>" % (sys.argv[0]) )
  print( "  crawls year <year> and puts output <output file> using the specified number of windows" )
  sys.exit( 1 )

def main( argv ):
  if( len(argv) < 4 ):
    usage()

  year = argv[1]
  nwin = int( argv[2] )
  fout = argv[3]

  fjud = open( "meta/coduri-judete.txt", "r" )
  coduri = [line.split(',')[0] for line in fjud.read().split('\n')]
  fjud.close()

  os.system( 'mkdir tmp' )
  crawl_proc = [ subprocess.Popen( ['python', 'crawler_base.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE ) for i in range( nwin ) ]

  # send queries
  win = 0
  for cod in coduri:
    crawl_proc[win].stdin.write(
      ("http://evaluare.edu.ro/%s/rezultate/%s/;tmp/%s.csv\n" % (year, cod, win)).encode()
    )
    win = (win + 1) % nwin

  for proc in crawl_proc:
    proc.stdin.write( b"END\n" )

  # wait for crawlers to finish
  for proc in crawl_proc:
    proc.communicate()

  os.system( 'cat %s > %s' % (
    ' '.join(['tmp/%d.csv' % (i,) for i in range( nwin )]),
    fout
  ))
  
  #for i in range( nwin ):
  #  os.system( 'rm tmp/%d.csv' % (i,) )
  #os.system( 'rmdir tmp' )

if __name__ == '__main__':
  main( sys.argv )
