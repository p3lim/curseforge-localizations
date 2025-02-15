#!/bin/bash

# check env
if [ -z "$CF_API_KEY" ]; then
  echo "Missing required env 'CF_API_KEY'"
  exit 1
fi
if [ -z "$CF_PROJECT_ID" ]; then
  # attempt to read project ID from TOC file
  regexID='## X-Curse-Project-ID: (.*?)$'
  while read -r line; do
    if [[ $line =~ $regexID ]]; then
      CF_PROJECT_ID="${BASH_REMATCH[1]}"
    fi
  done < <(grep -oP "$regexID" -- *.toc)
fi
if [ -z "$CF_PROJECT_ID" ]; then
  echo "Missing required env 'CF_PROJECT_ID'"
  exit 1
fi

# create temporary files
translations="$(mktemp)"
http_out="$(mktemp)"
trap 'rm -f "$translations" "$http_out"' EXIT

# define variables
declare -A strings
regex="L\[[\"']([^]]+)[\"']\]"

# scrape files for translation strings
while read -r file; do
  while read -r line; do
    strings["$line"]=true
  done < <(grep -oP "$regex" "$file")
done < <(find . -type f -name '*.lua')

# dump strings to temporary file
for str in "${!strings[@]}"; do
  echo "${str}=${strings[$str]}" >> "$translations"
done

# upload strings to CurseForge
# https://support.curseforge.com/en/support/solutions/articles/9000197321-curseforge-api
res=$(curl -sSL -X POST -w "%{http_code}" -o "$http_out" \
  -H "X-Api-Token: $CF_API_KEY" \
  -F 'metadata={ language: "enUS", "missing-phrase-handling": "DeletePhrase" }' \
  -F "localizations=<$translations" \
  "https://legacy.curseforge.com/api/projects/$CF_PROJECT_ID/localization/import"
) || {
  echo "Failed to upload"
  exit 1
}

case "$res" in
  200)
    echo "Successfully exported strings to CurseForge"
    exit 0
    ;;
  400)
    echo "Error exporting strings to CurseForge ($res):"
    cat "$http_out"
    echo
    exit 1
    ;;
  *)
    echo "Unknown error exporting strings to CurseForge ($res)"
    exit 1
    ;;
esac
