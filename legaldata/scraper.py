import logging


def run_legistlation_crawler():
    logging.info("Example 1: Crawl www.legislation.gov.au")
    from legaldata.legislation.crawler import ActCrawler

    save_path = "./_data/app_output_path/"
    index_url = "https://www.legislation.gov.au/Browse/Results/ByTitle/Acts/InForce/Pr/0/0/principal"

    for act in ActCrawler().get_acts(index_url, save_path, limit=2):
        print(f"{act}")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.DEBUG)

    vendor = "legistlation"
    output_path = "./_data/scrape_results/"

    if vendor == "legistlation":
        run_legistlation_crawler()

    elif vendor == "austlii":
        raise Exception(f"Austlii not currently supported")

    else:
        raise Exception(f"Unknown vendor {vendor}")
