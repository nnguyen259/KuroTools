from lib.parser import process_data, readint, readintoffset, readtextoffset, remove2MSB, get_actual_value_str
import disasm.ED9InstructionsSet as ED9InstructionsSet
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
                self.output_args.append(readintoffset(stream, out_ptr + id_out * 4, 4))
            for id_in in range(varin):
                self.input_args.append(readintoffset(stream, in_ptr + id_in * 4, 4))
            

            
            nb_structs = readint(stream, 4)
            structs_ptr = readint(stream, 4)

            for id_st in range(nb_structs):
                id_chr = readintoffset(stream, structs_ptr + id_st * 0xC + 0, 4, signed = True)
                nb_sth1 = readintoffset(stream, structs_ptr + id_st * 0xC + 4, 2)
                nb_sth2 = readintoffset(stream, structs_ptr + id_st * 0xC + 6, 2) 
                ptr_sth = readintoffset(stream, structs_ptr + id_st * 0xC + 8, 4)
                
                mysterious_array2 = []


                for id_arr in range(nb_sth2):
                    mysterious_array2.append(readintoffset(stream, ptr_sth + id_arr * 8 + 0, 4))
                    mysterious_array2.append(readintoffset(stream, ptr_sth + id_arr * 8 + 4, 4))

                mysterious_struct = { #Related to characters? Characters in the scene or something?
                "id": id_chr,
                "nb_sth1": nb_sth1,
                "array2": mysterious_array2,
                }
                self.structs.append(mysterious_struct)

            self.hash = readint(stream, 4)
            ptr_fun_name = remove2MSB(readint(stream, 4))
            if (ptr_fun_name < ED9InstructionsSet.smallest_data_ptr):
                ED9InstructionsSet.smallest_data_ptr = ptr_fun_name
            self.name = readtextoffset(stream, ptr_fun_name)
            self.instructions = []