_book01_stages = [
	# [stage-name, start-node, end-node, [badges]],
	['',		'000', '000', []],
	['stage1',	'001', '018', ['m1', 'm2', 'p1', 's1']],
	['stage2',	'020', '049', ['c1', 'm3']],
	['stage3',	'050', '089', ['c2', 'p2', 'x1', 'x2']],
	['stage4',	'090', '098', ['t1']],
	['stage5',	'099', '299', ['i1', 'i2', 'i3', 'p3', 's2', 's3', 'v1', 'v2', 'z1']],
	['stage6',	'300', '345', ['t2', 't3']],
	['stage7',	'350', '395', ['f1', 'i4', 'l1']],
	['stage8',	'400', '445', ['i5', 'l2', 'x3']],
	['stage9',	'450', '495', ['f2', 'l3', 'p4', 'x4']],
	['',		'500', '500', []],	# Final
]

_book01_optional_badges = ['z1']

_book01_info = {
	'prereq': 'book00',
	'stages': _book01_stages,
	'badges_optional': _book01_optional_badges,
	'files': ['script.js'],
	'default_file': 'script.js',
}
