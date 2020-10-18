import os
import shutil
from pathlib import Path
from legaldata.legislation import crawler
from legaldata.helpers import pdf2text

cache_path = "./_data/test_cache_path/"
save_path = "./_data/test_output_path/"


def remove_dirs():
    if os.path.exists(cache_path) and os.path.isdir(cache_path):
        shutil.rmtree(cache_path)
    if os.path.exists(save_path) and os.path.isdir(save_path):
        shutil.rmtree(save_path)


def test_get_acts_cached():
    remove_dirs()
    index_url = "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Pr/0/0/principal"
    save_filenames_typed = crawler.ActCrawler().get_acts(index_url, save_path, use_cache=True, limit=3, delay_sec=1)
    assert len(save_filenames_typed) > 0
    for file in save_filenames_typed:
        assert Path(file).is_file()


def test_get_acts_no_cache():
    remove_dirs()
    index_url = "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Pr/0/0/principal"
    save_filenames_typed = crawler.ActCrawler().get_acts(index_url, save_path, use_cache=False, limit=1, delay_sec=1)
    assert len(save_filenames_typed) > 0
    for file in save_filenames_typed:
        assert Path(file).is_file()


def xtest_pdf2text():
    for filename in os.listdir(save_path):
        if filename.endswith("pdf"):
            full_filename = save_path + filename
            print(full_filename)
            pdf2text.convert_pdfminer(full_filename)
