"""Helper module to create query based on filters"""


def get_query(filters, order_dir=None):
    """Creates a mongo query based on filters"""
    clean_filters = {key: val for key,
                     val in filters.items() if val is not None}
    query = {}
    for key in clean_filters:
        if key == 'is_resolved':
            query |= {key: clean_filters[key]}
        else:
            query |= {key: {'$in': clean_filters[key]}}

    if order_dir:
        order_by = [('created_at', 1)] if order_dir == 'asc' else [
            ('created_at', -1)]
    else:
        order_by = []

    return query, order_by
