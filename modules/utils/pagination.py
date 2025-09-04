import math
from flask import request

def paginate_query(query, page=None, per_page=None, default_per_page=10):
    if page is None:
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1
    if per_page is None:
        try:
            per_page = int(request.args.get('per_page', default_per_page))
        except ValueError:
            per_page = default_per_page

    page = max(page, 1)
    per_page = max(per_page, 1)

    # Handle list input
    if isinstance(query, list):
        total = len(query)
        start = (page - 1) * per_page
        end = start + per_page
        items = query[start:end]
        total_pages = math.ceil(total / per_page)
    else:
        total = query.order_by(None).count()
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        total_pages = math.ceil(total / per_page)
    
    return {
        'items': items,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages
    }
