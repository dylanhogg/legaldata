import logging
import datetime


def run_legislation_crawler():
    logging.info("Example 1: Crawl www.legislation.gov.au")
    from legaldata.legislation.crawler import ActCrawler

    crawler = ActCrawler()

    # Full run
    # delay_sec = 3
    # act_limit = None
    # save_path = "./_data/full_v1/legislation.com.au/"
    # index_urls = crawler.get_index_pages()

    # Test run
    delay_sec = 1
    act_limit = 3
    save_path = (
        "./_data/app_output_path_no_limit/legislation.com.au/"
        if act_limit is None
        else f"./_data/app_output_path_limit_{act_limit}/legislation.com.au/"
    )
    index_urls = [
        "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Ag/0/0/principal",
        "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Pr/0/0/principal",
    ]

    start = datetime.datetime.now()
    index_count = len(index_urls)
    for i, index_url in enumerate(index_urls):
        logging.info(f"Index {i} of {index_count}: Took: {datetime.datetime.now() - start} Url: {index_url}")
        for act in crawler.get_acts_from_index(index_url, save_path, act_limit=act_limit, delay_sec=delay_sec):
            logging.debug(f"act: {act}\n")

    logging.info(f"Finished. Took {datetime.datetime.now() - start}")


def run_austlii_crawler():
    logging.info("Example 2: Crawl austlii.edu.au")
    from legaldata.austlii.crawler import ActCrawler

    crawler = ActCrawler()

    # Full run
    # delay_sec = 3
    # act_limit = None
    # save_path = "./_data/full_v1/austlii.edu.au/"
    # index_urls = crawler.get_index_pages()

    # Test run
    delay_sec = 1
    act_limit = 3
    save_path = (
        "./_data/app_output_path_no_limit/austlii.edu.au/"
        if act_limit is None
        else f"./_data/app_output_path_limit_{act_limit}/austlii.edu.au/"
    )
    index_urls = [
        "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-A.html",
        "http://www.austlii.edu.au/cgi-bin/viewtoc/au/legis/cth/consol_act/toc-K.html",
    ]

    start = datetime.datetime.now()
    index_count = len(index_urls)
    for i, index_url in enumerate(index_urls):
        logging.info(f"Index {i} of {index_count}: Took: {datetime.datetime.now() - start} Url: {index_url}")
        for act in crawler.get_acts_from_index(index_url, save_path, act_limit=act_limit, delay_sec=delay_sec):
            logging.debug(f"act: {act}\n")

    logging.info(f"Finished. Took {datetime.datetime.now() - start}")


if __name__ == "__main__":
    log_level = logging.INFO
    logging.basicConfig(format="%(asctime)s\t[%(levelname)s] %(name)s:\t%(message)s", level=log_level)

    vendor = "austlii"

    if vendor == "legislation":
        run_legislation_crawler()

    elif vendor == "austlii":
        run_austlii_crawler()

    else:
        raise Exception(f"Unknown vendor {vendor}")
