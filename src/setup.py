import setuptools

with open("README.md") as fh:
    long_description = fh.read()

try:
    REQUIREMENTS = list(open("requirements.txt").read().splitlines())
except OSError:
    REQUIREMENTS = []

setuptools.setup(
    name="hootingyard",
    version="0.0.1",
    author="Salim Fadhley & Glyn Webster",
    author_email="salimfadhley@gmail.com",
    description="Hooting Yard archive amnagement",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=["hootingyard"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
)
