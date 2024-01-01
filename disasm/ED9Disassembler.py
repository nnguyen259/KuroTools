import math
import struct
import os
from pathlib import Path
from lib.parser import process_data, readint, readintoffset, readtextoffset, remove2MSB, get_actual_value_str
from disasm.script import script
import disasm.ED9InstructionsSet as ED9InstructionsSet
import traceback
from processcle import processCLE

def get_var_symbol(var_names, stack) -> str:
    if len(stack)-1 not in var_names:
        var_names[len(stack)-1] = "VAR_" + str(len(stack)-1)
        output = var_names[len(stack)-1]
    else:
        output = var_names[len(stack)-1]
    return output

class ED9Disassembler(object):
    def __init__(self, markers, decomp):
        self.markers = markers
        self.decomp = decomp
        self.smallest_data_ptr = -1
        self.dict_stacks = {}
        self.instruction_stacks = {}
        self.variables_names = {}
        self.stream = None

    def parse(self, path):
        filename = Path(path).stem
        filesize = os.path.getsize(path)

        self.stream = open(path, "rb")
        magic = self.stream.read(4)
        if magic != b"#scp":
            with open(path, mode='rb') as encrypted_file: 
                fileContent = encrypted_file.read()
            decrypted_file = processCLE(fileContent)
            with open(path, "w+b") as outputfile:
                outputfile.write(decrypted_file)
            filesize = os.path.getsize(path)
            self.stream = open(path, "rb")
            
        self.stream.seek(0)
        self.smallest_data_ptr = filesize
        self.script = script(self.stream, filename, markers = self.markers)
        self.write_script()


    def write_script(self):
        python_file = open(self.script.name + ".py", "wt",encoding='utf8')
        python_file.write("from disasm.ED9Assembler import *\n\n")
        python_file.write("def script():\n")
        python_file.write("\n    create_script_header(\n")
        python_file.write("\tname= \"" + self.script.name+"\",\n")
        python_file.write("\tvarin= " + "[")
        for id_in in range(len(self.script.script_variables_in) - 1):
            python_file.write("[")
            python_file.write(self.wrap_conversion(self.script.script_variables_in[id_in][0]) + ", ")
            python_file.write(self.wrap_conversion(self.script.script_variables_in[id_in][1])) 
            python_file.write("],")
        if (len(self.script.script_variables_in) != 0):
            python_file.write("[")
            python_file.write(self.wrap_conversion(self.script.script_variables_in[len(self.script.script_variables_in) - 1][0]) + ", ")
            python_file.write(self.wrap_conversion(self.script.script_variables_in[len(self.script.script_variables_in) - 1][1])) 
            python_file.write("]")
            
        python_file.write("],\n")

        python_file.write("\tvarout= " + "[")
        for id_in in range(len(self.script.script_variables_out) - 1):
            python_file.write("[")
            python_file.write(self.wrap_conversion(self.script.script_variables_out[id_in][0]) + ", ")
            python_file.write(self.wrap_conversion(self.script.script_variables_out[id_in][1])) 
            python_file.write("],")
        if (len(self.script.script_variables_out) != 0):
            python_file.write("[")
            python_file.write(self.wrap_conversion(self.script.script_variables_out[len(self.script.script_variables_out) - 1][0]) + ", ")
            python_file.write(self.wrap_conversion(self.script.script_variables_out[len(self.script.script_variables_out) - 1][1])) 
            python_file.write("]")
        python_file.write("],\n")

        python_file.write("    )\n")

        functions_sorted_by_addr = self.script.functions.copy()
        functions_sorted_by_addr.sort(key=lambda fun: fun.start) 

        for f in self.script.functions:
            python_file.write(self.add_function_str(f))

        if (self.decomp == False):
            for f in functions_sorted_by_addr:
                self.add_return_addresses(f)
                python_file.write(self.disassemble_function(f))
        else:
            for f in functions_sorted_by_addr:
                python_file.write(self.decompile_function(f))

        python_file.write("\n    compile()")
        python_file.write("\n\nscript()")
        python_file.close()


    def add_function_str(self, function)->str:

        result = "    add_function(\n"
        result = result + "\tname= " + "\"" + function.name + "\",\n"
        result = result + "\tinput_args  = " + "["
        for id_in in range(len(function.input_args) - 1):
            result = result + self.wrap_conversion(function.input_args[id_in]) + ", "
        if (len(function.input_args) != 0):
            result = result + self.wrap_conversion(function.input_args[len(function.input_args) - 1]) 
        result = result + "],\n"

        result = result + "\toutput_args = " + "["
        for id_in in range(len(function.output_args) - 1):
            result = result + self.wrap_conversion(function.output_args[id_in]) + ", "
        if (len(function.output_args) != 0):
            result = result + self.wrap_conversion(function.output_args[len(function.output_args) - 1]) 
        result = result + "],\n"

        result = result + "\tb0= " +  str(hex(function.b0)) + ",\n"
        result = result + "\tb1= " +  str(hex(function.b1)) + ",\n"
        result = result + "    )\n\n"
        return result

    def update_stack(self, instruction, stack, instruction_id):
        try:
            functions = self.script.functions

            if instruction.op_code == 0x26: 
                pass  
            else: 
                
                op_code = instruction.op_code
                #print(str(hex(op_code)), " ", str(stack), " ", str(hex(instruction.addr)))
                if (op_code == 1): 

                    popped_els = int(instruction.operands[0].value/4)
                    for i in range(popped_els):
                        stack.pop()

                elif (op_code == 0) or (op_code == 4):
                    
                    stack.append(instruction_id)
                elif (op_code == 2) or (op_code == 3):
                    stack.append(instruction_id)
                elif (op_code == 5): 
                    stack.pop()
                elif (op_code == 6):  #We pop
                    #index1 = int(len(stack) + instruction.operands[0].value/4)
                    #index2 = stack[index1]
                    #stack[index2] = instruction_id
                    stack.pop()
                elif (op_code == 7): 
                    stack.append(instruction_id)
                elif (op_code == 8): 
                    stack.pop()
                elif (op_code == 9): 
                    stack.append(instruction_id)
                elif (op_code == 0x0A): 
                    stack.pop()
                elif (op_code == 0x0B):
                    pass
                elif (op_code == 0x0D):
                    pass 
                elif (op_code == 0x0C): 
                    index_fun = instruction.operands[0].value
                    called_fun = functions[index_fun]
                    varin = len(called_fun.input_args)
                    for i in range(varin + 2): 
                        stack.pop()
                elif (op_code == 0x0E): 
                    stack.pop()
                elif (op_code == 0x0F):
                    stack.pop()
                elif ((op_code >= 0x10) and(op_code <= 0x1E)):
                    stack.pop() 
                    stack.pop()
                    stack.append(instruction_id)
                elif ((op_code >= 0x1F) and (op_code <= 0x21)): 
                    stack.pop()
                    stack.append(instruction_id)
                elif (op_code == 0x22):
                    varin = instruction.operands[2].value
                    for i in range(varin + 5): 
                        stack.pop()
                elif (op_code == 0x23):
                    pass
                    
                elif (op_code == 0x24):
                    varin = instruction.operands[0].value
                    
                elif (op_code == 0x25):
                      stack.append(instruction_id)
                      stack.append(instruction_id)
                      stack.append(instruction_id)
                      stack.append(instruction_id)
                      stack.append(instruction_id)
                elif (op_code == 0x27):
                    count = instruction.operands[0].value
                    for i in range(count):
                        stack.pop()
        except Exception as err:
            print("WARNING: Something unexpected happening at address ", hex(instruction.addr))
            #print(err, traceback.format_exc())
                
    def add_var_to_stack(self, instruction, stack)->str:
        result = ""
        if len(stack)-1 not in self.variables_names:
            self.variables_names[len(stack)-1] = "VAR_" + str(len(stack)-1)
            output = self.variables_names[len(stack)-1]
        else:
            #The variable already exists, it can also happen in a push, in that case it becomes a SetVar
            output = self.variables_names[len(stack)-1]

        if (instruction.op_code == 5):
            index_referred = int((len(stack)) + instruction.operands[0].value/4 - 1)
            input = output
            output = self.variables_names[index_referred]
            result = "SetVarToAnotherVarValue(\""+ output + "\", input=\"" + input + "\")"
        elif (instruction.op_code == 6):
            index_referred = int((len(stack)) + instruction.operands[0].value/4 - 1)
            index_str = self.variables_names[index_referred]
            top_of_the_stack = self.variables_names[len(stack) - 1]
            result = "WriteAtIndex(\""+ top_of_the_stack + "\", index=\"" + index_str + "\")"
   
        return result


    def get_expression_str(self, instructions, instr_id, stack)->str:#from the first operand to the last operator if any
        result = ""
        parameters_str = []
        i = instr_id
        copy_stack = stack.copy()
        checkpoint = instr_id
        checkpoint_str = 0
        stack_checkpoint = copy_stack.copy()
        counter_exp = 0
        while i < len(instructions):
            instruction = instructions[i]
            op_code = instruction.op_code 
            if (op_code == 0):
                counter_exp = counter_exp + 1
                parameters_str.append(self.wrap_conversion(instruction.operands[0].value)) 
            elif (op_code == 2): 
                counter_exp = counter_exp + 1
                
                idx = int(len(copy_stack) + instruction.operands[0].value/4)
                variable_name = self.variables_names[idx]
                parameters_str.append("LoadVar(\""+ variable_name + "\")")
            elif (op_code == 3): 
                counter_exp = counter_exp + 1
                idx = int(len(copy_stack) + instruction.operands[0].value/4)
                variable_name = self.variables_names[idx]
                parameters_str.append("LoadVar2(\""+ variable_name + "\")")
            elif (op_code == 4): 
                counter_exp = counter_exp + 1
                parameters_str.append("LoadInt("+ str(instruction.operands[0].value) + ")")
            elif (op_code == 5): 
                break
            elif (op_code == 6): 
                break
            elif (op_code == 7): 
                counter_exp = counter_exp + 1
                parameters_str.append("Load32("+ str(instruction.operands[0].value) + ")")
            elif (op_code == 8): 
                break
            elif (op_code == 9): 
                counter_exp = counter_exp + 1
                parameters_str.append("LoadResult("+ str(instruction.operands[0].value) + ")")
            elif (op_code == 0x0A): 
                break
            elif (op_code == 0x0D): 
                break
            elif (op_code == 0x0C): #why call another function before the parameters were all pushed... if that happens, fuck
                break
            elif (op_code == 0x0E): 
                break
            elif (op_code == 0x0F): 
                break
            elif ((op_code >= 0x10) and(op_code <= 0x1E)):#Operations with two operands: the two are discarded and one (the result) is pushed => overall we popped one
                counter_exp = counter_exp - 1
                lowercase_name = instruction.name.lower()
                param_count = len(parameters_str)
    
                idx_top = len(copy_stack) - 1
                idx_top2 = len(copy_stack) - 2
    
                if len(parameters_str) == 0:
                    counter_exp = counter_exp + 1
                    variable_name_right = self.variables_names[idx_top]
                    
                    right = "TopVar(\"" + variable_name_right + "\")"
                else:
                    right = parameters_str[param_count - 1]
                    parameters_str.pop()
    
                if len(parameters_str) == 0: 
                    counter_exp = counter_exp + 1
                    variable_name_left = self.variables_names[idx_top2]
                    left = "TopVar(\"" + variable_name_left + "\")"
                else:
                    left = parameters_str[param_count - 2]
                    parameters_str.pop()
                full_instr_str = lowercase_name + "(" + left + ", " + right + ")"
                parameters_str.append(full_instr_str)
                
                
            elif ((op_code >= 0x1F) and (op_code <= 0x21)): #A single operand popped and the result is pushed => nothing changes in terms of stack occupation
                
                lowercase_name = instruction.name.lower()
                param_count = len(parameters_str)
                idx_top = len(copy_stack) - 1
                if len(parameters_str) == 0: 
                    counter_exp = counter_exp + 1
                    variable_name = self.variables_names[idx_top]
                    value = "TopVar(\"" + variable_name + "\")" 
                else:
                    value = parameters_str[param_count - 1]
                    parameters_str.pop()
                
                full_instr_str = lowercase_name + "(" + value + ")"
                parameters_str.append(full_instr_str)
    
                
    
            elif ((op_code == 0x22) or (op_code == 0x23) or (op_code == 0x24)): #For the same reason a regular call shouldn't happen here
                break
            elif (op_code == 0x25): #adds the return address and the current function address to the stack
                break
            elif (op_code == 0x27): 
                break
    
            self.update_stack(instruction, copy_stack, i)
            if counter_exp == 1:
                checkpoint = i
                checkpoint_str = len(parameters_str) - 1
                stack_checkpoint = copy_stack.copy()

            i = i + 1
    
        for j in range(checkpoint_str, len(parameters_str) - 1):
            parameters_str.pop()
    
        for parameter_str in parameters_str:
            result = result + parameter_str + ", "  
        if len(result) > 0:
            result = result[:-2]
        
        if len(stack_checkpoint)-1 not in self.variables_names.keys():
            self.variables_names[len(stack_checkpoint)-1] = "VAR_" + str(len(stack_checkpoint)-1)
            output = self.variables_names[len(stack_checkpoint)-1]
        else:
            output = self.variables_names[len(stack_checkpoint)-1]
        return ("AssignVar(" + "\"" + output + "\", " + result + ")", checkpoint - instr_id)
    
    def get_instruction_number_for_expression(self, instructions, start)->int:
        result = ""
        parameters_str = []
        i = start
        expected_operands = 1
        while expected_operands > 0:
            instruction = instructions[i]
            op_code = instruction.op_code 
            if (op_code == 0):
                expected_operands = expected_operands - 1
            elif (op_code == 2):  
                expected_operands = expected_operands - 1
            elif (op_code == 3):  
                expected_operands = expected_operands - 1
            elif (op_code == 4): 
                expected_operands = expected_operands - 1
            elif (op_code == 7): 
                expected_operands = expected_operands - 1
            elif (op_code == 9): 
                expected_operands = expected_operands - 1
            
            elif ((op_code >= 0x10) and(op_code <= 0x1E)):#Operations with two operands: the two are discarded and one (the result) is pushed => overall we popped one
                expected_operands = expected_operands - 1 + 2
                
            elif ((op_code >= 0x1F) and (op_code <= 0x21)): #A single operand popped and the result is pushed => nothing changes in terms of stack occupation
                pass
            
            elif (op_code == 0x26): 
                pass
            else: 
                break
            i = i - 1
        
        return start - i
    
    def get_param_str_from_instructions(self, instructions, start, end)->str:
        result = ""
        parameters_str = []
        for i in range(start, end + 1):
            instruction = instructions[i]
            op_code = instruction.op_code 
            
            if (op_code == 0):
                parameters_str.append(self.wrap_conversion(instruction.operands[0].value)) 
            elif (op_code == 2): 
                stack = self.instructions_stacks[i]
                idx = int(len(stack) + instruction.operands[0].value/4)
                variable_name = self.variables_names[idx]
                parameters_str.append("LoadVar(\""+ variable_name + "\")")
            elif (op_code == 3): 
                stack = self.instructions_stacks[i]
                idx = int(len(stack) + instruction.operands[0].value/4)
                variable_name = self.variables_names[idx]
                parameters_str.append("LoadVar2(\""+ variable_name + "\")")
            elif (op_code == 4): 
                parameters_str.append("LoadInt("+ str(instruction.operands[0].value) + ")")
            elif (op_code == 5): 
                raise ValueError('Should not happen.') 
            elif (op_code == 6): 
                raise ValueError('Should not happen.')
            elif (op_code == 7): 
                parameters_str.append("Load32("+ str(instruction.operands[0].value) + ")")
            elif (op_code == 8): 
                raise ValueError('Should not happen.')
            elif (op_code == 9): 
                parameters_str.append("LoadResult("+ str(instruction.operands[0].value) + ")")
            elif (op_code == 0x0A): 
                raise ValueError('Should not happen.')
            elif (op_code == 0x0D): 
                raise ValueError('Should not happen.')
            elif (op_code == 0x0C): #why call another function before the parameters were all pushed... if that happens, fuck
                raise ValueError('Should not happen.')
            elif (op_code == 0x0E): 
                raise ValueError('Should not happen.')
            elif (op_code == 0x0F): 
                raise ValueError('Should not happen.')
            elif ((op_code >= 0x10) and(op_code <= 0x1E)):#Operations with two operands: the two are discarded and one (the result) is pushed => overall we popped one
                lowercase_name = instruction.name.lower()
                param_count = len(parameters_str)
    
                stack = self.instructions_stacks[i]
                idx_top = len(stack) - 1
                idx_top2 = len(stack) - 2
    
                if len(parameters_str) == 0:
                    variable_name_right = self.variables_names[idx_top]
                    
                    right = "TopVar(\"" + variable_name_right + "\")" 
                else:
                    right = parameters_str[param_count - 1]
                    parameters_str.pop()
    
                if len(parameters_str) == 0: 
                    variable_name_left = self.variables_names[idx_top2]
                    left = "TopVar(\"" + variable_name_left + "\")" 
                   
                else:
                    left = parameters_str[param_count - 2]
                    parameters_str.pop()
                full_instr_str = lowercase_name + "(" + left + ", " + right + ")"
                parameters_str.append(full_instr_str)
                
                
            elif ((op_code >= 0x1F) and (op_code <= 0x21)): #A single operand popped and the result is pushed => nothing changes in terms of stack occupation
                lowercase_name = instruction.name.lower()
                param_count = len(parameters_str)
                stack = self.instructions_stacks[i]
                idx_top = len(stack) - 1
                if len(parameters_str) == 0: 
                    variable_name = self.variables_names[idx_top]
                    
                    variable_name = self.variables_names[idx_top]
                    value = "\"" + variable_name + "\""
                else:
                    value = parameters_str[param_count - 1]
                    parameters_str.pop()
                
                full_instr_str = lowercase_name + "(" + value + ")"
                parameters_str.append(full_instr_str)
                
            elif ((op_code == 0x22) or (op_code == 0x23) or (op_code == 0x24)): #For the same reason a regular call shouldn't happen here
                raise ValueError('Should not happen.')
            elif (op_code == 0x25): #adds the return address and the current function address to the stack
                raise ValueError('Should not happen.')
            elif (op_code == 0x27): 
                raise ValueError('Should not happen.')
        parameters_str.reverse()
        for parameter_str in parameters_str:
            result = result + parameter_str + ", "  
        if len(result) > 0:
            result = result[:-2]
        return result 
    
    
    
    def make_function_py_header(self, function)->str:
        result = "#-------------------------\n"
        result = result + "#original file addr: " + str(hex(function.start)) + "\n"
        result = result + "    set_current_function(\""+ function.name + "\")\n"
        for id_strct in range(len(function.structs)):
            result = result + "    add_struct(\n"
            result = result + "\tid = " + str((function.structs[id_strct]["id"]))+",\n"
            result = result + "\tnb_sth1 = " + str(hex(function.structs[id_strct]["nb_sth1"]))+",\n"

            result = result + "\tarray2 = ["
            for id_in in range(len(function.structs[id_strct]["array2"]) - 1):
                result = result + self.wrap_conversion(function.structs[id_strct]["array2"][id_in]) + ", "
            if (len(function.structs[id_strct]["array2"]) != 0):
                result = result + self.wrap_conversion(function.structs[id_strct]["array2"][len(function.structs[id_strct]["array2"])- 1]) 
            result = result + "],\n"

            result = result + "    )\n\n"
        return result

    def disassemble_instructions(self, function)->str:
        result = "#Instructions " + function.name + "\n\n"   
        for instruction in function.instructions:
            if instruction.addr in ED9InstructionsSet.locations_dict:
                result = result + "\n    Label(\""+ED9InstructionsSet.locations_dict[instruction.addr]+"\")\n\n"
            if instruction.op_code == 0x26 and self.markers == False: #Line Marker, we can separate with a new line
                result = result + "\n"
            else:
                result = result + "    " + instruction.to_string(self.stream) + "\n"
        return result

    def disassemble_function(self, function) -> str:

        fun_header = self.make_function_py_header(function)
        instructions = self.disassemble_instructions(function)
        
        return fun_header + instructions

    def decompile_function(self, function) -> str:

        fun_header = self.make_function_py_header(function)
        instructions = self.decompile_instructions(function)
        
        return fun_header + instructions

    

    def decompile_instructions(self, function) -> str:
        
        functions = self.script.functions
        result = "#Instructions " + function.name + "\n\n"   
        stack = [] #will contain the address of when the data was pushed onto the stack

        self.variables_names = {} #Key: the id of the first push, Value: a str, the name of the variable
        self.dict_stacks = {} #Key: the destination of a jump, Value: the stack state at the jump
        self.instructions_stacks = [] #record the stack for each instruction

        string_list = [] #line by line
        

        #first we add the input parameters of the function to the stack
        for in_id in range(len(function.input_args)):
            stack.append(-in_id -1)
            self.variables_names[in_id] = "PARAM_" + str(in_id)

        instruction_id = 0

        while instruction_id < len(function.instructions):

            skip = False

            decompiled_str = ""
            instruction = function.instructions[instruction_id]
            #If a label appears before reaching the jump(s), we continue with the current stack. If there was at least a jump
            #for this label, we recorded the stack earlier so we restore it
            if instruction.addr in ED9InstructionsSet.locations_dict:
                if ED9InstructionsSet.locations_dict[instruction.addr] in self.dict_stacks:
                    stack = self.dict_stacks[ED9InstructionsSet.locations_dict[instruction.addr]]

            self.instructions_stacks.append(stack.copy())
            
            if instruction.op_code == 0x26: #Line Marker, we can separate with a new line, and get rid of the instruction 
                if self.markers == True:
                    string_list.append(instruction.to_string(self.stream))
                else:
                    string_list.append("")
                instruction_id = instruction_id + 1
            else: #We try to reproduce the stack at any given point, to get rid of the stack index-based instructions (OP 2,3,4,5,6) in function and command calls 
                #if we encounter a jump of any sort, we store the content of the stack, and when we reach the destination, we restore that stack. The actual values don't matter, it is just used as an unique ID
                op_code = instruction.op_code
                
                #Try to parse an expression
                expressions_op_code = [0,2,3,4,7,9,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x20,0x21]
                if op_code in expressions_op_code:
                    (expr, nb_instr) = self.get_expression_str(function.instructions, instruction_id, stack)
                    string_list.append(expr)
                    self.update_stack(function.instructions[instruction_id], stack, instruction_id)
                    instruction_id = instruction_id + 1
                    for i in range(1, nb_instr+1):
                        self.instructions_stacks.append(stack.copy())
                        string_list.append("")
                       
                        self.update_stack(function.instructions[instruction_id], stack, instruction_id)
                        instruction_id = instruction_id + 1
                else:   
                
                
                    if (op_code == 5): 
                        decompiled_str = self.add_var_to_stack(instruction, stack)
                   
                    elif (op_code == 6):  #We pop
                        
                        decompiled_str = self.add_var_to_stack(instruction, stack)
                       
                
                    elif (op_code == 0x0B):
                        if instruction.operands[0].value in self.dict_stacks:
                            pass
                        else:
                            self.dict_stacks[instruction.operands[0].value] = stack.copy()
                    elif (op_code == 0x0D):
                        
                        varin = len(function.input_args)
                        if varin > 0:
                            string_list[len(string_list) - 1] = ""
                        decompiled_str = "Return()"
                        if instruction_id != len(function.instructions) - 1:
                            skip = True
                            string_list.append(decompiled_str)
                            instruction_id = instruction_id + 1
                            instruction = function.instructions[instruction_id]
                            while instruction.addr not in ED9InstructionsSet.locations_dict:
                                if (instruction.op_code == 0x26 and self.markers == True) or (instruction.op_code != 0x26):
                                    string_list.append(instruction.to_string(self.stream))
                                else:
                                    string_list.append("")
                                self.instructions_stacks.append([])
                                instruction_id = instruction_id + 1
                                if instruction_id > len(function.instructions) - 1:
                                    break
                                instruction = function.instructions[instruction_id]
                            
                    elif (op_code == 0x0C): 
                        index_fun = function.instructions[instruction_id].operands[0].value
                        called_fun = functions[index_fun]
                        varin = len(called_fun.input_args)
                        (start, remaining_params) = find_start_function_call(function.instructions, instruction_id, varin)                        
                        index_start = instruction_id + start
                        index_end = instruction_id - 1
                        params = self.get_param_str_from_instructions(function.instructions, index_start, index_end)
                        #Every parameter that has not been retrieved by the previous function was pushed some time ago and put in a variable,
                        #We don't want to compile them again, so we add them to the call just to inform the user using TopVar
                        range_start=len(stack) - varin + remaining_params
                        range_stop=len(stack) - varin
                        #Ceiling the start and stop cause sometimes the value comes as fractions when decompiling .dats in Ys X
                        params_id = range(math.floor(range_start) , math.floor(range_stop),-1)
                        decompiled_str =  "\"" + called_fun.name + "\", ["
                        ##print(called_fun.name)
                        ##print("\n")
                        additional_parameters = ""
                        for param_id in params_id:
                            additional_parameters = "TopVar(\"" + self.variables_names[param_id] + "\")," + additional_parameters
                            ##print(self.variables_names)
                            ##print("\n")
                        additional_parameters = additional_parameters[:-1]
                            
                        all_params = ""
                        if (len(additional_parameters)>0):  
                            all_params = additional_parameters
                        if (len(params)>0):
                            if (len(all_params)>0):
                                all_params = all_params + ", " + params
                            else: 
                                all_params = params
                        else:
                            all_params = all_params[:-1]
                        decompiled_str = decompiled_str + all_params + "]"
                        for i in range(index_start, index_end + 1): 
                            string_list[i] = ""
                        #removing return address and function index too
                        idx_return_addr = stack[len(stack) - 1 - varin]
                        #If there is something between the return address and the parameters being pushed just before the function call, we play it safe and 
                        #don't decompile in a single function call
                        if index_start - idx_return_addr > 1:
                            decompiled_str = "CallFunctionWithoutReturnAddr(" + decompiled_str + ")"
                            
                            addr = function.instructions[idx_return_addr].operands[0].value
                            function_index = function.instructions[idx_return_addr - 1].operands[0].value
                            if addr in ED9InstructionsSet.locations_dict:
                                label = ED9InstructionsSet.locations_dict[addr]
                            else:
                                label = "Loc_"+ str(ED9InstructionsSet.location_counter)
                                ED9InstructionsSet.locations_dict[addr] = label
                                ED9InstructionsSet.location_counter = ED9InstructionsSet.location_counter + 1

                            #both following pushes will need variable names, which were added previously while going through the expression
                            #the stack at this point is 
                            pos_return = len(stack) - 1 - varin
                            pos_caller_index = len(stack) - 2 - varin
                            if pos_return in self.variables_names.keys():
                                return_addr_var = self.variables_names[pos_return]
                            else:
                                return_addr_var = "VAR_" + str(pos_return)
                            
                            if pos_caller_index in self.variables_names.keys():
                                caller_index_var = self.variables_names[pos_caller_index]
                            else:
                                caller_index_var = "VAR_" + str(pos_caller_index)


                            string_list[idx_return_addr] = "AssignVar(\""+return_addr_var + "\", ReturnAddress(\"" + label + "\"))"
                            string_list[idx_return_addr - 1] = "AssignVar(\""+caller_index_var + "\", CallerID())"
                        else:
                            decompiled_str = "CallFunction(" + decompiled_str + ")"
                            for i in range(idx_return_addr - 1, idx_return_addr + 1): 
                                string_list[i] = ""
                    
                    elif (op_code == 0x0E): 

                        nb_instr = self.get_instruction_number_for_expression(function.instructions, instruction_id - 1)
                        index_start = instruction_id - nb_instr
                        index_end = instruction_id - 1
                        params = self.get_param_str_from_instructions(function.instructions, index_start, index_end)
                        decompiled_str =  "JumpWhenTrue(\"" + function.instructions[instruction_id].operands[0].value + "\", "+ params + ")"
                        for i in range(nb_instr): #removing return address and function index too
                            string_list[index_start + i] = ""
                    
                        if instruction.operands[0].value in self.dict_stacks:
                            pass
                        else:
                            self.dict_stacks[instruction.operands[0].value] = stack.copy()
                            self.dict_stacks[instruction.operands[0].value].pop()
                    elif (op_code == 0x0F): 
                        nb_instr = self.get_instruction_number_for_expression(function.instructions, instruction_id - 1)
                        index_start = instruction_id - nb_instr
                        index_end = instruction_id - 1
                        params = self.get_param_str_from_instructions(function.instructions, index_start, index_end)
                        decompiled_str =  "JumpWhenFalse(\"" + function.instructions[instruction_id].operands[0].value + "\", "+ params + ")"
                        for i in range(nb_instr): #removing return address and function index too
                            string_list[index_start + i] = ""
                    
                        if instruction.operands[0].value in self.dict_stacks:
                            pass
                        else:
                            self.dict_stacks[instruction.operands[0].value] = stack.copy()
                            self.dict_stacks[instruction.operands[0].value].pop()
                
                    elif (op_code == 0x22):
                        script_file = get_actual_value_str(self.stream, function.instructions[instruction_id].operands[0].value)
                        called_fun = get_actual_value_str(self.stream, function.instructions[instruction_id].operands[1].value)
                        varin = function.instructions[instruction_id].operands[2].value
                        (start, remaining_params) = find_start_function_call(function.instructions, instruction_id, varin)                        
                        index_start = instruction_id + start
                        index_end = instruction_id - 1
                        params = self.get_param_str_from_instructions(function.instructions, index_start, index_end)
                        #Every parameter that has not been retrieved by the previous function was pushed some time ago and put in a variable,
                        #We don't want to compile them again, so we add them to the call just to inform the user using TopVar
                        params_id = range(len(stack) - varin + remaining_params ,len(stack) - varin, -1)
                        decompiled_str =  script_file + ", " + called_fun + ", ["
                        additional_parameters = ""
                        for param_id in params_id:
                            additional_parameters = "TopVar(\"" + self.variables_names[param_id] + "\")," + additional_parameters
                        additional_parameters = additional_parameters[:-1]
                        all_params = ""
                        if (len(additional_parameters)>0):  
                            all_params = additional_parameters
                            
                        if (len(params)>0):
                            if (len(all_params)>0):
                                all_params = all_params + ", " + params
                            else: 
                                all_params = params
                        else:
                            all_params = all_params[:-1]
                        decompiled_str = decompiled_str + all_params + "]"
                        
                        for i in range(index_start, index_end + 1): 
                            string_list[i] = ""

                        idx_return_addr = stack[len(stack) - 1 - varin]

                        if index_start - idx_return_addr > 1:
                            decompiled_str = "CallFunctionFromAnotherScriptWithoutReturnAddr(" + decompiled_str + ")"
                            
                            addr = function.instructions[idx_return_addr].operands[0].value
                            if addr in ED9InstructionsSet.locations_dict:
                                label = ED9InstructionsSet.locations_dict[addr]
                            else:
                                label = "Loc_"+ str(ED9InstructionsSet.location_counter)
                                ED9InstructionsSet.locations_dict[addr] = label
                                ED9InstructionsSet.location_counter = ED9InstructionsSet.location_counter + 1
                            string_list[idx_return_addr] = "PUSHRETURNADDRESSFROMANOTHERSCRIPT(\"" + label + "\")"
                            
                        else:
                            decompiled_str = "CallFunctionFromAnotherScript(" + decompiled_str + ")"
                            string_list[idx_return_addr] = ""
                    
                    elif (op_code == 0x23):
                        script_file = get_actual_value_str(self.stream, function.instructions[instruction_id].operands[0].value)
                        called_fun = get_actual_value_str(self.stream, function.instructions[instruction_id].operands[1].value)
                        varin = function.instructions[instruction_id].operands[2].value
                        start_params = 0
                        if varin > 0:
                            start_params = varin * 2 #The successive Load and Save results
                            if (function.instructions[instruction_id - 1 - varin].op_code == 1):
                                start_params = start_params + 1 
                        else:
                            if (function.instructions[instruction_id - 1].op_code == 1):
                                string_list[instruction_id - 1] = ""
                                stack = self.instructions_stacks[instruction_id - 1]
                            
                        #if there is something in the stack, it will need to be removed, including the input params
                        #here start should point to the first instruction likely to be the last parameter of the function
                        start_params = instruction_id - start_params 
                        (start, remaining_params) = find_start_function_call(function.instructions, start_params, varin)                        
                        index_start = start_params + start
                        index_end = start_params - 1
                        params = self.get_param_str_from_instructions(function.instructions, index_start, index_end)
                        decompiled_str =  "CallFunctionFromAnotherScript2(" + script_file + ", " + called_fun +", ["
                        params_id = range(len(stack) - varin + remaining_params ,len(stack) - varin ,-1)
                        additional_parameters = ""
                        for param_id in params_id:
                            additional_parameters = "TopVar(\"" + self.variables_names[param_id] + "\")," + additional_parameters 
                        additional_parameters = additional_parameters[:-1]
                        all_params = ""
                        if (len(additional_parameters)>0):  
                            all_params = additional_parameters
                            
                        if (len(params)>0):
                            if (len(all_params)>0):
                                all_params = all_params + ", " + params
                            else: 
                                all_params = params
                        else:
                            all_params = all_params[:-1]
                        decompiled_str = decompiled_str + all_params + "])"
                        
                        for i in range(index_start, instruction_id): #We remove all POPs/Load and Save results
                            string_list[i] = ""

                        if varin > 0:
                            stack = self.instructions_stacks[index_start]
                            
                        
                    elif (op_code == 0x24):
                        varin = function.instructions[instruction_id].operands[0].value
                        #For a command call we remove the final pop only
                        (start, remaining_params) = find_start_function_call(function.instructions, instruction_id, varin)                        
                        index_start = instruction_id + start
                        index_end = instruction_id - 1
                        params = self.get_param_str_from_instructions(function.instructions, index_start, index_end)
                        decompiled_str =  "Command(\"" + function.instructions[instruction_id].operands[1].value + "\", ["
                        params_id = range(len(stack) - varin + remaining_params ,len(stack) - varin ,-1)
                        additional_parameters = ""
                        for param_id in params_id:
                            additional_parameters = "TopVar(\"" + self.variables_names[param_id] + "\")," + additional_parameters 
                        additional_parameters = additional_parameters[:-1]
                        all_params = ""
                        if (len(additional_parameters)>0):  
                            all_params = additional_parameters
                            
                        if (len(params)>0):
                            if (len(all_params)>0):
                                all_params = all_params + ", " + params
                            else: 
                                all_params = params
                        else:
                            all_params = all_params[:-1]
                        decompiled_str = decompiled_str + all_params + "])"
                        
                        for i in range(index_start, index_end + 1): 
                            string_list[i] = ""
                    
                        if varin > 0:
                            instruction_id = instruction_id + 1 #skip the pop
                            self.instructions_stacks.append(stack.copy())
                            for i in range(varin): 
                                self.instructions_stacks[len(self.instructions_stacks) - 1].pop()
                            string_list.append("")
                    elif (op_code == 0x25):
                          pass
                    elif (op_code == 0x27):
                        count = instruction.operands[0].value
                    
                    if (skip == False):
                        if (len(decompiled_str)>0):
                            string_list.append(decompiled_str)
                        else:
                            string_list.append(instruction.to_string(self.stream))
                        self.update_stack(function.instructions[instruction_id], stack, instruction_id)
                        instruction_id = instruction_id + 1
           

        for instruction_id in range(len(function.instructions)):
            instruction = function.instructions[instruction_id]
            if instruction.addr in ED9InstructionsSet.locations_dict:
                result = result + ("\n    Label(\""+ED9InstructionsSet.locations_dict[instruction.addr]+"\")\n\n")
            line = string_list[instruction_id]
            if len(line) > 0:
                line = "    " + line + "\n"
            result = result + line
        return result


    def add_return_addresses(self, function): 
        functions = self.script.functions
        
        #print("NEW FUN: ", str(hex(self.start)))
        stack = [] 
        dict_stacks = {} 
        stack_list = []
        #first we add the input parameters of the function to the stack
        for in_id in range(len(function.input_args)):
            stack.append(-in_id -1)

        instruction_id = 0
        
        while instruction_id < len(function.instructions):
            stack_list.append(stack.copy())
            update_stack_needed = True
            instruction = function.instructions[instruction_id]
            if instruction.addr in ED9InstructionsSet.locations_dict:
                if ED9InstructionsSet.locations_dict[instruction.addr] in self.dict_stacks:
                    stack = self.dict_stacks[ED9InstructionsSet.locations_dict[instruction.addr]]
            if (instruction.op_code == 0x0B):
                if instruction.operands[0].value in self.dict_stacks:
                    pass
                else:
                    self.dict_stacks[instruction.operands[0].value] = stack.copy()
            elif (instruction.op_code == 0x0D):
                if instruction_id != len(function.instructions) - 1:
                    update_stack_needed = False
                    instruction_id = instruction_id + 1
                    instruction = function.instructions[instruction_id]
                    while instruction.addr not in ED9InstructionsSet.locations_dict:
                        instruction_id = instruction_id + 1
                        if instruction_id > len(function.instructions) - 1:
                            break
                        instruction = function.instructions[instruction_id]
                    
            elif (instruction.op_code == 0x0E): 
                if instruction.operands[0].value in self.dict_stacks:
                    pass
                else:
                    self.dict_stacks[instruction.operands[0].value] = stack.copy()
                    self.dict_stacks[instruction.operands[0].value].pop()
            elif (instruction.op_code == 0x0F):
                if instruction.operands[0].value in self.dict_stacks:
                    pass
                else:
                    self.dict_stacks[instruction.operands[0].value] = stack.copy()
                    self.dict_stacks[instruction.operands[0].value].pop()
            elif instruction.op_code == 0x0C: #Found a function call
                #We now attempt to find all the input parameters of the function and identify the return address (which should be pushed right before them)
                index_fun = instruction.operands[0].value
                called_fun = functions[index_fun]
                #instruction.operands[0] = ED9InstructionsSet.operand(functions[instruction.operands[0].value].name, False) 
                varin = len(called_fun.input_args)
                
                starting_instruction_id = stack[len(stack) -1 - varin]
                last_instruction = function.instructions[starting_instruction_id]
                
                
                function.instructions[starting_instruction_id].name = "PUSHRETURNADDRESS"
                addr = last_instruction.operands[0].value
                if addr in ED9InstructionsSet.locations_dict:
                    label = ED9InstructionsSet.locations_dict[addr]
                else:
                    label = "Loc_"+ str(ED9InstructionsSet.location_counter)
                    ED9InstructionsSet.locations_dict[addr] = label
                    ED9InstructionsSet.location_counter = ED9InstructionsSet.location_counter + 1
                function.instructions[starting_instruction_id].operands[0] = ED9InstructionsSet.operand(label, False)
                #The previous instruction is likely where the call really starts, it pushes a small unsigned integer (maybe some kind of stack size allocated for the called function?)
                function.instructions[starting_instruction_id - 1].text_before = "#Calling " + called_fun.name + "\n    "
                function.instructions[starting_instruction_id - 1].name = "PUSHCALLERFUNCTIONINDEX"
                function.instructions[starting_instruction_id - 1].operands.clear()# = ED9InstructionsSet.operand(functions[function.instructions[starting_instruction_id - 1].operands[0].value].name, False)
            elif instruction.op_code == 0x23:
                varin = instruction.operands[2].value
                
                if (function.instructions[instruction_id - 1 - varin].op_code == 1):
                    stack = stack_list[instruction_id - 1 - varin]

            elif instruction.op_code == 0x25: 
               addr = instruction.operands[0].value
               if addr in ED9InstructionsSet.locations_dict:
                   label = ED9InstructionsSet.locations_dict[addr]
               else:
                   label = "Loc_"+ str(ED9InstructionsSet.location_counter)
                   ED9InstructionsSet.locations_dict[addr] = label
                   ED9InstructionsSet.location_counter = ED9InstructionsSet.location_counter + 1
               instruction.operands[0] = ED9InstructionsSet.operand(label, False)
               #The previous instruction is likely where the call really starts, it pushes a small unsigned integer (maybe some kind of stack size allocated for the called function?)
            if (update_stack_needed):
                self.update_stack(instruction, stack, instruction_id)
                instruction_id = instruction_id + 1

            if instruction.op_code == 0x0C: #If there was a call, the operand becomes the name of the function rather than the index; should actually be in another function coming after this one
                index_fun = instruction.operands[0].value
                called_fun = functions[index_fun]
                instruction.operands[0] = ED9InstructionsSet.operand(functions[instruction.operands[0].value].name, False) 
                

    def wrap_conversion(self, value: int)->str:
        removeLSB = value & 0xC0000000
        actual_value = remove2MSB(value)
        MSB = removeLSB >> 0x1E
        if (MSB == 3):
            return "\"" + readtextoffset(self.stream, actual_value).replace("\n", "\\n") + "\"" 
        elif (MSB == 2):
            actual_value = actual_value << 2 
            bytes = struct.pack("<i",actual_value)
            return "FLOAT(" + str(struct.unpack("<f", bytes)[0]) + ")"
        elif (MSB == 1):
            return "INT(" + str((int(actual_value))) + ")"
        else:
            return "UNDEF(" + str(hex(int(actual_value))) + ")"

def find_start_function_call(instructions, instruction_id, varin)->int:
    counter_in = varin
    instruction_counter = -1
    while(counter_in > 0):
        current_instruction = instructions[instruction_id + instruction_counter]
        op_code = current_instruction.op_code
        if (op_code == 0):
            counter_in = counter_in - 1 
        elif (op_code == 1):
            popped_els = current_instruction.operands[0].value/4
            counter_in = counter_in + popped_els
        elif (op_code == 2): 
            counter_in = counter_in - 1
        elif (op_code == 3):  
            counter_in = counter_in - 1
        elif (op_code == 4):  
            counter_in = counter_in - 1
        elif (op_code == 5):  
            counter_in = counter_in + 1
        elif (op_code == 6): 
            counter_in = counter_in + 1
        elif (op_code == 7): 
            counter_in = counter_in - 1
        elif (op_code == 8): 
            counter_in = counter_in + 1
        elif (op_code == 9): 
            counter_in = counter_in - 1
        elif (op_code == 0x0A): 
            counter_in = counter_in + 1
        elif (op_code == 0x0D): 
            break
        elif (op_code == 0x0C): #why call another function before the parameters were all pushed... if that happens, fuck
            break
        elif (op_code == 0x0E): 
            counter_in = counter_in + 1
        elif (op_code == 0x0F): 
            counter_in = counter_in + 1
        elif ((op_code >= 0x10) and(op_code <= 0x1E)):#Operations with two operands: the two are discarded and one (the result) is pushed => overall we popped one
            counter_in = counter_in + 1
        elif ((op_code >= 0x1F) and (op_code <= 0x21)): #A single operand popped and the result is pushed => nothing changes in terms of stack occupation
            counter_in = counter_in + 1 - 1
        elif ((op_code == 0x22) or (op_code == 0x23) or (op_code == 0x24)): #For the same reason a regular call shouldn't happen here
           break
        elif (op_code == 0x25): 
            counter_in = counter_in - 1
            counter_in = counter_in - 1
            counter_in = counter_in - 1
            counter_in = counter_in - 1
            counter_in = counter_in - 1
        elif (op_code == 0x27): 
            count = current_instruction.operands[0].value
            for i in range(count):
                counter_in = counter_in + 1
        instruction_counter = instruction_counter - 1

    if (instruction_id + instruction_counter == -1):
        return (instruction_counter + 1, counter_in)
    current_instruction = instructions[instruction_id + instruction_counter]
    while(current_instruction.op_code == 0x26):
        instruction_counter = instruction_counter - 1
        current_instruction = instructions[instruction_id + instruction_counter]
    
    return (instruction_counter + 1, counter_in)