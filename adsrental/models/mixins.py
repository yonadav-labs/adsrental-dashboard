
import re
import datetime
import typing

from django.utils import timezone
from django.db.models import Q


class FulltextSearchMixin():
    findterms = re.compile(r'"([^"]+)"|(\S+)').findall
    normspace = re.compile(r'\s{2,}').sub

    @classmethod
    def normalize_query(cls, query_string: str) -> typing.List[str]:
        '''
        Splits the query string in invidual keywords, getting rid of unecessary spaces and grouping quoted words together.
        Example:
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
            ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
        '''

        return [cls.normspace('', (t[0] or t[1]).strip()) for t in cls.findterms(query_string)]

    @classmethod
    def get_timedelta_filter(cls, field_name: str, **kwargs: int) -> Q:
        now = timezone.localtime(timezone.now())
        return Q(**{
            field_name: now + datetime.timedelta(**kwargs),
        })

    @classmethod
    def get_fulltext_filter(cls, query_string: str, search_fields: typing.List[str]) -> Q:
        '''
        Returns a query, that is a combination of Q objects.
        That combination aims to search keywords within a model by testing the given search fields.
        '''

        query = None  # Query to search for every search term
        terms = cls.normalize_query(query_string)
        # raise ValueError(terms)
        for term in terms:
            or_query = None  # Query to search for a given term in each field
            for field_name in search_fields:
                q = Q(**{
                    "{}__icontains".format(field_name): term
                })
                if or_query is None:
                    or_query = q
                else:
                    or_query = or_query | q
            if query is None:
                query = or_query
            else:
                query = query & or_query

        return query
