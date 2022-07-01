import subprocess
import sys

def usage():
  print( "Usage: python %s <output_file>" % (sys.argv[0]) )
  sys.exit( 1 )

if( len(sys.argv) < 2 ):
  usage()

output = sys.argv[1]

open(output, 'w').close() # clear output file

for jud in range( 42 ):
  subprocess.run([
    'python', 'crawler_judet_EN.py',
    '-o', output,
    'http://evaluare.edu.ro/Evaluare/CandFromJudAlfa.aspx?Jud=%s&PageN=1' % (str( 1 + jud ))
  ])