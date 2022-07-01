import subprocess
import sys

def usage():
  print( "Usage: python %s <output_file>" % (sys.argv[0]) )
  sys.exit( 1 )

if( len(sys.argv) < 2 ):
  usage()

output = sys.argv[1]

meta_str = open("meta/meta-judete-num.txt", "r").read()
meta = [line.split(',') for line in meta_str.split('\n')]

open(output, 'w').close() # clear output file

for jud in meta:
  subprocess.run([
    'python', 'crawler_judet_EN.py',
    '-o', output,
    '--judet', jud[0],
    'http://evaluare.edu.ro/Evaluare/CandFromJudAlfa.aspx?Jud=%s&PageN=1' % (jud[1])
  ])