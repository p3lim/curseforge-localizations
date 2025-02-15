# CurseForge Localizations

A small shell script to manage localization strings for World of Warcraft AddOns when using [CurseForge's localization feature](https://support.curseforge.com/en/support/solutions/articles/9000197356-project-localization).

It will (recursively) scan Lua files for text matching the [AceLocale](https://www.wowace.com/projects/ace3/pages/api/ace-locale-3-0) format (e.g. `L["An example"]`), then upload them to CurseForge. In essence it'll keep the strings used in the project code in-sync with CurseForge. It's a perfect companion to [localization substitution](https://github.com/BigWigsMods/packager/wiki/Localization-Substitution) in packagers.

> Using AceLocale in your project is not required, the structure it defines has become the default that many libraries/addons use, and AceLocale is the most common way to use it.

The script uses the [CurseForge Upload API](https://support.curseforge.com/en/support/solutions/articles/9000197321-curseforge-api), which requires authentication (see below).

## Usage

For it to work it needs two environment variables:

- `CF_API_KEY` - generate one here: <https://authors-old.curseforge.com/account/api-tokens>
- `CF_PROJECT_ID` - see the right column of your project's webpage on CurseForge
  - if not provided the script will attempt to scan TOC files for the `X-Curse-Project-ID` field and use its value

And you obviously need to enable the Localization feature on CurseForge for your project;

> `https://legacy.curseforge.com/wow/addons/YOUR_PROJECT/settings/general`

Additional environment variables that adjust how it runs:

- `HANDLE_MISSING` - when an existing string on CurseForge doesn't exist in the Lua files, one of:
  - `DoNothing` (default)
  - `DeletePhrase` (recommended to keep things clean)
  - `DeleteIfTranslationsOnlyExistForSelectedLanguage`
  - `DeleteIfNoTranslations`
- `NAMESPACE` - (advanced) if you're using this then you know what you're doing

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
          HANDLE_MISSING: DeletePhrase # optional
```
