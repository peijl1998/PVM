# 简易虚拟机设计报告
   
## 一、虚拟机硬件结构
   
### （一） 数据通路

1. 整体框架

![img](http://oy0lnxej5.bkt.clouddn.com/vm1.png)
                                                                         

2. 简要概述
   - 虚拟机整体硬件框架由`CPU`、`内存`、`I/O`三部分构成，其中`CPU`部分又由`寄存器组`、`运算器`组成。
   - 各个部分之间通过总线连接。（在软件实现中通过`调用函数接口`体现。）
    
### （二）中央处理器

1. 虚拟机的`CPU`部分由`寄存器组`、`运算器`组成。
2. `寄存器组`分为`特殊寄存器组`和`通用寄存器组`，共16个寄存器。
   - 特殊寄存器组：
     - CC(Condition Code Register): 条件码寄存器，维护`CF`(进位标志)、`ZF`(零标志)、`SF`(符号标志)、`OF`(溢出标志)，供条件转移指令使用。
     - PC(Program Counter): 程序计数器，维护当前执行程序指令的地址。
     - SP(Stack Pointer): 栈指针，维护栈区的栈顶地址。
   - 通用寄存器组：
     - 供程序指令代码临时存储、保存返回值等。
     - 定义为`R1` 、`R2`......`R13`。
3. `ALU`提供基本的算术逻辑运算，从而实现指令系统的功能。
4. 虚拟机的`CPU`为**64位**， 因此将寄存器设置为能够存储64位数据（方便统一处理，CC也设置为64位）。

    
###（三）主存储器

1. 虚拟机的主存储器大小为`1024 * 1024`字节，即`1MB`存储空间，每个存储单元为`8bits`。

2. 由于内存大小为`1MB`，地址范围为0x00000~0xFFFFF。

3. 主存储器将设置`程序代码区`、`数据区`、`栈区`三大分区：

   |  分区名称  |        功能        |       地址范围       |
   | :--------: | :----------------: | :------------------: |
   | 程序代码区 |    存储指令序列    | 0x00000~0x3FFFF |
   |   数据区   | 存储程序需要的数据 | 0x40000~0xAFFFF |
   |    栈区    |       程序栈       | 0xB0000~0xFFFFF |


   
###（四）I/O

1. 虚拟机的主要`I/O`设备为`显示设备`、`磁盘`。
2. 显示设备提供`结果显示`、`设备监控`两大功能，统一由`显示控制器`协调处理。
   - 显示控制器：在软件实现中体现为一子函数，能够打包程序运行结果与寄存器等设备的运行时数值并交由显示设备输出。
   - 设备监控：为用户提供监视寄存器、主存储器数值的接口。
   - 结果显示：前期设计为命令行版本，后期设计为动画演示。
3. 磁盘主要负责存储`源代码`，`磁盘控制器`能够将程序源代码送至`I/O`接口处并转换成虚拟机能够识别的可执行程序，再送往主存储器中的程序代码区。



## 二、指令集架构

1. 操作数与寻址模式

   - 操作数：
     - 立即数，64位数据，用`I`表示。
     - 寄存器，寄存器序号，用`R`表示。
     - 内存，内存地址，用`M`表示。
   - 操作数类别：
     - `RR`：寄存器到寄存器。
     - `RM`：寄存器到内存。
     - `MR`：内存到寄存器。
     - `IR`：立即数到寄存器。
     - `IM`：立即数到内存。
     - 考虑到CPU时序问题，禁止`MM`(内存到内存)的寻址方式。
   - 寻址模式：
     - 直接寻址，例如`IM`中，M直接给出`0x2ffff`来进行内存直接寻址。
     - 间接寻址，例如`RM`中，M可以用`%rsp`来取得寄存器存储地址对应的内存数值，完成间接寻址。

2. 指令集 （S：源操作数  D：目的操作数）

   |    指令    | 操作数类别 |                        说明                         |
   | :--------: | :--------: | :-------------------------------------------------: |
   |    HLT     |     无     |                      停机指令                       |
   | RRMOV S,D  |     RR     |              一般传送，D<----S               |
   | IRMOV S,D  |     IR     |              一般传送，D<----S               |
   | RMMOV S,D  |     RM     |              一般传送，D<----S               |
   | MRMOV S,D  |     MR     |              一般传送，D<----S               |
   |   PUSH S   |     R      |            入栈，*SP<----S，SP++             |
   |   POP D    |     R      |            出栈，D<----*​SP，SP--             |
   |   INC D    |     R      |               自增，D<----D+1                |
   |   DEC D    |     R      |               自减，D<----D-1                |
   |  ADD S,D   |     RR     |                加，D<----D+S                 |
   |  SUB S,D   |     RR     |                减，D<----D-S                 |
   |  IMUL S,D  |     RR     |                乘，D<----D*S                 |
   |  DIV S,D   |     RR     |                除，D<----D/S                 |
   |   NOT D    |     R      |                 非，D<----~D                 |
   |  XOR S,D   |     RR     |               异或，D<----D^S                |
   |   OR S,D   |     RR     |                或，D<----D\|S                |
   |  AND S,D   |     RR     |                与，D<----D&S                 |
   |  SAL k,D   |     IR     |               左移，D<----D<<k               |
   |  SAR k,D   |     IR     |         右移，D<----D>>k（算数右移）         |
   | CMP S1,S2  |     RR     |                     比较，S2-S1                     |
   | TEST S1,S2 |     RR     |                     测试，S1&S2                     |
   |  JMP ADDR  |     R      |      无条件转移，PC<----ADDR（下同），       |
   |  JE ADDR   |     R      |                 条件转移，条件：ZF                  |
   |  JNE ADDR  |     R      |                 条件转移，条件：~ZF                 |
   |  JLE ADDR  |     R      |             条件转移，条件：(SF^OF)\|ZF             |
   |  JL ADDR   |     R      |                条件转移，条件：SF^OF                |
   |  JGE ADDR  |     R      |              条件转移，条件：~(SF^OF)               |
   |  JG ADDR   |     R      |            条件转移，条件：~(SF^OF)&~ZF             |
   | CMOVLE S,D |     RR     | 条件传送，条件：(SF^OF)\|ZF，D<----S（下同） |
   | CMOVL S,D  |     RR     |                条件传送，条件：SF^OF                |
   | CMOVE S,D  |     RR     |                 条件传送，条件：ZF                  |
   | CMOVNE S,D |     RR     |                 条件传送，条件：~ZF                 |
   | CMOVGE S,D |     RR     |             条件传送，条件：~（SF^OF）              |
   | CMOVG S,D  |     RR     |            条件传送，条件：~(SF^OF)&~ZF             |
   |  RECHO S   |     R      |                     寄存器输出                      |
   |  MECHO S   |     M      |                    主存储器输出                     |
   |  INPUT S   |     M      |                    主存储器输入                     |
   |    RET     |     无     |                        返回                         |
   |   INT S    |     R      |                 调用中断服务子程序                  |

## 三、虚拟机软件实现架构

### （一）整体框架 

![52171606747](http://oy0lnxej5.bkt.clouddn.com/vm2.png)

### （二）细节描述

1. 数据结构

   - 寄存器：由于每个寄存器存储64位数据，虚拟机采用长度为`REG_SIZE=16`的64位整型数组来模拟寄存器组。其中`REG[0]~REG[12]`为通用寄存器，而`REG[13]~REG[15]`分别为`SP(栈指针)`、`PC(程序计数器)`、`CC(状态码寄存器)`。

     ```c
     int REG_SP = 13, REG_PC = 14, REG_CC = 15;
     int64_t REG[REG_SIZE];
     ```

   - 主存储器：由于虚拟机功能有限，将汇编代码作为可执行程序，因此主存储器采用两种数据结构来模拟。

     - 程序代码区： 虚拟机定义了一种结构体来存储每一条指令，并且将所有指令存储于该类型的结构体数组中，结构体索引就是程序代码再主存储器中的地址，`PC`指向该结构体数组中的某一位置。结构体定义如下：

       ```c
       typedef struct instruction {
           char insName[6];
           int64_t S;
           int64_t D;
       }instruction;
       ```

       其中`insName`、`S`、`D`分别表示指令名称、源操作数、目的操作数。程序代码区则由该类型的结构体数组构成，如下（其中，`CODE_SIZE`表示程序代码区大小）：

       ```c
       instruction *MEM_CODE[CODE_SIZE];
       ```

     - 数据区和栈区：主存储器中另两个分区将直接用字节数组模拟，具体定义如下(其中`DATA_SIZE`表示数据区的大小，`STACK_SIZE`表示栈区的大小):

       ```c
       uint32_t DATA_SIZE = 0x6FFFF, STACK_SIZE = 0x4FFFF;
       int8_t MEM[DATA_SIZE + STACK_SIZE];
       ```

       需要注意的地方是，由于主存储器的存储单元为`1Byte`，而数据总线是`64Bits`，因此每一个数据需要四个存储单元存放，本虚拟机采用**大端模式**，即数据的高字节存放在内存的低地址。例如$(1111111111110000000011111010101001010101000000000000000000000000)_2$在内存中表示为（从低到高读）：

       | 0x00000  | 0x00001  | 0x00002  | 0x00003  | 0x00004  | 0x00005  | 0x00006  | 0x00007  |
       | -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- |
       | 11111111 | 11110000 | 00001111 | 10101010 | 01010101 | 00000000 | 00000000 | 00000000 |

2. 控制器与接口

   - PVM.c：包含`Vm_load()`、`Vm_run()`、`Vm_initialize`，分别负责虚拟机程序装载、程序运行、硬件初始化的功能。
   - ALU.c：包含各个指令的具体操作。
   - utils.c：包含如进制转换、字符处理等工具函数。