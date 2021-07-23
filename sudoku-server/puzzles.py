#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Andy Wilson, Michael Darling, David Stracuzzi, Shelley Leger
Sandia National Laboratories
February 25, 2020

Defines set of test sudoku problems to use to test the sudoku infrastructure
"""

puzzles = {
    'test2-i24e40': '300000700000001000000060000000700015400300000000000020610000800000540900002000000',
    'test3-i29e35': '300000700000001000000060000000700015900500000000000020610000800000340900002000000',
    'test4-i28e36': '300000700000001000000090000000700014800600000000000020610000800000540300002000000',
    'test5-i23e41': '560000040000010700000000000000400060030000005018000000700604000200000100000000003',
    'test6-i26e38': '560000040000010700000000000000800060030000005019000000700604000200000100000000003',
    'test7-i26e36hp10': '010000200800300000000000500050000410000700060002008000900000073000050000000040000',
    'test8-i32e32hp2': '010000208500406000000000000306000050000020700004000000020010000000300060800000000',
    'test9-i29e35hp2': '083000200000091000000000000100000409020300000000070000007600500000800030900000000',
    'test10-i29e35hp7': '000090750801000000000000000050000400000801000000600000470020000000100006300000080',
    'test11-i36e28hp2': '000090800704000000100000000050480000000000010090000000200600500000107000000000308',
    'test12-i36e28np1': '300000700000010400506000000000200035000000080000070000070600100040005000000300000',
    'test13-i34e30np1': '100000300700600000000200000060030400025000000000000800007500002300080000000000010',
    'test14-i24e38np3': '100000300800007000000200000027640000060500000000000100000000042300080000000000060',
    'test15-i28e34np3': '100000305600900000000080200000760010020800000050000000400000700000001000000050000',
    'test16-i26e36np3': '100000305800400000000070200000640080020700000050000000400000600000001000000050000',
    'test17-i24e38np4hp4': '300000670000201000080000000000570800021000000400000000600030000000000042000000009',
    'test18-i29e35np3hp4': '560000030000901000000000000809000010070060000000000000104800000000050607000000200',
    'test19-i21e41np8hp3': '100000306070800000000000200000236000004000085000000000000500040390000000600000000',
    'test20-i22e42np3hp7': '100000306500040000000010000000000051060000200030800000700000040000602000000300000',
    'test21-i16e47np1hp2': '100000340406000800000900000800040000000700009000000000097000050000031000020000000',
    'test22-i33e18nt1xw1': '000400067064200000007106042000860304401000700706940000170004000940000200000010400',
    'test23-i16e32nt1xw1': '700000021500402000200807000021500000073200610045700230407000802302070100106020000',
    'test24-i10e41nt2xw2': '000500061516020000970060000061400000000650910000000680100806000300000506600705108',
    'test25-i16e32nt1xw1': '400000081300021000100700000048010000000060210016000000601000354700504108854136000',
    'test26-i8e41pp1nt4xw2xyzw1': '000605021070302000020408000100960250032087400760020000200850000000700802600200000',
    'test27-i32e31yw3': '560000040700003000000800000008000030090200000000040000600050100000000908000000200',
    'test28-i27e36yw1': '205700000800050300000000000090000100000200000000000030030081000400000020000900007',
    'test29-i27e36yw1': '700200050000030080100000000400060700060080000000000100039500000000700000080000000',
    'test30-i29e34yw1': '080000670000310000000000000000200005240000000000000013501400000000007800300000000',
    'test31-i36e27yw1': '080000670000510000000000000000200004230000000000000051405300000000007800100000000',
    'test32-i25e38np2hp4yw1': '000200090010000030050008000200900000000400500000000100400006020000030700000010000',
    'test33-i26e38np2hp3yw1': '042080000000000001080000000700103000000000480600000000150600000000000540000900000',
    'test34-i26e38np2hp3yw1': '042080000000000001080000000700103000000000480900000000150600000000000540000700000',
    'test35-i24e40np3hp2yw1': '000040380050070000010000000000502008600000700000100000000200010407000000300000000',
    'test36-i30e33np2hp2yw1': '100036000020000840000000000603050000500700000000000020040800000000000503000200000',
    'easy1': '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..',
    'easy2': '......9.7...42.18....7.5.261..9.4....5.....4....5.7..992.1.8....34.59...5.7......',
    'easy3': '...1254....84.....42.8......3.....95.6.9.2.1.51.....6......3.49.....72....1298...',
    'easy4': '..61.24.......457..2.9.31.8.8...56.96...9...19.13...4.5.42.9.8..627.......85.13..',
    'medium1': '...439...4..6..8..395.....472..8..9....217....3..9..282.....417..9..2..3...841...',
    'hard1': '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......',
    # 'hard2': '6.2.5.........3.4..........43...8....1....2........7..5..27...........81...6.....',
    # 'hard3': '...5...........5.697.....2...48.2...25.1...3..8..3.........4.7..13.5..9..2...31..',
    'hard4': '3..6.9.12..7.....6.2...1......74...3..29.65..1...23......8...9.5.....3..29.3.7..4',
    'fiendish1': '.....5.8....6.1.43..........1.5........1.6...3.......553.....61........4.........',
    'fiendish2': '85...24..72......9..4.........1.7..23.5...9...4...........8..7..17..........36.4.',
    # 'fiendish3': '..53.....8......2..7..1.5..4....53...1..7...6..32...8..6.5....9..4....3......97..',
    'fiendish4': '..32.4...24.5...7.......6..9..7..1...87...53...2..5..7..1.......3...6.98...8.23..',

    'naked_single_test': '246.7..38...3.6.7437..4.6....8.2.7..1.......6..7.3.4....4.8..6986.4....791..6..42',
    'naked_pair_test': '4.....938.32.941...953..24.37.6.9..4529..16736.47.3.9.957..83....39..4..24..3.7.9',
    'naked_pair_test_2': '.8..9..3..3.....699.2.63158.2.8.459.8519.7.463946.587.563.4.9872......15.1..5..2.',
    'hidden_pair_test': '.........9.46.7....768.41..3.97.1.8.7.8...3.1.513.87.2..75.261...54.32.8.........',
    'hidden_pair_test_2': '72.4.8.3..8.....474.1.768.281.739......851......264.8.2.968.41334......8168943275',
    'naked_triple_test': '.7.4.8.29..2.....4854.2...7..83742...2.........32617......936122.....4.313.642.7.',
    'naked_triple_test_2': '294513..66..8423193..697254....56....4..8..6....47....73.164..59..735..14..928637',
    'hidden_triple_test': '.....1.3.231.9.....65..31..6789243..1.3.5...6...1367....936.57...6.198433........',
    'naked_quad_test': '....3..86....2..4..9..7852.3718562949..1423754..3976182..7.3859.392.54677..9.4132',
    # 'hidden_quad_test': '9.15...46425.9..8186..1..2.5.2.......19...46.6.......2196.4.2532...6.817.....1694',
    'pointing_pair_test': '.179.36......8....9.....5.7.72.1.43....4.2.7..6437.25.7.1....65....3......56.172.',
    'pointing_pair_test_2': '.32..61..41..........9.1...5...9...4.6.....713...2...5...5.8.........519.57..986.',
    'pointing_triple_test': '93..5....2..63..95856..2.....318.57...5.2.98..8...5......8..1595.821...4...56...8',
    'box_line_reduction': '.16..78.3.9.8.....87...1.6..48...3..65...9.82.39...65..6.9...2..8...29369246..51.',
    'box_line_reduction_2': '.2.9437159.4...6..75.....4.5..48....2.....4534..352....42....81..5..426..9.2.85.4',
    'xwing_test': '1.....569492.561.8.561.924...964.8.1.64.1....218.356.4.4.5...169.5.614.2621.....5',
    # 'xwing_test_2': '.......9476.91..5..9...2.81.7..5..1....7.9....8..31.6724.1...7..1..9..459.....1..',
    'ywing_test': '9..24.....5.69.231.2..5..9..9.7..32...29356.7.7...29...69.2..7351..79.622.7.86..9',
    # 'xyz_wing_test': '.92..175.5..2....8....3.2...75..496.2...6..75.697...3...8.9..2.7....3.899.38...4.',
    # 'xyz_wing_test_2': '6.......85..9.8..782...1.3.34.2.9.8.2...8.3..18.3.7.2575.4...929....5..44...9...3',
    # 'swordfish_test_333': '52941.7.3..6..3..2..32......523...76637.5.2..19.62753.3...6942.2..83.6..96.7423.5',
    # 'swordfish_test_222': '926...1..537.1.42.841...6.3259734816714.6..3.36812..4.1.2....84485.7136.6.3.....1',
    # 'swordfish_test_323': '.2..43.69..38962..96..25.3.89.56..136...3.....3..81.263...1..7...96743.227.358.9.',

    # TODO MAL this and the others commented out don't finish without help
    'underconstrained1': '.8...9743.5...8.1..1.......8....5......8.4......3....6.......7..3.5...8.9724...5.',
    # 'underconstrained2': '53..7....6..1.5....98....6.8.......34..8.3..17...2...6.6....28....419..5....8..79',
    # 'underconstrained3': '..97.......48.9.7......2.3....3.6...3..1....9..6....58..8.3....5.....1869.2......',
    # 'underconstrained4': '......23....3.8.64....4.9.8573.......8652937.......8456.5.1....71...2....48......',
    # 'underconstrained5': '.21...9.36........83962...19...31.....2...3.....9....87...69152........92.5...74.',
    # 'underconstrained6': '.7.4.1..8.16.3...45.4........7.8..9.6..123........6......6...532.8.....6.......8.',

    # INSOLUBLE BY PROPAGATION (BASED ON EASY 0)
    'insoluble_by_propagation': '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.8..',

    # INSOLUBLE BY INITIAL STATE CONFLICT (BASED ON EASY 0)
    'insoluble_by_initial_state_conflict': '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.6..',

}

games = {
    'test_game1_6_operators_open': {
        'puzzles': ['test2-i24e40', 'easy1', 'xwing_test', 'hard4', 'underconstrained1', 'test7-i26e36hp10'],
        'config_alterations': {}
    },
    'test_game1_6': {
        'puzzles': ['test2-i24e40', 'easy1', 'xwing_test', 'hard4', 'underconstrained1', 'test7-i26e36hp10'],
        'config_alterations': {'randomly_apply': ['select_ops_upfront']}
    },
    'test_game1_4': {
        'puzzles': ['test2-i24e40', 'xwing_test', 'hard4', 'underconstrained1'],
        'config_alterations': {'randomly_apply': ['select_ops_upfront']}
    },
    'test_game_ptgprs': {
        'puzzles': ['pointing_pair_test...goal=A9', 'pointing_pair_test...goal=E2', 'pointing_pair_test...goal=B1'],
        'config_alterations': {'randomly_apply': ['select_ops_upfront']}
    },
    'pilot_test_a_board': {
        # 'test7-i26e36hp10?goal=C6?costlyops=inclusion,pointingpairs,nakedpairs,xwings?name=Pilot Test Board?select_ops_upfront'
        'puzzles': ['test7-i26e36hp10...goal=C6...name=Pilot Test Board...question=Can C6 be a 7?',
                    'test7-i26e36hp10...goal=C6...name=Pilot Test Board2...select_ops_upfront...question=Can C6 be odd?'],
        'config_alterations': {'costly_ops': ['inclusion', 'pointingpairs', 'nakedpairs', 'xwings']}
    },
    'test_logical_operators_in_sequence': {
        'puzzles': ['test2-i24e40...name=Test Inclusion...goal=C6...question=Can C6 be 4?...answer=no',
                    'test9-i29e35hp2...name=Test Pointing Pairs...goal=C6...question=Can C6 equal A2 or A3?...answer=yes',
                    'test7-i26e36hp10...name=Test Naked Pairs...goal=C6...question=Can C6 be greater than 5?...answer=no',
                    'hidden_pair_test_2...name=Test Hidden Pairs...goal=F7...question=Can F7 be odd?...answer=yes',
                    'box_line_reduction_2...name=Test Pointing Triples...goal=C5...question=Can C5 be less than 5?...answer=yes',
                    'hidden_triple_test...name=Test Naked Triples...goal=A9...question=Can A9 be greater than 5?...answer=no',
                    #'...name=Test Hidden Triples...goal=...question=',
                    'xwing_test...name=Test X-Wings...goal=G6...question=Can G6 equal A7 or A8 or A9?...answer=no',
                    'test29-i27e36yw1...name=Test Y-Wings...goal=E8...question=Can E9 be a square (1 or 4 or 9)?',
                    #'...name=Test XYZ-Wings...goal=...question=',
                    #'...name=Test Naked Quads...goal=...question=',
                    #'...name=Test Hidden Quads...goal=...question=',
                    ]
    },
    'training_games': {
        'puzzles': [
            # Requires 2 calls to inclusion, resolved after 1st call to inclusion (doesn't require 2nd)
            'easy2...goal=E7...name=Training #1...question=Can E7 be 6?...answer=no',
            'easy2...goal=E7...name=Training #1...question=Can E7 be 6?...answer=no...select_ops_upfront',
            # Requires pointingpairs and inclusion, with final call to pointing pairs to resolve (no call to inclusion after pointing pairs)
            'test11-i36e28hp2...goal=B8...name=Training #2...question=Can B8 be odd?...answer=yes',
            'test11-i36e28hp2...goal=B8...name=Training #2...question=Can B8 be odd?...answer=yes...select_ops_upfront',
            # Requires pointingpairs and inclusion, but doesn't require last call to inclusion _after_ pointing pairs
            'test16-i26e36np3...goal=F3...name=Training #3...question=Can F3 be 3 or 7?...answer=no',
            'test16-i26e36np3...goal=F3...name=Training #3...question=Can F3 be 3 or 7?...answer=no...select_ops_upfront',
        ]
    },
    'training_games_select_ops_upfront': {
        'puzzles': [
            'easy2...goal=E7...name=Training #1...question=Can E7 be 6?...answer=no...select_ops_upfront',
            'test11-i36e28hp2...goal=B8...name=Training #2...question=Can B8 be odd?...answer=yes...select_ops_upfront',
            'test16-i26e36np3...goal=F3...name=Training #3...question=Can F3 be 3 or 7?...answer=no...select_ops_upfront',
        ]
    },
    'training_games_always_select': {
        'puzzles': [
            'easy2...goal=E7...name=Training #1...question=Can E7 be 6?...answer=no',
            'test11-i36e28hp2...goal=B8...name=Training #2...question=Can B8 be odd?...answer=yes',
            'test16-i26e36np3...goal=F3...name=Training #3...question=Can F3 be 3 or 7?...answer=no',
        ]
    },
    'training_games1_select_ops_upfront': {
        'puzzles': [
            'easy2...goal=E7...name=Training #1...question=Can E7 be 6?...answer=no...select_ops_upfront',
        ]
    },
    'training_game2_select_ops_upfront': {
        'puzzles': [
            'test11-i36e28hp2...goal=B8...name=Training #2...question=Can B8 be odd?...answer=yes...select_ops_upfront',
        ]
    },
    'training_games3_select_ops_upfront': {
        'puzzles': [
            'test16-i26e36np3...goal=F3...name=Training #3...question=Can F3 be 3 or 7?...answer=no...select_ops_upfront',
        ]
    },
    'training_games1_always_select': {
        'puzzles': [
            'easy2...goal=E7...name=Training #1...question=Can E7 be 6?...answer=no',
        ]
    },
    'training_game2_always_select': {
        'puzzles': [
            'test11-i36e28hp2...goal=B8...name=Training #2...question=Can B8 be odd?...answer=yes',
        ]
    },
    'training_games3_always_select': {
        'puzzles': [
            'test16-i26e36np3...goal=F3...name=Training #3...question=Can F3 be 3 or 7?...answer=no',
        ]
    },
    'weedout_games': {
        'puzzles': [
            # Requires pointing pairs and inclusion; doesn't require last inclusion after pointing pairs (poss. 1 4 6 7 9)
            'test36-i30e33np2hp2yw1...goal=F7...name=WeedOut #1...question=Can F7 be 1, 6, or 7?...answer=yes',
            'test36-i30e33np2hp2yw1...goal=F7...name=WeedOut #1...question=Can F7 be 1, 6, or 7?...answer=yes...select_ops_upfront',
            # Requires 4 calls to inclusion, resolved after 3rd call to inclusion (doesn't require 4th) (poss. 5 7 8 9)
            'test4-i28e36...goal=B1...name=WeedOut #2...question=Can B1 be greater than 5?...answer=no',
            'test4-i28e36...goal=B1...name=WeedOut #2...question=Can B1 be greater than 5?...answer=no...select_ops_upfront',
            # Requires just 1 inclusion call to solve
            'test22-i33e18nt1xw1...goal=A2...name=WeedOut #3...question=Can A2 be 3?...answer=no',
            'test22-i33e18nt1xw1...goal=A2...name=WeedOut #3...question=Can A2 be 3?...answer=no...select_ops_upfront',
        ]
    },
    'weedout_games_always_select': {
        'puzzles': [
            'test36-i30e33np2hp2yw1...goal=F7...name=WeedOut #1...question=Can F7 be 1, 6, or 7?...answer=yes',
            'test4-i28e36...goal=B1...name=WeedOut #2...question=Can B1 be greater than 5?...answer=no',
            'test22-i33e18nt1xw1...goal=A2...name=WeedOut #3...question=Can A2 be 3?...answer=no',
        ]
    },
    'weedout_games_select_ops_upfront': {
        'puzzles': [
            'test36-i30e33np2hp2yw1...goal=F7...name=WeedOut #1...question=Can F7 be 1, 6, or 7?...answer=yes...select_ops_upfront',
            'test4-i28e36...goal=B1...name=WeedOut #2...question=Can B1 be greater than 5?...answer=no...select_ops_upfront',
            'test22-i33e18nt1xw1...goal=A2...name=WeedOut #3...question=Can A2 be 3?...answer=no...select_ops_upfront',
        ]
    },
    'weedout_games1_select_ops_upfront': {
        'puzzles': [
            'test36-i30e33np2hp2yw1...goal=F7...name=WeedOut #1...question=Can F7 be 1, 6, or 7?...answer=yes...select_ops_upfront',
        ]
    },
    'weedout_games2_select_ops_upfront': {
        'puzzles': [
            'test4-i28e36...goal=B1...name=WeedOut #2...question=Can B1 be greater than 5?...answer=no...select_ops_upfront',
        ]
    },
    'weedout_games3_select_ops_upfront': {
        'puzzles': [
            'test22-i33e18nt1xw1...goal=A2...name=WeedOut #3...question=Can A2 be 3?...answer=no...select_ops_upfront',
        ]
    },
    'weedout_games1_always_select': {
        'puzzles': [
            'test36-i30e33np2hp2yw1...goal=F7...name=WeedOut #1...question=Can F7 be 1, 6, or 7?...answer=yes',
        ]
    },
    'weedout_games2_always_select': {
        'puzzles': [
            'test4-i28e36...goal=B1...name=WeedOut #2...question=Can B1 be greater than 5?...answer=no',
        ]
    },
    'weedout_games3_always_select': {
        'puzzles': [
            'test22-i33e18nt1xw1...goal=A2...name=WeedOut #3...question=Can A2 be 3?...answer=no',
        ]
    },
    'logical_operators_mturk_test_suite': {
        'puzzles': [
            # Goal: something that gets resolved by second-to-last logical operator

            # Inclusion
            # Requires 1 call to inclusion; resolved after last (1) inclusion call
            'medium1...goal=I3...name=Sudoku Test #01...question=Is I3 prime (2, 3, 5, or 7)?...answer=yes',
            'medium1...goal=I3...name=Sudoku Test #01...question=Is I3 prime (2, 3, 5, or 7)?...answer=yes...select_ops_upfront',
            # Requires 2 calls to inclusion; resolved after 1st call *** training / weed out ***
            'naked_single_test...goal=E6...name=Sudoku Test #02...question=Is E6 less than 5?...answer=yes',
            'naked_single_test...goal=E6...name=Sudoku Test #02...question=Is E6 less than 5?...answer=yes...select_ops_upfront',
            # Requires 4 calls to inclusion; resolved by exclusion propagation of 3rd call
            'test2-i24e40...goal=B2...name=Sudoku Test #03...question=Is B2 less than 6?...answer=no',
            'test2-i24e40...goal=B2...name=Sudoku Test #03...question=Is B2 less than 6?...answer=no...select_ops_upfront',
            # Requires 4 calls to inclusion; resolved on 3rd inclusion (no exclusion) to be 2
            'test3-i29e35...goal=E2...name=Sudoku Test #04...question=Is E2 6?...answer=no',
            'test3-i29e35...goal=E2...name=Sudoku Test #04...question=Is E2 6?...answer=no...select_ops_upfront',
            # Requires 3 calls to inclusion; resolved after 2nd call
            'test6-i26e38...goal=C5...name=Sudoku Test #05...question=Is C5 7?...answer=no',
            'test6-i26e38...goal=C5...name=Sudoku Test #05...question=Is C5 7?...answer=no...select_ops_upfront',

            # Process: search for last call to highest-level operator that has at least one non-exclusion operator call after it (if only one call, it can be the last).
            # Pick most uncertain cell (or a cell if that call doesn't resolve any uncertainty) before the call as the goal.
            # Determine how uncertainty changes before the next logical operator.
            # Design a question that is answerable by how the uncertainty changes by the time the next logical operator is called.
            # Do this experiment with all logical operators, not just the ones chosen for this test.

            # Pointing Pairs
            # Requires 1 pointing pairs call and 6 inclusion calls; 1 inclusion call happens after the pointing pairs call but is not required to answer.
            'test8-i32e32hp2...goal=H2...name=Sudoku Test #06...question=Is H2 7?...answer=no',
            'test8-i32e32hp2...goal=H2...name=Sudoku Test #06...question=Is H2 7?...answer=no...select_ops_upfront',
            # Requires 2 pointing pairs calls. Question resolved by first, where following inclusion, pointing pairs, inclusion solves the board.
            'test9-i29e35hp2...goal=C6...name=Sudoku Test #07...question=Is C6 equal to A2 or A3?...answer=yes',
            'test9-i29e35hp2...goal=C6...name=Sudoku Test #07...question=Is C6 equal to A2 or A3?...answer=yes...select_ops_upfront',
            # Requires 1 pointing pairs, 6 inclusions. Pointing pairs solves the board with exclusion.
            'test15-i28e34np3...goal=F9...name=Sudoku Test #08...question=Is F9 odd?...answer=yes',
            'test15-i28e34np3...goal=F9...name=Sudoku Test #08...question=Is F9 odd?...answer=yes...select_ops_upfront',
            # Requires 1 pointing pairs, 6 inclusions. Board requires 2 inclusions afterwards, but question is resolved prior to those.
            'test13-i34e30np1...goal=A6...name=Sudoku Test #09...question=Is A6 5?...answer=no',
            'test13-i34e30np1...goal=A6...name=Sudoku Test #09...question=Is A6 5?...answer=no...select_ops_upfront',
            # Requires 2 pointing pairs, 6 inclusions. Question resolved by first pointing pairs.
            'hard1...goal=B9...name=Sudoku Test #10...question=Is B9 greater than 3?...answer=yes',
            'hard1...goal=B9...name=Sudoku Test #10...question=Is B9 greater than 3?...answer=yes...select_ops_upfront',

            # Naked Pairs
            # 1 naked pairs, 2 pointingpairs, 7 inclusion. Solved by exclusion after nakedpairs
            # C6 1, 2, 6, 9 -> 1, 2
            'test7-i26e36hp10...name=Sudoku Test #11...goal=C6...question=Is C6 greater than 5?...answer=no',
            'test7-i26e36hp10...name=Sudoku Test #11...goal=C6...question=Is C6 greater than 5?...answer=no...select_ops_upfront',
            # 1 naked pair, 2 pointing pairs, 2 inclusions. Solved by exclusion after nakedpairs
            # A6 -> 1, 2 -> 1
            # Try operator before naked pairs. Pointing pairs.
            # Still A6 -> 1, 2, not resolved by nakedpairs. Try to reduce uncertainty otherwise.
            # B5 1, 2, 7, 8 -> 7, 8
            'naked_pair_test_2...goal=B5...name=Sudoku Test #12...question=Is B5 greater than 5?...answer=yes',
            'naked_pair_test_2...goal=B5...name=Sudoku Test #12...question=Is B5 greater than 5?...answer=yes...select_ops_upfront',
            # 1 naked pairs, 2 pointing pairs, 5 inclusions. Requires 1 inclusion to solve after (followed by inclusion, pointingpairs to solve the board).
            # I5 4, 5, 7 -> 4, 5, 7. Need better option, so look at what's resolved before next inclusion.
            # A1 1, 5, 6, 7 -> 6, 7
            'fiendish4...goal=A1...name=Sudoku Test #13...question=Is A1 greater than 5?...answer=yes',
            'fiendish4...goal=A1...name=Sudoku Test #13...question=Is A1 greater than 5?...answer=yes...select_ops_upfront',
            # 1 nakedpair, 3 pointingpairs, 10 inclusion. 1 inclusion after nakedpair.
            # F6 2, 3, 4, 5, 7, 9 -> no change after nakedpair, requires an inclusion also to get to -> 2, 3, 4, 7, 9
            'test10-i29e35hp7...goal=F6...name=Sudoku Test #14...question=Is F6 5?...answer=no',
            'test10-i29e35hp7...goal=F6...name=Sudoku Test #14...question=Is F6 5?...answer=no...select_ops_upfront',
            # 1 naked pair, 2 pointingpairs, 10 inclusions. Solved by exclusion after nakedpairs.
            # B2 3, 4, 9 -> 3
            'test14-i24e38np3...goal=B2...name=Sudoku Test #15...question=Is B2 a perfect square (1, 4, or 9)?...answer=no',
            'test14-i24e38np3...goal=B2...name=Sudoku Test #15...question=Is B2 a perfect square (1, 4, or 9)?...answer=no...select_ops_upfront',

            # Y Wings
            # 1 ywings, 1 nakedpairs, 6 inclusion. Solved by exclusion immediately after y-wings
            # H9 3, 5 -> 3
            # 'test29-i27e36yw1...name=Sudoku Test #16...goal=E8...question=Can E9 be a square (1 or 4 or 9)?',
            'test29-i27e36yw1...name=Sudoku Test #16...goal=H9...question=Is H9 3?...answer=yes',
            'test29-i27e36yw1...name=Sudoku Test #16...goal=H9...question=Is H9 3?...answer=yes...select_ops_upfront',
            # 1 ywings, 2 pointing pairs, 7 inclusions. solved by exclusion immediately after.
            # H3 6, 9 -> 9
            'test32-i25e38np2hp4yw1...goal=H3...name=Sudoku Test #17...question=Is H3 even?...answer=no',
            'test32-i25e38np2hp4yw1...goal=H3...name=Sudoku Test #17...question=Is H3 even?...answer=no...select_ops_upfront',
            # 1 ywings, 2 pointing pairs, 9 inclusions. Solved by exclusion after ywing
            # I2 5, 7 -> 5
            # 'test27-i32e31yw3...goal=%%...name=Sudoku Test #20...question=%%?...answer=%%',
            # 1 ywing, 9 inclusion. solved by exclusion immediately after.
            # B8 4, 8 -> 4
            # Solve prior to ywing insted.
            # B9 8, 9 -> No change prior to ywing. Try reducing uncertainty instead.
            # G9 2, 6, 7 -> 7
            'test30-i29e34yw1...goal=G9...name=Sudoku Test #18...question=Is G9 odd?...answer=yes',
            'test30-i29e34yw1...goal=G9...name=Sudoku Test #18...question=Is G9 odd?...answer=yes...select_ops_upfront',
            # 1 ywing, 2 pointing pairs, 2 inclusion. solved by exclusion immediately after
            # F3 1, 3, 4, 5, 6, 8 -> 1, 3, 4, 5, 6
            # 'ywing_test...goal=%%...name=Sudoku Test #18...question=%%?...answer=%%',
            # 1 Ywing, 6 inclusion. Solved immediately after ywing by exclusion.
            # E8 4, 6, 9 -> 4, 9
            'test28-i27e36yw1...goal=E8...name=Sudoku Test #19...question=Is E8 a perfect square (1, 4, or 9)?...answer=yes',
            'test28-i27e36yw1...goal=E8...name=Sudoku Test #19...question=Is E8 a perfect square (1, 4, or 9)?...answer=yes...select_ops_upfront',
            # 1 ywings, 9 inclusion. Solved after ywing by exclusion.
            # B8 3, 8 -> 3
            # 'test31-i36e27yw1...goal=%%...name=Sudoku Test #20...question=%%?...answer=%%',
            # 1 ywings, 2 pointing pairs, 7 inclusion. Solved immediately after ywings by exclusion
            # H3 6, 9 -> 6
            # 'test32-i25e38np2hp4yw1...goal=%%...name=Sudoku Test #20...question=%%?...answer=%%',
            # 1 ywings, 2 pointing pairs, 5 inclusion. ywings followed by inclusion.
            # D5 1, 2, 5, 6 -> no change. Need a different question prior to inclusion.
            # C3 3, 5 -> 3
            'box_line_reduction...goal=C3...name=Sudoku Test #20...question=Is C3 greater than 4?...answer=no',
            'box_line_reduction...goal=C3...name=Sudoku Test #20...question=Is C3 greater than 4?...answer=no...select_ops_upfront',
        ]
    },
    'logical_operators_mturk_option1_select_upfront': {
        'puzzles': [
            # Inclusion 1
            'medium1...goal=I3...name=Sudoku Test #01...question=Is I3 prime (2, 3, 5, or 7)?...answer=yes...select_ops_upfront',
            'naked_single_test...goal=E6...name=Sudoku Test #02...question=Is E6 less than 5?...answer=yes...select_ops_upfront',
            'test2-i24e40...goal=B2...name=Sudoku Test #03...question=Is B2 less than 6?...answer=no...select_ops_upfront',
            # Pointing Pairs 1
            'test15-i28e34np3...goal=F9...name=Sudoku Test #08...question=Is F9 odd?...answer=yes...select_ops_upfront',
            'test13-i34e30np1...goal=A6...name=Sudoku Test #09...question=Is A6 5?...answer=no...select_ops_upfront',
            # Naked Pairs 1
            'naked_pair_test_2...goal=B5...name=Sudoku Test #12...question=Is B5 greater than 5?...answer=yes...select_ops_upfront',
            'fiendish4...goal=A1...name=Sudoku Test #13...question=Is A1 greater than 5?...answer=yes...select_ops_upfront',
            # Y Wings 1
            'test32-i25e38np2hp4yw1...goal=H3...name=Sudoku Test #17...question=Is H3 even?...answer=no...select_ops_upfront',
            'test28-i27e36yw1...goal=E8...name=Sudoku Test #19...question=Is E8 a perfect square (1, 4, or 9)?...answer=yes...select_ops_upfront',
            'test30-i29e34yw1...goal=G9...name=Sudoku Test #18...question=Is G9 odd?...answer=yes...select_ops_upfront',
        ]
    },
    'logical_operators_mturk_option2_select_upfront': {
        'puzzles': [
            # Inclusion 2
            'test3-i29e35...goal=E2...name=Sudoku Test #04...question=Is E2 6?...answer=no...select_ops_upfront',
            'test6-i26e38...goal=C5...name=Sudoku Test #05...question=Is C5 7?...answer=no...select_ops_upfront',
            # Pointing Pairs 2
            'hard1...goal=B9...name=Sudoku Test #10...question=Is B9 greater than 3?...answer=yes...select_ops_upfront',
            'test8-i32e32hp2...goal=H2...name=Sudoku Test #06...question=Is H2 7?...answer=no...select_ops_upfront',
            'test9-i29e35hp2...goal=C6...name=Sudoku Test #07...question=Is C6 equal to A2 or A3?...answer=yes...select_ops_upfront',
            # Naked Pairs 2
            'test7-i26e36hp10...name=Sudoku Test #11...goal=C6...question=Is C6 greater than 5?...answer=no...select_ops_upfront',
            'test10-i29e35hp7...goal=F6...name=Sudoku Test #14...question=Is F6 5?...answer=no...select_ops_upfront',
            'test14-i24e38np3...goal=B2...name=Sudoku Test #15...question=Is B2 a perfect square (1, 4, or 9)?...answer=no...select_ops_upfront',
            # Y Wings 2
            'test29-i27e36yw1...name=Sudoku Test #16...goal=H9...question=Is H9 3?...answer=yes...select_ops_upfront',
            'box_line_reduction...goal=C3...name=Sudoku Test #20...question=Is C3 greater than 4?...answer=no...select_ops_upfront',
        ]
    },
    'logical_operators_mturk_option1_always_select': {
        'puzzles': [
            # Inclusion 1
            'medium1...goal=I3...name=Sudoku Test #01...question=Is I3 prime (2, 3, 5, or 7)?...answer=yes',
            'naked_single_test...goal=E6...name=Sudoku Test #02...question=Is E6 less than 5?...answer=yes',
            'test2-i24e40...goal=B2...name=Sudoku Test #03...question=Is B2 less than 6?...answer=no',
            # Pointing Pairs 1
            'test15-i28e34np3...goal=F9...name=Sudoku Test #08...question=Is F9 odd?...answer=yes',
            'test13-i34e30np1...goal=A6...name=Sudoku Test #09...question=Is A6 5?...answer=no',
            # Naked Pairs 1
            'naked_pair_test_2...goal=B5...name=Sudoku Test #12...question=Is B5 greater than 5?...answer=yes',
            'fiendish4...goal=A1...name=Sudoku Test #13...question=Is A1 greater than 5?...answer=yes',
            # Y Wings 1
            'test32-i25e38np2hp4yw1...goal=H3...name=Sudoku Test #17...question=Is H3 even?...answer=no',
            'test28-i27e36yw1...goal=E8...name=Sudoku Test #19...question=Is E8 a perfect square (1, 4, or 9)?...answer=yes',
            'test30-i29e34yw1...goal=G9...name=Sudoku Test #18...question=Is G9 odd?...answer=yes',
        ]
    },
    'logical_operators_mturk_option2_always_select': {
        'puzzles': [
            # Inclusion 2
            'test3-i29e35...goal=E2...name=Sudoku Test #04...question=Is E2 6?...answer=no',
            'test6-i26e38...goal=C5...name=Sudoku Test #05...question=Is C5 7?...answer=no',
            # Pointing Pairs 2
            'hard1...goal=B9...name=Sudoku Test #10...question=Is B9 greater than 3?...answer=yes',
            'test8-i32e32hp2...goal=H2...name=Sudoku Test #06...question=Is H2 7?...answer=no',
            'test9-i29e35hp2...goal=C6...name=Sudoku Test #07...question=Is C6 equal to A2 or A3?...answer=yes',
            # Naked Pairs 2
            'test7-i26e36hp10...name=Sudoku Test #11...goal=C6...question=Is C6 greater than 5?...answer=no',
            'test10-i29e35hp7...goal=F6...name=Sudoku Test #14...question=Is F6 5?...answer=no',
            'test14-i24e38np3...goal=B2...name=Sudoku Test #15...question=Is B2 a perfect square (1, 4, or 9)?...answer=no',
            # Y Wings 2
            'test29-i27e36yw1...name=Sudoku Test #16...goal=H9...question=Is H9 3?...answer=yes',
            'box_line_reduction...goal=C3...name=Sudoku Test #20...question=Is C3 greater than 4?...answer=no',
        ]
    },
    'logical_operators_mturk_optionA_select_upfront': {
        'puzzles': [
            # Inclusion A
            'medium1...goal=I3...name=Sudoku Test #01...question=Is I3 prime (2, 3, 5, or 7)?...answer=yes...select_ops_upfront',
            # Pointing Pairs A
            'test13-i34e30np1...goal=A6...name=Sudoku Test #09...question=Is A6 5?...answer=no...select_ops_upfront',
            # Naked Pairs A
            'fiendish4...goal=A1...name=Sudoku Test #13...question=Is A1 greater than 5?...answer=yes...select_ops_upfront',
            # Y Wings A
            'test28-i27e36yw1...goal=E8...name=Sudoku Test #19...question=Is E8 a perfect square (1, 4, or 9)?...answer=yes...select_ops_upfront',
            'test30-i29e34yw1...goal=G9...name=Sudoku Test #18...question=Is G9 odd?...answer=yes...select_ops_upfront',
        ]
    },
    'logical_operators_mturk_optionB_select_upfront': {
        'puzzles': [
            # Inclusion B
            'naked_single_test...goal=E6...name=Sudoku Test #02...question=Is E6 less than 5?...answer=yes...select_ops_upfront',
            'test2-i24e40...goal=B2...name=Sudoku Test #03...question=Is B2 less than 6?...answer=no...select_ops_upfront',
            # Pointing Pairs B
            'test15-i28e34np3...goal=F9...name=Sudoku Test #08...question=Is F9 odd?...answer=yes...select_ops_upfront',
            # Naked Pairs B
            'naked_pair_test_2...goal=B5...name=Sudoku Test #12...question=Is B5 greater than 5?...answer=yes...select_ops_upfront',
            # Y Wings B
            'test32-i25e38np2hp4yw1...goal=H3...name=Sudoku Test #17...question=Is H3 even?...answer=no...select_ops_upfront',
        ]
    },
    'logical_operators_mturk_optionC_select_upfront': {
        'puzzles': [
            # Inclusion C
            'test3-i29e35...goal=E2...name=Sudoku Test #04...question=Is E2 6?...answer=no...select_ops_upfront',
            # Pointing Pairs C
            'hard1...goal=B9...name=Sudoku Test #10...question=Is B9 greater than 3?...answer=yes...select_ops_upfront',
            # Naked Pairs C
            'test7-i26e36hp10...name=Sudoku Test #11...goal=C6...question=Is C6 greater than 5?...answer=no...select_ops_upfront',
            'test14-i24e38np3...goal=B2...name=Sudoku Test #14...question=Is B2 a perfect square (1, 4, or 9)?...answer=no...select_ops_upfront',
            # Y Wings C
            'box_line_reduction...goal=C3...name=Sudoku Test #20...question=Is C3 greater than 4?...answer=no...select_ops_upfront',
        ]
    },
    'logical_operators_mturk_optionD_select_upfront': {
        'puzzles': [
            # Inclusion D
            'test6-i26e38...goal=C5...name=Sudoku Test #05...question=Is C5 7?...answer=no...select_ops_upfront',
            # Pointing Pairs D
            'test8-i32e32hp2...goal=H2...name=Sudoku Test #06...question=Is H2 7?...answer=no...select_ops_upfront',
            'test9-i29e35hp2...goal=C6...name=Sudoku Test #07...question=Is C6 equal to A2 or A3?...answer=yes...select_ops_upfront',
            # Naked Pairs D
            'test10-i29e35hp7...goal=F6...name=Sudoku Test #14...question=Is F6 5?...answer=no...select_ops_upfront',
            # Y Wings D
            'test29-i27e36yw1...name=Sudoku Test #16...goal=H9...question=Is H9 3?...answer=yes...select_ops_upfront',
        ]
    },
    'logical_operators_mturk_optionA_always_select': {
        'puzzles': [
            # Inclusion A
            'medium1...goal=I3...name=Sudoku Test #01...question=Is I3 prime (2, 3, 5, or 7)?...answer=yes',
            # Pointing Pairs A
            'test13-i34e30np1...goal=A6...name=Sudoku Test #09...question=Is A6 5?...answer=no',
            # Naked Pairs A
            'fiendish4...goal=A1...name=Sudoku Test #13...question=Is A1 greater than 5?...answer=yes',
            # Y Wings A
            'test28-i27e36yw1...goal=E8...name=Sudoku Test #19...question=Is E8 a perfect square (1, 4, or 9)?...answer=yes',
            'test30-i29e34yw1...goal=G9...name=Sudoku Test #18...question=Is G9 odd?...answer=yes',
        ]
    },
    'logical_operators_mturk_optionB_always_select': {
        'puzzles': [
            # Inclusion B
            'naked_single_test...goal=E6...name=Sudoku Test #02...question=Is E6 less than 5?...answer=yes',
            'test2-i24e40...goal=B2...name=Sudoku Test #03...question=Is B2 less than 6?...answer=no',
            # Pointing Pairs B
            'test15-i28e34np3...goal=F9...name=Sudoku Test #08...question=Is F9 odd?...answer=yes',
            # Naked Pairs B
            'naked_pair_test_2...goal=B5...name=Sudoku Test #12...question=Is B5 greater than 5?...answer=yes',
            # Y Wings B
            'test32-i25e38np2hp4yw1...goal=H3...name=Sudoku Test #17...question=Is H3 even?...answer=no',
        ]
    },
    'logical_operators_mturk_optionC_always_select': {
        'puzzles': [
            # Inclusion C
            'test3-i29e35...goal=E2...name=Sudoku Test #04...question=Is E2 6?...answer=no',
            # Pointing Pairs C
            'hard1...goal=B9...name=Sudoku Test #10...question=Is B9 greater than 3?...answer=yes',
            # Naked Pairs C
            'test7-i26e36hp10...name=Sudoku Test #11...goal=C6...question=Is C6 greater than 5?...answer=no',
            'test14-i24e38np3...goal=B2...name=Sudoku Test #14...question=Is B2 a perfect square (1, 4, or 9)?...answer=no',
            # Y Wings C
            'box_line_reduction...goal=C3...name=Sudoku Test #20...question=Is C3 greater than 4?...answer=no',
        ]
    },
    'logical_operators_mturk_optionD_always_select': {
        'puzzles': [
            # Inclusion D
            'test6-i26e38...goal=C5...name=Sudoku Test #05...question=Is C5 7?...answer=no',
            # Pointing Pairs D
            'test8-i32e32hp2...goal=H2...name=Sudoku Test #06...question=Is H2 7?...answer=no',
            'test9-i29e35hp2...goal=C6...name=Sudoku Test #07...question=Is C6 equal to A2 or A3?...answer=yes',
            # Naked Pairs D
            'test10-i29e35hp7...goal=F6...name=Sudoku Test #14...question=Is F6 5?...answer=no',
            # Y Wings D
            'test29-i27e36yw1...name=Sudoku Test #16...goal=H9...question=Is H9 3?...answer=yes',
        ]
    },
    'extra_games': {
        'puzzles': [
            # Exclusion only; resolved with anything
            # These are un-checked by Shelley other than to confirm that they don't need any operators.
            'easy1...goal=D2...name=No Logical Ops Required #1...question=Is D2 greater than 4?...answer=no',
            'easy1...goal=D2...name=No Logical Ops Required #1...question=Is D2 greater than 4?...answer=no...select_ops_upfront',
            'easy4...goal=A2...name=No Logical Ops Required #2...question=Is A2 odd?...answer=yes',
            'easy4...goal=A2...name=No Logical Ops Required #2...question=Is A2 odd?...answer=yes...select_ops_upfront',

            # May require intermediate operators.
            'box_line_reduction_2...name=Extra Manipulations Required Beyond Logical Ops #1...goal=C5...question=Is C5 less than 5?...answer=yes',
            'box_line_reduction_2...name=Extra Manipulations Required Beyond Logical Ops #1...goal=C5...question=Is C5 less than 5?...answer=yes...select_ops_upfront',
            'hidden_pair_test_2...goal=F7...name=Extra Manipulations Required Beyond Logical Ops #2...question=Is F7 odd?...answer=yes',
            'hidden_pair_test_2...goal=F7...name=Extra Manipulations Required Beyond Logical Ops #2...question=Is F7 odd?...answer=yes...select_ops_upfront',
            'pointing_pair_test_2...goal=E7...name=Extra Manipulations Required Beyond Logical Ops #3...question=Is E7 8?...answer=no',
            'pointing_pair_test_2...goal=E7...name=Extra Manipulations Required Beyond Logical Ops #3...question=Is E7 8?...answer=no...select_ops_upfront',
            'pointing_pair_test...goal=H4...name=Extra Manipulations Required Beyond Logical Ops #4...question=Is H4 even?...answer=no',
            'pointing_pair_test...goal=H4...name=Extra Manipulations Required Beyond Logical Ops #4...question=Is H4 even?...answer=no...select_ops_upfront',
            'xwing_test...goal=E8...name=Extra Manipulations Required Beyond Logical Ops #5...question=Is E8 more than 5?...answer=no',
            'xwing_test...goal=E8...name=Extra Manipulations Required Beyond Logical Ops #5...question=Is E8 more than 5?...answer=no...select_ops_upfront',
            'hidden_triple_test...name=Extra Manipulations Required Beyond Logical Ops #6...goal=A9...question=Is A9 greater than 5?...answer=no',
            'hidden_triple_test...name=Extra Manipulations Required Beyond Logical Ops #6...goal=A9...question=Is A9 greater than 5?...answer=no...select_ops_upfront',
            'xwing_test...name=Extra Manipulations Required Beyond Logical Ops #7...goal=G6...question=Is G6 equal to A7 or A8 or A9?...answer=no',
            'xwing_test...name=Extra Manipulations Required Beyond Logical Ops #7...goal=G6...question=Is G6 equal to A7 or A8 or A9?...answer=no...select_ops_upfront',
            'naked_quad_test...goal=B2...name=Extra Manipulations Required Beyond Logical Ops #8...question=Is B2 a multiple of 3 (3 or 6 or 9)?...answer=yes',
            'naked_quad_test...goal=B2...name=Extra Manipulations Required Beyond Logical Ops #8...question=Is B2 a multiple of 3 (3 or 6 or 9)?...answer=yes...select_ops_upfront',

            # ...select_ops_upfront
            # ...costly_ops': ['inclusion', 'pointingpairs', 'naked pairs', 'ywings']
        ]
    }
}
