#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

// macro definition
#define RR 1
#define RM 2 
#define IM 3
#define IR 4
#define MR 5
#define RN 6
#define MN 7
#define IN 8


// Constant
MEM_SIZE = 1024 * 1024; //Byte
REG_NUM = 16;
CODE_S = 0x0;
DATA_S = 0x40000;
STACK_S = 0x80000;
PC_REG = 14
SP_REG = 15 
//GLOBAL VARIABLE
FLAG_JMP = 0

// Memory
uint8_t *MEM;



//Register
uint64_t *REG;

// Instruction DS
typedef struct instruction {
	char opName[5];
	char S[20];
	char D[20];
}ins; 
// Temporary code section
ins *INS;

int mode_interpret(char S[20], char D[20], uint64_t *s, uint64_t *d) {
	int mode = 0;
	return mode;
}

void op_exec(ins *I) {
	switch (I->opName) {
		case "MOV": {
			uint64_t s, d;
			int mode = mode_interpret(I->S, I->D, &s, &d);
			switch (mode) {
				case RR: {  
					REG[d] = REG[s];                                                                                                               
					break;
				}
				case RM: {
					MEM[d] = REG[s];
					break;
				} 
				case IM: {
					MEM[d] = s;
					break;
				}
				case IR: {
					REG[d] = s;
					break;
				}
				case MR: {
					REG[s] = MEM[d];
					break;
				}
			}
			break;
		}
		case "PUSH": {
			uint64_t s;
			int mode = mode_interpret(I->S, NULL, &s, NULL);
			switch (mode) {
				case IN: REG[SP_REG] = s; break;
				case MN: REG[SP_REG] = MEM[s]; break;
				case RN: REG[SP_REG] = REG[s]; break; 
			} 
			break;
		}
		case "POP": {
			uint64_t d;
			int mode = mode_interpret(NULL, I->D, NULL, &d);
			switch (mode) {
				case RN: REG[d] = REG[SP_REG]; break;
				case MN: MEM[d] = REG[SP_REG]; break; 
			}
			break;
		}
		case "INC": {
			uint64_t d;
			int mode = mode_interpret(NULL, I->D, NULL, &d);
			switch (mode) {
				case MN: MEM[d]++; break;
				case RN: REG[d]++; break;
			} 
			break;
		}
		case "DEC": {
			uint64_t d;
			int mode = mode_interpret(NULL, I->D, NULL, &d);
			switch (mode) {
				case MN: MEM[d]--; break;
				case RN: REG[d]--; break;
			} 
			break;
		}
		case "NOT": {
			uint64_t d;
			int mode = mode_interpret(NULL, I->D, NULL, &d);
			switch (mode) {
				case MN: MEM[d] = !MEM[d]; break;
				case RN: REG[d] = !REG[d]; break;
			} 
			break;
		}
		case "ADD": {
			uint64_t s,d;
			int mode = mode_interpret(I->S, I->D, &s, &d);
			switch (mode) {
				case IR: REG[d] += s; break;
				case IM: MEM[d] += s; break;
				case RR: REG[d] += REG[s]; break;
				case RM: MEM[d] += REG[s]; break;
				case MR: REG[d] += MEM[s]; break;
			}
			break;
		}
		case "SUB": {
			uint64_t s,d;
			int mode = mode_interpret(I->S, I->D, &s, &d);
			switch (mode) {
				case IR: REG[d] -= s; break;
				case IM: MEM[d] -= s; break;
				case RR: REG[d] -= REG[s]; break;
				case RM: MEM[d] -= REG[s]; break;
				case MR: REG[d] -= MEM[s]; break;
			}
			break;
		}
		case "IMUL": {
			uint64_t s,d;
			int mode = mode_interpret(I->S, I->D, &s, &d);
			switch (mode) {
				case IR: REG[d] *= s; break;
				case IM: MEM[d] *= s; break;
				case RR: REG[d] *= REG[s]; break;
				case RM: MEM[d] *= REG[s]; break;
				case MR: REG[d] *= MEM[s]; break;
			}
			break;
		}
		case "DIV": {
			uint64_t s,d;
			int mode = mode_interpret(I->S, I->D, &s, &d);
			switch (mode) {
				case IR: REG[d] /= s; break;
				case IM: MEM[d] /= s; break;
				case RR: REG[d] /= REG[s]; break;
				case RM: MEM[d] /= REG[s]; break;
				case MR: REG[d] /= MEM[s]; break;
			}
			break;
		}
		case "XOR": {
			uint64_t s,d;
			int mode = mode_interpret(I->S, I->D, &s, &d);
			switch (mode) {
				case IR: REG[d] ^= s; break;
				case IM: MEM[d] ^= s; break;
				case RR: REG[d] ^= REG[s]; break;
				case RM: MEM[d] ^= REG[s]; break;
				case MR: REG[d] ^= MEM[s]; break;
			}
			break;
		}
		case "OR": {
			uint64_t s,d;
			int mode = mode_interpret(I->S, I->D, &s, &d);
			switch (mode) {
				case IR: REG[d] |= s; break;
				case IM: MEM[d] |= s; break;
				case RR: REG[d] |= REG[s]; break;
				case RM: MEM[d] |= REG[s]; break;
				case MR: REG[d] |= MEM[s]; break;
			}
			break;
		}
		case "AND": {
			uint64_t s,d;
			int mode = mode_interpret(I->S, I->D, &s, &d);
			switch (mode) {
				case IR: REG[d] &= s; break;
				case IM: MEM[d] &= s; break;
				case RR: REG[d] &= REG[s]; break;
				case RM: MEM[d] &= REG[s]; break;
				case MR: REG[d] &= MEM[s]; break;
			}
			break;
		}
		case "SAL": {
			uint64_t s,d;
			int mode = mode_interpret(I->S, I->D, &s, &d);
			switch (mode) {
				case IR: REG[d] << s; break;
				case IM: MEM[d] << s; break;
				case RR: REG[d] << REG[s]; break;
				case RM: MEM[d] << REG[s]; break;
				case MR: REG[d] << MEM[s]; break;
			}
			break;
		}
		case "SAR": {
			uint64_t s,d;
			int mode = mode_interpret(I->S, I->D, &s, &d);
			switch (mode) {
				case IR: REG[d] >> s; break;
				case IM: MEM[d] >> s; break;
				case RR: REG[d] >> REG[s]; break;
				case RM: MEM[d] >> REG[s]; break;
				case MR: REG[d] >> MEM[s]; break;
			}
			break;
		}
		case "CMP": {
			
			break;
		}
		case "TEST": {
			break;
		}
		case "SETE": {
			break;
		}
		case "SETNE": {
			break;
		}
		case "SETS": {
			break;
		}
		case "SETNS": {
			break;
		}
		case "SETG": {
			break;
		}
		case "SETGE": {
			break;
		}
		case "SETL": {
			break;
		}
		case "SETLE": {
			break;
		}
		case "JMP": {
			break;
		}
		case "JE": {
			break;
		}
		case "JNE": {
			break;
		} 
		case "JS": {
			break;
		}
		case "JNS": {
			break;
		}
		case "JG": {
			break;
		}
		case "JGE": {
			break;
		}
		case "JL": {
			break;
		}
		case "JLE": {
			break;
		}
		case "RET": {  
			break;
		}
		case "STP": {
			break;
		}
		case "ECHO": {
			break;
		}
	}
}



void Initial() {
	MEM = (uint8_t *)malloc(sizeof(uint8_t) * MEM_SIZE);
	for (int i = 0; i < MEM_SIZE; i++) MEM[i] = 0;                    // Memory Initial
	
	REG = (uint64_t *)malloc(sizeof(uint64_t) * REG_NUM);
	for (int i = 0; i < REG_NUM; i++) REG[i] = 0;
	
	REG[PC_REG]= CODE_S;
	REG[SP_REG] = STACK_S;
	
	INS = (ins *)malloc(sizeof(ins) * (DATA_S - STACK_S)); PC = 0;   //temporary 
	printf("Initial Finished!\nPress any key to continue.");
	getchar();	
}

void Load(FILE *file) {    // 暂时将代码区另开结构体数组，后续将其转换为二进制形式与栈、数据统一 
	int i = 0;
	while (fscanf(file, "%s %s %s", INS[i++].opName, INS[i++].S, INS[i++].D) == 3) ;
	// 临时：  指令必须写成  这样的三个字符串 
	printf("Load Finished! Total Ins number:%d\nPress any key to continue.", i);
	getchar();
}

void Run() {
	ins *currentIns = NULL;
	currentIns = &INS[PC];
	while ( !strcmp(currentIns->opName, "STP") ) {
		op_exec(currentIns);
		if (!FLAG_JMP)
			PC++;
		currentINs = &INS[PC];
	}
} 

int main(int argc, char **argv)
{
	char asm_filename[20];
	
	if (argc != 2) {
		printf("Input Error!\n");
		exit(-1);
	}
	
	strcpy(filename, argc[1]);
	
	FILE *asm_file = fopen(asm_filename, "r");
	if (asm_file == NULL) {
		printf("The file %s doesn't exist\n", argv[1]);
		exit(-1)
	}
	
	Initialize();
	Load(asm_file);
	Run();
	
	return 0;
}
