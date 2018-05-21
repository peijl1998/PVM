

!!! Readme是从实验文档用户手册部分直接复制而来，排版不够美观，可直接查看repo中的<a href="
实验文档.pdf">实验文档.pdf</a>文件



## （1） **安装说明**

Simple-VM使用Python3.6和PyGtk开发，开发系统是Linux，用户应该实现配置相似的环境，下面给出PyGtk在Linux下的安装，打开terminal，输入以下命令：

```python 
sudo apt-get install -y python-gtk2
```

当环境准备完成后，将PVM.py文件放在目录下，执行：

 

```python
python3 PVM.py
```



即可进入PVM的启动界面。

 

## （2） **加载程序**

Simple-VM采用图形化加载方式，在启动界面可以点击加载按钮，选择特定的用户代码，Simple-VM会自动进行加载，将代码转换成虚拟机可识别的数据结构并存入内存。如图6-1，值得注意的是，Simple-VM未对用户选择的文件进行内容筛选，即用户应保证输入的文件是你想执行的txt文件，而不是其他格式的文件。

 

![img](file:///C:\Users\45371\AppData\Local\Temp\ksohtml\wps834D.tmp.jpg) 

![img](file:///C:\Users\45371\AppData\Local\Temp\ksohtml\wps835E.tmp.png) 

 

## （3） **查看虚拟机状态**

当代码加载完毕，虚拟机会进入运行状态。用户可以在显示栏选择不同的的虚拟机状态信息进行查看，数据区可以查看用户数据区和堆栈区的内容，代码区可以查看用户代码和中断代码，Simple-VM专门将堆栈和中断代码区用绿色高亮表示，以便用户区分，特殊寄存器也作了相似的处理，用红色高亮表示，显示区则输出虚拟机或代码需要输出的信息（输出结果、异常信息等）。Simple-VM为了方便用户查看状态，使用了区间查看的方式（因为内存空间很大，即使时滚动布局，用户也很难找到特定的数据），用户可以输入起始位置和结束位置从而查看对应区段的内容，见图6-2。

 

![img](file:///C:\Users\45371\AppData\Local\Temp\ksohtml\wps835F.tmp.png)![img](file:///C:\Users\45371\AppData\Local\Temp\ksohtml\wps8360.tmp.jpg)![img](file:///C:\Users\45371\AppData\Local\Temp\ksohtml\wps8361.tmp.jpg) 

 

 

 

## （4） **功能按钮**

Simple-VM提供了一组功能按钮供用户调试使用，分别为单步执行模式按钮、暂停按钮、关机按钮、单步执行控制按钮、运行频率按钮、中断按钮。按钮功能如其名，其中单步执行控制按钮只有在单步执行模式下才有效，当点击时会进行下一步操作（画面刷新、指令执行等），见图6-3。

 

![img](file:///C:\Users\45371\AppData\Local\Temp\ksohtml\wps8371.tmp.png)![img](file:///C:\Users\45371\AppData\Local\Temp\ksohtml\wps8372.tmp.jpg) 

 

 

## （5） **输入框**

Simple-VM提供了一个输入框，方便输入指令的执行，当虚拟机执行INPUT指令时，虚拟机会读取输入框的内容，用户可以在INPUT指令之前输入（否则INPUT会等待用户输入），但是用户需要明白输入框需要用”#”结尾，即”123#”表示输入数字123，另外Simple-VM的输入框采取Expander的方式，能够随时隐藏，如图6-4。

 

![img](file:///C:\Users\45371\AppData\Local\Temp\ksohtml\wps8383.tmp.jpg) 

 

![img](file:///C:\Users\45371\AppData\Local\Temp\ksohtml\wps8384.tmp.png)![![img](file:///C:/Users/45371/AppData/Local/Temp/ksohtml/wps8385.tmp.jpg?lastModify=1526902277)img](file:///C:\Users\45371\AppData\Local\Temp\ksohtml\wps8385.tmp.jpg) 

 

 

## （6） **个性化配置**

Simple-VM提供了一定的配置功能，在启动界面可以选择进入设置界面从而进行一些虚拟机的配置，可以更改数据区大小、代码区大小、堆栈区起始位置、寄存器数量、虚拟机名称，所谓虚拟机名称是指在运行界面子标题的字符串，没有实际功能。

![img](file:///C:\Users\45371\AppData\Local\Temp\ksohtml\wps8396.tmp.png)![img](file:///C:\Users\45371\AppData\Local\Temp\ksohtml\wps8397.tmp.jpg) 