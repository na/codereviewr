"""TODO: [1] Build regex with css options.""" 

"""

    pygments formatter
    
    Formatter for and only for Diff lexer
    
    Creates a table for formatting unified_diff files.  First column contains line numbers of original file
    and second column contains line numbers of the new file and the third and final column contains the compared code
    
    options: see HtmlFormatter options
        note: care needs to be taken when specifying css classes.  Currently the regexs can be broken by these option.  

	LineLinkHtmlFormatter
	Formatter for pygments syntax highlighting which adds anchor tags to the line number

"""
import StringIO
import re
from pygments.formatters import HtmlFormatter

class CodereviewerHtmlFormatter(HtmlFormatter):

    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        j=1
        yield 0, '<pre><table>'
        for i, t in source:
            if i == 1:
                b = '<tr id="line-%d"><td>' % j
                e = '</td></tr>'
                t = b+t+e
                # it's a line of formatted code
                yield i, t
                j += 1
        yield 0, '</table></pre>'

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
                             (i%sp == 0 and '<a name="%s-%d" class="special">%*d</a>'
                              or '<a name="%s-%d">%*d</a>') % (la, i, mw, i)
                             or '')
                            for i in range(fl, fl + lncount)])
        else: 
            ls = '\n'.join([(i%st == 0 and ('<a name="%s-%d">%*d</a>' % (la, i, mw, i)) or '') # added </a><a href=#>
                            for i in range(fl, fl + lncount)])
            #ls = ''
            #for i in range (fl, fl+ lncount):
            #	ls = ls + '<a href=%s-%d>%d</a>\n' % (la,i,i) 
        yield 0, ('<table class="%stable">' % self.cssclass +
                  '<tr><td class="linenos"><pre>' + 
                  ls + '</pre></td><td class="code">')
        yield 0, dummyoutfile.getvalue()
        yield 0, '</td></tr></table>'

class DiffHtmlFormatter(HtmlFormatter):
    def wrap(self, source, outfile):
        return self._tablize(source)
    
    def _tablize(self, inner):
        i = 0
        yield 0, ('<table'+ (self.cssclass and ' class="%s"' % self.cssclass)
             + (self.cssstyles and ' style="%s"' % self.cssstyles) + '><colgroup><col class="lineno" /><col class="lineno" /><col class="codecontent" /></colgroup><thead>')
        for t, line in inner:
            #the first two lines are details about the two things compared
            if i == 0:
                yield 0, '<tr><th>'
                yield t, line.replace('---','') 
                yield 0, '</th>'
            elif i == 1:
                yield 0,'<th>'
                yield t, line.replace('+++','')
                yield 0, '</th><th></th><tr></thead><tbody>'
            else:   
                #check if it is an info line about the diffs
                """[1]"""       
                regex = '(?<=^<span\sclass="..">@@\s-)\d+,\d+|\d+,\d+(?=\s@@</span>$)' # does the line look like <span class="gu">@@ -8,3 +7,3 @@</span> 
                lineinfo = re.findall(regex,line) #get the details, i.e. -8,3 +7,3 where 8=line number of original and 3=number of lines and 7=line number of sugg. and 3=number of lines
                
                if len(lineinfo) == 2:#this line is an info line, process line number info
                    parentlineno = int(lineinfo[0].split(',')[0])
                    parentnumlines = int(lineinfo[0].split(',')[1])
                    childlineno = int(lineinfo[0].split(',')[0])
                    childnumlines = int(lineinfo[1].split(',')[1])
                    if i != 2:
                        yield 0 , '<tr><th>&hellip;</th><th>&hellip;</th><td></td</tr>>'
                        parentlineno -= 1
                        childlineno -= 1
                else:
                    regex = '(?<=^<span class="..">)-\+|(?<=^<span class="..">)-|(?<=^<span class="..">)\+' #check for a minus or plus
                    compinfo = re.findall(regex,line)
                    if len(compinfo) == 0 or (len(compinfo)==1 and compinfo[0] == '-+'): # non changed line
                        yield 0, '<tr><th>%s</th><th>%s</th><td>' % (str(parentlineno), str(childlineno))
                        yield t, line.replace('  ','&nbsp; &nbsp; ')
                        yield 0, '</td></tr>'
                        parentlineno += 1
                        childlineno += 1
                    elif compinfo[0]=='-':#line is a deletion from original code
                        yield 0, '<tr><th>%s</th><th></th><td>' % str(parentlineno)
                        yield t, line.replace('  ','&nbsp; &nbsp; ')
                        yield 0,'</td></tr>'
                        parentlineno += 1
                    elif compinfo[0]=='+':
                        yield 0, '<tr><th></th><th>%s</th><td>' % str(childlineno)
                        yield t, line.replace('  ','&nbsp; &nbsp; ')
                        yield 0,'</td></tr>'
                        childlineno += 1
                        
            i += 1
        yield 0, '</tbody></table>'
