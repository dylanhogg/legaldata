import os
import filetype
import logging
import mimetypes
import string
import shutil
import pickle
from typing import List, Tuple, Dict
from urllib.request import urlretrieve
from pathlib import Path
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self):
        self.default_cache_path = ".legaldata-cache/"

    @staticmethod
    def valid_filename(name) -> str:
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = name.lower()
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
    def _get_header_info(headers) -> Tuple[str, str]:
        filename = headers.get("Content-Disposition").split("filename=")[1]
        content_type = headers.get("Content-Type").partition(";")[0].strip()
        ext = mimetypes.guess_extension(content_type)
        if ext is None:
            logging.info(f"Unknown file type for content_type: {content_type}")
            ext = ".unk"
        return filename, ext

    @staticmethod
    def _get_save_filename(act_title, save_file_prefix, header_filename, header_ext) -> Tuple[str, str]:
        title_filename = "" if act_title is None else Crawler.valid_filename(act_title) + "_"
        header_filename = header_filename.lower()

        if header_ext.lower() in header_filename.lower():
            filename = f"{save_file_prefix}{title_filename}{header_filename}"
        else:
            filename = f"{save_file_prefix}{title_filename}{header_filename}{header_ext}"

        return filename.lower(), header_ext.lower()

    def _scrape_file(self, act, download_link, save_path, save_file_prefix, cache_path, use_cache) -> Tuple[str, str, bool]:
        assert download_link is not None
        assert save_path is not None
        assert save_file_prefix is not None

        cache_filename = f"{cache_path}legal-{self.valid_filename(download_link)}.urlretrieve"
        cache_filename_exists = Path(cache_filename).is_file()
        pkl_cache_filename = f"{cache_path}legal-{self.valid_filename(download_link)}.pkl"
        pkl_cache_filename_exists = Path(pkl_cache_filename).is_file()

        logging.debug(f"use_cache = {use_cache}")

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
            save_filename, file_ext = self._get_save_filename(act.title, save_file_prefix, header_filename, header_ext)
            save_filepath_abs = os.path.abspath(os.path.join(save_path, save_filename))
            logging.info(f"Copy new cached file {cache_filename} to {save_filepath_abs}")

            assert Path(cache_filename).is_file()
            shutil.copy2(cache_filename, save_filepath_abs)

        else:
            logging.debug(f"Skipping download file: {cache_filename}")
            loaded_from_cache = True

            # Load process pkl_cache_filename
            with open(pkl_cache_filename, "rb") as f:
                (file_bytes, cache_filename, headers) = pickle.load(f)
                header_filename, header_ext = self._get_header_info(headers)
                save_filename, file_ext = self._get_save_filename(act.title, save_file_prefix, header_filename, header_ext)
                save_filepath_abs = os.path.abspath(os.path.join(save_path, save_filename))
                logging.info(f"Copy old cached file {cache_filename} to {save_filepath_abs}")

                # TODO: should maybe save file_bytes to save_filename instead of relying on cache_filename existing?
                assert Path(cache_filename).is_file()
                shutil.copy2(cache_filename, save_filepath_abs)

        assert Path(save_filepath_abs).is_file()
        return save_filepath_abs, file_ext, loaded_from_cache
