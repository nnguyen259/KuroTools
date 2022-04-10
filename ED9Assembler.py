from ED9Disassembler import function, script
import struct
import ED9InstructionsSet
from lib.parser import process_data, readint, readintoffset, readtextoffset, remove2MSB, get_actual_value_str
from lib.packer import write_dword_in_byte_array
#ED9InstructionsSet.init_command_names_dicts()


current_addr_scripts_var = 0
current_addr_structs = 0
current_addr_code = 0

current_script = script()

functions_offsets = []

#arrays containing the addresses where strings are referred to

strings_offsets_code          = []
jump_dict = {} # Key: String ("Loc_XXX") Value: (Vector of Index of pointers to update, Index of destination)


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

def FLAG_UNDEF(value: int)->int:
    return value & 0x3FFFFFFF
def FLAG_INT(value: int)->int:
    return (value & 0x3FFFFFFF) | 0x40000000
def FLAG_FLOAT(value: float)->int:
    float_bytes = struct.pack("<f",value)
    float_uint = struct.unpack("<I", float_bytes)[0]
    float_uint = float_uint >> 2
    return (float_uint & 0x3FFFFFFF) | 0x80000000
def FLAG_STR(value: int)->int:
    return (value & 0x3FFFFFFF) | 0xC0000000


def add_struct(id, nb_sth1, array2):
    global current_function
    mysterious_struct = { 
        "id": id,
        "nb_sth1": nb_sth1,
        "array2": array2,
        }
    current_function.structs.append(mysterious_struct)

def add_function():
    global current_script
    global current_function
    
    current_script.functions.append(current_function)

def declare_function(id, name, hash, input_args, output_args, b0, b1):
    global current_function
    current_function = function()
    current_function.start = current_addr_code
    current_function.id = id
    current_function.name = name
    current_function.hash = hash
    current_function.input_args = input_args
    current_function.output_args = output_args
    current_function.b0 = b0
    current_function.b1 = b1
    
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
    start_code_section              = start_script_variables + len(current_script.script_variables_in) * 4 + len(current_script.script_variables_out) * 4
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
        #Here there is a risk an input variable is an undefined... Need to fix that later (In fact I believe you still have to mention the type here, unfortunately...)
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
        for vin_scp in current_script.script_variables_in:
            if type(vin_scp) == str:
                bin_script_var_section = bin_script_var_section + bytearray(struct.pack("<I", 0)) #placeholder
                strings_offsets_script_var.append((current_addr_script_vars, vin_scp)) 
            else:
                bin_script_var_section = bin_script_var_section + bytearray(struct.pack("<I", vin_scp))
            current_addr_script_vars = current_addr_script_vars  + 4
        for vout_scp in current_script.script_variables_out:
            if type(vout_scp) == str:
                bin_script_var_section = bin_script_var_section + bytearray(struct.pack("<I", 0)) #placeholder
                strings_offsets_script_var.append((current_addr_script_vars, vout_scp)) 
            else:
                bin_script_var_section = bin_script_var_section + bytearray(struct.pack("<I", vout_scp))
            current_addr_script_vars = current_addr_script_vars  + 4
            
    #updating the jumps destination
    
    
    for j in jump_dict.items():
        for start in j[1].addr_start:
            write_dword_in_byte_array("<I", bin_code_section, start, start_code_section + j[1].addr_destination)
    
            
    string_section_addr = start_strings_section     
    
    #first we write the strings from the code
    for str_data in strings_offsets_code:
        where_to_update_ptr = str_data[0]
        actual_string       = str_data[1]
        output = actual_string.encode("utf-8") + b"\0"
        bin_string_section = bin_string_section + output 
        write_dword_in_byte_array("<I", bin_code_section, where_to_update_ptr, FLAG_STR(string_section_addr))
        string_section_addr = string_section_addr + len(output)
    
    bin_file = header_b + bin_function_header_section + bin_fun_output_vars_section + bin_fun_input_vars_section 
    bin_file = bin_file +  bin_structs_section + bin_structs_params_section 
    bin_file = bin_file + bin_script_var_section + bin_code_section
    
    for str_data in strings_offsets_fun_names:
        where_to_update_ptr = str_data[0]
        actual_string       = str_data[1]
        output = actual_string.encode("utf-8") + b"\0"
        bin_string_section = bin_string_section + output 
        write_dword_in_byte_array("<I", bin_file, where_to_update_ptr, FLAG_STR(string_section_addr))
        string_section_addr = string_section_addr + len(output)

    for str_data in strings_offsets_fun_varout:
        where_to_update_ptr = str_data[0]
        actual_string       = str_data[1]
        output = actual_string.encode("utf-8") + b"\0"
        bin_string_section = bin_string_section + output 
        write_dword_in_byte_array("<I", bin_file, where_to_update_ptr, FLAG_STR(string_section_addr))
        string_section_addr = string_section_addr + len(output)
    
    for str_data in strings_offsets_fun_varin:
        where_to_update_ptr = str_data[0]
        actual_string       = str_data[1]
        output = actual_string.encode("utf-8") + b"\0"
        bin_string_section = bin_string_section + output 
        write_dword_in_byte_array("<I", bin_file, where_to_update_ptr, FLAG_STR(string_section_addr))
        string_section_addr = string_section_addr + len(output)

    for str_data in strings_offsets_struct_params:
        where_to_update_ptr = str_data[0]
        actual_string       = str_data[1]
        output = actual_string.encode("utf-8") + b"\0"
        bin_string_section = bin_string_section + output 
        write_dword_in_byte_array("<I", bin_file, where_to_update_ptr, FLAG_STR(string_section_addr))
        string_section_addr = string_section_addr + len(output)
    
    for str_data in strings_offsets_script_var:
        where_to_update_ptr = str_data[0]
        actual_string       = str_data[1]
        output = actual_string.encode("utf-8") + b"\0"
        bin_string_section = bin_string_section + output 
        write_dword_in_byte_array("<I", bin_file, where_to_update_ptr, FLAG_STR(string_section_addr))
        string_section_addr = string_section_addr + len(output)
    
    
    
    bin_file = bin_file + bin_string_section
    
    dat_file = open("test.dat", "wb")
    dat_file.write(bin_file)
    dat_file.close()

def create_script_header(varin, varout):
    global current_script

    current_script.script_variables_in = varin
    current_script.script_variables_out = varout


def PushUndefined(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<I", FLAG_UNDEF(value)))
   
    result = bytearray([0, 4]) + b_arg
    
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)


def PushString(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = bytearray([0, 4]) + b_arg
    bin_code_section = bin_code_section + result
    strings_offsets_code.append((current_addr_code + 2, value)) #recording address for when we know where the string are compiled
    current_addr_code = current_addr_code + len(result)
  
def PushReturnAddress(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = bytearray([0, 4]) + b_arg
    bin_code_section = bin_code_section + result
    if value in jump_dict:
        jump_dict[value].addr_start.append(current_addr_code + 2) #recording address for when we know where the string are compiled
    else:
        jump_dict[value] = jump()
        jump_dict[value].addr_start.append(current_addr_code + 2)
    current_addr_code = current_addr_code + len(result)

def PushFloat(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<I", FLAG_FLOAT(value))) 
    result = bytearray([0, 4]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def PushInteger(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<I", FLAG_INT(value))) 
    result = bytearray([0, 4]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def Pop(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<B", value)) 
    result = bytearray([1]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def RetrieveElementAtIndex(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([2]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)


def RetrieveElementAtIndex2(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([3]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def RetrieveElementAtIndexInteger(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([4]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def PutBackAtIndex(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([5]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def PutBack(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([6]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def Load32(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([7]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def Store32(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<i", value)) 
    result = bytearray([8]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def Load8(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<B", value)) 
    result = bytearray([9]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def Store8(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<B", value)) 
    result = bytearray([0x0A]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def JumpTo(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = bytearray([0x0B]) + b_arg
    bin_code_section = bin_code_section + result
    if value in jump_dict:
        jump_dict[value].addr_start.append(current_addr_code + 1) #recording address for when we know where the string are compiled
    else:
        jump_dict[value] = jump()
        jump_dict[value].addr_start.append(current_addr_code + 1)
    current_addr_code = current_addr_code + len(result)

def Label(value):
    global current_addr_code
    global bin_code_section

    if value in jump_dict:
        jump_dict[value].addr_destination = current_addr_code
    else:
        jump_dict[value] = jump()
        jump_dict[value].addr_destination = current_addr_code

def Call(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<H", value)) 
    result = bytearray([0x0C]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + 3

def Exit():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x0D])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def JumpIfFalse(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<I", 0)) 
    result = bytearray([0x0E]) + b_arg
    bin_code_section = bin_code_section + result
    if value in jump_dict:
        jump_dict[value].addr_start.append(current_addr_code + 1) #recording address for when we know where the string are compiled
    else:
        jump_dict[value] = jump()
        jump_dict[value].addr_start.append(current_addr_code + 1)
    current_addr_code = current_addr_code + len(result)

def JumpIfTrue(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<I", 0)) 
    result = bytearray([0x0F]) + b_arg
    bin_code_section = bin_code_section + result
    if value in jump_dict:
        jump_dict[value].addr_start.append(current_addr_code + 1) #recording address for when we know where the string are compiled
    else:
        jump_dict[value] = jump()
        jump_dict[value].addr_start.append(current_addr_code + 1)
    current_addr_code = current_addr_code + len(result)

def Add():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x10])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def Subtract():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x11])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def Multiply():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x12])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def Divide():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x13])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def Modulo():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x14])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def Equal():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x15])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def NonEqual():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x16])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def GreaterThan():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x17])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def GreaterOrEq():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x18])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def LowerThan():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x19])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def LowerOrEq():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x1A])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def And():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x1B])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def Or():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x1C])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def Or2():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x1D])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)
def Or3():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x1E])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def Negative():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x1F])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def IsTrue():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x20])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def Xor():
    global current_addr_code
    global bin_code_section

    result = bytearray([0x21])
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def CallFromAnotherScript(str1, str2, var):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = bytearray([0x22]) + b_arg
    strings_offsets_code.append((current_addr_code + 1, str1)) 
    
    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = result + b_arg
    strings_offsets_code.append((current_addr_code + 5, str2)) 
    b_arg = bytearray(struct.pack("<B", var)) #placeholder
    result = result + b_arg
    bin_code_section = bin_code_section + result

    current_addr_code = current_addr_code + len(result)

def CallFromAnotherScript2(str1, str2, var):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = bytearray([0x23]) + b_arg
    strings_offsets_code.append((current_addr_code + 1, str1)) 
    
    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = result + b_arg
    strings_offsets_code.append((current_addr_code + 5, str2)) 
    b_arg = bytearray(struct.pack("<B", var)) 
    result = result + b_arg
    bin_code_section = bin_code_section + result

    current_addr_code = current_addr_code + len(result)

def RunCommand(var, command_name):
    global current_addr_code
    global bin_code_section
    (id_struct, op_code) = ED9InstructionsSet.reverse_commands_dict[command_name]

    struct_b = bytearray(struct.pack("<B", id_struct))
    op_code_b = bytearray(struct.pack("<B", op_code))
    nb_var_b = bytearray(struct.pack("<B", var))
    result = bytearray([0x24]) + struct_b + op_code_b + nb_var_b
    
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def Instr_0x25(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<I", 0)) #placeholder
    result = bytearray([0x25]) + b_arg
    bin_code_section = bin_code_section + result
    if value in jump_dict:
        jump_dict[value].addr_start.append(current_addr_code + 1) #recording address for when we know where the string are compiled
    else:
        jump_dict[value] = jump()
        jump_dict[value].addr_start.append(current_addr_code + 1)
    current_addr_code = current_addr_code + len(result)

def AddLineMarker(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<H", value))
    result = bytearray([0x26]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def Pop2(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<B", value))
    result = bytearray([0x27]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

def DebugLogInt(value):
    global current_addr_code
    global bin_code_section

    b_arg = bytearray(struct.pack("<i", value))
    result = bytearray([0x28]) + b_arg
    bin_code_section = bin_code_section + result
    current_addr_code = current_addr_code + len(result)

