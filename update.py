#!/usr/bin/env python3

import os
import sys
import re
import json
import glob
import argparse
import textwrap
import requests
from luaparser import ast
from luaparser import astnodes

MIN_PYTHON_VERSION = (3, 13)

if sys.version_info < MIN_PYTHON_VERSION:
  sys.stderr.write(f'Error: this script requires Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or later\n')
  sys.exit(1)

CF_URL = 'https://legacy.curseforge.com/api/projects/%s/localization/import'
VALID_LANGS = (
  'enUS',
  'deDE',
  'esES',
  'esMX',
  'frFR',
  'itIT',
  'koKR',
  'ptBR',
  'ruRU',
  'zhCN',
  'zhTW',
)
VALID_HANDLERS = (
  'DoNothing',
  'DeletePhrase',
  'DeleteIfTranslationsOnlyExistForSelectedLanguage',
  'DeleteIfNoTranslations',
)


def parse_arguments():
  parser = argparse.ArgumentParser(add_help=False, formatter_class=argparse.RawTextHelpFormatter)

  required = parser.add_argument_group('required arguments:')
  required.add_argument('-k', '--key', help='API key or path to file that contains the key for CurseForge,\ncan also be defined as CF_API_KEY environment variable')
  required.add_argument('-i', '--id', help='project ID on CurseForge')

  optional = parser.add_argument_group('optional arguments:')
  optional.add_argument('-l', '--lang', help=f'base language of strings (default = {VALID_LANGS[0]})', default=VALID_LANGS[0], metavar='OPT')
  optional.add_argument('-m', '--missing', help=f'how to handle missing phrases (default = {VALID_HANDLERS[0]})', default=VALID_HANDLERS[0], metavar='OPT')
  optional.add_argument('-n', '--namespace', help='namespace to upload to', metavar='OPT')
  optional.add_argument('-e', '--exclude', help='pattern of files and/or directories to ignore', action='append', metavar='OPT')
  optional.add_argument('-d', '--dry', help='dry-run, print strings instead of uploading', action='store_true')
  optional.add_argument('-h', '--help', help='show this help message', action='store_true')

  args = parser.parse_args()
  if args.help:
    parser.print_help()
    sys.exit(0)

  if not args.key:
    if 'CF_API_KEY' in os.environ:
      args.key = os.environ['CF_API_KEY']
  else:
    if os.path.isfile(args.key):
      with open(args.key, 'r') as file:
        args.key = file.readline().rstrip()

  if not args.id:
    toc_pattern = re.compile(r'^## X-Curse-Project-ID: (.+)$')
    for path in glob.glob('**/*.toc', recursive=True):
      with open(path, 'r') as file:
        for line in file:
          match = toc_pattern.search(line)
          if match:
            args.id = match.group(1)
            break

  return args


def get_metadata(args):
  metadata = {}
  if args.namespace:
    metadata['namespace'] = args.namespace

  if args.lang in VALID_LANGS:
    metadata['language'] = args.lang
  else:
    print('error: invalid language defined')
    print(f'       must be one of: {json.dumps(VALID_LANGS)[1:-1]}')
    sys.exit(1)

  if args.missing in VALID_HANDLERS:
    metadata['missing-phrase-handling'] = args.missing
  else:
    print('error: invalid missing phrase handler')
    print(f'       must be one of: {json.dumps(VALID_HANDLERS)[1:-1]}')
    sys.exit(1)

  return metadata


def escape(s):
  if isinstance(s, bool):
    return str(s).lower() # lua syntax
  return f'"{s.replace("\\'", "'").replace("\n", "\\n").replace("\t", "\\t")}"'


def get_strings(args):
  excludes = []
  if args.exclude:
    for path in args.exclude:
      excludes.append(glob.translate(path, recursive=True))

  string_keys = []
  string_pairs = {}

  # traverse files
  exclude_pattern = f'({")|(".join(excludes)})'
  for path in glob.glob('**/*.lua', recursive=True):
    if excludes and re.match(exclude_pattern, path):
      continue

    # read file
    with open(path, 'r') as file:
      # traverse lua tree, finding the table "L" when it's indexed or a value is assigned
      tree = ast.parse(file.read())
      for node in ast.walk(tree):
        if isinstance(node, astnodes.Index):
          if hasattr(node.value, 'id') and node.value.id == 'L':
            string_keys.append(node.idx.raw)
        elif isinstance(node, astnodes.Assign):
          if (
            hasattr(node.targets[0], 'value')
            and hasattr(node.targets[0].value, 'id')
            and node.targets[0].value.id == 'L'
          ):
            if isinstance(node.values[0], astnodes.String):
              string_pairs[node.targets[0].idx.raw] = node.values[0].raw

  for key in string_keys:
    if key not in string_pairs.keys():
      string_pairs[key] = True

  # convert to lua
  strings = []
  for key, value in string_pairs.items():
    strings.append(f'L[{escape(key)}] = {escape(value)}')

  return strings


def upload_strings(args, strings):
  if not args.key:
    print('error: missing API key')
    sys.exit(1)

  if not args.id:
    print('error: missing project ID')
    sys.exit(1)

  res = requests.post(
    CF_URL % args.id,
    headers = {
      'X-Api-Token': args.key
    },
    files = {
      'metadata': (None, json.dumps(get_metadata(args))),
      'localizations': (None, '\n'.join(strings)),
    },
  )

  if res.status_code == 403:
    # the API doesn't know how to handle this error
    print('error: failed to upload')
    print('       this is usually caused by a bad project ID')
    sys.exit(1)

  data = json.loads(res.content)
  if res.status_code == 200:
    print(data['message'])
  else:
    # do some trimming on the message
    msg = data['errorMessage'].replace(args.key, '***').strip()
    print(f'error: failed to upload:\n{textwrap.indent(msg, " " * 7)}')
    sys.exit(1)


if __name__ == '__main__':
  args = parse_arguments()
  strings = get_strings(args)

  if args.dry:
    for s in strings:
      print(s)
  else:
    upload_strings(args, strings)
