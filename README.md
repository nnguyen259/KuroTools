# KuroTools
Tools for working with Kuro no Kiseki .dat and .tbl files

# ED9Disassembler
ED9Disassembler is an experimental tool to disassemble and reassemble the script files (.dat) from The Legend of Heroes: Kuro no Kiseki. The tool translates the binary content of each script into a series of instructions written in a stack-based language.

The main purpose of this tool is only for research as the game is not ready to be modded right now (being on PS4 only).
If you have any sort of question about how the scripts work or want to contribute with the research, don't hesitate to drop by the Kiseki Modding Discord https://discord.gg/6szDMdwEdH.

Usage:

Using Python, call the dat2py.py script like this:

<PYTHON_PATH> dat2py.py <Path to the dat file to be disassembled> --markers <True/False> --decompile <True/False> --debug <True/False>
  
A few explainations on each option: 
- markers set to True means that the disassembler will also disassemble the instructions adding Line Markers, which should only be useful for debug purpose (It is not certain but that is my guess).
Keeping them is important if you want to compare the original script with yours, but otherwise I don't think they are important at all
- decompile set to False means the script will be disassembled into raw instructions, which is often very hard to make sense of as there is a invisible stack evolving in the background.
When set to True, the script attempts to merge some instructions into patterns such as function calls, expressions, conditions, etc. However, it might be a bit risky to use it while the disassembling method is safer. I suggest using the decompiled for short mod attempts/to understand what is going on, but for heavier projects, you might want to use the disassembling. Also, contact me if you end up screwing up a file using the decompilation as I might be able to help fixing it.
In general, if you want more information on the decompilation, you can contact me on discord.
- the debug option is to force the disassembler to disassemble the file even though there are problems with the stack (which could happen) by default, set it to False
  
Current state:
  
Right now the code is a mess. I suggest treating it as a black box for now. If you want to know more details on the implementation, just contact me privately.
As of today, the tool is able to disassemble and reassemble all the scena files of the game identically to the original files except the following:

  a1000\
  m3100\
  c0400\
  sys_event
  
They all have some weird stuff going on (although the difference is very minor and might not actually be important at all)
  
If there is a need to edit those specific files, just contact me and I'll help.
 
