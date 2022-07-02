import sys
import crawler_judet_EN

def usage():
  print( "Usage: python %s <output_file> <mod> <r>" % (sys.argv[0]) )
  print( " puts data from regions mod * n + r in <output_file>" )
  sys.exit( 1 )

def main( argv ):
  if( len(argv) < 4 ):
    usage()

  output = argv[1]
  mod = int( argv[2] )
  r = int( argv[3] )

  open(output, 'w').close() # clear output file

  jud = r
  while jud < 42:
    crawler_judet_EN.main([
      'crawler_judet_EN.py',
      '-o', output,
      'http://evaluare.edu.ro/Evaluare/CandFromJudAlfa.aspx?Jud=%s&PageN=1' % (str( 1 + jud ))
    ])

    jud += mod
  print('')

  crawler_judet_EN.del_browser()

if __name__ == '__main__':
  main( sys.argv )
