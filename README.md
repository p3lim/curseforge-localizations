# CurseForge Localizations

Sync localization strings in World of Warcraft AddOns to [CurseForge's localizations](https://support.curseforge.com/en/support/solutions/articles/9000197356-project-localization).

It will (recursively) scan Lua files for text matching the [AceLocale](https://www.wowace.com/projects/ace3/pages/api/ace-locale-3-0) format (e.g. `L["An example"]`), then upload them to CurseForge. In essence it'll keep the strings used in the project code in-sync with CurseForge. It's a perfect companion to [localization substitution](https://github.com/BigWigsMods/packager/wiki/Localization-Substitution) in packagers.

> Using AceLocale in your project is not required, the structure it defines has become the default that many libraries/addons use, AceLocale is just the most common use-case.

The script uses the [CurseForge Upload API](https://support.curseforge.com/en/support/solutions/articles/9000197321-curseforge-api), which requires authentication (see below).

## Usage

> This tool requires Python >=3.13 and [requests](https://pypi.org/project/requests/).

```
usage: update.py [-k KEY] [-i ID] [-l OPT] [-m OPT] [-n OPT] [-e OPT] [-p OPT] [-d] [-h]

required arguments::
  -k, --key KEY        API key or path to file that contains the key for CurseForge,
                       can also be defined as CF_API_KEY environment variable
  -i, --id ID          project ID on CurseForge

optional arguments::
  -l, --lang OPT       base language of strings (default = enUS)
  -m, --missing OPT    how to handle missing phrases (default = DoNothing)
  -n, --namespace OPT  namespace to upload to
  -e, --exclude OPT    pattern of files and/or directories to ignore
  -p, --pattern OPT    regex pattern used to find strings
  -d, --dry            dry-run, print strings instead of uploading
  -h, --help           show this help message
```

For the tool to work correctly (i.e. upload strings) it needs at minimum two pieces of information:

- it needs the API key to talk to the CurseForge API
  - you can generate one here: <https://authors-old.curseforge.com/account/api-tokens>
  - the script can read this from a file, an environment variable, or as a plain string argument
- it needs the project ID on CurseForge
  - see the right column of your project's webpage on CurseForge
  - if this is not provided as an argument the script will attempt to find it from the `X-Curse-Project-ID` field in nearby TOC files, as it's commonly used/defined that was by other tools

And you obviously need to enable the Localization feature on CurseForge for your project;

> `https://legacy.curseforge.com/wow/addons/YOUR_PROJECT/settings/general`

The additional options should be pretty straight-forward, although some are quite advanced.  
Please refer to the CurseForge support article for some of them.

If you have any questions on how to use the script, feel free to open a [discussion](https://github.com/p3lim/curseforge-localizations/discussions).

## Example workflow

The script can be used as an [action](https://docs.github.com/en/actions) in a GitHub [workflow](https://docs.github.com/en/actions/writing-workflows/about-workflows);

```yaml
name: Upload localization strings to CurseForge

on:
  push:
    branches:
      - master
    tags-ignore:
      - '**'

permissions:
  contents: read # required to install python dependencies

jobs:
  upload:
    runs-on: ubuntu-latest
    steps:
      - name: Clone project
        uses: actions/checkout@v4

      - name: Upload localizations
        uses: p3lim/curseforge-localizations@v2
        with:
          handle_missing: DeletePhrase # optional
          exclude: | # optional
            libs/*
            testing.lua
        env:
          CF_API_KEY: ${{ secrets.CF_API_KEY }}
```
