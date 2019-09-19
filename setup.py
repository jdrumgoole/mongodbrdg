

from setuptools import setup, find_packages
import os
import glob
from mongodbrdg.version import __VERSION__

pyfiles = [f for f in os.listdir(".") if f.endswith(".py")]

setup(
    name="mongdbrdg",
    version=__VERSION__,

    author="Joe Drumgoole",
    author_email="joe@joedrumgoole.com",
    description="MongoDB Bridge - Random data generator for MongoDB",
    long_description=
    '''
Use mongodbrdg to generate random data for MongoDB. Use the -h option
to see how to generate data. We generate data using a seed and the same
seed will generate the same data. The data is random but looks like
real data. We use the Mimesis package to generate the data.
''',

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
        'Programming Language :: Python :: 3.7'],

    install_requires=["pymongo",
                      "nose",
                      "dnspython"],

    packages=find_packages(),

    data_files=[],
    python_requires='>3.7',
    scripts=[],
    entry_points={
        'console_scripts': [
            'mongodbrdg=mongodbrdg.mongdbrdg_main:main',
        ]
    },

    test_suite='nose.collector',
    tests_require=['nose'],
)
