import os
import time
import logging
import mimetypes
import string
import shutil
import pickle
from typing import Tuple
import urllib
from pathlib import Path
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self):
        self.default_cache_path = ".legaldata-cache/"

    @staticmethod
    def valid_filename(name) -> str:
        if name is None:
            return None

        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = name.lower()
        filename = filename.replace("https://", "")
        filename = filename.replace("http://", "")
        filename = filename.replace("/", "_")
        filename = "".join(c for c in filename if c in valid_chars)
        filename = filename.replace(" ", "_")
        filename = filename.strip("_")
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
        content_val = headers.get("Content-Disposition")
        filename = (
            None
            if content_val is None or len(content_val.split("filename=")) < 2
            else content_val.split("filename=")[1]
        )
        content_type_val = headers.get("Content-Type")
        content_type = (
            "" if content_type_val is None or len(content_type_val) == 0 else content_type_val.partition(";")[0].strip()
        )
        ext = mimetypes.guess_extension(content_type)
        if ext is None:
            logging.info(f"Unknown file type for content_type: {content_type}")
        else:
            ext = ext.lower()
        return filename, ext

    @staticmethod
    def _savefile(
        save_path, cache_filename, act_title, save_file_prefix, header_filename, header_ext, download_filename
    ) -> str:
        title_filename = "" if act_title is None else Crawler.valid_filename(act_title)
        header_filename = Crawler.valid_filename(header_filename)

        if header_filename is None:
            filename = f"{save_file_prefix}{title_filename}_{download_filename}"
        else:
            filename = f"{save_file_prefix}{title_filename}_{header_filename}"

        if header_ext is not None and header_ext.lower() not in filename.lower():
            filename = filename + header_ext

        save_filepath = os.path.join(save_path, filename.lower())
        logging.info(f"Save file to {save_filepath}")

        assert Path(cache_filename).is_file()
        save_filepath_abs = os.path.abspath(save_filepath)
        shutil.copy2(cache_filename, save_filepath_abs)
        assert Path(save_filepath_abs).is_file()

        return save_filepath_abs

    def _scrape_file(
        self, act, download_link, save_path, save_file_prefix, cache_path, use_cache, retry_attempts=5
    ) -> Tuple[str, str, bool, bool]:
        assert download_link is not None
        assert save_path is not None
        assert save_file_prefix is not None

        cache_filename = f"{cache_path}legal-{self.valid_filename(download_link)}.urlretrieve"
        cache_filename_exists = Path(cache_filename).is_file()
        pkl_cache_filename = f"{cache_path}legal-{self.valid_filename(download_link)}.pkl"
        pkl_cache_filename_exists = Path(pkl_cache_filename).is_file()
        download_filename = os.path.basename(download_link)

        logging.debug(f"use_cache = {use_cache}")

        if not use_cache or not pkl_cache_filename_exists or not cache_filename_exists:
            logging.debug(f"Scraping file from url: {download_link}")
            loaded_from_cache = False

            attempts = 0
            headers = {}
            urlretrieve_success = False
            while attempts < retry_attempts:
                try:
                    # Save file from url to disk and get filename and http headers
                    # urlretrieve can throw many exceptions including urllib.error.ContentTooShortError
                    _, headers = urllib.request.urlretrieve(download_link, cache_filename)
                    urlretrieve_success = True
                except Exception as ex:
                    attempts += 1
                    retry_sleep = attempts * 10
                    logging.warning(
                        f"Attempt #{attempts} urlretrieve error. url: {download_link}"
                        f", exception: {ex} (sleeping for {retry_sleep} sec)"
                    )
                    time.sleep(retry_sleep)
                    continue
                else:
                    break

            if not urlretrieve_success:
                logging.error(f"Failed to urlretrieve url {download_link} after {attempts} attempts, skipping url.")
                # TODO: write to and error file/log
                return "", "", False, False

            header_filename, header_ext = self._get_header_info(headers)
            logging.debug(f"header_filename = {header_filename}")
            logging.debug(f"header_ext = {header_ext}")

            download_split = os.path.splitext(download_link)
            download_ext = "" if len(download_split) < 2 else download_split[1]
            if len(download_ext) > 0 and header_ext is not None and download_ext.lower() != header_ext.lower():
                # NOTE: for Astlii .txt files when .txt file requested we actually get .html page with dl links
                logging.info(
                    f"Download vs header extension mismatch ({download_ext} vs {header_ext}) for download_link {download_link}"
                )

            # Pickle binary file contents and headers for cache retrieval
            with open(cache_filename, mode="rb") as f_in:
                file_bytes = f_in.read()
                with open(pkl_cache_filename, "wb") as f_out:
                    pickle.dump((file_bytes, cache_filename, headers), f_out, protocol=pickle.HIGHEST_PROTOCOL)

            # Copy file to target save_path
            save_filepath_abs = Crawler._savefile(
                save_path, cache_filename, act.title, save_file_prefix, header_filename, header_ext, download_filename
            )

        else:
            logging.debug(f"Skipping download file: {cache_filename}")
            loaded_from_cache = True

            # Load process pkl_cache_filename
            with open(pkl_cache_filename, "rb") as f:
                (file_bytes, cache_filename, headers) = pickle.load(f)
                header_filename, header_ext = self._get_header_info(headers)

                # Copy file to target save_path
                save_filepath_abs = Crawler._savefile(
                    save_path,
                    cache_filename,
                    act.title,
                    save_file_prefix,
                    header_filename,
                    header_ext,
                    download_filename,
                )

        return save_filepath_abs, header_ext, loaded_from_cache, True
