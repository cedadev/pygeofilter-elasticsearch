# encoding: utf-8
"""
Elasticsearch backend for
"""
__author__ = 'Richard Smith'
__date__ = '30 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from pygeofilter.backends.evaluator import Evaluator, handle
from . import filters
from pygeofilter import ast
from pygeofilter import values


class ElasticsearchFilterEvaluator(Evaluator):
    """Filter evaluator for Elasticsearch."""

    def __init__(self, field_mapping):
        self.field_mapping = field_mapping

    @handle(ast.Not)
    def not_(self, node, sub):
        return filters.negate(sub)

    @handle(ast.And, ast.Or)
    def combination(self, node, lhs, rhs):
        return filters.combine((lhs, rhs), node.op.value)

    @handle(ast.Comparison, subclasses=True)
    def comparison(self, node, lhs, rhs):
        return filters.compare(
            lhs,
            rhs,
            node.op.value
        )

    @handle(ast.Between)
    def between(self, node, lhs, low, high):
        return filters.between(
            lhs,
            low,
            high,
            node.not_
        )

    @handle(ast.Attribute)
    def attribute(self, node):
        return filters.attribute(node.name, self.field_mapping)

    @handle(*values.LITERALS)
    def literal(self, node):
        return filters.literal(node)

    @handle(ast.Like)
    def like(self, node, lhs):
        return filters.like(
            lhs,
            node.pattern,
            node.wildcard,
            node.singlechar,
            node.escapechar,
            node.not_
        )

    @handle(ast.In)
    def in_(self, node, lhs, *options):
        return filters.contains(
            lhs,
            options,
            node.not_
        )



def to_filter(ast, field_mapping=None):
    """ Helper function to translate AST to Django Query expressions.

        :param ast: the abstract syntax tree
    """
    return ElasticsearchFilterEvaluator(field_mapping).evaluate(ast)
