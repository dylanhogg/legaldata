import filetype
import logging
import mimetypes
import string
import shutil
import pickle
from typing import List, Tuple, Dict
from urllib.request import urlopen, urlretrieve
from pathlib import Path
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self):
        self.default_cache_path = ".legaldata-cache/"

    @staticmethod
    def valid_filename(url) -> str:
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = url.lower()
        filename = filename.replace("https://", "")
        filename = filename.replace("http://", "")
        filename = filename.replace("/", "_")
        filename = "".join(c for c in filename if c in valid_chars)
        filename = filename.replace(" ", "_")
        return filename

    @staticmethod
    def load(filename) -> BeautifulSoup:
        html = open(filename).read()
        soup = BeautifulSoup(html, "html.parser")
        return soup

    @staticmethod
    def save(obj, filename) -> None:
        with open(filename, "w") as f:
            f.write(str(obj))

    @staticmethod
    def _get_header_info(headers):
        filename = headers.get("Content-Disposition").split("filename=")[1]
        content_type = headers.get("Content-Type").partition(";")[0].strip()
        ext = mimetypes.guess_extension(content_type)
        if ext is None:
            logging.info(f"Unknown file type for content_type: {content_type}")
            ext = ".unk"
        return filename, ext

    def _scrape_file(self, download_link, save_path, cache_path, use_cache) -> Tuple[str, bool]:
        save_filename_no_ext = f"{save_path}legal-{self.valid_filename(download_link)}"
        cache_filename = f"{cache_path}legal-{self.valid_filename(download_link)}.urlretrieve"
        cache_filename_exists = Path(cache_filename).is_file()
        pkl_cache_filename = f"{cache_path}legal-{self.valid_filename(download_link)}.pkl"
        pkl_cache_filename_exists = Path(pkl_cache_filename).is_file()

        logging.debug(f"use_cache = {use_cache}")
        logging.debug(f"pkl_cache_filename = {pkl_cache_filename}")

        if not use_cache or not pkl_cache_filename_exists or not cache_filename_exists:
            logging.debug(f"Scraping file from url: {download_link}")
            loaded_from_cache = False

            # Save file from url to disk and get filename and http headers
            _, headers = urlretrieve(download_link, cache_filename)
            header_filename, header_ext = self._get_header_info(headers)
            logging.debug(f"header_filename = {header_filename}")
            logging.debug(f"header_ext = {header_ext}")

            # Pickle binary file contents and headers for cache retrieval
            with open(cache_filename, mode="rb") as f_in:
                file_bytes = f_in.read()
                with open(pkl_cache_filename, "wb") as f_out:
                    pickle.dump((file_bytes, cache_filename, headers), f_out, protocol=pickle.HIGHEST_PROTOCOL)

            # Copy file to target save_path
            save_filename = save_filename_no_ext + header_ext
            logging.debug(f"Copy new cached file {cache_filename} to {save_filename}")
            shutil.copy2(cache_filename, save_filename)

        else:
            logging.debug(f"Skipping download file: {cache_filename}")
            loaded_from_cache = True

            # Load process pkl_cache_filename
            with open(pkl_cache_filename, "rb") as f:
                (file_bytes, cache_filename, headers) = pickle.load(f)
                header_filename, header_ext = self._get_header_info(headers)
                save_filename = save_filename_no_ext + header_ext
                logging.debug(f"Copy old cached file {cache_filename} to {save_filename}")
                # TODO: should maybe save file_bytes to save_filename instead of relying on cache_filename existing?
                shutil.copy2(cache_filename, save_filename)

        return save_filename, loaded_from_cache
