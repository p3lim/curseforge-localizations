# CurseForge Localizations

A small shell script to manage localization strings in World of Warcraft AddOns.

It will (recursively) scan Lua files in the directory it's run in for strings that matches the standard AceLocale format, then upload that to CurseForge, pruning all other strings not present in the files.

For it to work it needs two environment variables:

- `CF_API_KEY` - generate one here: <https://authors-old.curseforge.com/account/api-tokens>
- `CF_PROJECT_ID` - see the right column of your project's webpage on CurseForge
	- the script will scan TOC files for the `X-Curse-Project-ID` field if this is not provided

## Assumptions

The script has a few assumptions in the way it works:

- you have enabled the Localization feature on CurseForge for your project
	- enable it at `https://legacy.curseforge.com/wow/addons/YOUR_PROJECT/settings/general`
- all strings you want to upload are defined in Lua files using the AceLocale format, e.g;
	- `L["This is an example"]` or
	- `L['This is an example']`
- you don't keep any already translated strings in your project
	- e.g. it is assumed you use substitutions from a packager, so all your localization files are empty

## Example workflow

```yaml
name: Import localization strings to CurseForge

on:
  push:
    branches:
      - master
    tags-ignore:
      - '**'

jobs:
  template:
    runs-on: ubuntu-latest
    steps:
      - name: Clone project
        uses: actions/checkout@v4

      - name: Upload localizations
        uses: p3lim/curseforge-localizations@v1
        env:
          CF_API_KEY: ${{ secrets.CF_API_KEY }}
```
