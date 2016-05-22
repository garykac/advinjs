# Adventures in JavaScript
# Build script

import distutils.core
import filecmp
import getopt
import os
import re
import shutil
import subprocess
import sys

from parser import Parser

_version = '0.1'

_book = 'book01'

_stages = [
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

_badge_id2name = {
	'c1': 'Collision I - Basic',
	'c2': 'Collision II - Advanced',
	'f1': 'Fluff I - Ouch',
	'f2': 'Fluff II - Glasses',
	'i1': 'Treasure I - Key',
	'i2': 'Treasure II - Finish',
	'i3': 'Treasure III - Potion',
	'i4': 'Treasure IV - Coin',
	'i5': 'Treasure V - Better Potion',
	'l1': 'Level I',
	'l2': 'Level II',
	'l3': 'Level III',
	'm1': 'Movement I - Horizontal',
	'm2': 'Movement II - Friction',
	'm3': 'Movement III - Gravity',
	'p1': 'Platform I - Base',
	'p2': 'Platform II - Four Sided',
	'p3': 'Platform III - Pattern',
	'p4': 'Platform IV - Moving',
	's1': 'Sprite I - Origin',
	's2': 'Sprite II - Image',
	's3': 'Sprite III - Direction',
	't1': 'Transition I - Levels',
	't2': 'Transition II - Title',
	't3': 'Transition III - Timer',
	'v1': 'Vitality I - Health',
	'v2': 'Vitality II - Reincarnation',
	'x1': 'Monster I - Stationary',
	'x2': 'Monster II - Roaming',
	'x3': 'Monster III - Animate',
	'x4': 'Monster IV - Projectile',
	'z1': 'Challenge I',
}
_badge_name2id = {}
_optional_badges = ['z1']

_images = {
	'images/player/normal.png': '20x24',
	'images/player/happy.png': '20x24',
	'images/player/ooo.png': '20x24',
	'images/player/sad.png': '30x17',
	'images/player/glasses.png': '20x24',
	'images/player/icon.png': '14x17',
	'images/monsters/vlad.png': '20x24',
	'images/monsters/henrietta.png': '30x30',
	'images/monsters/rufus.png': '28x26',
	'images/monsters/prescott.png': '26x28',
	'images/monsters/doppleganger.png': '20x24',
	'images/monsters/falco1.png': '40x24',
	'images/monsters/falco2.png': '40x24',
	'images/monsters/octoboss1.png': '38x24',
	'images/monsters/octoboss2.png': '38x24',
	'images/monsters/octoboss3.png': '38x24',
	'images/monsters/eyes0.png': '20x20',
	'images/monsters/eyes1.png': '20x20',
	'images/monsters/eyes2.png': '20x20',
	'images/monsters/ball-left.png': '10x5',
	'images/monsters/ball-right.png': '10x5',
	'images/items/key.png': '18x20',
	'images/items/gem.png': '21x27',
	'images/items/potion.png': '16x23',
	'images/items/coin.png': '20x20',
	'images/items/potion-1.png': '16x23',
	'images/items/potion-2.png': '16x23',
	'images/items/potion-3.png': '16x23',
	'images/items/potion-4.png': '16x23',
	'images/items/potion-5.png': '16x23',
	'images/items/potion-6.png': '16x23',
	'images/items/potion-7.png': '16x23',
	'images/items/potion-8.png': '16x23',
	'images/items/potion-9.png': '16x23',
	'images/items/potion-10.png': '16x23',
	'images/items/potion-11.png': '16x23',
	'images/items/potion-12.png': '16x23',
	'images/items/potion-13.png': '16x23',
	'images/items/potion-14.png': '16x23',
	'images/items/potion-15.png': '16x23',
	'images/backgrounds/block.png': '20x20',
	'images/backgrounds/block2.png': '20x20',
	'images/backgrounds/block-red.png': '20x20',
	'images/backgrounds/candycane.png': '20x20',
	'images/backgrounds/dirt.png': '40x20',
	'images/backgrounds/brick.png': '9x8',
	'images/backgrounds/post.png': '10x10',
	'images/backgrounds/wheel.png': '10x10',
	'images/backgrounds/gate-closed.png': '30x40',
	'images/backgrounds/gate-open.png': '30x40',
}

_functions = [
	'setup',

	'handle_load',
	'handle_keydown',
	'handle_keyup',

	'init',
	'init_game',

	'init_player',
	'init_player_sprite',
	'update_player_sprite',

	'init_level_defaults',
	'init_level0_title',
	'init_level1',
	'init_level2',
	'init_level3',

	'add_platforms',
	'add_default_platforms',
	'add_moving_platforms',
	'create_platform',

	'add_monsters',
	'add_projectile_monsters',
	'add_eyeball_monsters',
	'create_monster',

	'add_items',
	'add_potion_item',
	'create_item',

	'create_goal',

	'start_level',
	'complete_level',
	'lose_life',
	'adjust_health',

	'set_transform_xy',
	'set_transform',
	'reset_transform',

	'draw',
	'erase',
	'draw_platforms',
	'draw_monsters',
	'draw_items',
	'draw_goal',
	'draw_player',
	'draw_status',

	'draw_title_screen',
	'draw_transition_screen',

	'update_platforms',
	'update_monsters',
	'update_items',
	'update_player',

	'check_input',

	'check_collisions',
	'check_platform_collisions',
	'check_monster_collisions',
	'check_item_collisions',
	'check_goal_collisions',

	'collide',

	'update_world',
]

def init_globals():
	global _badge_name2id

	for id, name in _badge_id2name.items():
		_badge_name2id[name] = id

def error(msg):
	print 'Error: %s' % msg
	sys.exit(1)

# ----------

class StageGenerator(object):
	def __init__(self, stage_id, options):
		self.options = options

		self.id = stage_id
		self.stage_name = _stages[stage_id][0]

		# The base node (from the previous stage) that we need
		# to copy as a baseline for the start node.
		self.source_node = _stages[stage_id-1][2]

		# The first node in this stage.
		self.start_node = _stages[stage_id][1]

		# The final node in this stage.
		self.end_node = _stages[stage_id][2]

		# The first node in the next stage.
		# We need to verify that the final node links here.
		self.next_stage_node = _stages[stage_id+1][1]

		# List of badges that are allowed in this stage.
		self.stage_badges = _stages[stage_id][3]

		# List of nodes to process.
		self.nodelist = [self.start_node]

		# Set of nodes in this stage.
		self.nodes = set([])

		# Set of badges that are granted in this node.
		self.node_badges = {}

		# List of links for each node.
		self.links = {}

		# The title for each node.
		self.titles = {}

		self.paths = []

		self.path_checks = []

	def log_node(self, node, msg):
		if self.options['trace'] in node:
			print msg

	def process(self):
		print 'Processing stage%d' % self.id

		while self.nodelist:
			curr = self.nodelist.pop(0)
			if curr != self.end_node:
				self.calc_links(curr, False)
		self.calc_links(self.end_node, True)

		errors = 0

		if self.options['html']:
			print 'Generating HTML pages'
			make_dir(os.path.join(_book, self.stage_name))
			for n in sorted(self.nodes):
				errors += self.process_node_create_html(_book, self.stage_name, n)
		if self.options['pathcheck']:
			print 'Verifying paths'
			errors += self.verify_paths(_book)

		#for t in sorted(self.titles.keys()):
		#	print t, self.titles[t]

		return errors

	# Calculating links

	def check_badge(self, badge):
		badge_id = _badge_name2id[badge]
		if not badge_id in self.stage_badges:
			error('Invalid badge "%s"' % badge)

	def calc_badges(self, badge_str):
		badges = badge_str.split('; ')
		for i in range(0, len(badges)):
			self.check_badge(badges[i])
		return badges

	def add_badge(self, node, badge):
		if not node in self.node_badges:
			self.node_badges[node] = []
		self.node_badges[node].append(badge)

	def add_link(self, link):
		link_src = link[0]
		link_tgt = link[1]
		if link_src == link_tgt:
			error('link points to self: %s' % link_src)
		#self.log_node([link_src, link_tgt], '%s -> %s' % (link_src, link_tgt))

		if not link_src in self.links:
			self.links[link_src] = []
		self.links[link_src].append(link)

		if not link_src in self.nodes:
			self.nodes.add(link_src)
		if not link_tgt in self.nodes:
			self.nodelist.append(link[1])
			self.nodes.add(link_tgt)

	def calc_links(self, node, final):
		found_finish = False
		found_stage_link = False

		self.log_node([node], 'calc_links for %s' % node)
		if self.options['verbose']:
			print 'calc_links for %s' % node

		filename = os.path.join('src', _book, self.stage_name, node + '.txt')
		if not os.path.exists(filename):
			error('Unable to find node: %s' % filename)
		f = open(filename, 'r')
		if not node in self.links:
			self.links[node] = []
		for line in f:
			line = line.rstrip()

			if final:
				if line[0:4] == 'GOTO':
					m = re.match(r'GOTO (\d\d\d) STAGE (\d+)', line)
					if m:
						target = m.group(1)
						next_stage = m.group(2)
						# Make sure it links to the next stage.
						if target == self.next_stage_node:
							found_stage_link = True
						else:
							error('Unexpected next stage: found "%s", expected "%s"' % (target, self.next_stage_node))
						continue
					m = re.match(r'GOTO (\d\d\d) END', line)
					if m:
						if self.id != len(_stages)-2:
							error('Unexpected end of game in node: %s' % node)
						found_stage_link = True
						continue
					error('Unknown GOTO format in final node: GOTO "%s"' % line)
				if line[0:12] == 'FINISH_STAGE':
					found_finish = True
				continue

			if line[0:4] == 'GAIN':
				m = re.match(r'GAIN (.+)', line)
				if m:
					badge = m.group(1)
					self.check_badge(badge)
					self.add_badge(node, badge)
					continue

			if line[0:4] == 'GOTO':
				m = re.match(r'GOTO (\d\d\d) IF_BADGE (.+)', line)
				if m:
					target = m.group(1)
					badges = self.calc_badges(m.group(2))
					self.add_link([node, target, 'IF_BADGE', badges])
					continue
				m = re.match(r'GOTO (\d\d\d) IF_NOT_BADGE (.+)', line)
				if m:
					target = m.group(1)
					badges = self.calc_badges(m.group(2))
					self.add_link([node, target, 'IF_NOT_BADGE', badges])
					continue
				m = re.match(r'GOTO (\d\d\d) IF (.+)', line)
				if m:
					target = m.group(1)
					reason = m.group(2)
					self.add_link([node, target, 'IF', reason])
					continue
				m = re.match(r'GOTO (\d\d\d) IF_WANT_BADGE (.+)', line)
				if m:
					target = m.group(1)
					badges = self.calc_badges(m.group(2))
					self.add_link([node, target, 'IF_WANT_BADGE', badges])
					continue
				m = re.match(r'GOTO (\d\d\d)', line)
				if m:
					target = m.group(1)
					self.add_link([node, target, ''])
					continue
				error('Unknown GOTO format: GOTO "%s"' % line)

			if line[0:8] == 'TITLE = ':
				self.titles[node] = line[8:]

		if final:
			if not (found_finish and found_stage_link):
				error('Final node %s missing finish or final link' % node)
		else:
			if len(self.links[node]) == 0:
				error('No links found for %s' % node)

	# Processing nodes

	def process_node_create_html(self, book, stage, node):
		if self.options['verbose']:
			print 'html', node
		errors = 0
		infile = os.path.join('src', book, stage, node + '.txt')
		success = True
		try:
			parser = Parser()
			if not parser.parse(infile, node, _images, book=book, stage=stage):
				success = False
		except Exception as e:
			print 'Exception:', e
			success = False

		if not success:
			print '%s' % node
			print 'Parse failure'
			errors += 1
			sys.exit(0)
		parser.export_html(os.path.join(book, stage, node + '.html'))

		return errors

	def process_node_path(self, book, stage_src, src, stage_dst, dst, node_path):
		if self.options['verbose']:
			print 'path %s -> %s' % (src, dst)
		#print node_path
		errors = 0

		copy_snapshot_dir(book, stage_src, src, stage_dst, dst)

		node = dst[0:3]
		file = node + '.txt'
		success = True
		try:
			parser = Parser()
			if not parser.parse(self.stage_name, file, node, dst, _images):
				success = False
		except:
			success = False

		if not success:
			print '%s -> %s' % (src, dst)
			print node_path
			print 'Parse failure'
			errors += 1
			sys.exit(0)

		if not self.check_function_order(dst):
			print '%s -> %s' % (src, dst)
			print node_path
			print 'Function order fail'
			errors += 1
			sys.exit(0)
		return errors

	# Verify paths

	def verify_paths(self, book):
		errors = 0
		self.calc_path_checks()

		for path in self.path_checks:
			#print path
			check = path[0]
			src = path[1]
			tgt = path[2]

			if check == 'TRANS':
				node_path = path[3]
				self.process_node_path(book, self.stage_name, src, self.stage_name, tgt, node_path)
			elif check == 'TRANS_BASE':
				node_path = path[3]
				self.process_node_path(book, _stages[self.id-1][0], src, self.stage_name, tgt, node_path)
			elif check == 'EQ':
				errors += self.check_equal(src, tgt)
			elif check == 'COPY':
				copy_snapshot_dir(book, self.stage_name, src, self.stage_name, tgt)
			else:
				error('Unknown check: %s' % check)
		return errors

	def calc_badge_code(self, badges):
		return ''.join([_badge_name2id[x] for x in badges])

	def add_path(self, src, tgt, badges, path_so_far):
		badge_code = self.calc_badge_code(badges)
		tgt_code = tgt + badge_code
		new_path = path_so_far[:]
		new_path.append(tgt_code)
		self.path_checks.append(['TRANS', src, tgt_code, new_path])
		self.log_node([src, tgt], 'adding path: %s -> %s' % (src, tgt_code))
		self.paths.append([tgt, badges[:], new_path])

	def calc_path_checks(self):
		base = _stages[self.id-1][2]
		start = _stages[self.id][1]
		end = _stages[self.id][2]

		end_nodes = []
		done_nodes = set()

		self.paths.append([start, [], [start]])
		self.path_checks.append(['TRANS_BASE', base, start, [start]])
		while self.paths:
			state = self.paths.pop(0);
			node = state[0]
			badges = state[1]
			path_so_far = state[2]

			self.log_node([node], state)
			node_id = node[0:3]
			node_code = node_id + self.calc_badge_code(badges)
			self.log_node([node], 'Processing %s' % node_code)

			if node_id == end:
				self.log_node([node], 'adding %s to list of end nodes' % node_code)
				if not node_code in end_nodes:
					end_nodes.append([node_code, path_so_far[:]])
				# Make sure all the badges have been obtained.
				for b in self.stage_badges:
					if not _badge_id2name[b] in badges and not b in _optional_badges:
						error('End of %s without obtaining badge: %s' % (self.stage_name, _badge_id2name[b]))
				continue
			links = self.links[node_id]

			# Update badges for this node.
			if node_id in self.node_badges:
				new_badges = self.node_badges[node_id]
				for new_badge in new_badges:
					if new_badge in badges:
						error('Node %s already has %s' % (node_code, new_badge))
					self.log_node([node], 'Node %s contains badge %s' % (node_id, new_badge))
					badges.append(new_badge)

			if node_code in done_nodes:
				self.log_node([node], 'skipping %s because its done already' % node_code)
				continue
			done_nodes.add(node_code)

			self.log_node([node], 'Node %s has links:' % node_code)
			if False:
				for link in links:
					print '\t', link
			for link in links:
				tgt = link[1]
				cond = link[2]
				self.log_node([node, tgt], 'Processing %s link to %s. %s' %(node, tgt, cond))
				if cond == '':
					self.add_path(node_code, tgt, badges, path_so_far)
					break
				elif cond == 'IF':
					# 'IF' paths are at player discretion so there can be more than one
					self.add_path(node_code, tgt, badges, path_so_far)
				elif cond == 'IF_BADGE':
					req_badges = link[3]
					all_req = True
					for b in req_badges:
						if not b in badges:
							self.log_node([node,tgt], 'skipping link to %s because of missing %s' % (tgt, b))
							all_req = False
					if all_req:
						self.add_path(node_code, tgt, badges, path_so_far)
						break
				elif cond == 'IF_WANT_BADGE':
					# Link is valid if player is missing at least one of the badges
					available_badges = link[3]
					all = True
					for b in available_badges:
						if not b in badges:
							self.add_path(node_code, tgt, badges, path_so_far)
							all = False
					if all:
						self.log_node([node,tgt], 'skipping link to %s because player has all badges' % tgt)
						#log('yay! all badges')
				elif cond == 'IF_NOT_BADGE':
					nreq_badges = link[3]
					if len(nreq_badges) != 1:
						error('too many nreq badges')
					b = nreq_badges[0]
					if b in badges:
						self.log_node([node,tgt], 'skipping link to %s because already have %s' % (tgt, b))
					else:
						self.add_path(node_code, tgt, badges, path_so_far)
						break
				else:
					print link
					error('not processing')

		# If there are multiple paths to the stage's end node, make sure that
		# the generated code is identical.
		if len(end_nodes) > 1:
			for i in range(1, len(end_nodes)):
				self.path_checks.append(['EQ', end_nodes[0], end_nodes[i]])
		if end_nodes[0][0] != end_nodes[0][0][0:3]:
			self.path_checks.append(['COPY', end_nodes[0][0], end_nodes[0][0][0:3]])

	def check_equal(self, path1, path2):
		errors = 0

		filename1 = path1[0]
		path_so_far1 = path1[1]
		filename2 = path2[0]
		path_so_far2 = path2[1]

		#print '%s == %s' % (filename1, filename2)

		file1 = os.path.join('snapshots', self.stage_name, filename1, 'script.js')
		file2 = os.path.join('snapshots', self.stage_name, filename2, 'script.js')

		with open(file1) as f1:
			lines1 = f1.readlines()
		with open(file2) as f2:
			lines2 = f2.readlines()

		bad_count = 0
		bad1 = []
		bad2 = []
		for i in range(0, len(lines1)):
			if lines1[i] != lines2[i]:
				if bad_count == 0:
					print '%s == %s' % (filename1, filename2)
					print 'Error: files not equal'
					errors += 1
				if bad_count > 10:
					break
				bad_count += 1
				bad1.append(lines1[i].rstrip())
				bad2.append(lines2[i].rstrip())

		if len(bad1) != 0:
			print filename1
			print path_so_far1
			for line in bad1:
				print '1:', line
			print filename2
			print path_so_far2
			for line in bad2:
				print '2:', line

		return errors

	# Verify that the functions occur in the correct order
	def check_function_order(self, dst):
		findex = 0
		f = open(os.path.join('snapshots', self.stage_name, dst, 'script.js'), 'r')
		for line in f:
			m = re.match(r'function (.+)\(', line)
			if m:
				fname = m.group(1)
				while _functions[findex] != fname:
					findex += 1
					if findex >= len(_functions):
						print 'Failed to find', fname
						return False
		f.close()
		return True

def make_dir(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)

def rm_dir(dir):
	if os.path.exists(dir):
		shutil.rmtree(dir)

def copy_snapshot_dir(book, stage_src, src, stage_dst, dst):
	snapshot_src = os.path.join('snapshots', book, stage_src, src)
	snapshot_dst = os.path.join('snapshots', book, stage_dst, dst)

	# Copy from dir so we can update it
	distutils.dir_util.copy_tree(snapshot_src, snapshot_dst)

def copy_core_snapshot_files():
	distutils.dir_util.copy_tree('baseline', 'snapshots/book01/000')

def create_main_html_files(options):
	print 'Creating baseline.zip'
	subprocess.call(['zip', '-r', 'baseline.zip', 'baseline'])

	errors = 0
	errors += process_html('src/index.txt', 'index.html', options)
	errors += process_html('src/baseline.txt', 'baseline.html', options)
	errors += process_html('src/howtoplay.txt', 'howtoplay.html', options)

	if errors != 0:
		error('Error processing core html files')

def create_book_files(book, options):
	print 'Creating images.zip'
	subprocess.call(
			['zip', '-r', 'images.zip', 'images',
				'-i', '*.png'],
			cwd = book)

	errors = process_html('src/%s/images.txt' % book, '%s/images.html' % book, options)
	if errors != 0:
		error('Error processing core html files')

def process_html(infile, outfile, options):
	"""
	Process simple (non-node) src file and generate an HTML file.
	"""
	errors = 0
	name = os.path.splitext(os.path.basename(infile))[0]
	success = True
	if options['verbose']:
		print '  %s -> html' % infile
	try:
		parser = Parser()
		if not parser.parse(infile, name, _images):
			print 'Failure during parse_main'
			success = False
	except:
		print 'Parsing exception:', sys.exc_info()[0]
		success = False

	if not success:
		print '%s' % file
		print 'Parse failure'
		errors += 1
	else:
		parser.export_html(outfile)

	return errors

def usage():
	print 'Usage: %s <options>' % sys.argv[0]
	print "where <options> are:"
	print "  --html"
	print "  --pathcheck"
	print "  --clean"
	print "  --stage <stage-id>"
	print "  --trace <node-id>"
	print "  --verbose"
	print "and <stage-id> is '1', '2', ...  or 'all'"
	print "and <node-id> is the 3-digit node number"
	sys.exit(2)

def main():
	print "Adventures in JavaScript"
	print "Build script", _version

	try:
		opts, args = getopt.getopt(sys.argv[1:],
			'hpcs:t:v',
			['html', 'pathcheck', 'clean', 'stage=', 'trace=', 'verbose'])
	except getopt.GetoptError:
		usage()

	options = {
		'html': False,
		'pathcheck': False,
		'trace': '',
		'verbose': False,
	}

	clean = False
	all_stages = False
	stage = 1
	for opt, arg in opts:
		if opt in ('-h', '--html'):
			options['html'] = True
		elif opt in ('-o', '--pathcheck'):
			options['pathcheck'] = True
		elif opt in ('-c', '--clean'):
			clean = True
		elif opt in ('-s', '--stage'):
			if arg == 'all':
				all_stages = True
			else:
				stage = int(arg)
		elif opt in ('-t', '--trace'):
			options['trace'] = True
		elif opt in ('-v', '--verbose'):
			options['verbose'] = True

	stages = []
	if all_stages:
		stages = range(1, len(_stages)-1)
	else:
		if stage <= 0 or stage >= len(_stages)-1:
			error('Invalid stage %s' % stage)
		stages.append(stage)

	if clean:
		if all_stages:
			if options['pathcheck']:
				print 'Creating core snapshot files'
				rm_dir('snapshots')
				make_dir('snapshots')
				copy_core_snapshot_files()
			if options['html']:
				print 'Creating core HTML files'
				create_main_html_files(options)
		else:
			if options['pathcheck']:
				rm_dir(os.path.join('snapshots', _book, _stages[stage][0]))
			if options['html']:
				rm_dir(os.path.join(_book, _stages[stage][0]))

	create_book_files(_book, options)

	errors = 0
	init_globals()
	for s in stages:
		sg = StageGenerator(s, options)
		errors += sg.process()

	print 'Errors:', errors

if __name__ == '__main__':
	main()
