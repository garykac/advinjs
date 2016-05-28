import os.path
import re
import shutil
import sys

from parse_code import Parse_Code

class Parser(object):
	def __init__(self, stagegen, options, pathcheck=False):
		self.stagegen = stagegen
		self.book = None
		self.stage = None
		self.images = {}
		self.default_file = None
		if self.stagegen:
			self.book = self.stagegen.book
			self.stage = self.stagegen.stage_name
			self.images = self.stagegen.images
			self.default_file = self.stagegen.default_file

		self.pathcheck = pathcheck

		self.data = []

		# A stack of parse modes.
		self.parse_mode = ['top']

		# The full id of the node, with any badge annotations appended to the
		# base node name.
		self.fullnodeid = ''

		# The simple node id (just the number).
		self.nodeid = ''

		self.in_copy_file = False

		self.current_file = ''
		self.current_line = 0

		# Top-level parsers.
		self.parse_code = Parse_Code(self, 'code', self.default_file, pathcheck, options)

		self.parsers = [
			self.parse_code,
		]

		self.mode_parser = {
			'code': self.parse_code,
		}

	def parse(self, infile, nodeid, fullnodeid=None, todo=False):
		"""
		nodeid: The name of the node being parse. This is the same as the
			infile without the path or extension.
		"""
		self.nodeid = nodeid
		self.fullnodeid = fullnodeid
		if self.fullnodeid == None:
			self.fullnodeid = nodeid
		self.show_todo = todo
		self.dir_depth = len(infile.split('/')) - 2

		if not os.path.isfile(infile):
			self.error('File "%s" doesn\'t exist' % infile)

		try:
			self.fileobj = open(infile, 'r')
		except IOError as e:
			self.error('Unable to open "%s": %s' % (infile, e))

		self.current_file = infile
		success = self.parse_input()

		self.fileobj.close()
		return success

	def export_html(self, outfile):
		self.print_html(outfile)


	# ---------------
	# Parsing helpers
	# These are used by the other parsers.
	# ---------------

	def error(self, msg):
		"""Report a syntax or other user error."""
		print 'Error %s(%d): %s' % (self.current_file, self.current_line, msg)
		sys.exit(1)

	def warning(self, msg):
		"""Report a warning."""
		print 'Warning %s(%d): %s' % (self.current_file, self.current_line, msg)

	def current_mode(self):
		"""Return the string containing the current parsing mode."""
		return self.parse_mode[-1]

	def enter_mode(self, new_mode):
		"""Switch to the specified parsing mode."""
		self.parse_mode.append(new_mode)

	def exit_mode(self, curr_mode):
		"""Exit the current parsing mode."""
		m = self.parse_mode.pop()
		if m != curr_mode:
			self.internal_error('Exiting wrong mode: %s (expected: %s)' % (m, curr_mode))

	def add_data(self, type, data):
		self.data.append([type, data])

	def expand_text_type(self, text, start_char, end_char, span_class):
		done = False
		curr_text = text
		new_text = ''
		while not done:
			pattern = r'^([^' + start_char + ']*)' + start_char + '([^' + end_char + ']+)' + end_char + '(.*)$'
			m = re.match(pattern, curr_text)
			if m:
				new_text += '%s<span class="%s">%s</span>' % (m.group(1), span_class, m.group(2))
				curr_text = m.group(3)
			else:
				done = True
		new_text += curr_text
		return new_text

	def expand_text(self, text, color):
		text = self.expand_text_type(text, r'\{', r'\}', 'thinking');
		text = text.replace('a href=', 'a href!!!');
		if color:
			text = self.expand_text_type(text, r'\=', r'\=', 'code-inline-color');
		else:
			text = self.expand_text_type(text, r'\=', r'\=', 'code-inline');
		text = text.replace('a href!!!', 'a href=');
		return text

	def set_table_columns(self, cols):
		self.image_table_columns = cols
		if cols == '1':
			self.image_table_class = 'col-sm-12 col-md-12'
		elif cols == '2':
			self.image_table_class = 'col-sm-6 col-md-6'
		elif cols == '3':
			self.image_table_class = 'col-sm-6 col-md-4'
		elif cols == '4':
			self.image_table_class = 'col-sm-6 col-md-3'
		elif cols == '6':
			self.image_table_class = 'col-sm-6 col-md-2'
		else:
			self.error('Invalid table column: %s' % cols)

	# ----------------
	# Internal parsing
	# ----------------

	def parse_input(self):
		self.current_line = 0
		for line in self.fileobj:
			self.current_line += 1

			# Strip whitespace and comments.
			comment = line.find('//')
			if comment == 0:
				line = ''
			line = line.strip()

			if not self.parse_line(line):
				self.error('Unable to parse: %s' % line)
				return False
		return self.current_mode() == 'top'

	def parse_line(self, line):
		if len(line) == 0:
			return True

		mode = self.current_mode()
		if mode == 'top':
			if not self.parse_toplevel(line):
				self.error('Unrecognized line: %s' % line)
				return False
		elif mode in self.mode_parser:
			parser = self.mode_parser[mode]
			if not parser.parse_line(line):
				self.error('Unrecognized line: %s' % line)
				return False
		else:
			self.error_internal('Bad parsing mode: %s' % mode)
			return False
		return True

	def parse_toplevel(self, line):
		if re.match(r'TITLE = ', line):
			self.title = line[8:]
			return True
		if re.match(r'ID = ', line):
			self.id = line[5:]
			return True
		if re.match(r'B: ', line):
			self.add_data('B', line[3:])
			return True
		if re.match(r'U: ', line):
			self.add_data('U', line[3:])
			return True
		if re.match(r'N: ', line):
			self.add_data('N', line[3:])
			return True
		if re.match(r'ADMIN ', line):
			self.add_data('ADMIN', line[6:])
			return True
		if re.match(r'HTML ', line):
			self.add_data('HTML', line[5:])
			return True
		if re.match(r'TODO ', line):
			self.add_data('TODO', line[5:])
			if self.show_todo:
				print self.nodeid, line
			return True
		if re.match(r'FIGURE ', line):
			self.add_data('FIGURE', line[7:])
			return True
		if re.match(r'SCREENSHOT ', line):
			self.add_data('SCREENSHOT', line[11:])
			return True
		if re.match(r'RUN_VERIFY', line):
			self.add_data('RUN_VERIFY', '')
			return True
		if re.match(r'GAIN ', line):
			self.add_data('GAIN', line[5:])
			return True
		if re.match(r'GOTO ', line):
			self.add_data('GOTO', line[5:])
			return True
		if re.match(r'FINISH_STAGE ', line):
			self.add_data('FINISH_STAGE', line[13:])
			return True

		if re.match(r'CREATE_DIR ', line):
			dir = line[11:]
			self.add_data('CREATE_DIR', dir)
			return True
		if re.match(r'CREATE_FILE ', line):
			file = line[12:]
			self.add_data('CREATE_FILE', file)
			if self.pathcheck:
				dst = os.path.join('snapshots', self.book, self.stage, self.fullnodeid, file)
				f = open(dst, 'w')
				f.close()
			return True
		if re.match(r'BEGIN_COPY_FILE', line):
			self.in_copy_file = True
			self.add_data('BEGIN_COPY_FILE', '')
			return True
		if re.match(r'END_COPY_FILE', line):
			self.in_copy_file = False
			self.add_data('END_COPY_FILE', '')
			return True
		if re.match(r'COPY_FILE', line):
			if not self.in_copy_file:
				self.error('COPY_FILE outside of BEGIN/END')
			path = line[10:]
			self.add_data('COPY_FILE', path)
			if self.pathcheck:
				src = os.path.join(self.book, path)
				dst = os.path.join('snapshots', self.book, self.stage, self.fullnodeid, path)
				dir = os.path.dirname(dst)
				if not os.path.exists(dir):
					os.makedirs(dir)
				if not os.path.exists(src):
					self.error('Unable to find: %s' % src)
				shutil.copy(src, dst)
			return True

		if re.match(r'BEGIN_IMAGE_TABLE ', line):
			self.add_data('BEGIN_IMAGE_TABLE', line[18:])
			return True
		if re.match(r'TABLE_IMAGE ', line):
			self.add_data('TABLE_IMAGE', line[12:])
			return True
		if re.match(r'END_IMAGE_TABLE', line):
			self.add_data('END_IMAGE_TABLE', '')
			return True

		if re.match(r'BEGIN_TASK_LIST', line):
			self.add_data('BEGIN_TASK_LIST', '')
			return True
		if re.match(r'END_TASK_LIST', line):
			self.add_data('END_TASK_LIST', '')
			return True
		if re.match(r'TASK_LIST_ITEM ', line):
			self.add_data('TASK_LIST_ITEM', line[15:])
			return True
		if re.match(r'TASK_LIST_ITEM_START', line):
			self.add_data('TASK_LIST_ITEM_START', '')
			return True
		if re.match(r'TASK_LIST_ITEM_DATA ', line):
			self.add_data('TASK_LIST_ITEM_DATA', line[20:])
			return True
		if re.match(r'TASK_LIST_ITEM_END', line):
			self.add_data('TASK_LIST_ITEM_END', '')
			return True

		if self.stage == None:
			if re.match(r'H1 ', line):
				self.add_data('H1', line[3:])
				return True
			if re.match(r'H2 ', line):
				self.add_data('H2', line[3:])
				return True
			if re.match(r'H3 ', line):
				self.add_data('H3', line[3:])
				return True
			if re.match(r'BYLINE ', line):
				self.add_data('BYLINE', line[7:])
				return True
			if re.match(r'INFO ', line):
				self.add_data('INFO', line[5:])
				return True

			if re.match(r'BEGIN_SCREENSHOT_TABLE', line):
				self.add_data('BEGIN_SCREENSHOT_TABLE', '')
				return True
			if re.match(r'SCREENSHOT_TABLE_IMAGE ', line):
				self.add_data('SCREENSHOT_TABLE_IMAGE', line[23:])
				return True
			if re.match(r'END_SCREENSHOT_TABLE', line):
				self.add_data('END_SCREENSHOT_TABLE', '')
				return True

			if re.match(r'BEGIN_MAIN_TABLE', line):
				self.add_data('BEGIN_MAIN_TABLE', '')
				return True
			if re.match(r'MAIN_TABLE_IMAGE ', line):
				self.add_data('MAIN_TABLE_IMAGE', line[17:])
				return True
			if re.match(r'END_MAIN_TABLE', line):
				self.add_data('END_MAIN_TABLE', '')
				return True

			if re.match(r'BEGIN_LIST', line):
				self.add_data('BEGIN_LIST', '')
				return True
			if re.match(r'LIST_ITEM ', line):
				self.add_data('LIST_ITEM', line[10:])
				return True
			if re.match(r'END_LIST', line):
				self.add_data('END_LIST', '')
				return True

			if re.match(r'FOOTNOTE ', line):
				self.add_data('FOOTNOTE', line[9:])
				return True
			if re.match(r'PRE_FILE ', line):
				self.add_data('PRE_FILE', line[9:])
				return True

		parser = None
		for p in self.parsers:
			if p.match_toplevel(line):
				parser = p
				break

		if parser is not None:
			return parser.start_parse_mode()

		return False

	# -----------
	# HTML output
	# -----------

	def print_html(self, outfile):
		try:
			fout = open(outfile, 'w')
		except IOError as e:
			self.error('Unable to open "%s" for writing: %s' % (outfile, e))

		self.print_html_header(fout)
		if self.stage != None:
			fout.write('<h1>%s : %s</h1>\n' % (self.id, self.title))

		for d in self.data:
			if d[0] == 'B':
				fout.write('<div class="name">Balthazar:</div><p class="balthazar">%s</p>\n' % self.expand_text(d[1], True))
			elif d[0] == 'U':
				fout.write('<div class="name">You:</div><p class="you">%s</p>\n' % self.expand_text(d[1], True))
			elif d[0] == 'BEGIN_CODE':
				fout.write('<div class="panel panel-default">\n')
			elif d[0] == 'BEGIN_CODE_INFO':
				filename = self.stagegen.default_file
				text = d[1]
				m = re.match(r'\((.+)\) (.+)', d[1])
				if m:
					filename = m.group(1)
					text = m.group(2)
				fout.write('<div class="panel panel-default">\n')
				fout.write('<div class="panel-code-header"><span class="panel-code-header-filename">%s:</span> %s</div>' % (filename, self.expand_text(text, False)))
			elif d[0] == 'CODE':
				css_path = ('../' * self.dir_depth) + 'css'
				fout.write('<div class="panel-code code">')
				for line in d[1]:
					type = line[0]
					line = line[1:].replace('\t', '    ')
					if type == '.':
						fout.write('<span class="context">%s</span>\n' % line)
					elif type == '+':
						fout.write('<img src="%s/plus.png" width="15" height="15"/><span class="add">%s</span>\n' % (css_path, line))
					elif type == '-':
						fout.write('<img src="%s/cross.png" width="15" height="15"/><span class="delete">%s</span>\n' % (css_path, line))
					elif type == '>':
						fout.write('<span class="indent">%s</span>\n' % line)
					elif type != '^':
						self.error('Unknown mark: "%s"' % type)
				fout.write('</div>\n')
			elif d[0] == 'END_CODE':
				fout.write('</div>\n')
			elif d[0] == 'END_CODE_OK':
				fout.write('<div class="panel-code-footer">Run your code in a browser and verify that there are no errors.</div>')
				fout.write('</div>\n')
			elif d[0] == 'END_CODE_ERROR':
				fout.write('<div class="panel-code-footer">If you run your code now, you\'ll see an error because %s.</div>' % self.expand_text(d[1], False))
				fout.write('</div>\n')
			elif d[0] == 'GOTO':
				m = re.match(r'(\d\d\d) IF_BADGE (.+)', d[1])
				if m:
					target = m.group(1)
					badgenames = m.group(2)
					badges = badgenames.split('; ')
					fout.write('<p class="alert alert-info"><a href="%s.html"><span class="goto">GOTO %s</span></a> if you already have the ' % (target, target))
					if len(badges) == 1:
						fout.write('<span class="badge-check">%s</span> badge.' % badges[0])
					else:
						for i in range(0, len(badges)):
							if i != 0:
								fout.write(' and ')
							fout.write('<span class="badge-check">%s</span>' % badges[i])
						fout.write(' badges.')
					fout.write('</p>\n')
					continue
				m = re.match(r'(\d\d\d) IF_NOT_BADGE (.+)', d[1])
				if m:
					target = m.group(1)
					badgenames = m.group(2)
					badges = badgenames.split('; ')
					fout.write('<p class="alert alert-info"><a href="%s.html"><span class="goto">GOTO %s</span></a> if you NOT have the ' % (target, target))
					if len(badges) == 1:
						fout.write('<span class="badge-check">%s</span> badge.' % badges[0])
					else:
						for i in range(0, len(badges)):
							if i != 0:
								fout.write(' and ')
							fout.write('<span class="badge-check">%s</span>' % badges[i])
						fout.write(' badges.')
					fout.write('</p>\n')
					continue
				m = re.match(r'(\d\d\d) IF (.+)', d[1])
				if m:
					target = m.group(1)
					reason = m.group(2)
					target_link = target
					if self.stage == None:
						target_link = 'book01/stage1/' + target
					fout.write('<p class="alert alert-info"><a href="%s.html"><span class="goto">GOTO %s</span></a> if you want to %s</p>\n' % (target_link, target, reason))
					continue
				m = re.match(r'(\d\d\d) IF_WANT_BADGE (.+)', d[1])
				if m:
					target = m.group(1)
					badgenames = m.group(2)
					badges = badgenames.split('; ')
					fout.write('<p class="alert alert-info"><a href="%s.html"><span class="goto">GOTO %s</span></a> if you want to get your ' % (target, target))
					if len(badges) == 1:
						fout.write('<span class="badge-check">%s</span> badge.' % badges[0])
					else:
						num_badges = len(badges)
						for i in range(0, num_badges):
							if i != 0 and i != num_badges - 1:
								fout.write(', ')
							elif i == num_badges - 1:
								fout.write(' or ')
							fout.write('<span class="badge-check">%s</span>' % badges[i])
						fout.write(' badges.')
					fout.write('</p>\n')
					continue
				m = re.match(r'(\d\d\d) STAGE (.+)', d[1])
				if m:
					target = m.group(1)
					next_stage = m.group(2)
					fout.write('<p class="alert alert-info"><a href="../stage%s/%s.html"><span class="goto">GOTO %s</span></a> to proceed to stage %s.</p>\n' % (next_stage, target, target, next_stage))
					continue
				m = re.match(r'END', d[1])
				if m:
					fout.write('<p class="alert alert-info">End of Game.</p>\n')
					continue
				m = re.match(r'(\d\d\d)(.*)', d[1])
				if m:
					target = m.group(1)
					extra = m.group(2)
					if len(extra) != 0:
						self.error('Unknown format: GOTO "%s"' % d[1])
					target_link = target
					if self.stage == None:
						target_link = 'book01/stage1/' + target
					fout.write('<p class="alert alert-info"><a href="%s.html"><span class="goto">GOTO %s</span></a></p>\n' % (target_link, target))
					continue
				self.error('Unknown format: GOTO "%s"' % d[1])
			elif d[0] == 'FIGURE':
				m = re.match(r'([a-zA-Z0-9\/\-\.]+) (\d+)x(\d+)', d[1])
				if m:
					file = '../figures/' + m.group(1)
					width = m.group(2)
					height = m.group(3)
					fout.write('<div class="row">\n')
					fout.write('<div class="col-md-12"><div class="image-table">\n')
					fout.write('<a href="%s"><img class="figure" src="%s" width="%s" height="%s" /></a>\n' % (file, file, width, height))
					fout.write('</div></div>\n')
					fout.write('</div>\n')
					continue
				self.error('Unknown format: FIGURE "%s"' % d[1])
			elif d[0] == 'SCREENSHOT':
				m = re.match(r'([a-zA-Z0-9\/\-\.]+) (\d+)x(\d+)', d[1])
				if m:
					file = '../screenshots/' + m.group(1)
					width = m.group(2)
					height = m.group(3)
					fout.write('<div class="row">\n')
					fout.write('<div class="col-md-12"><div class="image-table">\n')
					fout.write('<a href="%s"><img class="screenshot" src="%s" width="%s" height="%s" /></a>\n' % (file, file, width, height))
					fout.write('</div></div>\n')
					fout.write('</div>\n')
					continue
				self.error('Unknown format: SCREENSHOT "%s"' % d[1])
			elif d[0] == 'ADMIN':
				fout.write('<p class="admin">%s</p>\n' % self.expand_text(d[1], True))
			elif d[0] == 'GAIN':
				badge = d[1]
				fout.write('<p class="alert alert-success"><strong>Congratulations!</strong> You\'ve earned the <span class="badge-gain">%s</span> badge!</p>\n' % badge)
			elif d[0] == 'RUN_VERIFY':
				fout.write('<p class="run">RUN your code in a browser and verify that it loads without errors.</p>\n')

			elif d[0] == 'CREATE_DIR':
				fout.write('<div class="alert alert-info"><p>Create the following directory in your project:</p><ul class="list-group"><li class="list-group-item"><span class="code-inline">%s</span></li></ul></div>\n' % d[1])
			elif d[0] == 'CREATE_FILE':
				fout.write('<div class="alert alert-info"><p>Create the following file in your project:</p><ul class="list-group"><li class="list-group-item"><span class="code-inline">%s</span></li></ul></div>\n' % d[1])
			elif d[0] == 'BEGIN_COPY_FILE':
				fout.write('<div class="alert alert-info"><p>Copy the following files into your project:</p><ul class="list-group">\n')
			elif d[0] == 'COPY_FILE':
				fout.write('<li class="list-group-item"><span class="code-inline">%s</span></li>\n' % d[1])
			elif d[0] == 'END_COPY_FILE':
				fout.write('</ul></div>\n')

			elif d[0] == 'BEGIN_TASK_LIST':
				fout.write('<ul class="list-group">\n')
			elif d[0] == 'END_TASK_LIST':
				fout.write('</ul>\n')
			elif d[0] == 'TASK_LIST_ITEM':
				fout.write('<li class="list-group-item">%s</li>\n' % d[1])
			elif d[0] == 'TASK_LIST_ITEM_START':
				fout.write('<li class="list-group-item">\n')
			elif d[0] == 'TASK_LIST_ITEM_DATA':
				fout.write('<p>%s</p>\n' % self.expand_text(d[1], True))
			elif d[0] == 'TASK_LIST_ITEM_END':
				fout.write('</li>\n')

			elif d[0] == 'BEGIN_IMAGE_TABLE':
				m = re.match(r'(\d+)', d[1])
				if m:
					self.set_table_columns(m.group(1))
					fout.write('<div class="row">\n')
					continue
				self.error('Unknown format: BEGIN_IMAGE_TABLE "%s"' % d[1])
			elif d[0] == 'TABLE_IMAGE':
				m = re.match(r'([a-zA-Z0-9\/\-\.]+) (\d+)x(\d+) (.*)', d[1])
				if m:
					file = m.group(1)
					width = m.group(2)
					height = m.group(3)
					caption = m.group(4)
					if not os.path.exists(os.path.join(self.book, file)):
						self.error('Table image does not exist: %s' % file)
					if not file in self.images:
						self.error('Unknown image file: "%s"' % file)
					(w, h) = self.images[file].split('x')
					#print w, h
					#print int(w), int(h)
					#print int(w) * 2, int(h) *2
					if (int(w) * 2) != int(width) or (int(h) * 2) != int(height):
						self.error('Bad image size: %s x %s' % (width, height))

					fout.write('<div class="%s"><div class="image-table">\n' % self.image_table_class)
					fout.write('<a href="../%s"><img src="../%s" width="%s" height="%s" /></a>\n' % (file, file, width, height))
					fout.write('<div class="caption"><p align="center">%s</p></div>\n' % caption)
					fout.write('</div></div>\n')
					continue
				self.error('Unknown format: TABLE_IMAGE "%s"' % d[1])
			elif d[0] == 'END_IMAGE_TABLE':
				fout.write('</div>\n')

			elif d[0] == 'TODO':
				fout.write('<!-- TODO: %s -->\n' % d[1])
			elif d[0] == 'FINISH_STAGE':
				fout.write('<p class="alert alert-success"><strong>Congratulations!</strong> You\'ve have finished <span class="stage">Stage %s</span> and your character has gained a level.</p>\n' % d[1])
				fout.write('<ul class="list-group">\n')
				fout.write('<li class="list-group-item">\n')
				fout.write(self.expand_text('<p>Before proceeding to the next stage, make a backup of your current =game= directory by copying it into a new directory called =stage%s=.</p>\n', True) % d[1])
				fout.write(self.expand_text('<p>Continue working in your =game= directory.</p>\n', True))
				fout.write('</li>\n')
				fout.write('</ul>\n')

			# Main html files.
			elif d[0] == 'H1':
				fout.write('<h1>%s</h1>\n' % d[1])
			elif d[0] == 'H2':
				fout.write('<h2>%s</h2>\n' % d[1])
			elif d[0] == 'H3':
				fout.write('<h3>%s</h3>\n' % d[1])
			elif d[0] == 'HTML':
				fout.write('%s\n' % d[1])
			elif d[0] == 'BYLINE':
				fout.write('<p class="byline">%s</p>\n' % d[1])
			elif d[0] == 'INFO':
				fout.write('<p class="info">%s</p>\n' % self.expand_text(d[1], True))

			elif d[0] == 'BEGIN_SCREENSHOT_TABLE':
				fout.write('<div class="row">\n')
				self.set_table_columns('4')
			elif d[0] == 'SCREENSHOT_TABLE_IMAGE':
				m = re.match(r'([a-zA-Z0-9\/\-\.]+) (\d+)x(\d+) (.*)', d[1])
				if m:
					file = m.group(1)
					width = m.group(2)
					height = m.group(3)
					caption = m.group(4)
					if not os.path.exists(file):
						self.error('Screenshot image does not exist: %s' % file)
					fout.write('<div class="%s"><div class="image-table">\n' % self.image_table_class)
					fout.write('<a href="%s"><img class="screenshot-small" src="%s" width="%s" height="%s" /></a>\n' % (file, file, width, height))
					fout.write('<div class="caption"><p align="center">%s</p></div>\n' % caption)
					fout.write('</div></div>\n')
					continue
				self.error('Unknown format: SCREENSHOT_TABLE_IMAGE "%s"' % d[1])
			elif d[0] == 'END_SCREENSHOT_TABLE':
				fout.write('</div>\n')

			elif d[0] == 'BEGIN_MAIN_TABLE':
				fout.write('<table class="image-table"><tr>\n')
				self.captions = []
			elif d[0] == 'MAIN_TABLE_IMAGE':
				m = re.match(r'([a-zA-Z0-9\/\-\.]+) (\d+)x(\d+) (.*)', d[1])
				if m:
					file = m.group(1)
					width = m.group(2)
					height = m.group(3)
					caption = m.group(4)
					fout.write('<td><a href="%s" class="image-table"><img src="%s" width="%s" height="%s" /></a></td>\n' % (file, file, width, height))
					self.captions.append(caption)
					continue
				self.error('Unknown format: MAIN_TABLE_IMAGE "%s"' % d[1])
			elif d[0] == 'END_MAIN_TABLE':
				fout.write('</tr><tr>\n')
				for cap in self.captions:
					fout.write('<td><span class="code-inline">%s</span></td>\n' % cap)
				fout.write('</tr></table>\n')

			elif d[0] == 'BEGIN_LIST':
				fout.write('<ul>\n')
			elif d[0] == 'LIST_ITEM':
				fout.write('<li>%s</li>\n' % d[1])
			elif d[0] == 'END_LIST':
				fout.write('</ul>\n')

			elif d[0] == 'FOOTNOTE':
				fout.write('<hr/><p class="footnote">%s</p>\n' % d[1])
			elif d[0] == 'PRE_FILE':
				fout.write('<pre class="code">\n')
				f = open(d[1], 'r')
				for line in f:
					fout.write(line.replace('<', '&lt;'))
				fout.write('</pre>\n')

			else:
				self.error('Unknown parser command: %s %s' % (d[0], d[1]))
				fout.write('%s: %s\n' % (d[0], d[1]))

		self.print_html_footer(fout)
		fout.close()

	def print_html_header(self, fout):
		fout.write('<html>\n')
		fout.write('<head>\n')
		if self.stage == None:
			fout.write('<title>%s</title>\n' % (self.title))
		else:
			fout.write('<title>%s : %s</title>\n' % (self.id, self.title))
		fout.write('\n')

		fout.write('<link rel="stylesheet" href="%scss/bootstrap.min.css">\n' % ('../' * self.dir_depth))
		fout.write('<link type="text/css" rel="stylesheet" href="%scss/style.css" />\n' % ('../' * self.dir_depth))

		# Used for title and navbar: Trade Winds is for Adventure and Sacramento is the script font.
		fout.write("<link href='http://fonts.googleapis.com/css?family=Trade+Winds' rel='stylesheet' type='text/css'>\n")
		fout.write("<link href='http://fonts.googleapis.com/css?family=Sacramento' rel='stylesheet' type='text/css'>\n")
		# Used for headings.
		fout.write("<link href='http://fonts.googleapis.com/css?family=Piedra' rel='stylesheet' type='text/css'>\n")
		# Used for Balthazar text.
		fout.write("<link href='http://fonts.googleapis.com/css?family=Aclonica' rel='stylesheet' type='text/css'>\n")
		# No longer used.
		#fout.write("<link href='http://fonts.googleapis.com/css?family=Sigmar+One' rel='stylesheet' type='text/css'>\n")
		#fout.write("<link href='http://fonts.googleapis.com/css?family=Shanti' rel='stylesheet' type='text/css'>\n")
		#fout.write("<link href='http://fonts.googleapis.com/css?family=Abel' rel='stylesheet' type='text/css'>\n")
		#fout.write("<link href='http://fonts.googleapis.com/css?family=Philosopher:400,700,400italic,700italic' rel='stylesheet' type='text/css'>\n")
		fout.write('\n')

		fout.write('<script>\n')
		fout.write("\t(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){\n")
		fout.write("\t(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),\n")
		fout.write("\tm=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)\n")
		fout.write("\t})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');\n")
		fout.write("\tga('create', 'UA-1163903-6', 'auto');\n")
		fout.write("\tga('send', 'pageview');\n")
		fout.write('</script>\n')

		fout.write('\n')
		fout.write('</head>\n')
		fout.write('\n')
		fout.write('<body>\n')
		fout.write('<div class="navbar navbar-inverse navbar-static-top" role="navigation"><div class="container"><div class="navbar-header">\n')
		fout.write('<a class="navbar-brand" href="../index.html"><span class="title1">Adventures in</span> <span class="title2">JavaScript</span></a>\n')
		fout.write('</div></div></div>\n')
		fout.write('<div class="container">\n')

	def print_html_footer(self, fout):
		fout.write('</div>\n')
		fout.write('</body>\n')
		fout.write('</html>\n')
