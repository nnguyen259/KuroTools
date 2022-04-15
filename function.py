
from lib.parser import process_data, readint, readintoffset, readtextoffset, remove2MSB, get_actual_value_str
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

    
    