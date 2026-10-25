from Isa import INT, FPA, FPM, LSU

UNIT_ALIAS = {
    'int_adder': INT, 'integer_adder': INT, 'integer adder': INT, 'int': INT,
    'fp_adder': FPA, 'fp adder': FPA, 'fpadd': FPA,
    'fp_mult': FPM, 'fp_multiplier': FPM, 'fp multiplier': FPM, 'fpmul': FPM,
    'ld_st': LSU, 'ld_st_unit': LSU, 'load/store unit': LSU,
    'load_store_unit': LSU, 'lsu': LSU, 'memory': LSU,
}


class Config:
    def __init__(self):
        self.rs = {INT: 2, FPA: 3, FPM: 2, LSU: 3}
        self.ex = {INT: 1, FPA: 3, FPM: 20, LSU: 1}
        self.fu = {INT: 1, FPA: 1, FPM: 1, LSU: 1}
        self.pipelined = {INT: False, FPA: True, FPM: True, LSU: False}
        self.mem_cycles = 4
        self.rob = 128
        self.cdb_buffer = 1