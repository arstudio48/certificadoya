#!/usr/bin/env python3
"""Query Google Search Console for certificadoya.es data (last 14 days) - v2."""
import json, os
from datetime import datetime, timedelta

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.expanduser(
    '/home/arturo/.hermes/home/.config/gcloud/application_default_credentials.json'
)

from google.auth import default
from googleapiclient.discovery import build

end_date = datetime.utcnow().date()
start_date = end_date - timedelta(days=14)

try:
    credentials, project = default(scopes=['https://www.googleapis.com/auth/webmasters'])
    service = build('webmasters', 'v3', credentials=credentials)

    site_url = 'sc-domain:certificadoya.es'

    # 1. Overall stats
    req_body = {
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
        'dimensions': [],
        'rowLimit': 1
    }
    overall = service.searchanalytics().query(siteUrl=site_url, body=req_body).execute()
    total_impressions = 0
    total_clicks = 0
    avg_position = 0.0
    if overall.get('rows'):
        r = overall['rows'][0]
        total_impressions = r.get('impressions', 0)
        total_clicks = r.get('clicks', 0)
        avg_position = r.get('position', 0.0)

    # 2. Top 10 queries by impressions
    req_top_imp = {
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
        'dimensions': ['query'],
        'rowLimit': 25,
        'orderBy': [{'fieldName': 'impressions', 'sortOrder': 'DESCENDING'}]
    }
    top_imp = service.searchanalytics().query(siteUrl=site_url, body=req_top_imp).execute()
    top_queries = []
    if top_imp.get('rows'):
        for r in top_imp['rows'][:10]:
            if r.get('impressions', 0) > 0:
                top_queries.append({
                    'query': r['keys'][0],
                    'impressions': r['impressions'],
                    'clicks': r['clicks'],
                    'position': round(r['position'], 1)
                })

    # 3. Top queries by best position (position < 30, at least 1 impression)
    best_position_queries = []
    for r in top_imp.get('rows', []):
        pos = r.get('position', 100)
        if pos < 30 and r.get('impressions', 0) >= 1:
            best_position_queries.append({
                'query': r['keys'][0],
                'position': round(pos, 1),
                'impressions': r['impressions'],
                'clicks': r['clicks']
            })
            if len(best_position_queries) >= 5:
                break

    result = {
        'available': True,
        'period': f"{start_date.isoformat()} → {end_date.isoformat()}",
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'avg_position': round(avg_position, 1),
        'top_queries_by_impressions': top_queries[:5],
        'top_queries_by_position': best_position_queries
    }

except Exception as e:
    result = {
        'available': False,
        'error': str(e)
    }

print(json.dumps(result, indent=2, ensure_ascii=False))