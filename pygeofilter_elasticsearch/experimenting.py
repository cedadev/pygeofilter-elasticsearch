# encoding: utf-8
"""

"""
__author__ = 'Richard Smith'
__date__ = '30 Jun 2021'
__copyright__ = 'Copyright 2018 United Kingdom Research and Innovation'
__license__ = 'BSD - see LICENSE file in top-level package directory'
__contact__ = 'richard.d.smith@stfc.ac.uk'

from pygeofilter.ast import get_repr
from pygeofilter.parsers.cql_json import parse as parse_json
# from pygeofilter.parsers.cql import parse as parse_text
from pygeofilter_elasticsearch import to_filter
import json

# cql_expr = "prop1=10 AND prop2>45"
cql_expr = "'abc' < 'bce'"
cql_json_expr = json.dumps({
    'eq': [{'property': 'platform'}, 'faam']
})
cql_json_expr2 = json.dumps(
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
cql_json_expr3 = json.dumps({
    "like": [
        {"property": "name"},
        "Smith."
    ],
    "singleChar": ".",
    "nocase": True
})


# cql_json_expr3 = json.dumps(
#     {
#         'and': [
#             {
#                 'eq': [{'property': 'platform'}, 'faam']
#             },
#             {
#                 'eq': [{'property': 'flight_number'}, 'b069']
#             },
#             {
#                 'anyinteracts': [
#                     {'property': 'datetime'},
#                     ['2005-01-04T00:00:00', '2005-01-06T00:00:00']
#                 ]
#             }
#         ]
#     }
# )
# cql_expr = 'platform="faam" AND flight_number="b069" AND datetime ANYINTERACTS 2005-01-04T00:00:00/2005-01-06T00:00:00'

# ast = parse_text(cql_expr)


def run_example(id, expr):
    print('#' * 10)
    print(f'Example {id}')
    print('#' * 10)
    ast = parse_json(expr)
    print(get_repr(ast))
    filters = to_filter(ast)
    print(filters)
    print(filters.to_dict())
    print()


# Example 1
run_example(1, cql_json_expr)

# Example 2
run_example(2, cql_json_expr2)

# Example 3
run_example(3, cql_json_expr3)
