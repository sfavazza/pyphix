import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyPhix",
    version="0.1",
    author="Samuele Favazza",
    author_email="sfavazza.github@gmail.com",
    description="The Python Fixed Point module",
    url="https://github.com/sfavazza/pyphix",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
    ],
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering",
    ),
)
