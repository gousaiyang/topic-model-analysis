from stackapi import StackAPI

from util import merge_whitespaces

site = StackAPI('stackoverflow')
site.max_pages = 10000


def soapi_search(query, *, begindate):
    excerpts = site.fetch('/search/excerpts', q=query, order='desc',
                          sort='activity', fromdate=int(begindate.timestamp()))

    for item in excerpts['items']:
        item_type = item['item_type']
        item_id = item['%s_id' % item_type]

        yield {
            'id': '%s-%s' % (item_type, item_id),
            'text': merge_whitespaces(item['body']),
            'title': merge_whitespaces(item['title']),
            'tags': ','.join(item['tags']),
            'type': item_type,
            'last_activity_date': item['last_activity_date'],
            'creation_date': item['creation_date'],
            'answering_question': item['question_id']
            if item_type == 'answer' else None,
            'question_score': item['question_score'],
            'is_accepted': item['is_accepted'],
            'is_answered': item['is_answered'],
            'score': item['score'],
            'question_has_accepted_answer': item.get('has_accepted_answer'),
            'question_answer_count': item.get('answer_count')
        }
