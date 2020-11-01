# Legal Data (alpha version)

[![pypi Version](https://img.shields.io/pypi/v/legaldata.svg?logo=pypi)](https://pypi.org/project/legaldata/)
![Latest Tag](https://img.shields.io/github/v/tag/dylanhogg/legaldata)
![Depenencies](https://img.shields.io/librariesio/github/dylanhogg/legaldata)

A package for getting getting Australian legal data from various sources with cache support.


### Install from PyPi

```shell script
pip install legaldata
```

### legislation.com.au example

```python
from legaldata.legislation.crawler import ActCrawler

crawler = ActCrawler()
save_path = "./legislation.com.au/"

for index_url in crawler.get_index_pages():
    acts = crawler.get_acts_from_index(index_url, save_path)
```


### austlii.edu.au example

```python
from legaldata.austlii.crawler import ActCrawler

crawler = ActCrawler()
save_path = "./austlii.edu.au/"

for index_url in crawler.get_index_pages():
    acts = crawler.get_acts_from_index(index_url, save_path)
```

Legal Data is distributed under the MIT license.
