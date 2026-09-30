"""
   Copyright [2025] [Rosalind Franklin Institute]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os

from setuptools import find_packages, setup

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")
) as fp:
    install_requires = fp.read().splitlines()

with open(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements-dev.txt")
) as fp:
    dev_requires = fp.read().splitlines()

setup(
    version="0.0.23",
    name="GlobusAPI",
    description="Containerized API for interacting with Globus.",
    url="https://github.com/rosalindfranklininstitute/rfi-globus-api",
    author="Joss Whittle, Sylvie Ramos, Dimitrios Bellos, Laura Shemilt, Nick Crawford, Gabryel Mason-Williams, Alex Lubbock",
    author_email="arc@rfi.ac.uk",
    packages=find_packages("src"),
    package_dir={"": "src"},
    test_suite="tests",
    classifiers=[
        "Operating System :: POSIX :: Linux",
    ],
    zip_safe=False,
    install_requires=install_requires,
    extras_require={"dev": dev_requires},
)
