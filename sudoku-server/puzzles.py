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
    'hard2': '6.2.5.........3.4..........43...8....1....2........7..5..27...........81...6.....',
    'hard3': '...5...........5.697.....2...48.2...25.1...3..8..3.........4.7..13.5..9..2...31..',
    'hard4': '3..6.9.12..7.....6.2...1......74...3..29.65..1...23......8...9.5.....3..29.3.7..4',
    'fiendish1': '.....5.8....6.1.43..........1.5........1.6...3.......553.....61........4.........',
    'fiendish2': '85...24..72......9..4.........1.7..23.5...9...4...........8..7..17..........36.4.',
    'fiendish3': '..53.....8......2..7..1.5..4....53...1..7...6..32...8..6.5....9..4....3......97..',
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
    'hidden_quad_test': '9.15...46425.9..8186..1..2.5.2.......19...46.6.......2196.4.2532...6.817.....1694',
    'pointing_pair_test': '.179.36......8....9.....5.7.72.1.43....4.2.7..6437.25.7.1....65....3......56.172.',
    'pointing_pair_test_2': '.32..61..41..........9.1...5...9...4.6.....713...2...5...5.8.........519.57..986.',
    'pointing_triple_test': '93..5....2..63..95856..2.....318.57...5.2.98..8...5......8..1595.821...4...56...8',
    'box_line_reduction': '.16..78.3.9.8.....87...1.6..48...3..65...9.82.39...65..6.9...2..8...29369246..51.',
    'box_line_reduction_2': '.2.9437159.4...6..75.....4.5..48....2.....4534..352....42....81..5..426..9.2.85.4',
    'xwing_test': '1.....569492.561.8.561.924...964.8.1.64.1....218.356.4.4.5...169.5.614.2621.....5',
    'xwing_test_2': '.......9476.91..5..9...2.81.7..5..1....7.9....8..31.6724.1...7..1..9..459.....1..',
    'ywing_test': '9..24.....5.69.231.2..5..9..9.7..32...29356.7.7...29...69.2..7351..79.622.7.86..9',
    'xyz_wing_test': '.92..175.5..2....8....3.2...75..496.2...6..75.697...3...8.9..2.7....3.899.38...4.',
    'xyz_wing_test_2': '6.......85..9.8..782...1.3.34.2.9.8.2...8.3..18.3.7.2575.4...929....5..44...9...3',
    'swordfish_test_333': '52941.7.3..6..3..2..32......523...76637.5.2..19.62753.3...6942.2..83.6..96.7423.5',
    'swordfish_test_222': '926...1..537.1.42.841...6.3259734816714.6..3.36812..4.1.2....84485.7136.6.3.....1',
    'swordfish_test_323': '.2..43.69..38962..96..25.3.89.56..136...3.....3..81.263...1..7...96743.227.358.9.',

    'underconstrained1': '.8...9743.5...8.1..1.......8....5......8.4......3....6.......7..3.5...8.9724...5.',
    'underconstrained2': '53..7....6..1.5....98....6.8.......34..8.3..17...2...6.6....28....419..5....8..79',
    'underconstrained3': '..97.......48.9.7......2.3....3.6...3..1....9..6....58..8.3....5.....1869.2......',
    'underconstrained4': '......23....3.8.64....4.9.8573.......8652937.......8456.5.1....71...2....48......',
    'underconstrained5': '.21...9.36........83962...19...31.....2...3.....9....87...69152........92.5...74.',
    'underconstrained6': '.7.4.1..8.16.3...45.4........7.8..9.6..123........6......6...532.8.....6.......8.',

    # INSOLUBLE BY PROPAGATION (BASED ON EASY 0)
    'insoluble_by_propagation': '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.8..',

    # INSOLUBLE BY INITIAL STATE CONFLICT (BASED ON EASY 0)
    'insoluble_by_initial_state_conflict': '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.6..',

}

games = {
    'test_game1_6': {
        'puzzles': ['test2-i24e40', 'easy1', 'xwing_test', 'hard4', 'underconstrained1', 'test7-i26e36hp10'],
        'config_alterations': ['select_ops_upfront']
    },
    'test_game1_4': {
        'puzzles': ['test2-i24e40', 'xwing_test', 'hard4', 'underconstrained1'],
        'config_alterations': ['select_ops_upfront']
    }
}
