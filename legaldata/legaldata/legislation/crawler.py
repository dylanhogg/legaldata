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
    """
    The Federal Register of Legislation is the authorised whole-of-government website for Commonwealth legislation
    and related documents. It contains the full text and details of the lifecycle of individual laws and the
    relationships between them.

    https://www.legislation.gov.au/Content/Linking
    """
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

    def get_acts(self, index_url, save_path, save_file_prefix="legislation.com.au_", cache_path=None, use_cache=True,
                 limit=None, delay_sec=5) -> List[str]:
        assert index_url is not None
        assert save_path is not None
        assert save_file_prefix is not None

        if cache_path is None:
            cache_path = self.default_cache_path

        os.makedirs(cache_path, exist_ok=True)
        os.makedirs(save_path, exist_ok=True)

        logging.debug(f"Crawling index_url: {index_url}")
        # TODO: handle multiple pages in index page!
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
            save_filename, loaded_from_cache = self._scrape_file(download_link, save_path, save_file_prefix, cache_path, use_cache)
            saved_act_filenames.append(save_filename)
            if not loaded_from_cache:
                time.sleep(delay_sec)

        # TODO: loop thru download_page_urls for act metadata also

        # TODO: return list of Act classes
        return saved_act_filenames

    @staticmethod
    def get_index_pages() -> List[str]:
        # TODO: scrape root index page to get these
        #       https://www.legislation.gov.au/Browse/ByTitle/Acts/InForce/0/0/Principal

        index_urls = [
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ab/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/AC/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ad/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ae/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ag/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ag/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ai/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Al/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/An/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ap/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ar/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/As/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/At/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Au/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Av/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ba/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Bi/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Bo/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Br/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Bu/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ca/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ce/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/CF/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ch/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ci/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Cl/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Co/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Cr/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/CS/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Cu/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Da/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/De/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Di/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Do/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ea/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ed/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Eg/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/El/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Em/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/En/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ep/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Eq/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Eu/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ev/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ex/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Fa/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Fe/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Fi/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Fl/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Fo/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Fr/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Fu/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ga/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ge/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Go/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Gr/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Gu/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ha/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/He/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Hi/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ho/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Hu/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Il/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Im/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/In/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ja/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Je/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ju/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/La/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Le/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Li/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Lo/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ma/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Me/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Mi/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Mo/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Mu/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/My/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Na/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ne/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/No/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Nu/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Oc/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Of/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ol/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Om/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Or/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ov/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Oz/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Pa/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Pe/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Pi/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Pl/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Po/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Pr/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ps/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Pu/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Qa/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ra/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Re/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ro/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ru/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Sa/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Sc/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Se/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Sh/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Sm/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Sn/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/So/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Sp/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/St/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Su/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Sy/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ta/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Te/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Th/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/To/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Tr/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Un/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ur/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/VE/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Wa/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/We/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Wh/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Wi/0/0/principal",
            "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Wo/0/0/principal",
        ]

        return index_urls
