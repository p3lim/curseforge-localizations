L["1st key string"]
L["2nd key split"] .. foo .. L['3rd key split end']
L["4rd key split"] .. "bar" .. L['5th key split end with word']
L['6th key escaped string']
L["7th key multi\nline"]
L['\t\t8th key indented with\nnewlines which shouldn\'t get broken'] = '1st value after 8th key'
L['OPTION1'] = "2st value"
L['OPTION2'] = "3nd value which should'nt split"
L['OPTION3'] = '4rd value which should\'nt split'
L["OPTION4"] = [[5th value
as multiline
block
no nesting]]
L["OPTION5"] = [=[6th value
as multiline
block
with 1 nesting]=]
L["OPTION6"] = [===[7th value
as multiline
block
with 3 nesting
and trailing newline
]===]
