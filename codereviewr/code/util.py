from pygments.formatters import HtmlFormatter
import StringIO
"""
	LineLinkHtmlFormatter
	Formatter for pygments syntax highlighting which adds anchor tags to the line number
"""
class LineLinkHtmlFormatter(HtmlFormatter):
		"""override to include anchor tags around the line numbers"""
		def _wrap_tablelinenos(self, inner):
			dummyoutfile = StringIO.StringIO()
			lncount = 0
			for t, line in inner:
				if t:
					lncount += 1
				dummyoutfile.write(line)

			fl = self.linenostart
			mw = len(str(lncount + fl - 1))
			sp = self.linenospecial
			st = self.linenostep
			la = self.lineanchors
			if sp:
				ls = '\n'.join([(i%st == 0 and
								 (i%sp == 0 and '<a href=#%s-%d class="special">%*d</a>'
								  or '<a href=#%s-%d>%*d</a>') % (la, i, mw, i)
								 or '')
								for i in range(fl, fl + lncount)])
			else: 
				ls = '\n'.join([(i%st == 0 and ('<a href=#%s-%d>%*d</a>' % (la, i, mw, i)) or '') # added </a><a href=#>
								for i in range(fl, fl + lncount)])
				#ls = ''
				#for i in range (fl, fl+ lncount):
				#	ls = ls + '<a href=%s-%d>%d</a>\n' % (la,i,i) 
			yield 0, ('<table class="%stable">' % self.cssclass +
					  '<tr><td class="linenos"><pre>' + 
					  ls + '</pre></td><td class="code">')
			yield 0, dummyoutfile.getvalue()
			yield 0, '</td></tr></table>'