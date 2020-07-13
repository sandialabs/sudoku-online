#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Michael Darling, Shelley Leger
Sandia National Laboratories
July 12, 2020

Scoring and dispatch system for sudoku game actions.
"""

operators_description = {
    'assign': {'function': 'expand_cell_with_assignment',
               'requested_arguments': ['cell_id', 'value'],
               'hardcoded_arguments': False,
               'cost': 10,
               'user_name': 'Assign: assign given value to cell.',
               'description': 'Return one board with the assignment '
               + 'and another (backup) with the exclusion.'},
    'exclude': {'function': 'expand_cell_with_assignment',
                'requested_arguments': ['cell_id', 'value'],
                'hardcoded_arguments': True,
                'cost': 10,
                'user_name': 'Exclude: remove given value from cell.',
                'description': 'Return one board with the exclusion '
                + 'and another (backup) with the assignment done.'},
    'pivot': {'function': 'expand_cell', 'requested_arguments': ['cell_id'],
              'cost': 50,
              'user_name': 'Pivot: expand all choices for cell.',
              'description': 'Return a separate board for each possible value '
              + 'in cell_id.'},
    'exclusion': {'function': 'logical_exclusion',
                  'cost': 100,
                  'user_name': 'Exclusion: exclude assigned values from cells in unit.',
                  'description': 'For each cell with a given value, remove '
                  + 'that value from all other cells in the same unit '
                  + '(row, column, and box)'},
    'inclusion': {'function': 'logical_inclusion',
                  'cost': 100,
                  'user_name': 'Inclusion: assign values that have only one possible cell.',
                  'description': 'Search board units for values '
                  + 'that have only one possible cell and make that assignment.'},
    'pointingpairs': {'function': 'find_pointing_candidates', 'hardcoded_arguments': 'pairs',
                      'cost': 250,
                      'user_name': 'Pointing pairs: remove aligned value pairs from other units.',
                      'description': 'If any one value is present only two or three times in just one unit, '
                      + 'then we can remove that number from the intersection of a number unit. '
                      + 'There are four types of intersections: '
                      + '1. A pair or triple in a box - if they are aligned on a row, the '
                      + 'value can be removed from the rest of the row. '
                      + '2. A pair or triple in a box, if they are aligned on a column, the '
                      + 'value can be removed from the rest of the column. '
                      + '3. A pair or triple on a row - if they are all in the same box, the '
                      + 'value can be removed from the rest of the box. '
                      + '4. A pair or triple on a column - if they are all in the same box, the '
                      + 'value can be removed from the rest of the box.'},
    'nakedpairs': {'function': 'find_naked_candidates', 'hardcoded_arguments': 'pairs',
                   'cost': 500,
                   'user_name': 'Naked pairs: remove exclusive value pairs from other cells in a unit.',
                   'description': 'A Naked Pair is two cells in the same unit with the same two values remaining.'},
    'hiddenpairs': {'function': 'find_hidden_candidates', 'hardcoded_arguments': 'pairs',
                    'cost': 1200,
                    'user_name': 'Hidden pairs: given exclusive value pairs, remove all other values from the two cells.',
                    'description': 'The cells in a hidden set contain values amongst them '
                    + 'that have been exlcuded from the rest of the cells in '
                    + 'the hidden set\'s common unit.  Therefore we can exclude '
                    + 'all other values from the cells in the set.'},
    'pointingtriples': {'function': 'find_pointing_candidates', 'hardcoded_arguments': 'triples',
                        'cost': 1300,
                        'user_name': 'Pointing triples: remove aligned value triples from other units.',
                        'description': 'If any one value is present only two or three times in just one unit, '
                        + 'then we can remove that number from the intersection of a number unit. '
                        + 'There are four types of intersections: '
                        + '1. A pair or triple in a box - if they are aligned on a row, the '
                        + 'value can be removed from the rest of the row. '
                        + '2. A pair or triple in a box, if they are aligned on a column, the '
                        + 'value can be removed from the rest of the column. '
                        + '3. A pair or triple on a row - if they are all in the same box, the '
                        + 'value can be removed from the rest of the box. '
                        + '4. A pair or triple on a column - if they are all in the same box, the '
                        + 'value can be removed from the rest of the box.'},
    'nakedtriples': {'function': 'find_naked_candidates', 'hardcoded_arguments': 'triples',
                     'cost': 1400,
                     'user_name': 'Naked triples: remove exclusive value triples from other cells in a unit.',
                     'description': 'A Naked Triple is any group of three cells in the same unit that contain'
                     + 'IN TOTAL 3 values. The combinations of candidates for a Naked Triple will be '
                     + 'one of the following: '
                     + '(123)(123)(123) - {3/3/3} in terms of candidates per cell '
                     + '(123)(123)(12) - {3/2/2} or some combination thereof '
                     + '(123)(12)(23) - {3/2/2} '
                     + '(12)(23)(13) - {2/2/2}'},
    'hiddentriples': {'function': 'find_hidden_candidates', 'hardcoded_arguments': 'triples',
                      'cost': 1600,
                      'user_name': 'Hidden triples: given exclusive value triples, remove all other values from the three cells.',
                      'description': 'The cells in a hidden set contain values amongst them '
                      + 'that have been exlcuded from the rest of the cells in '
                      + 'the hidden set\'s common unit.  Therefore we can exclude '
                      + 'all other values from the cells in the set.'},
    'xwings': {'function': 'find_wings', 'hardcoded_arguments': 'x',
               'cost': 1600,
               'user_name': 'X-wing.',
               'description': 'An X-Wing ocurrs when there are only 2 candidates for a value in each of '
               + '2 different units of the same kind and these candidates also lie on 2 other units '
               + 'of the same kind.  Then we can exclude this value from the latter two units.'},
    'ywings': {'function': 'find_wings', 'hardcoded_arguments': 'y',
               'cost': 1600,
               'user_name': 'Y-wing.',
               'description': 'In a Y-wing, a "hinge" cell forms a conjugate pair with cells in '
               + 'two different units.  For example if cell A1 has the values 2 and 1, cell '
               + 'B2 has the values 3 and 1, and cell A5 has the values 3 and 2, then we '
               + 'can elminate the value 3 from B5 or any other cell that is associated '
               + 'with B2 and A5.'},
    'xyzwings': {'function': 'find_wings', 'hardcoded_arguments': 'xyz',
                 'cost': 1600,
                 'user_name': 'XYZ-wing.',
                 'description': 'An XYZ-wing is an extension of Y-Wing in which three cells '
                 + 'contain only 3 different numbers between them, but they fall outside the '
                 + 'confines of one row/column/box, with t the hinge being able to see the other '
                 + 'two; those other two having only one number in common; and the apex having '
                 + 'all three numbers as candidates.  For example, if F9 has the values 1, 2, '
                 + 'and 4, D9 has 1 and 2, and F1 has 1 and 4, we can eliminate 1 from F7.'},
    'nakedquads': {'function': 'find_naked_candidates', 'hardcoded_arguments': 'quads',
                   'cost': 4000,
                   'user_name': 'Naked quads: remove exclusive value quads from other cells in a unit.',
                   'description': 'A Naked Quad is any group of four cells in the same unit '
                   + 'that contain IN TOTAL 4 values.  Therefore we can exclude '
                   + 'these four values from all other cells in the unit.'},
    'hiddenquads': {'function': 'find_hidden_candidates', 'hardcoded_arguments': 'quads',
                    'cost': 5000,
                    'user_name': 'Hidden quads: given exclusive value quads, remove all other values from the four cells.',
                    'description': 'The cells in a hidden set contain values amongst them '
                    + 'that have been exlcuded from the rest of the cells in '
                    + 'the hidden set\'s common unit.  Therefore we can exclude '
                    + 'all other values from the cells in the set.'}
}
