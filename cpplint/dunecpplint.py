#!/bin/env python
"""DUNE-specific overrides layered on top of vendored upstream cpplint.

This module loads the sibling vendored ``cpplint.py`` directly and overrides
only the DUNE-specific behavior while re-exporting the upstream API.
"""

import re
import importlib.util
from pathlib import Path

_CPPLINT_PATH = Path(__file__).resolve().with_name('cpplint.py')
_CPPLINT_SPEC = importlib.util.spec_from_file_location('dune_vendored_cpplint', _CPPLINT_PATH)
if _CPPLINT_SPEC is None or _CPPLINT_SPEC.loader is None:
  raise ImportError('Unable to load vendored cpplint.py at %s' % (_CPPLINT_PATH,))
_upstream_cpplint = importlib.util.module_from_spec(_CPPLINT_SPEC)
_CPPLINT_SPEC.loader.exec_module(_upstream_cpplint)

# Re-export upstream symbols so existing dunecpplint imports keep working.
for _name in dir(_upstream_cpplint):
  if not _name.startswith('__'):
    globals()[_name] = getattr(_upstream_cpplint, _name)

_RE_PATTERN_INCLUDE = re.compile(r'^\s*#\s*include\s*([<"])([^>"]*)[>"].*$')

_USAGE = """
Usage: dunecpplint.py [--verbose=#] [--output=vs7] [--filter=-x,+y,...]
                   [--counting=total|toplevel|detailed] [--root=subdir]
                   [--linelength=digits] [--headers=x,y,...]
                   [--quiet]
        <file> [file] ...

  You probably don't want to call this script directly but rather dunecpplint.sh

  The style guidelines this tries to follow are those in
    https://dune-daq-sw.readthedocs.io/en/latest/packages/styleguide/

JCF, Apr-3-2020: I can't vouch (yet) for anything below this line:
======================================================================
  Every problem is given a confidence score from 1-5, with 5 meaning we are
  certain of the problem, and 1 meaning it could be a legitimate construct.
  This will miss some errors, and is not a substitute for a code review.

  To suppress false-positive errors of a certain category, add a
  'NOLINT(category)' comment to the line.  NOLINT or NOLINT(*)
  suppresses errors of all categories on that line.

  The files passed in will be linted; at least one file must be provided.
  Default linted extensions are .cc, .cpp, .cu, .cuh and .h.  Change the
  extensions with the --extensions flag.

  Flags:

    output=vs7
      By default, the output is formatted to ease emacs parsing.  Visual Studio
      compatible output (vs7) may also be used.  Other formats are unsupported.

    verbose=#
      Specify a number 0-5 to restrict errors to certain verbosity levels.

    quiet
      Don't print anything if no errors are found.

    filter=-x,+y,...
      Specify a comma-separated list of category-filters to apply: only
      error messages whose category names pass the filters will be printed.
      (Category names are printed with the message and look like
      "[whitespace/indent]".)  Filters are evaluated left to right.
      "-FOO" and "FOO" means "do not print categories that start with FOO".
      "+FOO" means "do print categories that start with FOO".

      Examples: --filter=-whitespace,+whitespace/braces
                --filter=-,+build/include_what_you_use

      To see a list of all the categories used in cpplint, pass no arg:
         --filter=

    counting=total|toplevel|detailed
      The total number of errors found is always printed. If
      'toplevel' is provided, then the count of errors in each of
      the top-level categories like 'build' and 'whitespace' will
      also be printed. If 'detailed' is provided, then a count
      is provided for each category like 'build/class'.

    root=subdir
      The root directory used for deriving header guard CPP variable.
      By default, the header guard CPP variable is calculated as the relative
      path to the directory that contains .git, .hg, or .svn.  When this flag
      is specified, the relative path is calculated from the specified
      directory. If the specified directory does not exist, this flag is
      ignored.

      Examples:
        Assuming that top/src/.git exists (and cwd=top/src), the header guard
        CPP variables for top/src/chrome/browser/ui/browser.h are:

        No flag => CHROME_BROWSER_UI_BROWSER_H_
        --root=chrome => BROWSER_UI_BROWSER_H_
        --root=chrome/browser => UI_BROWSER_H_
        --root=.. => SRC_CHROME_BROWSER_UI_BROWSER_H_

    linelength=digits
      This is the allowed line length for the project. The default value is
      80 characters.

      Examples:
        --linelength=120

    extensions=extension,extension,...
      The allowed file extensions that cpplint will check

      Examples:
        --extensions=hpp,cpp

    headers=x,y,...
      The header extensions that cpplint will treat as .h in checks. Values are
      automatically added to --extensions list.

      Examples:
        --headers=hpp,hxx
        --headers=hpp

    cpplint.py supports per-directory configurations specified in CPPLINT.cfg
    files. CPPLINT.cfg file can contain a number of key=value pairs.
    Currently the following options are supported:

      set noparent
      filter=+filter1,-filter2,...
      exclude_files=regex
      linelength=80
      root=subdir
      headers=x,y,...

    "set noparent" option prevents cpplint from traversing directory tree
    upwards looking for more .cfg files in parent directories. This option
    is usually placed in the top-level project directory.

    The "filter" option is similar in function to --filter flag. It specifies
    message filters in addition to the |_DEFAULT_FILTERS| and those specified
    through --filter command-line flag.

    "exclude_files" allows to specify a regular expression to be matched against
    a file name. If the expression matches, the file is skipped and not run
    through liner.

    "linelength" allows to specify the allowed line length for the project.

    The "root" option is similar in function to the --root flag (see example
    above). Paths are relative to the directory of the CPPLINT.cfg.

    The "headers" option is similar in function to the --headers flag
    (see example above).

    CPPLINT.cfg has an effect on files in the same directory and all
    sub-directories, unless overridden by a nested configuration file.

      Example file:
        filter=-build/include_order,+build/include_alpha
        exclude_files=.*[BACKSLASH CHARACTER].cc

    The above example disables build/include_order warning and enables
    build/include_alpha as well as excludes all .cc from being
    processed by linter, in the current directory (where the .cfg
    file is located) and all sub-directories.
"""
_upstream_cpplint._USAGE = _USAGE

def PrintUsage(message):
  """Prints a brief usage string and exits, optionally with an error message.

  Args:
    message: The optional error message.
  """
  sys.stderr.write(_USAGE)
  if message:
    sys.exit('\nFATAL ERROR: ' + message)
  else:
    sys.exit(1)

def CheckForCopyright(filename, lines, error):
  """Logs an error if no Copyright message appears at the top of the file."""

  # We'll say it should occur by line 30. Don't forget there's a
  # dummy line at the front.

  maxline=30
  matching_lines=0

  # Try looking for something like this:
  #
  # * This is part of the DUNE DAQ Application Framework, copyright 2020.
  # * Licensing/copyright details are in the COPYING file that you should have received with this code.
  #
  # ...while allowing users to choose where to perform line breaks.

  line1="* This is part of the DUNE DAQ"
  line2="this code."
  for line in xrange(1, min(len(lines), maxline)):
    if line1 in lines[line]:
      matching_lines += 1
    elif line2 in lines[line]:
      matching_lines +=1

    if matching_lines == 2:
      break

  if matching_lines != 2:
    error(filename, 0, 'legal/copyright', 5,
          'The standard copyright message wasn\'t found.')
def CheckForNonStandardConstructs(filename, clean_lines, linenum, *args):
  r"""Logs an error if we see certain non-ANSI constructs ignored by gcc-2.

  Complain about several constructs which gcc-2 accepts, but which are
  not standard C++.  Warning about these in lint is one way to ease the
  transition to new compilers.
  - put storage class first (e.g. "static const" instead of "const static").
  - "\%" is an undefined character escape sequence.
  - text after #endif is not allowed.
  - invalid inner-style forward declaration.
  - >? and <? operators, and their >?= and <?= cousins.
  - don't use a #define outside of the context of a header guard

  Additionally, check for constructor/destructor style violations and reference
  members, as it is very convenient to do so while checking for
  gcc-2 compliance.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    args: Either ``(nesting_state, error)`` for newer upstream cpplint or
          ``(function_state, nesting_state, error)`` for older versions.
    error: A callable to which errors are reported, which takes 4 arguments:
           filename, line number, error level, and message
  """
  if len(args) == 2:
    function_state = None
    nesting_state, error = args
  elif len(args) == 3:
    function_state, nesting_state, error = args
  else:
    raise TypeError('CheckForNonStandardConstructs expected 2 or 3 trailing arguments, got %d' % (len(args),))

  # Remove comments from the line, but leave in strings for now.
  line = clean_lines.lines[linenum]

  for output_token in ["printf", "cout", "cerr"]:
    if Search(r'[\s:]%s[ .<(]' % (output_token), line):
      error(filename, linenum, 'runtime/output_format', 3,
            '\"%s\" should not be used for output in DUNE DAQ software.' % (output_token))

  # Remove escaped backslashes before looking for undefined escapes.
  line = line.replace('\\\\', '')

  if Search(r'^\s*#define\s+\S+\s+\S+', line):
    if not "TRACE_" in line:
      error(filename, linenum, 'build/define_used', 3,
            '#define appears to be used. Macros should generally be avoided if there\'s an alternative to them.')

  # For the rest, work with both comments and strings removed.
  line = clean_lines.elided[linenum]

  if Search(r'\b(const|volatile|void|char|short|int|long'
            r'|float|double|signed|unsigned'
            r'|schar|u?int8|u?int16|u?int32|u?int64)'
            r'\s+(register|static|extern|typedef)\b',
            line):
    error(filename, linenum, 'build/storage_class', 5,
          'Storage-class specifier (static, extern, typedef, etc) should be '
          'at the beginning of the declaration.')

  if Match(r'\s*#\s*endif\s*[^/\s]+', line):
    error(filename, linenum, 'build/endif_comment', 5,
          'Uncommented text after #endif is non-standard.  Use a comment.')

  if Match(r'\s*class\s+(\w+\s*::\s*)+\w+\s*;', line):
    error(filename, linenum, 'build/forward_decl', 5,
          'Inner-style forward declarations are invalid.  Remove this line.')

  if Search(r'(\w+|[+-]?\d+(\.\d*)?)\s*(<|>)\?=?\s*(\w+|[+-]?\d+)(\.\d*)?',
            line):
    error(filename, linenum, 'build/deprecated', 3,
          '>? and <? (max and min) operators are non-standard and deprecated.')

  if Search(r'^\s*const\s*string\s*&\s*\w+\s*;', line):
    # TODO(unknown): Could it be expanded safely to arbitrary references,
    # without triggering too many false positives? The first
    # attempt triggered 5 warnings for mostly benign code in the regtest, hence
    # the restriction.
    # Here's the original regexp, for the reference:
    # type_name = r'\w+((\s*::\s*\w+)|(\s*<\s*\w+?\s*>))?'
    # r'\s*const\s*' + type_name + '\s*&\s*\w+\s*;'
    error(filename, linenum, 'runtime/member_string_references', 2,
          'const string& members are dangerous. It is much better to use '
          'alternatives, such as pointers or simple constants.')

  if Search(r'typeid\s*\(', line) or Search(r'dynamic_cast', line):
    error(filename, linenum, 'runtime/rtti', 5,
          'Use of Run Time Type Information not allowed unless this code is meant to test other code' )

  if Search(r'[^a-zA-Z]NULL[^a-zA-Z]', line):
    error(filename, linenum, 'build/null_usage', 5, 
          'Use of NULL #define found; prefer using the nullptr keyword')

  if Search(r'[^\w]delete\s+', line) or Search(r'^delete\s+', line):
    error(filename, linenum, 'build/raw_ownership', 5,
          'The delete operator appears to be used; owning memory should be done with a smart pointer rather than a raw pointer' )

  if Search(r'catch\s*\(', line):
    if Search(r'catch\s*\(\s*\.\.\.\s*\)', line):
      with open(filename) as inf:
        if not Search(r"int\s+main", inf.read()):
          error(filename, linenum, 'runtime/exceptions', 5,
                'A catch-all-exceptions construct was found in a file which doesn\'t contain int main(); this can only be used to wrap main()' )
    elif not Search(r'catch\s*\(.*&.*\)', line):
      error(filename, linenum, 'runtime/exceptions', 5,
        'An exception appears to be getting caught here, but not via a reference. ' )
    
  if Search(r'(\+\+|\-\-)\w', line) and not Search(r'^\s*(\+\+|\-\-)[\w\[\]0-9\.]+[\s;){]*$', line) and \
      not Search(r'(for|while)\s*\(.*(\+\+|\-\-)\w.*\)', line):
    error(filename, linenum, 'runtime/increment_decrement', 5,
          'Increment/decrement operator should appear alone on its line unless in a while/for loop head')

  if Search(r'[\w\[\]0-9\.]+(\+\+|\-\-)', line) and not Search(r'^\s*[\w\[\]0-9\.]+(\+\+|\-\-)[\s;){]*$', line) and \
      not Search(r'(for|while)\s*\(.*[\w\[\]0-9\.]+(\+\+|\-\-).*\)', line):
    error(filename, linenum, 'runtime/increment_decrement', 5,
          'Increment/decrement operator should appear alone on its line unless in a while/for loop head')

  if Search(r'\s+unsigned\+', line) or Search(r'^unsigned\+', line) or Search(r'uint[0-9]+', line):
    error(filename, linenum, 'build/unsigned', 3,
          'An unsigned integer appears to be used here.')

  if Search(r'^\s*#include\s+.*\.\.?/.*', line):
    error(filename, linenum, 'build/include_path', 3,
          'An "." or ".." was used in an #include; relative paths are disallowed.')

  classinfo = nesting_state.InnermostClass()
  in_a_function = getattr(function_state, 'in_a_function', True)
  
  if Search(r'static\s+', line):
    if not classinfo and not in_a_function and not nesting_state.InClassDeclaration():
      error(filename, linenum, 'build/namespaces', 5,
            'static storage declaration outside of class or function not allowed (if this isn\'t a header, please contact John Freeman)')

  # Everything else in this function operates on class declarations.
  # Return early if the top of the nesting stack is not a class, or if
  # the class head is not completed yet.
  if not classinfo or not classinfo.seen_open_brace:
    return

  if classinfo.name not in CheckForNonStandardConstructs.ClassAccessSpecifiers:
    CheckForNonStandardConstructs.ClassAccessSpecifiers[classinfo.name] = []

  match = Search(r"(public|protected|private)\s*:", line)
  if match:
    if match.group(1) not in CheckForNonStandardConstructs.ClassAccessSpecifiers[classinfo.name]:
      CheckForNonStandardConstructs.ClassAccessSpecifiers[classinfo.name].append(match.group(1))

      if match.group(1) == "public" and ("private" in CheckForNonStandardConstructs.ClassAccessSpecifiers[classinfo.name] or \
                                         "protected" in CheckForNonStandardConstructs.ClassAccessSpecifiers[classinfo.name]):
        error(filename, linenum, 'readability/access_specifiers', 5, 
              'Access specifier \"public:\" appears after one (or both) of \"private:\" and/or \"protected:\", not before')
      if match.group(1) == "protected" and "private" in CheckForNonStandardConstructs.ClassAccessSpecifiers[classinfo.name]:
        error(filename, linenum, 'readability/access_specifiers', 5,
              'Access specifier \"protected:\" appears after \"private:\", not before')
    else:
      error(filename, linenum, 'readability/access_specifiers', 5,
            'Access specifier "%s" has already appeared in class %s' % (match.group(1), classinfo.name))

  # The class may have been declared with namespace or classname qualifiers.
  # The constructor and destructor will not have those qualifiers.
  base_classname = classinfo.name.split('::')[-1]

  # Look for single-argument constructors that aren't marked explicit.
  # Technically a valid construct, but against style.
  explicit_constructor_match = Match(
      r'\s+(?:(?:inline|constexpr)\s+)*(explicit\s+)?'
      r'(?:(?:inline|constexpr)\s+)*%s\s*'
      r'\(((?:[^()]|\([^()]*\))*)\)'
      % re.escape(base_classname),
      line)

  if explicit_constructor_match:
    is_marked_explicit = explicit_constructor_match.group(1)

    if not explicit_constructor_match.group(2):
      constructor_args = []
    else:
      constructor_args = explicit_constructor_match.group(2).split(',')

    # collapse arguments so that commas in template parameter lists and function
    # argument parameter lists don't split arguments in two
    i = 0
    while i < len(constructor_args):
      constructor_arg = constructor_args[i]
      while (constructor_arg.count('<') > constructor_arg.count('>') or
             constructor_arg.count('(') > constructor_arg.count(')')):
        constructor_arg += ',' + constructor_args[i + 1]
        del constructor_args[i + 1]
      constructor_args[i] = constructor_arg
      i += 1

    defaulted_args = [arg for arg in constructor_args if '=' in arg]
    noarg_constructor = (not constructor_args or  # empty arg list
                         # 'void' arg specifier
                         (len(constructor_args) == 1 and
                          constructor_args[0].strip() == 'void'))
    onearg_constructor = ((len(constructor_args) == 1 and  # exactly one arg
                           not noarg_constructor) or
                          # all but at most one arg defaulted
                          (len(constructor_args) >= 1 and
                           not noarg_constructor and
                           len(defaulted_args) >= len(constructor_args) - 1))
    initializer_list_constructor = bool(
        onearg_constructor and
        Search(r'\bstd\s*::\s*initializer_list\b', constructor_args[0]))
    copy_constructor = bool(
        onearg_constructor and
        Match(r'(const\s+)?%s(\s*<[^>]*>)?(\s+const)?\s*(?:<\w+>\s*)?&'
              % re.escape(base_classname), constructor_args[0].strip()))

    if (not is_marked_explicit and
        onearg_constructor and
        not initializer_list_constructor and
        not copy_constructor):
      if defaulted_args:
        error(filename, linenum, 'runtime/explicit', 5,
              'Constructors callable with one argument '
              'should be marked explicit.')
      else:
        error(filename, linenum, 'runtime/explicit', 5,
              'Single-parameter constructors should be marked explicit.')
    elif is_marked_explicit and not onearg_constructor:
      if noarg_constructor:
        error(filename, linenum, 'runtime/explicit', 5,
              'Zero-parameter constructors should not be marked explicit.')
def CheckLanguage(filename, clean_lines, linenum, file_extension,
                  include_state, nesting_state, error):
  """Checks rules from the 'C++ language rules' section of cppguide.html.

  Some of these rules are hard to test (function overloading, using
  uint32 inappropriately), but we do the best we can.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    file_extension: The extension (without the dot) of the filename.
    include_state: An _IncludeState instance in which the headers are inserted.
    nesting_state: A NestingState instance which maintains information about
                   the current stack of nested blocks being parsed.
    error: The function to call with any errors found.
  """
  # If the line is empty or consists of entirely a comment, no need to
  # check it.
  line = clean_lines.elided[linenum]
  if not line:
    return

  match = _RE_PATTERN_INCLUDE.search(line)
  if match:
    CheckIncludeLine(filename, clean_lines, linenum, include_state, error)
    return

  # Reset include state across preprocessor directives.  This is meant
  # to silence warnings for conditional includes.
  match = Match(r'^\s*#\s*(if|ifdef|ifndef|elif|else|endif)\b', line)
  if match:
    include_state.ResetSection(match.group(1))

  # Make Windows paths like Unix.
  fullname = os.path.abspath(filename).replace('\\', '/')

  # Perform other checks now that we are sure that this is not an include line
  CheckCasts(filename, clean_lines, linenum, error)
  CheckGlobalStatic(filename, clean_lines, linenum, error)

  if IsHeaderExtension(file_extension):
    # TODO(unknown): check that 1-arg constructors are explicit.
    #                How to tell it's a constructor?
    #                (handled in CheckForNonStandardConstructs for now)
    # TODO(unknown): check that classes declare or disable copy/assign
    #                (level 1 error)
    pass

  # Check if people are using the verboten C basic types.  The only exception
  # we regularly allow is "unsigned short port" for port.
  if Search(r'\bshort port\b', line):
    if not Search(r'\bunsigned short port\b', line):
      error(filename, linenum, 'runtime/int', 4,
            'Use "unsigned short" for ports, not "short"')
  else:
    match = Search(r'\b(short|long(?! +double)|long long)\b', line)
    if match:
      error(filename, linenum, 'runtime/int', 4,
            'Use int16/int64/etc, rather than the C type %s' % match.group(1))

  # Check if some verboten operator overloading is going on
  # TODO(unknown): catch out-of-line unary operator&:
  #   class X {};
  #   int operator&(const X& x) { return 42; }  // unary operator&
  # The trick is it's hard to tell apart from binary operator&:
  #   class Y { int operator&(const Y& x) { return 23; } }; // binary operator&
  if Search(r'\boperator\s*&\s*\(\s*\)', line):
    error(filename, linenum, 'runtime/operator', 4,
          'Unary operator& is dangerous.  Do not use it.')

  # Check for suspicious usage of "if" like
  # } if (a == b) {
  if Search(r'\}\s*if\s*\(', line):
    error(filename, linenum, 'readability/braces', 4,
          'Did you mean "else if"? If not, start a new line for "if".')

  # Check for potential memset bugs like memset(buf, sizeof(buf), 0).
  match = Search(r'memset\s*\(([^,]*),\s*([^,]*),\s*0\s*\)', line)
  if match and not Match(r"^''|-?[0-9]+|0x[0-9A-Fa-f]$", match.group(2)):
    error(filename, linenum, 'runtime/memset', 4,
          'Did you mean "memset(%s, 0, %s)"?'
          % (match.group(1), match.group(2)))

  if Search(r'\busing namespace\b', line):
    error(filename, linenum, 'build/namespaces', 5,
          'Do not use namespace using-directives.  '
          'Use using-declarations instead (if this isn\'t a header, please contact John Freeman)')

  # Detect variable-length arrays.
  match = Match(r'\s*(.+::)?(\w+) [a-z]\w*\[(.+)];', line)
  if (match and match.group(2) != 'return' and match.group(2) != 'delete' and
      match.group(3).find(']') == -1):
    # Split the size using space and arithmetic operators as delimiters.
    # If any of the resulting tokens are not compile time constants then
    # report the error.
    tokens = re.split(r'\s|\+|\-|\*|\/|<<|>>]', match.group(3))
    is_const = True
    skip_next = False
    for tok in tokens:
      if skip_next:
        skip_next = False
        continue

      if Search(r'sizeof\(.+\)', tok): continue
      if Search(r'arraysize\(\w+\)', tok): continue

      tok = tok.lstrip('(')
      tok = tok.rstrip(')')
      if not tok: continue
      if Match(r'\d+', tok): continue
      if Match(r'0[xX][0-9a-fA-F]+', tok): continue
      if Match(r'k[A-Z0-9]\w*', tok): continue
      if Match(r'(.+::)?k[A-Z0-9]\w*', tok): continue
      if Match(r'(.+::)?[A-Z][A-Z0-9_]*', tok): continue
      # A catch all for tricky sizeof cases, including 'sizeof expression',
      # 'sizeof(*type)', 'sizeof(const type)', 'sizeof(struct StructName)'
      # requires skipping the next token because we split on ' ' and '*'.
      if tok.startswith('sizeof'):
        skip_next = True
        continue
      is_const = False
      break
    if not is_const:
      error(filename, linenum, 'runtime/arrays', 1,
            'Do not use variable-length arrays.  Use an appropriately named '
            "('k' followed by CamelCase) compile-time constant for the size.")

  # Check for use of unnamed namespaces in header files.  Registration
  # macros are typically OK, so we allow use of "namespace {" on lines
  # that end with backslashes.
  if (IsHeaderExtension(file_extension)
      and Search(r'\bnamespace\s*{', line)
      and line[-1] != '\\'):
    error(filename, linenum, 'build/namespaces', 4,
          'Do not use unnamed namespaces in header files.  See '
          'the Unnamed Namespaces and Static Variables section of https://dune-daq-sw.readthedocs.io/en/latest/packages/styleguide/'
          ' for more information.')

# Register DUNE-specific overrides in the vendored cpplint module before main().
for _override_name in ('PrintUsage', 'CheckForCopyright', 'CheckForNonStandardConstructs', 'CheckLanguage'):
  setattr(_upstream_cpplint, _override_name, globals()[_override_name])

def main():
  return _upstream_cpplint.main()


if __name__ == '__main__':
  main()
