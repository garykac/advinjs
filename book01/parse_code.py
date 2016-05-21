import os
import re
import shutil

class Parse_Code(object):
	def __init__(self, parser, modename, options):
		self.parser = parser
		self.modename = modename
		self.options = options

		self.begin_code = 'BEGIN_CODE'
		self.begin_code_info = ''
		
		self.debug = options['debug']
		self.verify = options['verify']
		
		self.prefix = set(['.', '+', '>', '-'])
		self.lines = []

	def match_toplevel(self, line):
		p = self.parser		
		if re.match('BEGIN_CODE', line):
			self.begin_code = 'BEGIN_CODE'
			self.begin_code_info = ''
			if re.match('BEGIN_CODE_INFO', line):
				self.begin_code = 'BEGIN_CODE_INFO'
				self.begin_code_info = line[16:]
			elif line != 'BEGIN_CODE':
				p.error('Unrecognized BEGIN_CODE line: %s' % line)
			return True
		return False

	def start_parse_mode(self):
		p = self.parser		
		p.enter_mode(self.modename)
		self.lines = []
		return True

	def parse_line(self, line):
		p = self.parser
		end_code = ''
		end_code_info = ''
		if re.match('END_CODE', line):
			end_code = 'END_CODE'
			if re.match('END_CODE_OK', line):
				end_code = 'END_CODE_OK'
			elif re.match('END_CODE_ERROR', line):
				end_code = 'END_CODE_ERROR'
				end_code_info = line[15:]
			elif line != 'END_CODE':
				p.error('Unrecognized END_CODE line: %s' % line)
			
		if end_code != '':
			if self.verify:
				self.process_code()
			p.add_data(self.begin_code, self.begin_code_info)
			p.add_data('CODE', self.lines)
			p.add_data(end_code, end_code_info)
			p.exit_mode(self.modename)
			return True
		
		first = line[0]
		if not first in self.prefix:
			p.error('Unexpected code: %s' % line)
		self.lines.append(line)
		return True

	## Private
	
	def function_signature_match(self, line, line_pattern):
		m1 = re.match(r'function (.+)\(.*\) {', line)
		m2 = re.match(r'function (.+)\(\.\.\.\) {', line_pattern)
		if m1 and m2:
			if self.debug:
				print m1.group(1)
			return m1.group(1) == m2.group(1)
		return False
	
	def process_code(self):
		p = self.parser

		source_file = os.path.join('snapshots', p.stage, p.name, 'script.js')
		if not os.path.isfile(source_file):
			p.error('File "%s" doesn\'t exist' % source_file)
		try:
			fin = open(source_file, 'r')
		except IOError as e:
			p.error('Unable to open "%s": %s' % (fin, e))

		dst_file = os.path.join('snapshots', p.stage, p.name, 'script2.js')
		try:
			fout = open(dst_file, 'w')
		except IOError as e:
			p.error('Unable to open "%s" for writing: %s' % (fin, e))

		first_mode = self.lines[0][0]
		if first_mode != '.' and first_mode != '-':
			p.error('First line mode must be . or -: %s' % first_mode)
			
		match_index = 0;
		match_mode = 'search'
		for line in fin:
			line = line.rstrip()

			if match_index >= len(self.lines):
				match_mode = 'done'
			
			if match_mode == 'done':
				fout.write('%s\n' % line)
			else:
				match_line = self.lines[match_index][1:]

				if self.debug and match_mode != 'search':
					print 'mode', match_mode
					print '      line:', line
					print 'match_line:', match_line

				line_match_mode = self.lines[match_index][0]
				if match_mode == 'search':
					if line == match_line:
						match_mode = 'match'
						match_index += 1
						if self.debug:
							print 'mode -> match'
							print line
						if line_match_mode == '.':
							fout.write('%s\n' % line)
					elif self.function_signature_match(line, match_line):
						# Check for '...' in function parameters
						match_mode = 'match'
						match_index += 1
						if self.debug:
							print 'match f(...)'
						fout.write('%s\n' % line)
					else:
						fout.write('%s\n' % line)
				elif match_mode == 'match':
					while line_match_mode == '+' and not match_mode == 'done':
						# Inserting lines
						fout.write('%s\n' % match_line)
						if self.debug:
							print 'inserting:', match_line
						match_index += 1
						if match_index < len(self.lines):
							match_line = self.lines[match_index][1:]
							line_match_mode = self.lines[match_index][0]
						else:
							match_mode = 'done'
					if match_mode == 'done':
						fout.write('%s\n' % line)
						if self.debug:
							print 'writing umatched:', line
						continue
					if line_match_mode == '-':
						# Deleting line
						if line.lstrip() != match_line.lstrip():
							print 'Delete doesn\'t match'
							print ' found: "%s"' % line
							print 'expect: "%s"' % match_line
							p.error('Delete mismatch')
						match_index += 1
						if self.debug:
							print 'deleting:', match_line
					if line_match_mode == '>':
						# Changing indent
						if line.lstrip() != match_line.lstrip():
							print 'No indent match'
							print 'line1: "%s"' % line
							print 'line2: "%s"' % match_line
							p.error('Partial match')
						fout.write('%s\n' % match_line)
						match_index += 1
						if self.debug:
							print 'matching indent:', match_line
					if line_match_mode == '.':
						if re.match(r'\t+\.\.\.', match_line):
							match_mode = 'skip'
							if self.debug:
								print 'mode -> skip'
						elif line != match_line:
							print 'No more match'
							print 'line1: "%s"' % line
							print 'line2: "%s"' % match_line
							p.error('Partial match')
						fout.write('%s\n' % line)
						match_index += 1
						if self.debug:
							print 'matching:', line
				elif match_mode == 'skip':
					write_line = True
					if line == match_line:
						match_mode = 'match'
						if line_match_mode == '-':
							write_line = False
							if self.debug:
								print 'deleting:', match_line
						if self.debug:
							print 'mode -> match'
						match_index += 1
					if write_line:
						fout.write('%s\n' % line)
					
		
		fin.close()
		fout.close()
		
		if self.debug:
			print 'completed match'

		if match_mode != 'done':
			print self.lines
			p.error('Failed to match')
				
		# Replace original file with new one.
		shutil.move(dst_file, source_file)
