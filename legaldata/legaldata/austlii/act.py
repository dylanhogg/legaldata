from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Act:
    title: str
    file_code: str
    desc: str
    meta_tags: Dict[str, str]
    page_url: str
    download_links: List[str]
    loaded_from_cache: bool
    crawl_date: str
    saved_filenames: List[str]
