
import re
import datetime
import typing
import json

from django.utils import timezone
from django.conf import settings
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


class CommentsMixin():
    def get_comments(self):
        try:
            comments = json.loads(self.comments_cache)
        except (ValueError, TypeError):
            comments = self.get_comments_cache()
            self.comments_cache = json.dumps(comments)
            self.save()

        res = []
        for comment in comments:
            item = f'{comment["created"]} [{comment["username"]}] {comment["text"]}'
            if comment["response"]:
                item += f'\n >> Admin response: {comment["response"]}'
            res.append(item)
        return res

    def get_comments_cache(self):
        result = []
        for comment in self.comments.all().select_related('user').order_by('-created')[:50]:
            result.append(dict(
                created=comment.created.strftime(settings.SYSTEM_DATETIME_FORMAT),
                text=comment.text,
                username=comment.get_username(),
                is_admin=comment.user.is_superuser if comment.user else False,
                response=comment.response,
            ))
        return result

    def add_comment(self, message, user=None):
        'Add a comment to the model'
        self.comments.create(user=user, text=message)
        self.comments_cache = json.dumps(self.get_comments_cache())
        self.save()
