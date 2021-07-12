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

    def __init__(self, field_mapping, field_default):
        self.field_mapping = field_mapping
        self.field_default = field_default

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
        return filters.attribute(node.name, self.field_mapping, self.field_default)

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

    @handle(ast.TemporalPredicate, subclasses=True)
    def temporal(self, node, lhs, rhs):
        return filters.temporal(
            lhs,
            rhs,
            node.op.value
        )

    @handle(ast.SpatialComparisonPredicate, subclasses=True)
    def spatial_operation(self, node, lhs, rhs):
        ...

    @handle(ast.BBox)
    def bbox(self, node, lhs):
        ...


def to_filter(ast, field_mapping=None, field_default=None):
    """ Helper function to translate AST to Django Query expressions.

        :param ast: the abstract syntax tree
        :param field_mapping: Lookup from field name to data model.
        :param field_default: Default attribute value if not in lookup.
        Leave as `None` to use the field name as the default.
    """
    return ElasticsearchFilterEvaluator(field_mapping, field_default).evaluate(ast)
