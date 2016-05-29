# Adventures in JavaScript
# Build script

import argparse
import distutils.core
import filecmp
import os
import re
import shutil
import subprocess
import sys
import traceback

from parser.parser import Parser

from book00.book00 import _book00_info
from book01.book01 import _book01_info

_version = '0.1'

_books = {
	'book00': _book00_info,
	'book01': _book01_info,
}

def error(msg):
	print 'Error: %s' % msg
	sys.exit(1)

# ----------

class StageGenerator(object):
	def __init__(self, book, stage_id, options):
		self.options = options

		self.book = book
		self.prereq = _books[book]['prereq']
		self.stages = _books[book]['stages']
		self.badge_id2name = _books[book]['badges']
		self.badge_name2id = {}
		for id, name in self.badge_id2name.items():
			self.badge_name2id[name] = id
		self.badges_optional = _books[book]['badges_optional']
		self.images = _books[book]['images']
		self.files = _books[book]['files']
		self.default_file = _books[book]['default_file']
		self.load_function_list()

		self.id = stage_id
		self.stage_name = self.stages[stage_id][0]

		# The base node (from the previous stage) that we need
		# to copy as a baseline for the start node.
		self.source_node = self.stages[stage_id-1][2]

		# The first node in this stage.
		self.start_node = self.stages[stage_id][1]

		# The final node in this stage.
		self.end_node = self.stages[stage_id][2]

		# The first node in the next stage.
		# We need to verify that the final node links here.
		self.next_stage_node = self.stages[stage_id+1][1]

		# List of badges that are allowed in this stage.
		self.stage_badges = self.stages[stage_id][3]

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
		if self.options.trace in node:
			print msg

	def load_function_list(self):
		self.functions = []
		f = open(os.path.join('src', self.book, 'functions.txt'), 'r')
		for fname in f:
			self.functions.append(fname.rstrip())
		f.close()

	def process(self):
		print 'Processing %s stage%d' % (self.book, self.id)

		if self.options.pathcheck:
			self.copy_baseline_snapshot_files()

		while self.nodelist:
			curr = self.nodelist.pop(0)
			if curr != self.end_node:
				self.calc_links(curr, False)
		self.calc_links(self.end_node, True)

		errors = 0

		if self.options.html:
			make_dir(os.path.join(self.book, self.stage_name))
			for n in sorted(self.nodes):
				errors += self.process_node_create_html(n)
		if self.options.pathcheck:
			errors += self.verify_paths(self.book)

		#for t in sorted(self.titles.keys()):
		#	print t, self.titles[t]

		return errors

	def copy_baseline_snapshot_files(self):
		if self.prereq:
			# Todo copy files from pre-req's final output
			distutils.dir_util.copy_tree('baseline', 'snapshots/%s/000' % self.book)
		else:
			make_dir('snapshots/%s/000' % self.book)

	# Calculating links

	def check_badge(self, badge):
		badge_id = self.badge_name2id[badge]
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
		if self.options.verbose:
			print 'calc_links for %s' % node

		filename = os.path.join('src', self.book, self.stage_name, node + '.txt')
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
					m = re.match(r'GOTO END', line)
					if m:
						if self.id != len(self.stages)-2:
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

	def process_node_create_html(self, nodeid):
		if self.options.verbose:
			print 'html', nodeid
		errors = 0
		infile = os.path.join('src', self.book, self.stage_name, nodeid + '.txt')
		success = True
		try:
			parser = Parser(self, self.options)
			if not parser.parse(infile, nodeid, todo=True):
				success = False
		except Exception as e:
			print 'Exception:', e
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_exception(exc_type, exc_value, exc_traceback)
			success = False

		if not success:
			print '%s' % nodeid
			print 'Parse failure'
			errors += 1
			sys.exit(0)
		parser.export_html(os.path.join(self.book, self.stage_name, nodeid + '.html'))

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
				self.process_node_path(book, self.stages[self.id-1][0], src, self.stage_name, tgt, node_path)
			elif check == 'EQ':
				errors += self.check_equal(book, self.stage_name, src, tgt)
			elif check == 'COPY':
				copy_snapshot_dir(book, self.stage_name, src, self.stage_name, tgt)
			else:
				error('Unknown check: %s' % check)
		return errors

	def process_node_path(self, book, stage_src, src, stage_dst, dst, node_path):
		if self.options.verbose:
			print 'path %s -> %s' % (src, dst)
		#print node_path

		if stage_dst != self.stage_name:
			print '%s -> %s' % (src, dst)
			print 'Unexpected stage name: %s instead of %s' % (stage_dst, self.stage_name)
			errors += 1
			sys.exit(0)

		copy_snapshot_dir(book, stage_src, src, stage_dst, dst)

		errors = 0
		nodeid = dst[0:3]
		infile = os.path.join('src', book, stage_dst, nodeid + '.txt')
		success = True

		try:
			parser = Parser(self, self.options, pathcheck=True)
			if not parser.parse(infile, nodeid, fullnodeid=dst):
				success = False
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_exception(exc_type, exc_value, exc_traceback)
			success = False

		if not success:
			print '%s -> %s' % (src, dst)
			print node_path
			print 'Parse failure'
			errors += 1
			sys.exit(0)

		if not self.check_function_order(book, self.stage_name, dst):
			print '%s -> %s' % (src, dst)
			print node_path
			print 'Function order fail'
			errors += 1
			sys.exit(0)
		return errors

	def calc_badge_code(self, badges):
		return ''.join([self.badge_name2id[x] for x in badges])

	def add_path(self, src, tgt, badges, path_so_far):
		badge_code = self.calc_badge_code(badges)
		tgt_code = tgt + badge_code
		new_path = path_so_far[:]
		new_path.append(tgt_code)
		self.path_checks.append(['TRANS', src, tgt_code, new_path])
		self.log_node([src, tgt], 'adding path: %s -> %s' % (src, tgt_code))
		self.paths.append([tgt, badges[:], new_path])

	def calc_path_checks(self):
		base = self.stages[self.id-1][2]
		start = self.stages[self.id][1]
		end = self.stages[self.id][2]

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
					if not self.badge_id2name[b] in badges and not b in self.badges_optional:
						error('End of %s without obtaining badge: %s' % (self.stage_name, self.badge_id2name[b]))
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

	def check_equal(self, book, stage, path1, path2):
		errors = 0

		node1 = path1[0]
		path_so_far1 = path1[1]
		node2 = path2[0]
		path_so_far2 = path2[1]

		for file in self.files:
			#print '%s == %s' % (node1, node2)

			file1 = os.path.join('snapshots', book, stage, node1, file)
			file2 = os.path.join('snapshots', book, stage, node2, file)

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
						print '%s == %s' % (node1, node2)
						print 'Error: files not equal'
						errors += 1
					if bad_count > 10:
						break
					bad_count += 1
					bad1.append(lines1[i].rstrip())
					bad2.append(lines2[i].rstrip())

			if len(bad1) != 0:
				print node1
				print path_so_far1
				for line in bad1:
					print '1:', line
				print node2
				print path_so_far2
				for line in bad2:
					print '2:', line

		return errors

	# Verify that the functions occur in the correct order
	def check_function_order(self, book, stage, node):
		for file in self.files:
			findex = 0
			f = open(os.path.join('snapshots', book, stage, node, file), 'r')
			for line in f:
				m = re.match(r'function (.+)\(', line)
				if m:
					fname = m.group(1)
					while self.functions[findex] != fname:
						findex += 1
						if findex >= len(self.functions):
							print 'Failed to find', fname
							return False
			f.close()
		return True

def make_dir(dir):
	if dir != '' and not os.path.exists(dir):
		os.makedirs(dir)

def rm_dir(dir):
	if os.path.exists(dir):
		shutil.rmtree(dir)

def copy_snapshot_dir(book, stage_src, src, stage_dst, dst):
	"""
	Copy snapshot dir from previous node so we can update it.
	"""
	make_dir(os.path.join('snapshots', book, stage_dst))
	snapshot_src = os.path.join('snapshots', book, stage_src, src)
	snapshot_dst = os.path.join('snapshots', book, stage_dst, dst)

	distutils.dir_util.copy_tree(snapshot_src, snapshot_dst)

def create_main_html_files(options):
	if options.clean:
		print 'Creating baseline.zip'
		subprocess.call(['zip', '-r', 'baseline.zip', 'baseline'])

	errors = 0
	errors += process_html('src/index.txt', 'index.html', None, options)
	errors += process_html('src/baseline.txt', 'baseline.html', None, options)
	errors += process_html('src/howtoplay.txt', 'howtoplay.html', None, options)

	if errors != 0:
		error('Error processing core html files')

def create_book_files(book, options):
	if options.clean:
		print 'Creating images.zip'
		subprocess.call(
				['zip', '-r', 'images.zip', 'images',
					'-i', '*.png'],
				cwd = book)

	errors = process_html('src/%s/images.txt' % book, '%s/images.html' % book, book, options)
	if errors != 0:
		error('Error processing core html files')

def process_html(infile, outfile, book, options):
	"""
	Process simple (non-node) src file and generate an HTML file.
	"""
	errors = 0
	name = os.path.splitext(os.path.basename(infile))[0]
	make_dir(os.path.dirname(outfile))
	success = True
	if options.verbose:
		print '  %s -> html' % infile
	try:
		parser = Parser(None, options)
		if not parser.parse(infile, name):
			print 'Failure during parse_main'
			success = False
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		traceback.print_exception(exc_type, exc_value, exc_traceback)
		success = False

	if not success:
		print '%s' % file
		print 'Parse failure'
		errors += 1
	else:
		parser.export_html(outfile)

	return errors

def main():
	print "Adventures in JavaScript"
	print "Build script", _version

	argparser = argparse.ArgumentParser(
		description='Build and verify script for Adventures in JavasSript')
	argparser.add_argument('--book', required=True,
		help = 'The book to process. Use "all" for all books.')
	argparser.add_argument('--stage', required=True,
		help = 'The stage id to process. Use "all" for all stages.')
	argparser.add_argument('--clean', required=False, action='store_true',
		help = 'True to delete previous files before beginning.')
	argparser.add_argument('--verbose', required=False, action='store_true',
		help = 'True to print verbose output during processing.')
	argparser.add_argument('--html', required=False, action='store_true',
		help = 'True to generate html files.')
	argparser.add_argument('--pathcheck', required=False, action='store_true',
		help = 'True to verify paths between nodes are valid.')
	argparser.add_argument('--debug', required=False, action='store_true',
		help = 'Print additional debug info.')
	argparser.add_argument('--trace', required=False,
		help = 'Print additional debug trace info for this node.')
	argparser.set_defaults(clean=False, verbose=False, html=False, pathcheck=False, debug=False)
	args = argparser.parse_args()

	bookid = 0
	books = []
	if args.book == 'all':
		books = _books.keys()
	else:
		bookid = int(args.book)
		if bookid < 0 or bookid >= len(_books):
			error('Invalid book %s' % bookid)
		books.append('book%02d' % bookid)

	errors = 0
	for book in sorted(books):
		print 'Processing %s' % book

		book_info = _books[book]

		book_stages = book_info['stages']

		stage = 0
		stages = []
		if args.stage == 'all':
			stages = range(1, len(book_stages)-1)
		else:
			stage = int(args.stage)
			if stage <= 0 or stage >= len(book_stages)-1:
				error('Invalid stage %s' % stage)
			stages.append(stage)

		if args.clean:
			if args.stage == 'all':
				if args.pathcheck:
					print 'Creating core snapshot files'
					rm_dir('snapshots')
					make_dir('snapshots')
			else:
				if args.pathcheck:
					rm_dir(os.path.join('snapshots', book, book_stages[stage][0]))
				if args.html:
					rm_dir(os.path.join(book, book_stages[stage][0]))

		if args.html:
			create_book_files(book, args)

		for s in stages:
			sg = StageGenerator(book, s, args)
			errors += sg.process()

		if args.pathcheck:
			final_stage = book_stages[len(book_stages)-2][0]
			final_node = book_stages[len(book_stages)-2][2]
			print 'Copying final stage from', final_stage, final_node
			snapshot_src = os.path.join('snapshots', book, final_stage, final_node)
			snapshot_dst = os.path.join(book, 'final')
			make_dir(snapshot_dst)

			distutils.dir_util.copy_tree(snapshot_src, snapshot_dst)

	if args.html:
		print 'Creating core HTML files'
		create_main_html_files(args)

	if errors == 0:
		print 'Success!'
	else:
		print 'Errors:', errors

if __name__ == '__main__':
	main()
