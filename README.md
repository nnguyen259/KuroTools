# KuroTools
Tools for working with Kuro no Kiseki .dat and .tbl files

# Requirements
- Python 3.10 and +
If the file is encrypted (CLE encryption):
- zstandard package is required

# TBL editing tool (tbl2json/json2tbl)
tbl2json is used to decompile the game tables (.tbl files) into a .json file consisting of several decompiled entries. Each field of each entry has been named according to the schemas found in the schemas/headers folder. Not all schemas have been written as of yet, so feel free to contribute if you want to add one that is not yet supported.

json2tbl is used to recompile the .json files that have been decompiled with tbl2json. It will produce a tbl that is readable by the game.

Usage:
<PYTHON_PATH> tbl2json.py <Path to the tbl file to be decompiled>
(Note: it should be possible to just drag and drop your tbl file on tbl2json to produce the json)
<PYTHON_PATH> json2tbl.py <Path to the json file to be recompiled>

# ED9Disassembler (dat2py)

ED9Disassembler is an experimental tool to disassemble and reassemble the script files (.dat) from The Legend of Heroes: Kuro no Kiseki. The tool translates the binary content of each script into a series of instructions written in a stack-based language. The tool can also decrypt and decompress the script files from CLE PC version of the game.

If you have any sort of question regarding how the scripts work or want to contribute to the research, don't hesitate to drop by the Kiseki Modding Discord https://discord.gg/6szDMdwEdH.

Usage:

Using Python, call the dat2py.py script like this:

<PYTHON_PATH> dat2py.py <Path to the dat file to be disassembled> --markers <True/False> --decompile <True/False>
  
Default value for decompile is True.
  
A few explanations on each option:

- In the files compiled by falcom, markers exist between blocks of instructions, probably automatically integrated by their scripting tool, but they are only used for debugging. If you set the markers option to True, the "AddMarker" instruction will be present in the disassembled script (but it will have no effect in game). It is mainly used to ensure the content stays the same between the original file and the disassembled file.

- decompile set to False means the script will be disassembled into raw instructions, which is often very hard to make sense of as there is an invisible stack evolving in the background.
When set to True, the script attempts to merge some instructions into patterns such as function calls, expressions, conditions, etc. However, it might be a bit risky to use it while the disassembling method is safer. I suggest using the decompiled for short mod attempts/to understand what is going on, but for heavier projects, you might want to use the disassembling. 

Note: the tool can display a warning when disassembling some files. It's most likely due to weird patterns such as inacessible areas of code. For example code that will exit the function, but a jump comes right after the EXIT. Since we exit the function before jumping we never jump to that area of the code. The stack calculation is messed up and causes the warning. Normally you can ignore those warnings and get rid of the jump before compiling the files. For more information please contact Twn by email or drop by the Kiseki Modding Discord.

Finally mon9996_c00.dat is a broken file distributed by CLE. This is the only one with a 0x10 bytes long headers for functions which makes it unreadable and is a mystery.
 
