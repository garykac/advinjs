_book00_stages = [
	# [stage-name, start-node, end-node, [badges]],
	['',		'000', '000', []],
	['stage1',	'001', '080', ['c1']],
	['',		'500', '500', []],	# Final
]

_book00_badges = {
	'c1': 'Simple Badge',
}

_book00_optional_badges = []

_book00_images = {
}

_book00_functions = [
	'setup',

	'handle_load',
	'handle_keydown',
	'handle_keyup',

	'init',
	'init_game',
	'init_player',

	'draw',
	'erase',
	'draw_player',

	'update_player',

	'check_input',

	'update_world',
]

_book00_info = {
	'prereq': None,
	'stages': _book00_stages,
	'badges': _book00_badges,
	'badges_optional': _book00_optional_badges,
	'images': _book00_images,
	'files': [],
	'default_file': 'script.js',
	'functions': _book00_functions,
}
