import os
import re
import time
import logging
from pathlib import Path
from typing import List, Tuple, Dict
from urllib.request import urlopen
from bs4 import BeautifulSoup
from legaldata import base
from legaldata.legislation.act import Act


class ActCrawler(base.Crawler):
    def __init__(self):
        super(ActCrawler, self).__init__()

    def _scrape_page(self, url, cache_path, use_cache) -> Tuple[BeautifulSoup, bool]:
        cache_filename = f"{cache_path}legal-{self.valid_filename(url)}.html"
        cache_filename_exists = Path(cache_filename).is_file()
        loaded_from_cache = False

        logging.debug(f"use_cache = {use_cache}")
        logging.debug(f"cache_filename = {cache_filename}")

        if not use_cache or not cache_filename_exists:
            logging.debug(f"Scraping: {url}")
            response = urlopen(url)
            soup = BeautifulSoup(response, "html.parser")
            if cache_filename is not None:
                logging.debug(f"Saving to cache: {cache_filename}")
                self.save(soup, cache_filename)
        else:
            logging.debug(f"Loading from cache: {cache_filename}")
            soup = self.load(cache_filename)
            loaded_from_cache = True

        return soup, loaded_from_cache

    @staticmethod
    def _get_act_download_page_urls(soup) -> List[str]:
        # Match: /Details/C2018C00418/Download or /Details/<act_code>/Download
        act_codes = re.findall(r"../Details/([^/]*)/Download", str(soup))
        download_pages = [f"https://www.legislation.gov.au/Details/{code}/Download" for code in act_codes]
        return download_pages

    @staticmethod
    def _get_act(soup) -> Tuple[List[str], Dict]:
        # Match: /Details/C2014C00072/18b59cb0-976c-4721-ac2b-c5a57016703b or /Details/<act_code>/<guid>
        code_guids = re.findall(
            r"../Details/([^/]*/[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})", str(soup)
        )
        act_download_links = [f"https://www.legislation.gov.au/Details/{code_guid}" for code_guid in code_guids]
        act_download_links = list(set(act_download_links))

        act_metadata = {}

        # TODO: get act_metadata like act title, page size, series link, "In force - Latest Version" flag etc

        return act_download_links, act_metadata

    def get_acts(self, index_url, save_path, cache_path=None, use_cache=True, limit=None, delay_sec=0.5) -> List[str]:
        assert save_path is not None

        if cache_path is None:
            cache_path = self.default_cache_path

        os.makedirs(cache_path, exist_ok=True)
        os.makedirs(save_path, exist_ok=True)

        logging.debug(f"Crawling index_url: {index_url}")
        (seed_soup, loaded_from_cache) = self._scrape_page(index_url, cache_path, use_cache)
        download_page_urls = self._get_act_download_page_urls(seed_soup)

        all_act_download_links = []
        for i, download_page_url in enumerate(download_page_urls):
            if limit is not None and i >= limit:
                break

            logging.debug(f"Crawling download page: {download_page_url}")
            (download_soup, loaded_from_cache) = self._scrape_page(download_page_url, cache_path, use_cache)
            (single_act_download_links, act_metadata) = self._get_act(download_soup)
            all_act_download_links.extend(single_act_download_links)

        saved_act_filenames = []
        for download_link in all_act_download_links:
            save_filename, loaded_from_cache = self._scrape_file(download_link, save_path, cache_path, use_cache)
            saved_act_filenames.append(save_filename)
            if not loaded_from_cache:
                time.sleep(delay_sec)

        # TODO: loop thru download_page_urls for act metadata also

        # TODO: return list of Act classes
        return saved_act_filenames
