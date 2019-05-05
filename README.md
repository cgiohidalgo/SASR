# SASR
Semi-automatic systematic review (SASR): Is a tool that allows loading a .bib file that contains bibliographic references, the loaded data is processed obtaining basic statistics and showing the results in the graphs, creating a systematic review that is easy to understand and analyze. 

execute with python uploader.py

# #Installation
It is necessary to have a machine that has the following facilities:
Python 3.0+
Flask Framework
pip

with this, the tool will be ready to run :)

# #Configuration

go to / uploader / filter

open blog.py
uncomment
#init_db ()
 
run with: python uploader.py

open blog.py
comment
#init_db ()


It is essential to do the following to run on port 8000; otherwise the execution will be done through port 80.

go to / uploader

Open uploader.py, replace with this:

imports
import sys

from filer import create_app

if __name__ == '__main__':
    app = create_app ()
    app.debug = True
    app.run (host = '0.0.0.0', port = "8000")
    
    
CONGRATULATIONS :)
