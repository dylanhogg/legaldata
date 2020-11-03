# Legal Data

[![pypi Version](https://img.shields.io/pypi/v/legaldata.svg?logo=pypi)](https://pypi.org/project/legaldata/)
![Latest Tag](https://img.shields.io/github/v/tag/dylanhogg/legaldata)
![Depenencies](https://img.shields.io/librariesio/github/dylanhogg/legaldata)

A package for crawling Australian legal data from legislation.com.au and austlii.edu.au with cache support.

Please be respectful of server host resources by using a reasonable crawl delay, 
honouring robots.txt and crawling at times when the server load is lighter.  

### Install from PyPi

```shell script
pip install legaldata
```

### legislation.com.au example

This example will crawl Commonwealth Acts from [legislation.com.au](https://www.legislation.gov.au/) and copy 
files (docx, pdf, zip) to the save path.

```python
from legaldata.legislation.crawler import ActCrawler

crawler = ActCrawler()
save_path = "./legislation.com.au/"

for index_url in crawler.get_index_pages():
    acts = crawler.get_acts_from_index(index_url, save_path)
```


### austlii.edu.au example

This example will crawl Commonwealth Acts from [austlii.edu.au/](http://www.austlii.edu.au/) and copy 
files (rtf, txt) to the save path.

```python
from legaldata.austlii.crawler import ActCrawler

crawler = ActCrawler()
save_path = "./austlii.edu.au/"

for index_url in crawler.get_index_pages():
    acts = crawler.get_acts_from_index(index_url, save_path)
```

Legal Data is distributed under the MIT license.
