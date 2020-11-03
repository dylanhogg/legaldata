import os
import re
import time
import json
import dataclasses
import logging
import urllib
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import List, Tuple
from bs4 import BeautifulSoup
from legaldata import base
from legaldata.austlii.act import Act


class ActCrawler(base.Crawler):
    """
    AustLII is Australia's online free-access resource for Australian legal information, serving the needs of a
    multitude of users with over 700,000 hits daily. AustLII is a joint facility of the UTS and UNSW Faculties of Law.
    AustLII relies on the generosity of its contributors to operate. To make a tax deductible contribution please use
    our contribution form: http://www.austlii.edu.au/austlii/contributors/contribute.pdf

    http://www.austlii.edu.au/about.html
    """

    def __init__(self, user_agent="Mozilla/5.0 pypi.org/project/legaldata/"):
        super(ActCrawler, self).__init__()
        self.user_agent = user_agent
        opener = urllib.request.build_opener()
        opener.addheaders = [("User-Agent", self.user_agent)]
        urllib.request.install_opener(opener)

    def _scrape_page(self, url, cache_path, use_cache) -> Tuple[BeautifulSoup, bool]:
        cache_filename = f"{cache_path}austlii-{self.valid_filename(url)}.html"
        cache_filename_exists = Path(cache_filename).is_file()
        loaded_from_cache = False

        logging.debug(f"use_cache = {use_cache}")
        logging.debug(f"cache_filename = {cache_filename}")

        if not use_cache or not cache_filename_exists:
            logging.info(f"Scraping: {url}")

            # TODO: define new user-agent for legaldata
            req = urllib.request.Request(url, data=None, headers={"User-Agent": self.user_agent})
            response = urllib.request.urlopen(req)
            soup = BeautifulSoup(response, "html.parser")
            if cache_filename is not None:
                logging.debug(f"Saving to cache: {cache_filename}")
                self.save(soup, cache_filename)
        else:
            logging.info(f"Loading from cache: {cache_filename}")
            soup = self.load(cache_filename)
            loaded_from_cache = True

        return soup, loaded_from_cache

    @staticmethod
    def _get_act_download_page_urls(soup) -> List[str]:
        regex = r"cgi-bin/viewdoc/au/legis/cth/consol_act/[^/]+/"
        links = re.findall(regex, str(soup))
        download_pages = [f"http://www.austlii.edu.au/{link}" for link in links]
        download_pages = list(set(download_pages))
        return sorted(download_pages)

    @staticmethod
    def clean_details_text(s) -> List[str]:
        s = re.sub("[\n]{2,}", "$NL$", s)
        s = re.sub("[\n]+", " ", s)
        s = s.replace("$NL$", "\n")
        s = re.sub(" +", " ", s)
        return s.strip().split("\n")

    def get_acts_from_index(
        self,
        index_url,
        save_path,
        save_file_prefix="",
        cache_path=None,
        use_cache=True,
        act_limit=None,
        delay_sec=5,
    ) -> List[Act]:
        assert index_url is not None
        assert save_path is not None
        assert save_file_prefix is not None

        if cache_path is None:
            cache_path = self.default_cache_path

        os.makedirs(cache_path, exist_ok=True)
        os.makedirs(save_path, exist_ok=True)

        logging.info(f"Crawling index_url: {index_url}")
        logging.warning("TODO: Handle multiple pages in index page!")
        # TODO: WARN: Handle multiple pages in index page!
        #       Currently we hope all acts are on the first page, which appears to be the case but isn't tested.
        try:
            (seed_soup, loaded_from_cache) = self._scrape_page(index_url, cache_path, use_cache)
        except urllib.error.HTTPError as err:
            logging.error(
                f"Index page {index_url} retured HTTPError: {err} "
                f"(note that indexes K, X, Y, Z don't exist as of Oct 2020)"
            )
            return []
        download_page_urls = self._get_act_download_page_urls(seed_soup)
        logging.info(f"Number of download page URLs: {len(download_page_urls)}")

        # Get act information
        acts = []
        for i, download_page_url in enumerate(download_page_urls):
            if act_limit is not None and i >= act_limit:
                break

            logging.debug(f"Crawling download page: {download_page_url}")
            act = self._get_act(download_page_url, cache_path, use_cache)
            acts.append(act)

        # Download act files (pdf, docx, etc)
        for act in acts:
            act.saved_filenames = []
            for i, download_link in enumerate(act.download_links):
                # Save file (docx, rtf, txt, etc)
                save_filename, header_ext, loaded_from_cache, success = self._scrape_file(
                    act, download_link, save_path, save_file_prefix, cache_path, use_cache
                )
                if not success:
                    continue

                # For Austlii, when .txt file requested we actually get .html page with dl links in it,
                # so we parse the html page for the real .txt file link.
                download_split = os.path.splitext(download_link)
                download_ext = "" if len(download_split) < 2 else download_split[1]
                if len(download_ext) > 0 and header_ext is not None and header_ext.lower() != download_ext.lower():
                    # Download txt file from link in html page
                    (seed_soup, loaded_from_cache) = self._scrape_page(download_link, cache_path, use_cache)
                    redirected_download_link = self._get_act_redirected_download_page_url(seed_soup, download_link)
                    os.remove(save_filename)  # Remove redirect html page
                    save_filename, header_ext, loaded_from_cache, success = self._scrape_file(
                        act, redirected_download_link, save_path, save_file_prefix, cache_path, use_cache
                    )

                act.saved_filenames.append(os.path.basename(save_filename))
                # Save metadata
                if i == (len(act.download_links) - 1):
                    metadata_filename = os.path.splitext(save_filename)[0] + ".meta.json"
                    with open(metadata_filename, "w") as f:
                        metadata = json.dumps(dataclasses.asdict(act), indent=4)  # , sort_keys=True)
                        f.write(metadata)
                # Throttle
                if not loaded_from_cache:
                    time.sleep(delay_sec)

        return acts

    @staticmethod
    def _get_act_redirected_download_page_url(soup, download_link) -> str:
        # url: http://www8.austlii.edu.au/cgi-bin/download.cgi/cgi-bin/download.cgi/download/au/legis/cth/consol_act/anhcslia1998780.txt
        # download_link: http://www.austlii.edu.au/au/legis/cth/consol_act/amsaa1990405.txt
        # download_ext : .txt
        # header_ext   : .html

        download_filename = os.path.basename(download_link)
        regex = rf"http.+{download_filename}"
        links = re.findall(regex, str(soup))
        assert len(links) > 0
        return links[0]

    def _get_act(self, download_page_url, cache_path, use_cache) -> Act:
        (soup, loaded_from_cache) = self._scrape_page(download_page_url, cache_path, use_cache)

        # E.g. http://www.austlii.edu.au/au/legis/cth/consol_act/antsbna1999470.txt
        base_url = "http://www.austlii.edu.au"
        # base_url = "http://www8.austlii.edu.au"

        dl_div = soup.find("div", {"class": "side-download"})
        download_links = [base_url + x["href"] for x in dl_div.find_all("a")]
        download_links = list(set(download_links))

        # Get code
        file_code = "" if len(download_links) == 0 else os.path.splitext(os.path.basename(sorted(download_links)[0]))[0]

        # Get <title> tag
        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag is not None else ""

        # TODO: crawl the long title url if exists?
        # e.g.
        # main: http://www.austlii.edu.au/cgi-bin/viewdb/au/legis/cth/consol_act/antsbna1999470/
        # long: http://www.austlii.edu.au/cgi-bin/viewdoc/au/legis/cth/consol_act/antsbna1999470/longtitle.html

        # Get html <meta> tag info
        meta_tags_tuples = [(x.attrs.get("name", None), x.attrs.get("content", None)) for x in soup.find_all("meta")]
        meta_tags = dict([(x[0].strip().lower(), x[1].strip()) for x in meta_tags_tuples if x[0] is not None])
        desc = meta_tags.get("description", "")

        crawl_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        saved_filenames = []
        return Act(
            title,
            file_code,
            desc,
            meta_tags,
            download_page_url,
            download_links,
            loaded_from_cache,
            crawl_date,
            saved_filenames,
        )

    @staticmethod
    def get_index_pages() -> List[str]:
        # TODO: scrape root index page to get these
        #       https://www.legislation.gov.au/Browse/ByTitle/Acts/InForce/0/0/Principal

        index_urls = [
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-A.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-B.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-C.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-D.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-E.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-F.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-G.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-H.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-I.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-J.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-K.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-L.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-M.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-N.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-O.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-P.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-Q.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-R.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-S.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-T.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-U.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-V.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-W.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-X.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-Y.html",
            "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-Z.html",
        ]

        return index_urls
