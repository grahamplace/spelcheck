import pygments
import pygments.lexers
import pygments.formatters


class Highlighter(object):

    def __init__(self, style='monokai'):
        self._lexer = pygments.lexers.get_lexer_by_name('python3')
        self._formatter = pygments.formatters.get_formatter_by_name('terminal256', style=style)

    def highlight(self, source):
        return pygments.highlight(source, self._lexer, self._formatter)

    def get_tokens(self, source):
        return list(self._lexer.get_tokens_unprocessed(source))
