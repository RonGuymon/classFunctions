# classFunctions
A few simple functions that I use for teaching and demonstrations. Some of them are quite useful beyond those settings.

There are also instructions for publishing your own functions to PyPI.org so that you can easily use them on multiple computers and share them with others.

## Gradebook plotting functions

Both functions take the path to a Canvas gradebook CSV export. They find the assignment columns automatically, drop the test student and assignments with no submissions, and work whether or not there is a Yellowdig (`YD`) column.

```py
from class_functions import assignmentPlots2, parallelCoordinatesPlot

# Box plot and strip plot of scores
assignmentPlots2("gradebook.csv")

# Interactive parallel coordinates plot; run once to see the abbreviated
# column names, then exclude any assignments you don't want
parallelCoordinatesPlot("gradebook.csv", cols_to_exclude=["Q1", "H3"])
```

Optional arguments for both: `cols_to_exclude` (list of abbreviated assignment names), `normalize=True` (scale scores to 0-1), `replaceMissingWithZero=True`.

Note: `parallelCoordinatesPlot` no longer takes `numAssignments`, `startColIndex`, or `ydIndex`.

## Publish to PyPI 

First, run the terminal command if you don't already have these packages installed.
```bash
pip install setuptools wheel twine
```


In addition to the .py file that contains the functions, you will want to create other files with the file structure shown below, but using the folder and function names that are unique to your package.

### File structure
* class_functions/ 
    * class_functions/ 
        * \__init__.py 
        * main.py 
    * setup.py 
    * README.md 
    * requirements.txt 

#### \__init__.py 
Make sure to add the new function name to this file when you add a new function.
```py 
from .main import tidyUpCols, assignmentPlots, relocate, ...
```

#### main.py
This file contains the code for the class_functions package. Enter new functions in here.

#### setup.py
Use the code below, but make sure to include the packages needed for your module. Do not include modules like math, io, datetime, sqlite3, contextlib, and json that come with the standard Python distribution.

```py
from setuptools import setup, find_packages

# For using the README.md file as the project description
with open("README.md", "r") as f:
    description = f.read()

setup(
    name="class_functions",
    version="0.2.15", # Make sure to update this and the location of the whl file for each modification
    packages=find_packages(),
    install_requires=["pandas", "matplotlib", "seaborn", "plotly-express", "IPython"],
    # These next two lines are also needed to turn the README.md file into the project description
    long_description=description,
    long_description_content_type="text/markdown",
)
```

#### README.md 
This is the README.md file.

#### requirements.txt 
setuptools
wheel
twine

### Create the distribution and whl files  
Run the following shell command in the folder where setup.py is located:
```bash
python setup.py sdist bdist_wheel
```


### Test locally 
You can install this on your computer where your other Python libraries are located using the following terminal command from the folder where the setup.py file is located, but rather than the dist/class_functions... file, use the one for your module:
```bash 
pip install dist/class_functions-0.2.15-py3-none-any.whl
``` 
If you need to reinstall it, run it with `--force-reinstall` to force installation of the whl file.

You can now run the terminal command `pip list` to see the package listed with the others on your computer. You can also try using functions in a new IPYNB or PY file just like any other package.

### Upload to PyPI
First create an account on PyPI.org and create an API token. It's free to do so.

Then upload it using the following terminal command from the same folder as your setup.py file:
```bash
twine upload dist/*
```

If you just need to upload the files for a new version, then use this code:
```bash
twine upload dist/class_functions-0.2.15*
```

Be prepared to enter your API token. Alternatively, you can set environment variables so that they can be accessed as part of a workflow that does not need manual intervention. See below for how to do that. The environment variables and the values are: 

`TWINE_USERNAME="__token__"`  

`TWINE_PASSWORD="get this from pypi.org"`

Once It is uploaded, anyone can download and install the package using the terminal command: 

```bash
pip install class-functions
```

#### Viewing and setting environment variables

__Mac (Apple Silicon)__

* To view an individual variable, run the shell command `echo $TWINE_PASSWORD`
* To view all the variables, run the shell command `printenv` or `env`
* To view the file that contains all environment variables run the shell command `vim ~/.zshrc`
    * You can then add a new permanent one in there, and then be sure to run `source ~/.zshrc` to save and reload it.

__Windows__
* GUI approach: Press Windows key → type "environment variables" and select the edit environment variables, which will bring up a window
* To view an individual variable, run the shell command `echo %TWINE_PASSWORD%`
* To view all the variables, run the shell command `set`
* To create a new permanent environment variable, run the shell command `setx TWINE_PASSWORD "py-dwelasdf3...and the rest of the token"`
* To view the file that contains all environment variables run the shell command `vim ~/.zshrc`
    * Close the shell and open a new session to see the new variable.


#### Hattip
Thanks to [pixegami](https://www.youtube.com/watch?v=Kz6IlDCyOUY&ab_channel=pixegami) for the wonderful video detailing how to do this.