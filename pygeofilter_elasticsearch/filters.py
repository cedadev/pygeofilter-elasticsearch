# encoding: utf-8
"""
Filters
"""
__author__ = 'Richard Smith'
__date__ = '30 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Query
from operator import and_, or_
from functools import reduce
from datetime import datetime, timedelta

from typing import List, Union, Tuple


def attribute(name: str, field_mapping: dict = None, field_default=None) -> str:
    """Create an attribute lookup expression using a field mapping dictionary.

    :param name: the field name to filter
    :param field_mapping: lookup for field name.
    :param field_default: default value if field not in mapping.
    Leave as None to use the field name as the default

    :return: The attribute name
    """
    if field_default:
        field_default = field_default.substitute(name=name)

    if field_mapping:
        field = field_mapping.get(name, field_default or name)
    else:
        field = field_default or name

    return field


def literal(value):
    return value


def combine(sub_filters: List['elasticsearch_dsl.query.Query'], combinator: str = 'AND') -> 'elasticsearch_dsl.query.Q':
    """ Combine filters using a logical combinator

        :param sub_filters: the filters to combine
        :param combinator: a string: "AND" / "OR"

        :return: the combined filter
    """

    for sub_filter in sub_filters:
        assert isinstance(sub_filter, Query)

    assert combinator in ('AND', 'OR')

    op = and_ if combinator == "AND" else or_

    return reduce(lambda acc, q: op(acc, q) if acc else q, sub_filters)


OP_TO_COMP = {
    '<': ('range', 'lt'),
    '<=': ('range', 'lte'),
    '>': ('range', 'gt'),
    '>=': ('range', 'gte'),
    '<>': None,
    '=': None
}


def compare(lhs, rhs, op):
    assert isinstance(lhs, str)
    assert op in OP_TO_COMP

    comp = OP_TO_COMP[op]

    if comp:
        query_type, comparison = comp
        return Q(query_type, **{lhs: {comparison: rhs}})

    if op == '=':
        return Q('term', **{lhs: rhs})
    return ~Q('term', **{lhs: rhs})


def negate(sub_filter: 'elasticsearch_dsl.query.Query') -> 'elasticsearch_dsl.query.Query':
    """ Negate a filter, opposing its meaning.

        :param sub_filter: the filter to negate
        :return: the negated filter
    """
    assert isinstance(sub_filter, Query)
    return ~sub_filter


def between(lhs: str,
            low: Union[str, int, float],
            high: Union[str, int, float],
            not_: bool = False) -> 'elasticsearch_dsl.query.Query':
    """ Create a filter to match elements that have a value within a certain
        range.

        :param lhs: the field to compare
        :param low: the lower value of the range
        :param high: the upper value of the range
        :param not_: whether the range shall be inclusive (the default) or
                     exclusive

        :return: a comparison expression object
    """
    assert isinstance(lhs, str)

    q = Q('range', **{lhs: {'gte': low, 'lte': high}})
    return ~q if not_ else q


def like(lhs: str,
         pattern: str,
         wildcard: str,
         singlechar: str,
         escapechar: str,
         not_: bool = False,
         ) -> 'elasticsearch_dsl.query.Query':
    """ Create a filter to filter elements according to a string attribute using
        wildcard expressions.

        :param lhs: the field to compare
        :param rhs: the wildcard pattern: a string containing any number of '%'
                    characters as wildcards.
        :param case: whether the lookup shall be done case sensitively or not
        :param not_: whether the range shall be inclusive (the default) or
                     exclusive

        :return: a comparison expression object
    """
    assert isinstance(lhs, str)
    assert isinstance(pattern, str)

    elastic_wildcard = '*'
    elastic_singlechar = '?'
    elastic_escapechar = '\\'

    pattern = pattern.replace(wildcard, elastic_wildcard)
    pattern = pattern.replace(singlechar, elastic_singlechar)

    q = Q('query_string', query=pattern, fields=[lhs])

    return ~q if not_ else q


def contains(lhs: str,
             items: Tuple,
             not_: bool =False) -> 'elasticsearch_dsl.query.Query':
    """ Create a filter to match elements attribute to be in a list of choices.

        :param lhs: the field to compare
        :param items: a list of choices
        :param not_: whether the range shall be inclusive (the default) or
                     exclusive
        :return: a comparison expression object
    """
    assert isinstance(lhs, str)

    q = Q('terms', **{lhs: items})
    return ~q if not_ else q


def temporal(lhs: str,
             time_or_period: Union['datetime', Tuple['datetime'], Tuple['datetime', 'timedelta']],
             op: str) -> 'elasticsearch_dsl.query.Query':
    """ Create a temporal filter for the given temporal attribute.

        :param lhs: the field to compare
        :param time_or_period: the time instant or time span to use as a filter
        :param op: the comparison operation. one of ``"BEFORE"``,
                   ``"BEFORE OR DURING"``, ``"DURING"``, ``"DURING OR AFTER"``,
                   ``"AFTER"``.
        :return: a comparison expression object
    """
    assert isinstance(lhs, str)
    assert op in (
        "BEFORE",
        "BEFORE OR DURING",
        "DURING",
        "DURING OR AFTER",
        "AFTER",
    )

    low = None
    high = None

    if op in ("BEFORE", "AFTER"):
        if op == "BEFORE":
            high = time_or_period
        else:
            low = time_or_period
    else:
        low, high = time_or_period
        assert isinstance(low, datetime) or isinstance(high, datetime)

        if isinstance(low, timedelta):
            low = high - low

        if isinstance(high, timedelta):
            high = low + high

    if low and high:
        return between(lhs, low, high)
    elif low:
        return compare(lhs,low,'>=')
    else:
        return compare(lhs, high, '<=')
