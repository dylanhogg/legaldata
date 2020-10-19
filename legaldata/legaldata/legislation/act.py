from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class Act:
    title: str
    desc: str
    meta_tags: Dict[str, str]
    download_links: List[str]
    saved_filenames = List[str]
