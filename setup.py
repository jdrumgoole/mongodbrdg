

from setuptools import setup, find_packages
import os
import glob
from mongodbrdg.version import __VERSION__

pyfiles = [f for f in os.listdir(".") if f.endswith(".py")]

from os import path

import sys
python_major = sys.version_info[0]
python_minor = sys.version_info[1]

if python_major <= 2:
    sys.exit("Sorry, You are running python {0}.{1} which is not supported".format(python_major, python_minor))
elif python_minor < 6:
    sys.exit("Sorry, You are running python {0}.{1} which is not supported".format(python_major, python_minor))

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="mongodbrdg",
    version=__VERSION__,

    author="Joe Drumgoole",
    author_email="joe@joedrumgoole.com",
    description="MongoDB RDG - Random data generator for MongoDB",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="Apache 2.0",
    keywords="Random Data MongoDB",
    url="https://github.com/jdrumgoole/mongdb_random_data_generator",

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6'],

    install_requires=["pymongo",
                      "nose",
                      "mimesis",
                      "dnspython"],

    packages=find_packages(),

    data_files=[],
    project_urls={
        "github src" : "https://github.com/jdrumgoole/mongodb_random_data_generator",
        "Issues" : "https://github.com/jdrumgoole/mongodb_random_data_generator/issues",
    },
    python_requires='>=3.6',
    scripts=[],
    entry_points={
        'console_scripts': [
            'mongodbrdg=mongodbrdg.mongodbrdg_main:main',
        ]
    },

    test_suite='nose.collector',
    tests_require=['nose'],
)
