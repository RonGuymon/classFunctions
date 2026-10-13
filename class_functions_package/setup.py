from setuptools import setup, find_packages

# For using the README.md file as the project description
with open("README.md", "r") as f:
    description = f.read()

setup(
    name="class_functions",
    version="0.2.15",  # Make sure to update this and the location of the whl file for each modification
    description="A package of functions for use in creating educational material.",
    author="R. N. Guymon",
    author_email="rnguymon@illinois.edu",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "matplotlib",
        "seaborn",
        "plotly-express",
        "numpy",
        "IPython",
        "nbformat",
        "python-docx",
        "pygments",
        "docx",
        "platformdirs",
    ],
    entry_points={
        "console_scripts": [
            "nb2docx=class_functions.nb2docx:main",
        ],
    },
    # These next two lines are also needed to turn the README.md file into the project description
    long_description=description,
    long_description_content_type="text/markdown",
)
