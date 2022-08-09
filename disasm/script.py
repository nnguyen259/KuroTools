
import os
from lib.parser import process_data, readint, readintoffset, readtextoffset, remove2MSB, get_actual_value_str, identifytype
import disasm.ED9InstructionsSet as ED9InstructionsSet
import disasm.function as function

class script:

    def __init__(self, dat_file = None, name = "", markers = False):
        self.name = name
        script_variables_in = []
        script_variables_out = []
        functions = []
        if dat_file != None:
            #Parsing script header
            fourCC = readint(dat_file, 4)
            start_ptr = readint(dat_file, 4)
            functions_count = readint(dat_file, 4)
            script_variables_ptr = readint(dat_file, 4)
            script_variables_in_count = readint(dat_file, 4)
            script_variables_out_count = readint(dat_file, 4)
        
            #Retrieving script variables if any
            for id_var in range(script_variables_in_count):
                vars = []
                for id_field in range(2):
                    var = readintoffset(dat_file, script_variables_ptr + id_var * 8 + id_field * 4, 4)
                    if (identifytype(var) == "string"):
                        actual_ptr = remove2MSB(var)
                        if actual_ptr < ED9InstructionsSet.smallest_data_ptr:
                            ED9InstructionsSet.smallest_data_ptr = actual_ptr
                    vars.append(var)
                script_variables_in.append(vars)
            for id_var in range(script_variables_out_count):
                vars = []
                for id_field in range(2):
                    var = readintoffset(dat_file, script_variables_ptr + len(script_variables_in) * 8 + id_var * 8 + id_field * 4, 4)
                    if (identifytype(var) == "string"):
                        actual_ptr = remove2MSB(var)
                        if actual_ptr < ED9InstructionsSet.smallest_data_ptr:
                            ED9InstructionsSet.smallest_data_ptr = actual_ptr
                    vars.append(var)
                script_variables_out.append(vars)
            #Parsing functions headers 
            for id_fun in range(functions_count):
                functions.append(function.function(dat_file, id_fun))

            dat_file.seek(0, os.SEEK_END)
            file_size = dat_file.tell()
        
            functions.sort(key=lambda fun: fun.start) 

            for id_f in range(len(functions)):
               if (id_f < (len(functions) - 1)):
                   end_addr = functions[id_f + 1].start
               else:
                   end_addr = ED9InstructionsSet.smallest_data_ptr

               dat_file.seek(functions[id_f].start)
               #Reading the instructions

               while (dat_file.tell() < end_addr):
                   op_code = readint(dat_file, 1)
                   instruction = ED9InstructionsSet.instruction(dat_file, op_code)
                   functions[id_f].instructions.append(instruction)
                  
                   if ED9InstructionsSet.smallest_data_ptr < end_addr:
                       end_addr = ED9InstructionsSet.smallest_data_ptr

           

            functions.sort(key=lambda fun: fun.id) 

            
            

        self.functions = functions
        self.script_variables_in = script_variables_in
        self.script_variables_out = script_variables_out  

