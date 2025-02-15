# CurseForge Localizations

A small shell script to manage localization strings in World of Warcraft AddOns.

It will (recursively) scan Lua files in the directory it's run in for strings that matches the standard AceLocale format, then upload that to CurseForge, pruning all other strings not present in the files.

This script is **destructive** in that sense, so any strings _not_ in the project's source will be removed from CurseForge!

For it to work it needs two environment variables:

- `CF_API_KEY` - generate one here: <https://authors-old.curseforge.com/account/api-tokens>
- `CF_PROJECT_ID` - see the right column of your project's webpage on CurseForge
  - if this is not provided the script will attempt to scan TOC files at the base of the repository for the `X-Curse-Project-ID` field and use its value

## Assumptions

The script has a few assumptions in the way it works:

- you have enabled the Localization feature on CurseForge for your project
	- enable it at `https://legacy.curseforge.com/wow/addons/YOUR_PROJECT/settings/general`
- all strings you want to upload are defined in Lua files using the AceLocale format, e.g;
	- `L["This is an example"]` or
	- `L['This is an example']`

## Example workflow

```yaml
name: Upload localization strings to CurseForge

on:
  push:
    branches:
      - master
    tags-ignore:
      - '**'

jobs:
  upload:
    runs-on: ubuntu-latest
    steps:
      - name: Clone project
        uses: actions/checkout@v4

      - name: Upload localizations
        uses: p3lim/curseforge-localizations@v1
        env:
          CF_API_KEY: ${{ secrets.CF_API_KEY }}
```
