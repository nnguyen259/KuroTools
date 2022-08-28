
import struct
import disasm.ED9InstructionsSet as ED9InstructionsSet
import disasm.script as script
import disasm.function as function
from lib.parser import process_data, readint, readintoffset, readtextoffset, remove2MSB, get_actual_value_str
from lib.packer import write_dword_in_byte_array
import traceback
from lib.crc32 import compute_crc32

current_stack = []
dict_stacks = {}#Key: Label, Value: State of the stack at the jump
variable_names = {}#Key: Stack Index, Value: Symbol

stack_invalid = False #Whenever there is a EXIT, we at least need a Label right after
current_addr_scripts_var = 0
current_addr_structs = 0
current_addr_code = 0

current_script = script.script()
current_function_number = 0

functions_offsets = []
functions_sorted_by_id = []
#arrays containing the addresses where strings are referred to

strings_offsets_code          = []
jump_dict = {} # Key: String ("Loc_XXX") Value: (Vector of Index of pointers to update, Index of destination)
return_addr_vector = []

bin_code_section = bytearray([])

#all relevant addresses, will be computed once we get all the necessary data
start_functions_headers_section =  0x18
start_script_variables          = -1
start_functions_var_in          = -1
start_functions_var_out         = -1
start_structs_section           = -1
start_structs_params_section    = -1
start_code_section              = -1
start_strings_section           = -1



class jump:
    def __init__(self):
        self.addr_start = []
        self.addr_destination = -1
def retrieve_index_by_fun_name(name):
    global current_script
    for f in current_script.functions:
        if f.name == name:
            return f.id
    return -1

def UNDEF(value: int)->int:
    return value & 0x3FFFFFFF
def INT(value: int)->int:
    return (value & 0x3FFFFFFF) | 0x40000000
def FLOAT(value: float)->int:
    float_bytes = struct.pack("<f",value)
    float_uint = struct.unpack("<I", float_bytes)[0]
    float_uint = float_uint >> 2
    return (float_uint & 0x3FFFFFFF) | 0x80000000
def STR(value: int)->int:
    return (value & 0x3FFFFFFF) | 0xC0000000

def find_symbol_in_stack(symbol):
    
    global variable_names
    return list(variable_names.keys())[list(variable_names.values()).index(symbol)] 

def add_struct(id, nb_sth1, array2):
    global current_function
    mysterious_struct = { 
        "id": id,
        "nb_sth1": nb_sth1,
        "array2": array2,
        }
    current_function.structs.append(mysterious_struct)

def add_function(name, input_args, output_args, b0, b1):

    global current_script
    global current_function

    current_function = function.function()
    
    current_function.id = len(current_script.functions)
    current_function.name = name
    current_function.hash = compute_crc32(name)
    current_function.input_args = input_args
    current_function.output_args = output_args
    current_function.b0 = b0
    current_function.b1 = b1
    
    current_script.functions.append(current_function)
    functions_sorted_by_id.append(current_function) 
    functions_sorted_by_id.sort(key=lambda fun: fun.id) #whatever

def set_current_function(name):
    global current_function
    global current_function_number
    global current_stack
    global variable_names
    global stack_invalid 

    stack_invalid = False
    current_id = retrieve_index_by_fun_name(name)
    current_function = current_script.functions[current_id]
    
    variable_names.clear()
    current_stack.clear()
    
    current_function.start = current_addr_code
    for i in range(len(current_function.input_args)):
        current_stack.append(len(current_function.input_args)-i)
        variable_names[i] = "PARAM_" + str(i)
    current_function_number = current_function_number + 1
    
def compile():
    global current_script
    global bin_code_section

    bin_function_header_section = bytearray([])
    bin_script_header_section   = bytearray([])
    bin_fun_input_vars_section  = bytearray([])
    bin_fun_output_vars_section = bytearray([])
    bin_structs_section         = bytearray([])
    bin_structs_params_section  = bytearray([])
    bin_script_var_section      = bytearray([])
    bin_string_section          = bytearray([])

    strings_offsets_struct_params = []
    strings_offsets_script_var    = []
    strings_offsets_fun_varout    = []
    strings_offsets_fun_varin     = []
    strings_offsets_fun_names     = []

    #from here, we should have filled bin_code_section with placeholder pointers
    #now we need to get all the necessary addresses (we have everything so we should be able to get all of them)
    
    start_functions_var_out          = start_functions_headers_section + 0x20 * len(current_script.functions)
    
    total_in      = 0
    total_out     = 0
    total_structs = 0
    size_total_params_structs = 0
    
    for f in current_script.functions:
        total_in      = total_in      + len(f.input_args)
        total_out     = total_out     + len(f.output_args)
        total_structs = total_structs + len(f.structs)
        for s in f.structs:
            size_total_params_structs = size_total_params_structs + len(s["array2"]) * 4

    start_functions_var_in          = start_functions_var_out  + total_out * 4
    start_structs_section           = start_functions_var_in + total_in * 4
    start_structs_params_section    = start_structs_section + 3 * 4 * total_structs
    start_script_variables          = start_structs_params_section + size_total_params_structs
    start_code_section              = start_script_variables + len(current_script.script_variables_in) * 8 + len(current_script.script_variables_out) * 8
    start_strings_section           = start_code_section + len(bin_code_section)

    #building the script header
    fourCC = "#scp"
    header_b = bytearray(fourCC.encode("ASCII"))
    header_b = header_b + bytearray(struct.pack("<I", start_functions_headers_section))
    header_b = header_b + bytearray(struct.pack("<I", len(current_script.functions)))
    header_b = header_b + bytearray(struct.pack("<I", start_script_variables)) 
    header_b = header_b + bytearray(struct.pack("<I", len(current_script.script_variables_in))) 
    header_b = header_b + bytearray(struct.pack("<I", len(current_script.script_variables_out))) 

    current_addr_fun_var_in     = start_functions_var_in
    current_addr_fun_var_out    = start_functions_var_out
    current_addr_structs        = start_structs_section
    current_addr_structs_params = start_structs_params_section
    current_addr_script_vars    = start_script_variables

    current_script.functions.sort(key=lambda fun: fun.id) 

    for vin_scp in current_script.script_variables_in:
            for v in vin_scp:
                if type(v) == str:
                    bin_script_var_section = bin_script_var_section + bytearray(struct.pack("<I", 0)) #placeholder
                    strings_offsets_script_var.append((current_addr_script_vars,  v)) 
                else:
                    bin_script_var_section = bin_script_var_section + bytearray(struct.pack("<I",  v))
                current_addr_script_vars = current_addr_script_vars  + 4
    for vout_scp in current_script.script_variables_out:
        for v in vout_scp:
            if type(vout_scp) == str:
                bin_script_var_section = bin_script_var_section + bytearray(struct.pack("<I", 0)) #placeholder
                strings_offsets_script_var.append((current_addr_script_vars, v)) 
            else:
                bin_script_var_section = bin_script_var_section + bytearray(struct.pack("<I", v))
            current_addr_script_vars = current_addr_script_vars  + 4

    for f in current_script.functions:
        header_f = bytearray(struct.pack("<I", start_code_section + f.start))
        vars     = len(f.input_args) + (f.b0 << 8) + (f.b1 << 16) + (len(f.output_args) << 24)
        header_f = header_f + bytearray(struct.pack("<I", vars))
        header_f = header_f + bytearray(struct.pack("<I", current_addr_fun_var_out))
        header_f = header_f + bytearray(struct.pack("<I", current_addr_fun_var_in))
        header_f = header_f + bytearray(struct.pack("<I", len(f.structs)))
        header_f = header_f + bytearray(struct.pack("<I", current_addr_structs))
        header_f = header_f + bytearray(struct.pack("<I", f.hash))
        strings_offsets_fun_names.append((start_functions_headers_section + len(bin_function_header_section) + 0x1C, f.name)) 
        header_f = header_f + bytearray(struct.pack("<I", 0)) #placeholder
        bin_function_header_section = bin_function_header_section + header_f
        for vin in f.input_args:
            if type(vin) == str:
                bin_fun_input_vars_section = bin_fun_input_vars_section + bytearray(struct.pack("<I", 0)) #placeholder
                strings_offsets_fun_varin.append((current_addr_fun_var_in, vin)) 
            else:
                bin_fun_input_vars_section = bin_fun_input_vars_section + bytearray(struct.pack("<I", vin))
            current_addr_fun_var_in = current_addr_fun_var_in  + 4
        for vout in f.output_args:
            if type(vout) == str:
                bin_fun_output_vars_section = bin_fun_output_vars_section + bytearray(struct.pack("<I", 0)) #placeholder
                strings_offsets_fun_varout.append((current_addr_fun_var_out, vout)) 
            else:
                bin_fun_output_vars_section = bin_fun_output_vars_section + bytearray(struct.pack("<I", vout))
            current_addr_fun_var_out = current_addr_fun_var_out + 4
        for s in f.structs:
            bin_structs_section = bin_structs_section + bytearray(struct.pack("<i", s["id"]))
            bin_structs_section = bin_structs_section + bytearray(struct.pack("<H", (s["nb_sth1"])))
            bin_structs_section = bin_structs_section + bytearray(struct.pack("<H", int(len(s["array2"])/2))) #4 integers but two structs
            bin_structs_section = bin_structs_section + bytearray(struct.pack("<I", current_addr_structs_params))
            current_addr_structs = current_addr_structs + 0xC
            for el in s["array2"]:
                if type(el) == str:
                    bin_structs_params_section = bin_structs_params_section + bytearray(struct.pack("<I", 0)) #placeholder
                    strings_offsets_struct_params.append((current_addr_structs_params, el)) 
                else:
                    bin_structs_params_section = bin_structs_params_section + bytearray(struct.pack("<I", el))
                current_addr_structs_params = current_addr_structs_params  + 4
        
            
    #updating the jumps destination
    
    
    for j in jump_dict.items():
        for start in j[1].addr_start:
            write_dword_in_byte_array("<I", bin_code_section, start, start_code_section + j[1].addr_destination)
    for j in return_addr_vector:
        for start in j.addr_start:
            write_dword_in_byte_array("<I", bin_code_section, start, start_code_section + j.addr_destination)
    
            
    string_section_addr = start_strings_section     
    
    #first we write the strings from the code
    for str_data in strings_offsets_code:
        where_to_update_ptr = str_data[0]
        actual_string       = str_data[1]
        output = actual_string.encode("utf-8") + b"\0"
        bin_string_section = bin_string_section + output 
        write_dword_in_byte_array("<I", bin_code_section, where_to_update_ptr, STR(string_section_addr))
        string_section_addr = string_section_addr + len(output)
    
    bin_file = header_b + bin_function_header_section + bin_fun_output_vars_section + bin_fun_input_vars_section 
    bin_file = bin_file +  bin_structs_section + bin_structs_params_section 
    bin_file = bin_file + bin_script_var_section + bin_code_section
    
    for str_data in strings_offsets_fun_names:
        where_to_update_ptr = str_data[0]
        actual_string       = str_data[1]
        output = actual_string.encode("utf-8") + b"\0"
        bin_string_section = bin_string_section + output 
        write_dword_in_byte_array("<I", bin_file, where_to_update_ptr, STR(string_section_addr))
        string_section_addr = string_section_addr + len(output)

    for str_data in strings_offsets_fun_varout:
        where_to_update_ptr = str_data[0]
        actual_string       = str_data[1]
        output = actual_string.encode("utf-8") + b"\0"
        bin_string_section = bin_string_section + output 
        write_dword_in_byte_array("<I", bin_file, where_to_update_ptr, STR(string_section_addr))
        string_section_addr = string_section_addr + len(output)
    
    for str_data in strings_offsets_fun_varin:
        where_to_update_ptr = str_data[0]
        actual_string       = str_data[1]
        output = actual_string.encode("utf-8") + b"\0"
        bin_string_section = bin_string_section + output 
        write_dword_in_byte_array("<I", bin_file, where_to_update_ptr, STR(string_section_addr))
        string_section_addr = string_section_addr + len(output)

    for str_data in strings_offsets_struct_params:
        where_to_update_ptr = str_data[0]
        actual_string       = str_data[1]
        output = actual_string.encode("utf-8") + b"\0"
        bin_string_section = bin_string_section + output 
        write_dword_in_byte_array("<I", bin_file, where_to_update_ptr, STR(string_section_addr))
        string_section_addr = string_section_addr + len(output)
    
    for str_data in strings_offsets_script_var:
        where_to_update_ptr = str_data[0]
        actual_string       = str_data[1]
        output = actual_string.encode("utf-8") + b"\0"
        bin_string_section = bin_string_section + output 
        write_dword_in_byte_array("<I", bin_file, where_to_update_ptr, STR(string_section_addr))
        string_section_addr = string_section_addr + len(output)
    
    
    
    bin_file = bin_file + bin_string_section
    
    dat_file = open(current_script.name + ".dat", "wb")
    dat_file.write(bin_file)
    dat_file.close()

def create_script_header(name, varin, varout):
    global current_script
    current_script.name = name
    current_script.script_variables_in = varin
    current_script.script_variables_out = varout


#Instructions
def PUSHUNDEFINED(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.append(current_addr_code)
    b_arg = bytearray(struct.pack("<I", (value)))
   
    result = bytearray([0, 4]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
    
def PUSHCALLERFUNCTIONINDEX():
    global current_function
    #value = retrieve_index_by_fun_name(name)
    PUSHUNDEFINED(current_function.id)


def PUSHSTRING(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.append(current_addr_code)
    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = bytearray([0, 4]) + b_arg
    bin_code_section = bin_code_section + result
    strings_offsets_code.append((current_addr_code + 2, value)) #recording address for when we know where the string are compiled
    current_addr_code = current_addr_code + len(result)
  
def PUSHRETURNADDRESS(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.append(current_addr_code)
    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = bytearray([0, 4]) + b_arg
    bin_code_section = bin_code_section + result
    if value in jump_dict:
        jump_dict[value].addr_start.append(current_addr_code + 2) #recording address for when we know where the string are compiled
    else:
        jump_dict[value] = jump()
        jump_dict[value].addr_start.append(current_addr_code + 2)
    current_addr_code = current_addr_code + len(result)

def PUSHFLOAT(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.append(current_addr_code)
    b_arg = bytearray(struct.pack("<I", FLOAT(value))) 
    result = bytearray([0, 4]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def PUSHINTEGER(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.append(current_addr_code)
    b_arg = bytearray(struct.pack("<I", INT(value))) 
    result = bytearray([0, 4]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def POP(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    popped_els = int(value/4)
    try:
        for i in range(popped_els):
            current_stack.pop()
    except Exception as err:
        print("WARNING: Something unexpected happened, not necessarily a problem. Check the error below for more details: ")
        #print(err)
        traceback.print_stack()
        print("This is not an error!!!! Just a warning!! Your file will be generated!")
    b_arg = bytearray(struct.pack("<B", value)) 
    result = bytearray([1]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def RETRIEVEELEMENTATINDEX(value):
    global current_addr_code
    global bin_code_section

    current_stack.append(current_addr_code)
    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([2]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)


def RETRIEVEELEMENTATINDEX2(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.append(current_addr_code)
    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([3]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def PUSHCONVERTINTEGER(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.append(current_addr_code)
    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([4]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def PUTBACKATINDEX(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    index = int((len(current_stack)) + value/4)
    current_stack[index] = current_stack[len(current_stack) - 1]
    current_stack.pop()
    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([5]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def PUTBACK(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    index1 = int(len(current_stack) + value/4)
    index2 = current_stack[index1]
    #current_stack[index2] = current_stack[len(current_stack) - 1]
    current_stack.pop()

    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([6]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def LOAD32(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.append(current_addr_code)
    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([7]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def STORE32(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop()
    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([8]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def LOADRESULT(value):
    global current_addr_code
    global bin_code_section
    global current_stack
    addr = current_addr_code 
    current_stack.append(current_addr_code)
    b_arg = bytearray(struct.pack("<B", value)) 
    result = bytearray([9]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
    return addr
def SAVERESULT(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop()
    b_arg = bytearray(struct.pack("<B", value)) 
    result = bytearray([0x0A]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def JUMP(value):
    global current_addr_code
    global bin_code_section
    global current_stack
    global stack_invalid

    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = bytearray([0x0B]) + b_arg
    bin_code_section = bin_code_section + result
    if value in jump_dict:
        jump_dict[value].addr_start.append(current_addr_code + 1) #recording address for when we know where the string are compiled
    else:
        jump_dict[value] = jump()
        jump_dict[value].addr_start.append(current_addr_code + 1)
    current_addr_code = current_addr_code + len(result)
    if (stack_invalid == False):
        if value not in dict_stacks:
            dict_stacks[value] = current_stack.copy()

def Label(value):
    global current_addr_code
    global bin_code_section
    global current_stack 
    global stack_invalid

    if value in jump_dict:
        jump_dict[value].addr_destination = current_addr_code
    else:
        jump_dict[value] = jump()
        jump_dict[value].addr_destination = current_addr_code
    if value in dict_stacks:
        current_stack = dict_stacks[value]
        stack_invalid = False

def CALL(name):
    global current_addr_code
    global bin_code_section
    global functions_sorted_by_id
    global current_stack 
    value = retrieve_index_by_fun_name(name)
    varin = len(functions_sorted_by_id[value].input_args)

    for i in range(varin + 2): #removing return address and function index too
        current_stack.pop()
    b_arg = bytearray(struct.pack("<H", value)) 
    result = bytearray([0x0C]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + 3

def EXIT():
    global current_addr_code
    global bin_code_section
    global stack_invalid

    stack_invalid = True
    result = bytearray([0x0D])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def JUMPIFFALSE(value):
    global current_addr_code
    global bin_code_section
    global current_stack
    global stack_invalid

    current_stack.pop()
    b_arg = bytearray(struct.pack("<I", 0)) 
    result = bytearray([0x0F]) + b_arg
    bin_code_section = bin_code_section + result
    if value in jump_dict:
        jump_dict[value].addr_start.append(current_addr_code + 1) #recording address for when we know where the string are compiled
    else:
        jump_dict[value] = jump()
        jump_dict[value].addr_start.append(current_addr_code + 1)
    current_addr_code = current_addr_code + len(result)
    if (stack_invalid == False):
        if value not in dict_stacks:
            dict_stacks[value] = current_stack.copy()

def JUMPIFTRUE(value):
    global current_addr_code
    global bin_code_section
    global current_stack
    global stack_invalid

    current_stack.pop()
    b_arg = bytearray(struct.pack("<I", 0)) 
    result = bytearray([0x0E]) + b_arg
    bin_code_section = bin_code_section + result
    if value in jump_dict:
        jump_dict[value].addr_start.append(current_addr_code + 1) #recording address for when we know where the string are compiled
    else:
        jump_dict[value] = jump()
        jump_dict[value].addr_start.append(current_addr_code + 1)
    current_addr_code = current_addr_code + len(result)
    if (stack_invalid == False):
        if value not in dict_stacks:
            dict_stacks[value] = current_stack.copy()

def ADD():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x10])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def SUBTRACT():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x11])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def MULTIPLY():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x12])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def DIVIDE():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x13])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def MODULO():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x14])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def EQUAL():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x15])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def NONEQUAL():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x16])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def GREATERTHAN():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x17])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def GREATEROREQ():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x18])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def LOWERTHAN():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x19])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def LOWEROREQ():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x1A])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def AND_():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x1B])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def OR1():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x1C])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def OR2():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x1D])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def OR3():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.pop()
    current_stack.append(current_addr_code)

    result = bytearray([0x1E])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def NEGATIVE():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.append(current_addr_code)

    result = bytearray([0x1F])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def ISFALSE():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.append(current_addr_code)

    result = bytearray([0x20])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def XOR1():
    global current_addr_code
    global bin_code_section
    global current_stack

    current_stack.pop() 
    current_stack.append(current_addr_code)

    result = bytearray([0x21])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def CALLFROMANOTHERSCRIPT(str1, str2, var):
    global current_addr_code
    global bin_code_section
    global current_stack

    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = bytearray([0x22]) + b_arg
    strings_offsets_code.append((current_addr_code + 1, str1)) 
    
    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = result + b_arg
    strings_offsets_code.append((current_addr_code + 5, str2)) 
    b_arg = bytearray(struct.pack("<B", var)) #placeholder
    result = result + b_arg
    bin_code_section = bin_code_section + result

    for i in range(var + 5):
        current_stack.pop() 

    current_addr_code = current_addr_code + len(result)

def CALLFROMANOTHERSCRIPT2(str1, str2, var):
    global current_addr_code
    global bin_code_section
    global current_stack
    global current_function

    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = bytearray([0x23]) + b_arg
    strings_offsets_code.append((current_addr_code + 1, str1)) 
    
    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = result + b_arg
    strings_offsets_code.append((current_addr_code + 5, str2)) 
    b_arg = bytearray(struct.pack("<B", var)) 
    result = result + b_arg
    bin_code_section = bin_code_section + result

    #Here it's a hack for the disassembled version to not cause errors when recompiling. Normally I'd need to know the length of the stack
    #before the input arguments were added, but at the point of CALLFROMANOTHERSCRIPT2, there is no way I'd know (it has already been cleared)
    #So I can't restore it to its previous state. All I can do is add as many dummy elements in the stack as there are input parameters to the 
    #the current function, as usually there is no left over element in the stack except those (but it can happen, and if it happens, it will display
    # a warning saying a problem happened, but in disassembled mode we don't care about the stack which is correct since taken directly from
    #the original scripts, except if the user fucks it up somehow, then they will have a hard time debugging it (but just don't mod in disassembled version, really)
    #The only problem it will lead in the end is the user not being able to tell precisely what's on the stack, that's something they'll have to do manually
    for i in range(var):
        current_stack.pop()
    for i in range(len(current_function.input_args)):
        current_stack.append(0)


    current_addr_code = current_addr_code + len(result)

def RUNCMD(var, command_name):
    global current_addr_code
    global bin_code_section
    global current_stack

    (id_struct, op_code) = ED9InstructionsSet.reverse_commands_dict[command_name]

    struct_b = bytearray(struct.pack("<B", id_struct))
    op_code_b = bytearray(struct.pack("<B", op_code))
    nb_var_b = bytearray(struct.pack("<B", var))
    result = bytearray([0x24]) + struct_b + op_code_b + nb_var_b
    
    bin_code_section = bin_code_section + result

    current_addr_code = current_addr_code + len(result)

def PUSHRETURNADDRESSFROMANOTHERSCRIPT(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = bytearray([0x25]) + b_arg
    bin_code_section = bin_code_section + result
    if value in jump_dict:
        jump_dict[value].addr_start.append(current_addr_code + 1) 
    else:
        jump_dict[value] = jump()
        jump_dict[value].addr_start.append(current_addr_code + 1)

    current_stack.append(current_addr_code)
    current_stack.append(current_addr_code)
    current_stack.append(current_addr_code)
    current_stack.append(current_addr_code)
    current_stack.append(current_addr_code)

    current_addr_code = current_addr_code + len(result)

def ADDLINEMARKER(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<H", value))
    result = bytearray([0x26]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def POP2(value):
    global current_addr_code
    global bin_code_section
    global current_stack

    b_arg = bytearray(struct.pack("<B", value))
    result = bytearray([0x27]) + b_arg
    bin_code_section = bin_code_section + result

    popped_els = int(value)
    for i in range(popped_els):
        current_stack.pop()

    current_addr_code = current_addr_code + len(result)

def DEBUG(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<i", value))
    result = bytearray([0x28]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)


#Decompiled instructions
class instr:
    def __init__(self, id, params):
       self.id = id
       self.params = params

def Command(command_name, inputs):
    if type(inputs) == list:
        inputs.reverse()
    for str_exp in inputs:
        compile_expr(str_exp)
    RUNCMD(len(inputs), command_name)
    if (len(inputs) > 0):
        POP(len(inputs) * 4)

def AssignVar(symbol, expr):
    global current_stack
    global current_addr_code
    global variable_names

    compile_expr(expr)

    if symbol in variable_names.values():

        idx = find_symbol_in_stack(symbol)
        if (len(current_stack) - 1) > idx: #if the index we put the value to is not the top of the stack, we put it back at that index
            PUTBACKATINDEX(-(len(current_stack) - 1 - idx) * 4)
        elif (len(current_stack) - 1) == idx: #if it's already on top of the stack, it should have been pushed earlier so nothing to do
            pass
        else:
            raise Exception("This variable was destroyed") #I'll try to find a way to deal with that later if we end up with a PC version
    else:
        #if the symbol is not in the variable names dict, it's a new variable at an index that was never reached
        #still, we should verify the top of the stack + 1 doesn't already have a var name associated to it
        if (len(current_stack)-1) not in variable_names.keys():
            variable_names[len(current_stack)-1] = symbol
            
        else:
            raise Exception("There is already a different variable name associated to this stack index")
        
def SetVarToAnotherVarValue(symbolout, input): #SetVarToAnotherVarValue
    global current_stack
    global current_addr_code
    global variable_names
    
    if input not in variable_names.values():
        raise ErrorValue("Provided input variable name does not exist in the current function.")

    idx_in = find_symbol_in_stack(input)
    
    if symbolout in variable_names.values():
        idx = find_symbol_in_stack(symbolout)
        if idx_in == len(current_stack) - 1:
            
            PUTBACKATINDEX(-(len(current_stack) - idx - 1) * 4)
        else:
            RETRIEVEELEMENTATINDEX(-(len(current_stack) - idx_in) * 4)
            PUTBACKATINDEX(-(len(current_stack) - idx - 1) * 4)
    else:
        #The symbol provided needs to be added (it's basically a variable creation)
        if len(current_stack) not in variable_names.keys():
            variable_names[len(current_stack)] = symbol
            RETRIEVEELEMENTATINDEX(-(len(current_stack) - idx_in) * 4)
        else:
            RETRIEVEELEMENTATINDEX(-(len(current_stack) - idx_in) * 4)
            
            #raise Exception("There is already a different variable name associated to this stack index")
        
        

def WriteAtIndex(value_in, index): 
    global current_stack
    global current_addr_code
    global variable_names
    #This one: input is variable, it points to a location in stack with a number, that is the index the top of the stack
    #will be put to; so: input should exist. 

    if index not in variable_names.values():
        raise Exception("Provided input variable name does not exist in the current function.")

    idx_in = find_symbol_in_stack(index)
    
    if value_in in variable_names.values():
        idx = find_symbol_in_stack(value_in)
        if idx == len(current_stack) - 1:
            if idx_in < len(current_stack) - 1:
                PUTBACK(-(len(current_stack) - 1 - idx_in) * 4)
            else:
                raise Exception("The variable containing the index should still be in the stack")

                
        else:

            RETRIEVEELEMENTATINDEX(-(len(current_stack) - idx) * 4)
            PUTBACK(-(len(current_stack) - idx_in) * 4)
    else:
         raise Exception("The variable containing the element to write should exist but it doesn't.")

def compile_expr(input): #This only so I can know where to push the return address...
    global current_stack
    #possible types for input: 
    #compile_expr(LoadVar("Var1")) => compile_expr(instr)
    #compile_expr("Var1")  => compile_expr(str)
    #compile_expr(and_(LoadVar("Var1"), INT(0))) => compile_exp(list)
    #Meaning: if the type is a list, it is an operator
    #If the type is an instruction => compile it accordingly
    #If the type is neither of them, it is a constant, a Push will suffice
    if input is None:
        pass
    elif type(input) == instr:
        if input.id == 2:
            idx = find_symbol_in_stack(input.params[0])
            RETRIEVEELEMENTATINDEX(-(len(current_stack) - idx) * 4)
        elif input.id == 3:
            idx = find_symbol_in_stack(input.params[0])
            RETRIEVEELEMENTATINDEX2(-(len(current_stack) - idx) * 4)
        elif input.id == 4:
            PUSHCONVERTINTEGER(input.params[0])
        elif input.id == 7:
            LOAD32(input.params[0])
        elif input.id == 9:
            LOADRESULT(input.params[0])
        elif input.id == 0x22:
            PUSHCALLERFUNCTIONINDEX()
        elif input.id == 0x23:
            PUSHRETURNADDRESS(input.params[0])

    elif type(input) == list:

        for i in range(0,len(input)-1):
            compile_expr(input[i])
        if len(input) == 3:
            if input[2].id == 0x10:
                ADD()
            elif input[2].id == 0x11:
                SUBTRACT()
            elif input[2].id == 0x12:
                MULTIPLY()
            elif input[2].id == 0x13:
                DIVIDE()
            elif input[2].id == 0x14:
                MODULO()
            elif input[2].id == 0x15:
                EQUAL()
            elif input[2].id == 0x16:
                NONEQUAL()
            elif input[2].id == 0x17:
                GREATERTHAN()
            elif input[2].id == 0x18:
                GREATEROREQ()
            elif input[2].id == 0x19:
                LOWERTHAN()
            elif input[2].id == 0x1A:
                LOWEROREQ()
            elif input[2].id == 0x1B:
                AND_()
            elif input[2].id == 0x1C:
                OR1()
            elif input[2].id == 0x1D:
                OR2()
            elif input[2].id == 0x1E:
                OR3()
        elif len(input) == 2:
            if input[1].id == 0x1F:
              NEGATIVE()
            elif input[1].id == 0x20:
                ISFALSE()
            elif input[1].id == 0x21:
                XOR1()
    else:

        if type(input) == str:
            PUSHSTRING(input)
        else:
            PUSHUNDEFINED(input)

def LoadVar(symbol):
    #If there is a LoadVar, it was for a temporary use unless the final result is wrapped in a AssignVar instruction
    #So no need to create a new variable since it will be discarded from the stack next
    return instr(2, [symbol])

def LoadVar2(symbol):
    
    return instr(3, [symbol])

def LoadInt(symbol):
    return instr(4, [symbol])

def Load32(index):
    return instr(7, [index])

def LoadResult(index):
    return instr(9, [index])

def CallerID():
    return instr(0x22, [])
def ReturnAddress(loc):
    return instr(0x23, [loc])


def add(op1, op2):
    return [op1,op2, instr(0x10, [])]
def subtract(op1, op2):
    return [op1,op2, instr(0x11, [])]

def multiply(op1, op2):
    return [op1,op2, instr(0x12, [])]
def divide(op1, op2):
    return [op1,op2, instr(0x13, [])]
def modulo(op1, op2):
    return [op1,op2, instr(0x14, [])]
def equal(op1, op2):
    return [op1,op2, instr(0x15, [])]
def nonequal(op1, op2):
    return [op1,op2, instr(0x16, [])]
def greaterthan(op1, op2):
    return [op1,op2, instr(0x17, [])]
def greateroreq(op1, op2):
    return [op1,op2, instr(0x18, [])]
def lowerthan(op1, op2):
    return [op1,op2, instr(0x19, [])]
def loweroreq(op1, op2):
    return [op1,op2, instr(0x1A, [])]
def and_(op1, op2):
    return [op1,op2, instr(0x1B, [])]
def or1(op1, op2):
    return [op1,op2, instr(0x1C, [])]
def or2(op1, op2):
    return [op1,op2, instr(0x1D, [])]
def or3(op1, op2):
    return [op1,op2, instr(0x1E, [])]
def negative(op1):
    return [op1, instr(0x1F, [])]
def isfalse(op1):
    return [op1, instr(0x20, [])]
def xor1(op1):
    return [op1, instr(0x21, [])]

def Return():
    global current_function
    global current_stack 

    varin = len(current_function.input_args)
    if len(current_stack) > 0:
        POP(len(current_stack) * 4)
    EXIT()

def CreateVar(symbol, value):
    global current_stack
    #A load should have happened
    current_stack[len(current_stack) - 1] = symbol

def SetVar(symbolout, symbolin):  #OP5, we put symbolin into symbolout
    global current_stack
    idx = find_symbol_in_stack(symbolout)
    PUTBACKATINDEX(-(len(current_stack) - 1 - idx) * 4) #if idx = second slot at the top = len(stack) - 2, value = -4
    current_stack[idx] = symbolout

def CallFunction(fun_name, inputs): 
    
    global current_function
    global current_script
    global bin_code_section
    global current_addr_code
    global current_stack
    global jump_dict

    PUSHUNDEFINED(current_function.id)
    push_return_addr = current_addr_code
    PUSHUNDEFINED(0)
    
    CallFunctionWithoutReturnAddr(fun_name, inputs)

    return_ = jump()
    return_.addr_start.append(push_return_addr + 2)
    return_.addr_destination = current_addr_code
    return_addr_vector.append(return_)

def CallFunctionWithoutReturnAddr(fun_name, inputs): 
    
    global current_function
    global current_script
    global bin_code_section
    global current_addr_code
    global current_stack
    global jump_dict

    if type(inputs) == list:
        inputs.reverse()

    for str_exp in inputs:
        compile_expr(str_exp)

    CALL(fun_name)
    


def JumpWhenTrue(loc, condition): 
    #Adding the inputs
    compile_expr(condition)
    JUMPIFTRUE(loc)
def JumpWhenFalse(loc, condition): 
    compile_expr(condition)
    JUMPIFFALSE(loc)
   
def CallFunctionFromAnotherScript(file, fun, inputs): 
    global current_function
    global current_script
    global bin_code_section
    global current_addr_code
    global current_stack
    global jump_dict
    
    push_return_addr = current_addr_code
    #Adding 25 instr
    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = bytearray([0x25]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
    #updating the stack
    current_stack.append(push_return_addr)
    current_stack.append(push_return_addr)
    current_stack.append(push_return_addr)
    current_stack.append(push_return_addr)
    current_stack.append(push_return_addr)

    CallFunctionFromAnotherScriptWithoutReturnAddr(file, fun, inputs)

    return_ = jump()
    return_.addr_start.append(push_return_addr + 1)
    return_.addr_destination = current_addr_code
    return_addr_vector.append(return_)
    
    
   

  
def TopVar(symbol): #This one is dangerous, it should not be used (I actually don't see the point)
    #It should only be generated by the decompiler to help the user know which variable
    #is at the top of the stack when evaluating the expression/calling the function; if there is 
    #a TopVar, that means the element needs to be discarded after use, so it is very important to keep it
    #like this unless you know what you're doing

    return instr(0x29, [symbol])
  
def CallFunctionFromAnotherScriptWithoutReturnAddr(file, fun, inputs): 
    global current_function
    global current_script
    global bin_code_section
    global current_addr_code
    global current_stack
    global jump_dict
    

    #Adding the inputs
    if type(inputs) == list:
        inputs.reverse()

    for str_exp in inputs:
        compile_expr(str_exp)

    CALLFROMANOTHERSCRIPT(file, fun, len(inputs))

def CallFunctionFromAnotherScript2(file, fun, inputs): 
    
    global current_stack
    
    stack_before_call = current_stack.copy()
    #Adding the inputs
    if type(inputs) == list:
        inputs.reverse()

    for str_exp in inputs:
        compile_expr(str_exp)

    for i in range(1, len(inputs) + 1):
        SAVERESULT(i)
    if len(stack_before_call) > 0:
        POP(len(stack_before_call) * 4)
    for i in range(len(inputs), 0, -1):
        LOADRESULT(i)
    CALLFROMANOTHERSCRIPT2(file, fun, len(inputs))
    current_stack = stack_before_call.copy()
