import alu
import ui
import utils
import re

#--------------Configure Set-----------------------------------------------
filename = "test.txt"
debug = True

# REGISTER SET
NUM_REG = 16
PC_REG = 13
SP_REG = 14
CC_REG = 15

# MEMORY SET
LEN_MEM_DATA = 100
LEN_MEM_CODE = 100
POS_INTCODE = 60
POS_STACK = 40
#--------------------------------------------------------------------------

#--------------Variable Set------------------------------------------------

# REGISTER SET
REG = [0] * NUM_REG

# MEMORY SET
MEM_DATA = [0] * LEN_MEM
MEM_CODE = [{'insName':None,'op1':None,'op2':None}] * LEN_MEM_CODE

# INDICATOR SET
FLAG_JMP = False
#--------------------------------------------------------------------------


#---------------------Sub-Function-----------------------------------------
def VM_initial():
    MEM_DATA = [0] * LEN_MEM
    MEM_CODE = [{'insName':None,'op1':None,'op2':None}] * LEN_MEM_CODE
    REG = [0] * NUM_REG
    REG[PC_REG] = 0
    REG[SP_REG] = POS_STACK
    FLAG_JMP = False
    
    if (debug):
        print("Initialize Finished!")
        input("Press any key to continue.")

def VM_preprocess(filename):
    file = open(filename,"r+")
    new_file = ''
    for line in file.readlines():
        pos_comment = line.find("//")
        if (pos_comment ！= -1)：
            line = line[0:pos_comment]
        ins = re.compile('\s+').split(line)
        if (len(ins) == 1):
            ins.append('NULL')
            ins.append('NULL')
        elif (len(ins) == 2):
            ins.append('NULL')
        new_file = " ".join(ins) + '\n'
    file.write(new_file)
    if (debug):
        print("Preprocess Finished!")
        input("Press any key to continue.")
    

def VM_load(filename):
    ins = {'insName':None,'op1':None,'op2':None}
    file = open(filename,"r")
    insNum = 0
    for line in file.readlines():
        temp_ins = line.split(' ')
        ins['insName'] = temp_ins[0].upper()
        ins['op1'] = temp_ins[1]
        ins['op2'] = temp_ins[2]
        MEM_CODE[insNum] = ins
        insNum = insNum + 1
        if (debug):
            print(insNum,":  ",ins)
    
    if (debug):
        print("Load Finished and ins'number is ",insNum)
        input("Press any key to continue.")
    

def VM_run():
    currentIns = MEM_CODE[REG[PC_REG]]
    while (currentIns['insName'] != 'HLT'):
        if (debug):
            print("Currentins: ",currentIns)
        
        alu.ins_exec(currentIns)
        if (not FLAG_JMP):
            REG[PC_REG] = REG[PC_REG] + 1
        currentIns = MEM_CODE[REG[PC_REG]]
        



#--------------------------------------------------------------------------








# main 

VM_initial()
VM_preprocess(filename)
VM_load(filename)
VM_run()


