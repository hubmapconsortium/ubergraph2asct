from typing import Iterator

from oaklib.implementations import UbergraphImplementation

oi = UbergraphImplementation()

QUERY = """
    VALUES ?subject {{
        {subject}
    }}
    VALUES ?object {{
        {object}
    }}
    VALUES ?property {{
        {property}
    }}
    ?subject ?property ?object .
"""


def query_ubergraph(query) -> Iterator:
    """
    Query Ubergraph and return results
    """
    prefixes = get_prefixes(query, oi.prefix_map().keys())

    return oi.query(query=query, prefixes=prefixes)


def query_seed(seed, prop) -> Iterator:
    """
    Query Ubergraph for the seed terms and properties
    """
    return query_ubergraph(
        QUERY.format(
            subject=" ".join(seed), object=" ".join(seed), property=" ".join(prop)
        )
    )


def chunks(lst, n):
    """
    Chunk funtion
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def get_prefixes(text, prefix_map):
    """
    Filter prefix only on the seed terms
    """
    prefixes = []
    for prefix in prefix_map:
        if prefix in text:
            prefixes.append(prefix)

    return prefixes
