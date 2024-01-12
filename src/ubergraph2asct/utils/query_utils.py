from typing import Iterator

from oaklib.implementations import UbergraphImplementation

oi = UbergraphImplementation()
converter = oi.converter

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
    FILTER(?subject != ?object)
    # LIMIT
"""


def query_ubergraph(query) -> Iterator:
    """
    Query Ubergraph and return results
    """
    prefixes = get_prefixes(query, oi.prefix_map().keys())

    return oi.query(query=query, prefixes=prefixes)


def query_seed(seed, prop) -> str:
    """
    Query Ubergraph for the seed terms and properties
    """
    return extract_triples(
        query_ubergraph(
            QUERY.format(
                subject=" ".join(seed), object=" ".join(seed), property=" ".join(prop)
            )
        )
    )


def query_label(seed) -> str:
    """
    Query Ubergraph to retrieve labels for the terms in seed
    """
    query_l = """
        VALUES ?subject {{
            {subject}
        }}
        VALUES ?property {{
            {property}
        }}
        ?subject ?property ?object .
        # LIMIT
    """
    return extract_triples(
        query_ubergraph(query_l.format(subject=" ".join(seed), property="rdfs:label"))
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


def extract_triples(entry: Iterator) -> str:
    """
    Extract triples into NT format
    """
    return "\n".join(
        [
            f"{to_uri(r['subject'])} {to_uri(r['property'])} {to_uri(r['object'])} ."
            for r in entry
        ]
    )


def to_uri(curie: str) -> str:
    """
    Expand CURIE and add < > to the URI
    If it's a string, return input
    """
    is_curie = False
    expand = ""
    try:
        expand = converter.expand(curie)
        is_curie = True
    except ValueError:
        expand = curie

    return f"<{expand}>" if is_curie else f'"{expand}"'
