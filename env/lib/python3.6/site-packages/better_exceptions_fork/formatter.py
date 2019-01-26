from __future__ import absolute_import

import distutils.sysconfig
import inspect
import linecache
import os
import platform
import re
import site
import sys
import sysconfig
import traceback

import ansimarkup
from pygments.token import Token

from .color import SUPPORTS_COLOR
from .highlighter import Highlighter
from .repl import get_repl


PY3 = sys.version_info[0] >= 3

THEME = {
    'introduction': u'<y><b>{introduction}</b></y>',
    'cause': u'<b>{cause}</b>',
    'context': u'<b>{context}</b>',
    'location': u'  File "<g>{dirname}<b>{basename}</b></g>", line <y>{lineno}</y>, in <m>{source}</m>',
    'short_location': u'  File "<g>{dirname}<b>{basename}</b></g>", line <y>{lineno}</y>',
    'exception': u'<r><b>{type_}</b></r>:<b>{value}</b>',
    'inspect': u'    <c>{pipes}{cap} <b>{value}</b></c>',
}

MAX_LENGTH = 128


class ExceptionFormatter(object):

    CMDLINE_REGXP = re.compile(r'(?:[^\t ]*([\'"])(?:\\.|.)*(?:\1))[^\t ]*|([^\t ]+)')

    def __init__(self, colored=SUPPORTS_COLOR, theme=THEME, max_length=MAX_LENGTH, encoding=None):
        self._colored = colored
        self._theme = theme
        self._max_length = max_length
        self._encoding = encoding or 'ascii'
        self._pipe_char = self.get_pipe_char()
        self._cap_char =  self.get_cap_char()
        self._introduction = u'Traceback (most recent call last):'
        self._cause = getattr(traceback, '_cause_message', u"The above exception was the direct cause of the following exception:").strip()
        self._context = getattr(traceback, '_context_message', u"During handling of the above exception, another exception occurred:").strip()
        self._lib_dirs = self.get_lib_dirs()
        self._highlighter = Highlighter()

    def _get_char(self, value, default):
        try:
            value.encode(self._encoding)
        except UnicodeEncodeError:
            return default
        else:
            return value

    def get_pipe_char(self):
        return self._get_char(u'\u2502', u'|')

    def get_cap_char(self):
        return self._get_char(u'\u2514', u'->')

    def get_lib_dirs(self):
        # https://github.com/sametmax/devpy/blob/66a150817644edf825d19b80f644e7d05b2a3e86/src/devpy/tb.py#L10
        # https://stackoverflow.com/questions/122327/how-do-i-find-the-location-of-my-python-site-packages-directory/122340
        lib_dirs = [sysconfig.get_path('stdlib'), site.USER_SITE, distutils.sysconfig.get_python_lib()]
        if hasattr(sys, 'real_prefix'):
            lib_dirs.append(sys.prefix)
            lib_dirs.append(sysconfig.get_path('stdlib').replace(sys.prefix, sys.real_prefix))
        if hasattr(sys, 'getsitepackages'):
            lib_dirs += site.getsitepackages()
        return [os.path.abspath(d) for d in lib_dirs]

    def get_relevant_names(self, source):
        source = self.sanitize(source)
        tokens = self._highlighter.get_tokens(source)
        names = []

        name = ''
        for index, tokentype, value in tokens:
            if tokentype in Token.Name:
                name += value
                names.append((index, name))
            elif tokentype in Token.Operator and value == '.':
                name += '.'
            elif tokentype not in Token.Text:
                name = ''

        return names

    def get_relevant_values(self, source, frame):
        names = self.get_relevant_names(source)
        values = []

        for index, name in names:
            vals = name.split('.')
            identifier, attrs = vals[0], vals[1:]
            for variables in (frame.f_locals, frame.f_globals, frame.f_builtins):
                try:
                    val = variables[identifier]
                except KeyError:
                    continue

                try:
                    for attr in attrs:
                        val = getattr(val, attr)
                except Exception:  # @property could raise an error as side effect
                    pass
                else:
                    values.append((index, self.format_value(val)))

                break

        values.sort()
        return values

    def format_value(self, v):
        try:
            v = repr(v)
        except Exception:
            v = u'<unprintable %s object>' % type(v).__name__

        max_length = self._max_length
        if max_length is not None and len(v) > max_length:
            v = v[:max_length] + u'...'
        return v

    def split_cmdline(self, cmdline):
        return [m.group(0) for m in self.CMDLINE_REGXP.finditer(cmdline)]

    def get_string_source(self):
        cmdline = None
        if platform.system() == 'Windows':
            # TODO use winapi to obtain the command line
            return u''
        elif platform.system() == 'Linux':
            # TODO try to use proc
            pass

        if cmdline is None and os.name == 'posix':
            from subprocess import CalledProcessError, check_output as spawn

            try:
                cmdline = spawn(['ps', '-ww', '-p', str(os.getpid()), '-o', 'command='])
            except CalledProcessError:
                return u''

            if (PY3 and isinstance(cmdline, bytes)) or (not PY3 and isinstance(cmdline, str)):
                cmdline = cmdline.decode(sys.stdout.encoding or 'utf-8')
        else:
            # current system doesn't have a way to get the command line
            return u''

        cmdline = cmdline.strip()
        cmdline = self.split_cmdline(cmdline)

        extra_args = sys.argv[1:]
        if len(extra_args) > 0:
            if cmdline[-len(extra_args):] != extra_args:
                # we can't rely on the output to be correct; fail!
                return u''

            cmdline = cmdline[1:-len(extra_args)]

        skip = 0
        for i in range(len(cmdline)):
            a = cmdline[i].strip()
            if not a.startswith('-c'):
                skip += 1
            else:
                a = a[2:].strip()
                if len(a) > 0:
                    cmdline[i] = a
                else:
                    skip += 1
                break

        cmdline = cmdline[skip:]
        source = u' '.join(cmdline)

        return source

    def colorize(self, template, **kwargs):
        template = self._theme[template]
        if not self._colored:
            template = ansimarkup.strip(template)
        else:
            template = ansimarkup.parse(template)

        return template.format(**kwargs)

    def colorize_location(self, filepath, lineno, source=None):
        dirname, basename = os.path.split(filepath)
        if dirname:
            dirname += os.sep

        if source is None:
            template = 'short_location'
        else:
            template = 'location'

        return self.colorize(template, dirname=dirname, basename=basename, lineno=lineno, source=source)

    def colorize_traceback(self, full_traceback):
        pipe = re.escape(self._pipe_char)
        cap = re.escape(self._cap_char)
        reg = re.compile(u'^(?P<location>  File "(?P<filepath>.*?)", line (?P<lineno>(?:\\d+|\\?))(?:, in (?P<source>.*))?)\\n'
                         u'((?P<code>    .*\\n(?:\\s*\\^)?)'
                         u'(?P<inspect>(?:    [\\s(?:{pipe})]*(?:{cap})? .*\\n)*))?'.format(pipe=pipe, cap=cap),
                         flags=re.M)

        local = {}
        def sub(match):
            dct = match.groupdict()
            location = dct['location']
            filepath, lineno, source = dct['filepath'], dct['lineno'], dct['source']
            code, inspect = dct['code'], dct['inspect']

            if code is None:
                code = u''
            if inspect is None:
                inspect = u''

            if local:
                init = False
                is_previous_mine = local['is_previous_mine']
            else:
                init = True
                is_previous_mine = True

            is_mine = self.is_file_mine(filepath)
            if is_mine is None:
                is_mine = is_previous_mine

            if is_mine:
                location = self.colorize_location(filepath=filepath, lineno=lineno, source=source)
                if code:
                    code = self.colorize_source(code)
                if inspect:
                    reg_inspect = u'^    (?P<pipes>[\\s(?:{pipe})]*)(?P<cap>{cap})? (?P<value>.*)$'.format(pipe=pipe, cap=cap)
                    sub_inspect = lambda m: self.colorize('inspect', pipes=m.group('pipes'), cap=m.group('cap') or '', value=m.group('value'))
                    inspect = re.sub(reg_inspect, sub_inspect, inspect, flags=re.M)

            if (is_mine or is_previous_mine) and not init:
                location = u'\n' + location

            local['is_previous_mine'] = is_mine

            return u"{}\n{}{}".format(location, code, inspect)

        return reg.sub(sub, full_traceback)

    def colorize_source(self, source):
        if not self._colored:
            return source
        return self._highlighter.highlight(source)

    def is_file_mine(self, filepath):
        if filepath == "<string>":
            return None
        filepath = os.path.abspath(filepath)
        if not os.path.isfile(filepath):
            return False
        return not any(filepath.lower().startswith(d.lower()) for d in self._lib_dirs)

    def get_traceback_information(self, tb):
        lineno = tb.tb_lineno
        filename = tb.tb_frame.f_code.co_filename
        function = tb.tb_frame.f_code.co_name

        repl = get_repl()
        if repl is not None and filename in repl.entries:
            _, filename, source = repl.entries[filename]
            source = source.replace('\r\n', '\n').split('\n')[lineno - 1]
        elif filename == '<string>':
            source = self.get_string_source()
        else:
            source = linecache.getline(filename, lineno)
            if not PY3 and isinstance(source, str):
                source = source.decode('utf-8')

        source = source.strip()

        relevant_values = self.get_relevant_values(source, tb.tb_frame)

        return filename, lineno, function, source, relevant_values

    def format_traceback_frame(self, tb):
        traceback_information = self.get_traceback_information(tb)
        filename, lineno, function, source, relevant_values = traceback_information
        pipe_char, cap_char = self._pipe_char, self._cap_char

        lines = [source]
        for i in reversed(range(len(relevant_values))):
            col, val = relevant_values[i]
            pipe_cols = [pcol for pcol, _ in relevant_values[:i]]
            line = u''
            index = 0

            for pc in pipe_cols:
                line += (u' ' * (pc - index)) + pipe_char
                index = pc + 1

            line += u' ' * (col - index)
            val_lines = val.split(u'\n')
            first, others = val_lines[0], val_lines[1:]
            lines.append(line + cap_char + u' ' + first)
            preline = line + u' ' * (len(cap_char) + 1)
            for other in others:
                lines.append(preline + other)

        formatted = u'\n    '.join(lines)

        return (filename, lineno, function, formatted), source

    def format_traceback(self, tb=None):
        omit_last = False
        if not tb:
            try:
                raise Exception()
            except Exception:
                omit_last = True
                _, _, tb = sys.exc_info()
                assert tb is not None

        frames = []
        final_source = u''
        while tb:
            if omit_last and not tb.tb_next:
                break

            formatted, source = self.format_traceback_frame(tb)

            # special case to ignore runcode() here.
            if not (os.path.basename(formatted[0]) == 'code.py' and formatted[2] == 'runcode'):
                final_source = source
                frames.append(formatted)

            tb = tb.tb_next

        lines = traceback.format_list(frames)

        return u''.join(lines), final_source

    def sanitize(self, string):
        encoding = self._encoding
        return string.encode(encoding, errors='backslashreplace').decode(encoding)

    def format_exception(self, exc, value, tb, _seen=None):
        if _seen is None:
            _seen = {None}

        exc = type(value)
        _seen.add(value)

        if value:
            if getattr(value, '__cause__', None) not in _seen:
                for text in self.format_exception(type(value.__cause__),
                                                  value.__cause__,
                                                  value.__cause__.__traceback__,
                                                  _seen=_seen):
                    yield text
                yield u'\n\n' + self.colorize('cause', cause=self._cause) + u'\n\n\n'
            elif getattr(value, '__context__', None) not in _seen and not getattr(value, '__suppress_context__', True):
                for text in self.format_exception(type(value.__context__),
                                                  value.__context__,
                                                  value.__context__.__traceback__,
                                                  _seen=_seen):
                    yield text
                yield u'\n\n' + self.colorize('context', context=self._context) + u'\n\n\n'

        if tb is not None:
            # Print it from start so user have a clue if something goes wrong during formatting
            yield self.colorize('introduction', introduction=self._introduction) + u'\n\n'

        formatted, source = self.format_traceback(tb)
        if formatted:
            formatted += u'\n'

        if not str(value) and exc is AssertionError:
            colored_source = self.colorize_source(source)
            value.args = (colored_source,)
        exception_only = traceback.format_exception_only(exc, value)

        if exception_only and ':' in exception_only[-1]:
            type_, value = exception_only[-1].split(':', 1)
            exception_only[-1] = self.colorize('exception', type_=type_, value=value)

        full_traceback = formatted + u''.join(exception_only)
        full_traceback = self.colorize_traceback(full_traceback)

        yield self.sanitize(full_traceback)
