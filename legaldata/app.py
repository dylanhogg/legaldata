import logging
import datetime


def run_legislation_crawler():
    logging.info("Example 1: Crawl www.legislation.gov.au")
    from legaldata.legislation.crawler import ActCrawler

    crawler = ActCrawler()

    # limit = None
    act_limit = 2
    delay_sec = 1
    save_path = "./_data/app_output_path_no_limit/legislation" if act_limit is None else f"./_data/app_output_path_limit_{act_limit}/legislation"

    # index_urls = crawler.get_index_pages()
    index_urls = ["https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Pr/0/0/principal"]

    start = datetime.datetime.now()
    for index_url in index_urls:
        logging.info(f"index_url: {index_url}")
        for act in crawler.get_acts(index_url, save_path, act_limit=act_limit, delay_sec=delay_sec):
            logging.debug(f"act: {act}")

    logging.info(f"Finished. Took {datetime.datetime.now() - start}")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s\t[%(levelname)s] %(name)s:\t%(message)s", level=logging.INFO)

    vendor = "legislation"

    if vendor == "legislation":
        run_legislation_crawler()

    elif vendor == "austlii":
        raise Exception(f"Austlii not currently supported")

    else:
        raise Exception(f"Unknown vendor {vendor}")
