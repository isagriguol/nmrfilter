import subprocess
import os
import sys

dr = sys.argv[1]
subprocess.call(['python', './api/nmrfilter/nmrfilter.py', dr])
subprocess.call(['java', '-cp', './api/nmrfilter/*',
                 'uk.ac.dmu.simulate.Convert', dr])
cmd = ['python', './api/nmrfilter/respredict/predict_standalone.py',
       '--filename', os.path.join(dr, 'testall.smi'),
       '--format', 'sdf', '--nuc', '13C', '--sanitize', '--addhs', 'false',
       '>', os.path.join(dr, 'result/predc.json')]
os.system(' '.join(cmd))

cmd = ['python', './api/nmrfilter/respredict/predict_standalone.py',
       '--filename', os.path.join(dr, 'testall.smi'),
       '--format', 'sdf', '--nuc', '1H', '--sanitize', '--addhs', 'false',
       '>', os.path.join(dr, 'result/predh.json')]
os.system(' '.join(cmd))

subprocess.call(['java', '-cp', './api/nmrfilter/*',
                 'uk.ac.dmu.simulate.Simulate', dr])
subprocess.call(['python', './api/nmrfilter/nmrfilter2.py', dr])
