"""TODO: [1] Build regex with css options.""" 
"""
    pygments formatter
    
    Formatter for and only for Diff lexer
    
    Creates a table for formatting unified_diff files.  First column contains line numbers of original file
    and second column contains line numbers of the new file and the third and final column contains the compared code
    
    options: see HtmlFormatter options
        note: care needs to be taken when specifying css classes.  Currently the regexs can be broken by these option.  
"""
import re
from pygments.formatters import HtmlFormatter

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
""" def __init__(self, **options):
        HtmlFormatter.__init__(self, **options)
        
    def format(self, tokensource, outfile):
   
        source = self._format_lines(tokensource)
        if not self.nowrap:
            if self.linenos == 2:
                source = self._wrap_inlinelinenos(source)
            if self.lineanchors:
                source = self._wrap_lineanchors(source)
            source = self.wrap(source, outfile)
            if self.linenos == 1:
                source = self._wrap_tablelinenos(source)
            if self.full:
                source = self._wrap_full(source, outfile)

        for t, piece in source:
            if piece[1:5]=='span':
                outfile.write('delete')
                outfile.write(piece)
            else:
                outfile.write(piece)
    """