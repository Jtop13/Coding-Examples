The following files highlights skills
learned and applied over my
summer internship at NASA.

All of the work was completed in Python
for the sake of organization I used juptyer
notebooks, for the machine learning portion,
thats why the files have .ipynb extentsion


The folder Generation contains python scripts
that call methods from one another in order to
generate +500k synethic flux ropes developed from my
mentors mathematical model, in order to offer
enough data to train a neural network. I used pre-existing
files create.py and fractal_synth.py that were created by 
my colleagues in order to implement generate.py for the 
machine learning purpose.

The file CNN_1D... shows the process of reading the 
synetic files in, converting them to npz files and
passing them into a data generator(processor) and then
used for training. 

The Noise_Analysis file shows the model being tested on
real life flux ropes to "predict" their orientation.
Lots of statistics and graphical tools are used here 
to show how well the model performed. 
