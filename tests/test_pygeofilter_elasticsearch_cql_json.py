#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for `pygeofilter_elasticsearch` package.

These tests are produced against the pygeofilter CQL-JSON implementation.
"""

__author__ = """Richard Smith"""
__contact__ = 'richard.d.smith@stfc.ac.uk'
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"

import unittest
import json

from pygeofilter.parsers.cql_json import parse as parse_json

from pygeofilter_elasticsearch import to_filter


class CompareOutputMixin:
    def compare_output(self, expr, expected):
        ast = parse_json(expr)
        filters = to_filter(ast)
        query = filters.to_dict()

        self.assertDictEqual(query, expected)


class TestComparison(CompareOutputMixin, unittest.TestCase):

    def test_lt(self):
        expr = json.dumps({'lt': [{'property': 'cloud_cover'}, 50]})
        expected = {'range': {'cloud_cover': {'lt': 50}}}

        self.compare_output(expr, expected)

    def test_lte(self):
        expr = json.dumps({'lte': [{'property': 'cloud_cover'}, 50]})
        expected = {'range': {'cloud_cover': {'lte': 50}}}

        self.compare_output(expr, expected)

    def test_gt(self):
        expr = json.dumps({'gt': [{'property': 'cloud_cover'}, 50]})
        expected = {'range': {'cloud_cover': {'gt': 50}}}

        self.compare_output(expr, expected)

    def test_gte(self):
        expr = json.dumps({'gte': [{'property': 'cloud_cover'}, 50]})
        expected = {'range': {'cloud_cover': {'gte': 50}}}

        self.compare_output(expr, expected)

    @unittest.skip
    def test_ne(self):
        expr = json.dumps({'ne': [{'property': 'platform'}, 'faam']})
        expected = {'bool': {'must_not': [{'term': {'platform': 'faam'}}]}}

        self.compare_output(expr, expected)

    def test_eq(self):
        expr = json.dumps({'eq': [{'property': 'platform'}, 'faam']})
        expected = {'term': {'platform': 'faam'}}

        self.compare_output(expr, expected)


class TestCombine(CompareOutputMixin, unittest.TestCase):

    def test_AND_combine(self):
        expr = json.dumps(
            {
                'and': [
                    {
                        'eq': [{'property': 'platform'}, 'faam']
                    },
                    {
                        'eq': [{'property': 'flight_number'}, 'b069']
                    }
                ]
            }
        )
        expected = {'bool': {'must': [{'term': {'platform': 'faam'}}, {'term': {'flight_number': 'b069'}}]}}

        self.compare_output(expr, expected)

    def test_OR_combine(self):
        expr = json.dumps(
            {
                'or': [
                    {
                        'eq': [{'property': 'platform'}, 'faam']
                    },
                    {
                        'eq': [{'property': 'flight_number'}, 'b069']
                    }
                ]
            }
        )
        expected = {'bool': {'should': [{'term': {'platform': 'faam'}}, {'term': {'flight_number': 'b069'}}]}}

        self.compare_output(expr, expected)


class TestBetween(CompareOutputMixin, unittest.TestCase):

    def test_between(self):
        expr = json.dumps({
            "between": {
                "value": {"property": "depth"},
                "lower": 100.0,
                "upper": 150.0
            }
        })
        expected = {'range': {'depth': {'gte': 100.0, 'lte': 150.0}}}

        self.compare_output(expr, expected)


@unittest.skip
class TestLike(CompareOutputMixin, unittest.TestCase):

    def test_like(self):
        expr = json.dumps({
            "like": [
                {"property": "name"},
                "Smith."
            ],
            "singleChar": ".",
            "nocase": True
        })
        expected = {'query_string': {'fields': ['name'], 'query': 'Smith?'}}

        self.compare_output(expr, expected)


class TestIn(CompareOutputMixin, unittest.TestCase):

    def test_in(self):
        expr = json.dumps({
            "in": {
                "value": {"property": "cityName"},
                "list": ["Toronto", "Franfurt", "Tokyo", "New York"],
            }
        })
        expected = {'terms': {'cityName': ("Toronto", "Franfurt", "Tokyo", "New York")}}

        self.compare_output(expr, expected)


class TestTemporal(CompareOutputMixin, unittest.TestCase):

    def test_before(self):
        expr = json.dumps({})
        expected = {}
        ...

    def test_after(self):
        ...

    def test_before_or_during_dt_dt(self):
        ...

    def test_before_or_during_dt_td(self):
        ...

    def test_before_or_during_td_dt(self):
        ...

    def test_during_dt_dt(self):
        ...

    def test_during_dt_td(self):
        ...

    def test_during_td_dt(self):
        ...

    def test_during_or_after_dt_dt(self):
        ...

    def test_during_or_after_dt_td(self):
        ...

    def test_during_or_after_td_dt(self):
        ...

    @unittest.skip
    def test_anyinteracts(self):
        ...
