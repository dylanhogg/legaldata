from setuptools import setup, find_packages

version = "0.0.3"

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    install_requires = [x.strip() for x in f if x.strip()]

setup(
    name="legaldata",
    version=version,
    description="A package for getting getting Australian legal data from various sources with cache support.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dylanhogg/legaldata",
    author="Dylan Hogg",
    author_email="dylanhogg@gmail.com",
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Legal Industry",
        "Topic :: Software Development",
        "Topic :: Text Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="legal, law, data, crawler",
    package_dir={"": "legaldata"},
    packages=find_packages(where="legaldata"),
    python_requires=">=3.6, <4",
    install_requires=install_requires,
)
