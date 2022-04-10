
import os
import sys
from pathlib import Path
from typing import Union

from lib.parser import process_data, readint, readintoffset, readtextoffset, remove2MSB, get_actual_value_str, wrap_conversion
import ED9InstructionsSet 



class script:

    def __init__(self, dat_file = None):
        
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
                script_variables_in.append(readintoffset(dat_file, 4, script_variables_ptr + id_var * 4))
            for id_var in range(script_variables_out_count):
                script_variables_out.append(readintoffset(dat_file, 4, script_variables_ptr + script_variables_in_count * 4 + id_var * 4))
            #Parsing functions headers 
            for id_fun in range(functions_count):
                functions.append(function(dat_file, id_fun))

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
                   functions[id_f].instructions.append(ED9InstructionsSet.instruction(dat_file, op_code))
                   if ED9InstructionsSet.smallest_data_ptr < end_addr:
                       end_addr = ED9InstructionsSet.smallest_data_ptr

           

            functions.sort(key=lambda fun: fun.id) 

            for f in functions:
                f.add_return_addresses(functions)

            functions.sort(key=lambda fun: fun.start) 

        self.functions = functions
        self.script_variables_in = script_variables_in
        self.script_variables_out = script_variables_out  

    def write(self, dat_file):
        python_file = open("test.py", "wt",encoding='utf8')
        python_file.write("from ED9Assembler import *\n\n")
        python_file.write("def script():\n")
        python_file.write("\n    create_script_header(\n")
        
        python_file.write("\tvarin= " + "[")
        for id_in in range(len(self.script_variables_in) - 1):
            python_file.write(wrap_conversion(stream, self.script_variables_in[id_in]) + ", ")
        if (len(self.script_variables_in) != 0):
            python_file.write(wrap_conversion(stream, self.script_variables_in[len(self.script_variables_in) - 1])) 
        python_file.write("],\n")

        python_file.write("\tvarout= " + "[")
        for id_in in range(len(self.script_variables_out) - 1):
            python_file.write(wrap_conversion(stream, self.script_variables_out[id_in]) + ", ")
        if (len(self.script_variables_out) != 0):
            python_file.write(wrap_conversion(stream, self.script_variables_out[len(self.script_variables_out) - 1])) 
        python_file.write("],\n")

        python_file.write("    )\n")
        for f in self.functions:
            python_file.write(f.to_string(dat_file))
        python_file.write("\n    compile()")
        python_file.write("\n\nscript()")
        python_file.close()
class function:
    def __init__(self, stream = None, id = 0):
        self.id = id
        self.structs = []
        self.input_args = []
        self.output_args = []
        self.b0 = 0
        self.b1 = 0
        self.instructions = []
        self.hash = -1
        self.start = -1
        if stream != None:
            self.start = readint(stream, 4)
            varin = readint(stream, 1)
            self.b0 = readint(stream, 1)
            self.b1 = readint(stream, 1)
            varout = readint(stream, 1)

            

            out_ptr = readint(stream, 4)
            in_ptr = readint(stream, 4)

            for id_out in range(varout):
                self.output_args.append(readintoffset(stream, 4, out_ptr + id_out * 4))
            for id_in in range(varin):
                self.input_args.append(readintoffset(stream, 4, in_ptr + id_in * 4))
            

            
            nb_structs = readint(stream, 4)
            structs_ptr = readint(stream, 4)

            for id_st in range(nb_structs):
                id_chr = readintoffset(stream, 4, structs_ptr + id_st * 0xC + 0, signed = True)
                nb_sth1 = readintoffset(stream, 2, structs_ptr + id_st * 0xC + 4)
                nb_sth2 = readintoffset(stream, 2, structs_ptr + id_st * 0xC + 6) 
                ptr_sth = readintoffset(stream, 4, structs_ptr + id_st * 0xC + 8)
                
                mysterious_array2 = []


                for id_arr in range(nb_sth2):
                    mysterious_array2.append(readintoffset(stream, 4, ptr_sth + id_arr * 8 + 0))
                    mysterious_array2.append(readintoffset(stream, 4, ptr_sth + id_arr * 8 + 4))

                mysterious_struct = { #Related to characters? Characters in the scene or something?
                "id": id_chr,
                "nb_sth1": nb_sth1,
                "array2": mysterious_array2,
                }
                self.structs.append(mysterious_struct)

            self.hash = readint(stream, 4)
            ptr_fun_name = remove2MSB(readint(stream, 4))
            self.name = readtextoffset(stream, ptr_fun_name)
            self.instructions = []


    def to_string(self, stream) -> str:

        result = "#-------------------------\n"
        result = result + "    declare_function(\n"
        result = result + "\tid= " + str(hex(self.id)) + ",\n"
        result = result + "\tname= " + "\"" + self.name + "\",\n"
        result = result + "\thash= " +  str(hex(self.hash)) +",\n"
        result = result + "\tinput_args  = " + "["
        for id_in in range(len(self.input_args) - 1):
            result = result + wrap_conversion(stream, self.input_args[id_in]) + ", "
        if (len(self.input_args) != 0):
            result = result + wrap_conversion(stream, self.input_args[len(self.input_args) - 1]) 
        result = result + "],\n"

        result = result + "\toutput_args = " + "["
        for id_in in range(len(self.output_args) - 1):
            result = result + wrap_conversion(stream, self.output_args[id_in]) + ", "
        if (len(self.output_args) != 0):
            result = result + wrap_conversion(stream, self.output_args[len(self.output_args) - 1]) 
        result = result + "],\n"

        result = result + "\tb0= " +  str(hex(self.b0)) + ",\n"
        result = result + "\tb1= " +  str(hex(self.b1)) + ",\n"
        result = result + "    )\n\n"

        #Adding the structures as well
        for id_strct in range(len(self.structs)):
            result = result + "    add_struct(\n"
            result = result + "\tid = " + str((self.structs[id_strct]["id"]))+",\n"
            result = result + "\tnb_sth1 = " + str(hex(self.structs[id_strct]["nb_sth1"]))+",\n"

            result = result + "\tarray2 = ["
            for id_in in range(len(self.structs[id_strct]["array2"]) - 1):
                result = result + wrap_conversion(stream, self.structs[id_strct]["array2"][id_in]) + ", "
            if (len(self.structs[id_strct]["array2"]) != 0):
                result = result + wrap_conversion(stream, self.structs[id_strct]["array2"][len(self.structs[id_strct]["array2"])- 1]) 
            result = result + "],\n"

            result = result + "    )\n\n"

        result = result + "#Commands" + "\n"   
        for instruction in self.instructions:
            if instruction.addr in ED9InstructionsSet.locations_dict:
                result = result + "    Label(\""+ED9InstructionsSet.locations_dict[instruction.addr]+"\")\n"
            if instruction.op_code == 0x26: #Line Marker, we can separate with a new line
                result = result + "\n"
            result = result + "    " + instruction.to_string(stream) + "\n"
        result = result + "\n    add_function()\n"
        return result

    def add_return_addresses(self, functions): #Note: We can imagine the same type of function for OP24 where we stop after all arguments were passed to the command
        
        #right now it will only take care of the return address, but we can imagine decompile some other stuff like the entire function call overhead (the push, arithmetic/logic stack operations, the pop, etc)
        for instruction_id in range(len(self.instructions)):
            
            if self.instructions[instruction_id].op_code == 0x0C: #Found a function call
                #We now attempt to find all the input parameters of the function and identify the return address (which should be pushed right before them)
                index_fun = self.instructions[instruction_id].operands[0].value
                called_fun = functions[index_fun]
                varin = len(called_fun.input_args)
                counter_in = varin
                instruction_counter = -1
                while(counter_in > 0):
                    current_instruction = self.instructions[instruction_id + instruction_counter]
                    op_code = current_instruction.op_code
                    if (op_code == 0):
                        counter_in = counter_in - 1 #A single value has been pushed to the stack, it is an argument to the function
                    elif (op_code == 1): #not likely to happen, buuuut
                        popped_els = current_instruction.operands[0].value/4
                        counter_in = counter_in + popped_els
                    elif (op_code == 2):  #We retrieved the value of a previous push, but it's still a push
                        counter_in = counter_in - 1
                    elif (op_code == 3):  #Likely the same thing
                        counter_in = counter_in - 1
                    elif (op_code == 4):  #Likely the same thing
                        counter_in = counter_in - 1
                    elif (op_code == 5):  #We pop
                        counter_in = counter_in + 1
                    elif (op_code == 7): 
                        counter_in = counter_in - 1
                    elif (op_code == 8): 
                        counter_in = counter_in + 1
                    elif (op_code == 9): 
                        counter_in = counter_in - 1
                    elif (op_code == 0x0A): 
                        counter_in = counter_in + 1
                    elif (op_code == 0x0D): #not only exiting/entering the functions are tricky stack wise, but it should actually never happen here (why exit before the call, unless we missed something...)
                        raise ValueError('Unable to identify the return address of a function.')
                    elif (op_code == 0x0C): #why call another function before the parameters were all pushed... if that happens, fuck
                        raise ValueError('Unable to identify the return address of a function.')
                    elif (op_code == 0x0E): 
                        counter_in = counter_in + 1
                    elif (op_code == 0x0F): 
                        counter_in = counter_in + 1
                    elif ((op_code >= 0x10) and(op_code <= 0x1E)):#Operations with two operands: the two are discarded and one (the result) is pushed => overall we popped one
                        counter_in = counter_in + 1
                    elif ((op_code >= 0x1F) and (op_code <= 0x21)): #A single operand popped and the result is pushed => nothing changes in terms of stack occupation
                        counter_in = counter_in + 1 - 1
                    elif ((op_code == 0x22) or (op_code == 0x23) or (op_code == 0x24)): #For the same reason a regular call shouldn't happen here
                        raise ValueError('Unable to identify the return address of a function.')
                    elif ((op_code == 0x25) or (op_code == 0x27)): #Probably the instructions I understand the less, I think it shouldn't happen though.
                        raise ValueError('Unable to identify the return address of a function.')
                    elif (op_code == 0x28): 
                        counter_in = counter_in + 1
                    instruction_counter = instruction_counter - 1
                last_instruction = self.instructions[instruction_id + instruction_counter]
                
                if (last_instruction.name == "PushUndefined"): #For safety but should always be the case
                    self.instructions[instruction_id + instruction_counter].name = "PushReturnAddress"
                    addr = last_instruction.operands[0].value
                    if addr in ED9InstructionsSet.locations_dict:
                        label = ED9InstructionsSet.locations_dict[addr]
                    else:
                        label = "Loc_"+ str(ED9InstructionsSet.location_counter)
                        ED9InstructionsSet.locations_dict[addr] = label
                        ED9InstructionsSet.location_counter = ED9InstructionsSet.location_counter + 1
                    self.instructions[instruction_id + instruction_counter].operands[0] = ED9InstructionsSet.operand(label, False)
                    #The previous instruction is likely where the call really starts, it pushes a small unsigned integer (maybe some kind of stack size allocated for the called function?)
                    self.instructions[instruction_id + instruction_counter - 1].text_before = "#Calling " + called_fun.name + "\n    "





def parse(name: Union[str, bytes, os.PathLike]) -> None:
    global smallest_data_ptr

    filename = Path(name).stem
    filesize = os.path.getsize(name)
    with open(name, "rb") as dat_file:
       
        parsed_script = script(dat_file)
        parsed_script.write(dat_file)
        


if __name__ == "__main__":
    parse(sys.argv[1])
