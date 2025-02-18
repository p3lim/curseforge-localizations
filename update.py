#!/usr/bin/env python3

import os
import sys
import re
import json
import glob
import argparse
import textwrap
import requests

url = 'https://legacy.curseforge.com/api/projects/%s/localization/import'
valid_langs = ('enUS', 'deDE', 'esES', 'esMX', 'frFR', 'itIT', 'koKR', 'ptBR', 'ruRU', 'zhCN', 'zhTW')
valid_handlers = ('DoNothing', 'DeletePhrase', 'DeleteIfTranslationsOnlyExistForSelectedLanguage', 'DeleteIfNoTranslations')
default_pattern = r'L\[["\']([^]]+)["\']\](?:\s*=\s*["\']([^"\']+)["\'])?'

def parse_arguments():
  parser = argparse.ArgumentParser(add_help=False, formatter_class=argparse.RawTextHelpFormatter)

  required = parser.add_argument_group('required arguments:')
  required.add_argument('-k', '--key', help='API key or path to file that contains the key for CurseForge,\ncan also be defined as CF_API_KEY environment variable')
  required.add_argument('-i', '--id', help='project ID on CurseForge')

  optional = parser.add_argument_group('optional arguments:')
  optional.add_argument('-l', '--lang', help=f'base language of strings (default = {valid_langs[0]})', default=valid_langs[0], metavar='OPT')
  optional.add_argument('-m', '--missing', help=f'how to handle missing phrases (default = {valid_handlers[0]})', default=valid_handlers[0], metavar='OPT')
  optional.add_argument('-n', '--namespace', help='namespace to upload to', metavar='OPT')
  optional.add_argument('-e', '--exclude', help='pattern of files and/or directories to ignore', action='append', metavar='OPT')
  optional.add_argument('-p', '--pattern', help='regex pattern used to find strings', default=default_pattern, metavar='OPT')
  optional.add_argument('-d', '--dry', help='dry-run, print strings instead of uploading', action='store_true')
  optional.add_argument('-h', '--help', help='show this help message', action='store_true')

  args = parser.parse_args()
  if args.help:
    parser.print_help()
    sys.exit(0)

  return args

def validate_arguments(args):
  if not args.key:
    if 'CF_API_KEY' in os.environ:
      args.key = os.environ['CF_API_KEY']
  else:
    if os.path.isfile(args.key):
      with open(args.key, 'r') as file:
        args.key = file.readline().rstrip()

  if not args.id:
    toc_pattern = re.compile(r'## X-Curse-Project-ID: (.+)')
    for path in glob.glob('**/*.toc', recursive=True):
      with open(path, 'r') as file:
        for line in file:
          match = toc_pattern.search(line)
          if match:
            args.id = match.group(1)
            break

  if len(args.pattern) == 0:
    # stupid github
    args.pattern = default_pattern

def get_metadata(args):
  metadata = {}
  if args.namespace:
    metadata['namespace'] = args.namespace

  if args.lang in valid_langs:
    metadata['language'] = args.lang
  else:
    print('error: invalid language defined')
    print(f'       must be one of: {json.dumps(valid_langs)[1:-1]}')
    sys.exit(1)

  if args.missing in valid_handlers:
    metadata['missing-phrase-handling'] = args.missing
  else:
    print('error: invalid missing phrase handler')
    print(f'       must be one of: {json.dumps(valid_handlers)[1:-1]}')
    sys.exit(1)

  return metadata

def get_strings(args):
  strings = {}
  pattern = re.compile(args.pattern)

  if args.exclude and len(args.exclude) == 1 and args.exclude[0].count('\n') > 0:
    # stupid github doesn't support lists
    args.exclude = args.exclude[0].splitlines()

  excludes = []
  for path in args.exclude or []:
    excludes.append(glob.translate(path))

  exclude_pattern = f'({ ")|(".join(excludes) })'
  for path in glob.glob('**/*.lua', recursive=True):
    if len(excludes) and re.match(exclude_pattern, path):
      continue

    with open(path, 'r') as file:
      for line in file:
        match = pattern.search(line)
        if match:
          (key, value) = match.groups()

          # if there's no value store "True" in its place, as the AceLocale format CurseForge follows
          # will interpret that as "the key is the value", but if we find the value for the key then
          # store that instead
          if key in strings:
            if strings[key] is True:
              strings[key] = value or True
          else:
            strings[key] = value or True

  return strings

def upload_strings(args, strings):
  if not args.key:
    print('error: missing API key')
    sys.exit(1)

  if not args.id:
    print('error: missing project ID')
    sys.exit(1)

  res = requests.post(
    url % args.id,
    headers = {
      'X-Api-Token': args.key
    },
    files = {
      'metadata': (None, json.dumps(get_metadata(args))),
      'localizations': (None, '\n'.join([f'L[{json.dumps(k)}] = {json.dumps(v)}' for k,v in strings.items()]))
    }
  )

  if res.status_code == 403:
    # the API doesn't know how to handle this error
    print('error: failed to upload')
    print('       this is usually caused by a bad project ID')
    sys.exit(1)

  data = json.loads(res.content)
  if res.status_code == 200:
    print(data["message"])
  else:
    # do some trimming on the message
    msg = data["errorMessage"].replace(args.key, '***').strip()
    print(f'error: failed to upload:\n{textwrap.indent(msg, " " * 7)}')
    sys.exit(1)

if __name__ == '__main__':
  args = parse_arguments()

  validate_arguments(args)
  strings = get_strings(args)

  if args.dry:
    for key, value in strings.items():
      print(f'L[{json.dumps(key)}] = {json.dumps(value)}')
  else:
    upload_strings(args, strings)
