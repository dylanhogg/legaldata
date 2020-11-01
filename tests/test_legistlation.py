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
    act_limit = 3
    index_url = crawler.ActCrawler().get_index_pages()[0]
    acts = crawler.ActCrawler().get_acts_from_index(index_url, save_path, use_cache=True, act_limit=act_limit, delay_sec=1)
    assert len(acts) == act_limit
    for act in acts:
        assert act.title is not None and len(act.title) > 0
        assert len(act.download_links) == len(act.saved_filenames)
        for file in act.saved_filenames:
            assert Path(os.path.join(save_path, file)).is_file()


def test_get_acts_no_cache():
    remove_dirs()
    act_limit = 1
    index_url = crawler.ActCrawler().get_index_pages()[0]
    acts = crawler.ActCrawler().get_acts_from_index(index_url, save_path, use_cache=False, act_limit=act_limit, delay_sec=1)
    assert len(acts) == act_limit
    for act in acts:
        assert act.title is not None and len(act.title) > 0
        assert len(act.download_links) == len(act.saved_filenames)
        for file in act.saved_filenames:
            assert Path(os.path.join(save_path, file)).is_file()


def xtest_pdf2text():
    for filename in os.listdir(save_path):
        if filename.endswith("pdf"):
            full_filename = os.path.join(save_path, filename)
            print(full_filename)
            pdf2text.convert_pdfminer(full_filename)
