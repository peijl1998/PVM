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
long long MEM_SIZE = 1024 * 1024; //Byte
int REG_NUM = 16;
int CODE_S = 0x0;
int DATA_S = 0x40000;
int STACK_S = 0x80000;
int PC_REG = 14;
int SP_REG = 15 ;
//GLOBAL VARIABLE
int FLAG_JMP = 0;

// Memory
uint64_t *MEM;
int ZF = 0;
int SF = 0;
int OF = 0;


//Register
uint64_t *REG;

// Instruction DS
typedef struct instruction {
	char opName[20];
	char S[20];
	char D[20];
}ins; 
// Temporary code section
ins INS[10000];

int mode_interpret(char S[20], char D[20], uint64_t *s, uint64_t *d) {
	int mode = 0;
	return mode;
}


void Initial() {
	MEM = (uint64_t *)malloc(sizeof(uint64_t) * MEM_SIZE);

	for (int i = 0; i < MEM_SIZE; i++) MEM[i] = 0;                    // Memory Initial
	
	REG = (uint64_t *)malloc(sizeof(uint64_t) * REG_NUM);
	for (int i = 0; i < REG_NUM; i++) REG[i] = 0;
	
	REG[PC_REG]= 0;
	REG[SP_REG] = STACK_S;
	
	printf("Initial Finished!\nPress any key to continue.\n");
}

void Load(FILE *file) {    // 暂时将代码区另开结构体数组，后续将其转换为二进制形式与栈、数据统一 
	int i = 0;
	char a[10],b[10],c[10];
	while (fscanf(file, "%s %s %s", &INS[i].opName, &INS[i].S, &INS[i].D) >= 1) {
		printf("%s %s %s\n",INS[i].opName, INS[i].S, INS[i].D);
		i++;
	}
	printf("\n...Load Finished! Total Ins number:%d\nPress any key to continue.\n", i);
	getchar();
}

void monitor() {
	//REG
	for (int i = 0;i < REG_NUM;i++) {
		printf("%d  %d\n",i, REG[i]);
	}
	printf("\n");
	//CC
	printf("ZF:%d\n",ZF);
	
	getchar();
}

int toNum(char *s) {
    int l = strlen(s);
	int rnt = 0;
	for (int i = 0; i < l; i++) {
		rnt *= 10;
		rnt += (s[i] - '0');
	}
	return rnt;
}

void op_exec(ins *I) {
	if ( !strcmp(I->opName,"RRMOV")) {
		int s = toNum(I->S);
		int d = toNum(I->D);
		REG[d] = REG[s];
	}
	if ( !strcmp(I->opName,"IRMOV")) {
		int s = toNum(I->S);
		int d = toNum(I->D);
		REG[d] = s;
	}
    if ( !strcmp(I->opName,"RMMOV")) {
		int s = toNum(I->S);
		int d = REG[toNum(I->D)];
		MEM[d] = REG[s];
	}
    if ( !strcmp(I->opName,"MRMOV")) {
		int s = REG[toNum(I->S)];
		int d = toNum(I->D);
		REG[d] = MEM[s];
	}
    if (!strcmp(I->opName,"PUSH")) {
        int s = toNum(I->S);
        MEM[REG[SP_REG++]] = REG[s];
    }
    if (!strcmp(I->opName,"POP")) {
        int d = toNum(I->S);
        REG[d] = MEM[REG[SP_REG--]];
    }
    if (!strcmp(I->opName,"INC")) {
        int d = toNum(I->S);
        REG[d]++;
    }
    if (!strcmp(I->opName,"DEC")) {
        int d = toNum(I->S);
        REG[d]--;
    }
	if ( !strcmp(I->opName,"ADD")){
		int s = toNum(I->S);
		int d = toNum(I->D);
		REG[d] = REG[d] + REG[s];
	}
    if ( !strcmp(I->opName,"SUB")){
		int s = toNum(I->S);
		int d = toNum(I->D);
		REG[d] = REG[d] - REG[s];
	}
    if ( !strcmp(I->opName,"IMUL")){
		int s = toNum(I->S);
		int d = toNum(I->D);
		REG[d] = REG[d] * REG[s];
	}
    if ( !strcmp(I->opName,"DIV")){
		int s = toNum(I->S);
		int d = toNum(I->D);
		REG[d] = REG[d] / REG[s];
	}
    if (!strcmp(I->opName,"NOT")) {     //some problems maybe
        int d = toNum(I->S);
        REG[d] = ~REG[d];
    }
    if (!strcmp(I->opName,"XOR")) {
        int s = toNum(I->S);
        int d = toNum(I->D);
        REG[d] = REG[d] ^ REG[s];
    }
    if (!strcmp(I->opName,"OR")) {
        int s = toNum(I->S);
        int d = toNum(I->D);
        REG[d] = REG[d] | REG[s];
    }
    if (!strcmp(I->opName,"AND")) {
        int s = toNum(I->S);
        int d = toNum(I->D);
        REG[d] = REG[d] & REG[s];
    }
    if (!strcmp(I->opName,"SAL")) {
        int k = toNum(I->S);
        int d = toNum(I->D);
        REG[d] = REG[d] << k;
    }
    if (!strcmp(I->opName,"SAR")) {
        int k = toNum(I->S);
        int d = toNum(I->D);
        REG[d] = REG[d] >> k;
    }
    if (!strcmp(I->opName,"CMP")) {
        int s = toNum(I->S);
        int d = toNum(I->S);
        //减法的 状态修改部分
    }
    if (!strcmp(I->opName,"JMP")) {
        int addr = REG[toNum(I->S)];
        REG[PC_REG] = addr; 
    }
    if (!strcmp(I->opName,"JE") && ZF) {
        int addr = REG[toNum(I->S)];
        REG[PC_REG] = addr; 
    }
    if (!strcmp(I->opName,"JNE") && !ZF) {
        int addr = REG[toNum(I->S)];
        REG[PC_REG] = addr; 
    }
    if (!strcmp(I->opName,"JLE") && ((SF^OF)|ZF) ) {
        int addr = REG[toNum(I->S)];
        REG[PC_REG] = addr; 
    }
    if (!strcmp(I->opName,"JL") && (SF^OF) ) {
        int addr = REG[toNum(I->S)];
        REG[PC_REG] = addr; 
    }
    if (!strcmp(I->opName,"JGE") && (!(SF^OF)) ) {
        int addr = REG[toNum(I->S)];
        REG[PC_REG] = addr; 
    }
    if (!strcmp(I->opName,"JG") && ((!(SF^OF))|(!ZF)) ) {
        int addr = REG[toNum(I->S)];
        REG[PC_REG] = addr; 
    }
    if (!strcmp(I->opName,"RECHO")) {
        int s = toNum(I->S);
        printf("REG %d:%d\n",s,REG[s]);
    }
    if (!strcmp(I->opName,"MECHO")) {
        int s = REG[toNum(I->S)];
        printf("MEM %d:%d\n",s,MEM[s]);
    }
    if (!strcmp(I->opName,"INPUT")) {
        int s = REG[toNum(I->S)];
        scanf("Please input the data:\n>%d",&MEM[s]);
    }
}

void Run() {
	ins *currentIns = NULL;
	currentIns = &INS[REG[PC_REG]];
	while ( strcmp(currentIns->opName, "HLT") ) {
		printf("\n----%s %s %s-----\n",currentIns->opName,currentIns->S,currentIns->D);
	
		op_exec(currentIns);
		monitor();
		if (!FLAG_JMP)
			REG[PC_REG]++;
		currentIns = &INS[REG[PC_REG]];
	}
} 

int main(void)
{	
	FILE *file = fopen("pro.txt","r");
	Initial();
	Load(file);
	Run();
	
	return 0;
}
