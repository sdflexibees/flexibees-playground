import math
import json
from django.db import connection

def paginate(result, serializer, page=1, context=None, page_size=10):
    if page == '' or page is None or int(page) < 1:
        page = 1
    else:
        page = int(page)
    if isinstance(result, list):
        query = result[(page - 1) * page_size:page * page_size]
        total_results = len(result)
    else:
        query = result[(page - 1) * page_size:page * page_size]
        total_results = result.count()
    total_pages = math.ceil(total_results / page_size) if total_results != 0 else 1
    page_ids = list(range(1, total_pages + 1))
    results = serializer(query, many=True, context=context).data
    current_page = page
    result = {
        'page_ids': page_ids,
        'current_page': current_page,
        'next_page_id': current_page + 1 if current_page < total_pages else None,
        'total_pages': total_pages,
        'total_results': total_results,
        'results': results
    }
    return result

def query_paginate(query, count_query, page=1, page_size=10):
    cursor = connection.cursor()
    cursor.execute(f"{query} OFFSET {(page - 1) * page_size} LIMIT {page_size}")
    count = connection.cursor()
    count.execute(count_query)
    total_results = count.fetchall()[0][0]
    total_pages = math.ceil(total_results / page_size) if total_results != 0 else 1
    page_ids = list(range(1, total_pages + 1))
    current_page = page
    columns = [col[0] for col in cursor.description]
    raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    results =  json.loads(json.dumps(raw_results))
    result = {
        'page_ids': page_ids,
        'current_page': current_page,
        'next_page_id': current_page + 1 if current_page < total_pages else None,
        'total_pages': total_pages,
        'total_results': total_results,
        'results': results
    }
    return result

def paginate_list(result, count, page=1, page_size=3, context=None):
    '''
    Paginates the given result and returns the result dictionary
    '''
    total_pages = math.ceil(count / page_size) if count != 0 else 1
    page_ids = list(range(1, total_pages + 1))
    current_page = page

    result = {
        'page_ids': page_ids,
        'current_page': current_page,
        'next_page_id': current_page + 1 if current_page < total_pages else None,
        'total_pages': total_pages,
        'total_results': count,
        'page_size': page_size,
        'results': result
    }
    if context:
        result.update(context)
    return result