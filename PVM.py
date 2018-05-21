

####################################################
#                                                  #
#                    Simple-VM                     #
#      Simple Simulater to execute instructions.   #          
#                                                  #
#                                         by  Pei  # 
####################################################

# 加载相关库
import gi
import re
import time
import threading
gi.require_version('Gtk','3.0')
from gi.repository import Gtk, Pango, Gdk, GObject, GLib

# 线程初始化
GObject.threads_init()


#-------------------------------------全局常量与相关信号量定义-----------------------------------------------
filename = "program.txt"              # 预处理用户代码后保存的位置，即虚拟机每次执行的代码在磁盘存放位置        
INT_VECTOR = [0x186A0,0x186AA]        # 中断向量，Simple-VM预设了两组中断程序，其代码初始位置由中断向量给出
label_output = [""]                   # 存储显示区信息的结构
REG = []                              # 寄存器List数据结构，用来存储通用寄存器、特殊寄存器数值
MEM_DATA = []                         # 内存代码区Dictionary  List数据结构，用来存储中断代码以及用户代码
MEM_CODE = []                         # 内存数据区List数据结构，用来存储用户数据和堆栈数据                
NUM_REG = 16                          # 默认的寄存器数量
PC_REG = 13                           # PC在寄存器List中的位置
SP_REG = 14                           # SP在寄存器List中的位置
CC_REG = 15                           # CC在寄存器List中的位置
LEN_MEM_DATA = 65537                  # 内存数据区长度
LEN_MEM_CODE = 65535                  # 内存代码区长度，在GUI中，代码区地址需要加上数据区长度的偏移量
INT_START = 98302                     # 中断代码区起始位置
INT_END = 131071                      # 中断代码区结束位置
POS_STACK = 32768                     # 内存数据区的堆栈起始位置
POS_EXTEND = 60001                    # 内存待扩展区起始位置  内存数据区按地址顺序分别为数据区、堆栈区、待扩展区
HOST_NAME = "Pei"                     # 个性化配置中的虚拟机名

INT_NUMBER = 0                        # 中断序列号，用户中断时会记录对应的中断代码序号 
last_sp = 0                           # 上一次栈指针位置，单级中断只需要单个变量保存 
signal_run = False                    # True：虚拟机运行状态  False：虚拟机不运行
signal_pause = False                  # 虚拟机暂停信号
signal_onestep = False                # 虚拟机单步执行信号
signal_int_happen = False             # 虚拟机中断出现信号
signal_int_run = False                # 虚拟机中断正处理信号
signal_jmp = False                    # 虚拟机指令流中出现跳转信号
mutex_one = False                     # 虚拟机单步执行模式中的控制前进信号
frequency = 1                         # 虚拟机运行频率（用指令间延时估计）                
is_end = False                        # 虚拟机结束信号
error_happen = False                  # 虚拟机异常信号
#----------------------------------------------------------------------------------------------------------

#########################################
#                                       #
#                                       #
#        虚拟机图形主体：窗口类           #
#                                       #
#                                       #
#########################################

#---------------------启动窗口：继承自Gtk.Window，功能：窗口切换、选择用户代码、用户代码预处理-------------------
class StartWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Simple-VM")
        self.set_border_width(20)
        self.set_resizable(False)
        self.set_size_request(400,550)
        
        box = Gtk.VBox()
        
        # 图标设置
        grand = Gtk.Image.new_from_file("dog.png")
        box.pack_start(grand, False, False, 0)
        

        # 按钮设置
        box_option = Gtk.Box(spacing=10)

        # 设置键
        button_setting = Gtk.Button.new_from_icon_name("emblem-system-symbolic", Gtk.IconSize.MENU)
        button_setting.connect("clicked",self.on_setting_clicked)
        
        # 启动键
        button_start = Gtk.Button.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.MENU)
        button_start.connect("clicked",self.on_start_clicked)

        # 退出键
        button_quit = Gtk.Button.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
        button_quit.connect("clicked",self.on_quit_clicked)

        alignment = Gtk.Alignment.new(0.5,0.2,0,0)
        alignment.add(box_option)
        box_option.pack_start(button_setting,False,True,0)
        box_option.pack_start(button_start,False,True,0)
        box_option.pack_start(button_quit,False,True,0)
        

        # 附加信息


        none = Gtk.Label() # 空行标签

        # 软件名、软件功能简洁、软件用户手册链接
        label1 = Gtk.Label()
        label1.set_markup("<big><b>Simple-Virtual Machine</b></big>")
        label2 = Gtk.Label("")
        label2.set_markup("Simple Simulater To Execute built-in Instructions")
        font = Pango.FontDescription("Sans 7")
        label2.modify_font(font)
        label3 = Gtk.Label()
        label3.set_markup("<a href=\"silicat.info\" title=\"Click it\">More Details</a>")
        label3.modify_font(font)

        # 容器装入
        box.pack_start(label1,False,True,0)
        box.pack_start(alignment,True,True,0)
        box.pack_start(label2,False,True,0)
        box.pack_start(none,False,True,0)
        box.pack_start(label3,False,True,0)

        self.add(box)
    
    # 预处理程序
    def VM_preprocess(self, src_filename,new_filename):
        file = open(src_filename,"r")
        newF = open(new_filename,"w")
        new_file = ''
        for line in file.readlines():
            line = line.strip()
   
            # 处理空行
            if (len(line) == 0):
                continue
            
            # 处理用户注释
            pos_comment = line.find("//")
            if (pos_comment != -1):
                line = line[0:pos_comment - 1]
            
            # 读取用户指令进行双操作数扩展，不足的用NULL字段填充
            ins = re.compile('\s+').split(line)
            if (ins[-1]==""):
                ins = ins[0:-1]
            if (len(ins) == 1):
                ins.append('NULL')
                ins.append('NULL')
            elif (len(ins) == 2):
                ins.append('NULL')

            # 虚拟机主循环需要，设计问题，与实验无关，需要在HLT前加NOP指令
            if (ins[0] == "HLT"):
                new_file = new_file + "NOP NULL NULL\n"
            new_file = new_file + " ".join(ins) + '\n'
        
        # 将处理之后的代码存入新的文件，供虚拟机加载
        newF.write(new_file)
        file.close()
        newF.close()

    # 启动键响应事件函数，利用FileChooser控件供用户进行代码文件选择
    def on_start_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Choose File", self,Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.VM_preprocess(dialog.get_filename(),filename)
        dialog.destroy()
        
        # 成功选择用户代码之后，将虚拟机运行信号置有效并退出当前窗口
        global signal_run
        signal_run = True 
        
        self.destroy()
        Gtk.main_quit()
     
    # 配合FileChooser的文件筛选器
    def add_filters(self, dialog):
       filter_text = Gtk.FileFilter()
       filter_text.set_name("Text files")
       filter_text.add_mime_type("text/plain")
       dialog.add_filter(filter_text)

       filter_any = Gtk.FileFilter()
       filter_any.set_name("Any files")
       filter_any.add_pattern("*")
       dialog.add_filter(filter_any)
    
    # 设置键事件函数，退出当前窗口并进入设置界面
    def on_setting_clicked(self, button):
        self.destroy()
        Gtk.main_quit()
        setting_window = SettingWindow()
        setting_window.connect("delete-event",Gtk.main_quit)  
        setting_window.show_all()
        Gtk.main()  

    # 退出键事件函数，直接退出虚拟机
    def on_quit_clicked(self, button):
        Gtk.main_quit()

#-----------------------------------------------------------------------------------------------------------

#--------------------设置窗口：继承自Gtk.Window，功能：提供个性化配置，建议不要修改，用户手册给出推荐配置----------
class SettingWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Simple-VM")
        self.set_border_width(20)
        self.set_resizable(False)
        self.set_size_request(400,550)

        # 标题栏设置，将返回键设置在标题栏，体现了Simple-VM的简洁性
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Simple-VM"
        hb.set_subtitle("Setting")
        self.set_titlebar(hb)

        # 返回按钮，箭形图标
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button=Gtk.Button()
        button.add(Gtk.Arrow(arrow_type=Gtk.ArrowType.LEFT,shadow_type=Gtk.ShadowType.NONE))
        button.connect("clicked",self.on_clicked)
        box.add(button)
        hb.pack_start(box)

        # 设置信息：内存设置
        frame_memory = Gtk.Frame.new("Memory")
        frame_memory.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        vbox = Gtk.VBox()
        label = Gtk.Label("Data Size:"); self.entry1 = Gtk.Entry(); self.entry1.set_text(str(LEN_MEM_DATA)) 
        button1 = Gtk.Button(label="Confirm"); button1.connect("clicked",self.on_confirm_data)
        hbox = Gtk.HBox(); hbox.pack_start(label,True,False,0); hbox.pack_start(self.entry1,True,False,0); hbox.pack_start(button1,True,False,0)
        vbox.pack_start(hbox,True,False,0)
        label = Gtk.Label("Code Size:"); self.entry2 = Gtk.Entry(); self.entry2.set_text(str(LEN_MEM_CODE))
        button1 = Gtk.Button(label="Confirm"); button1.connect("clicked",self.on_confirm_code)
        hbox = Gtk.HBox(); hbox.pack_start(label,True,False,0); hbox.pack_start(self.entry2,True,False,0); hbox.pack_start(button1,True,True,0)
        vbox.pack_start(hbox,True,False,0)
        label = Gtk.Label("Position of Stack:"); self.entry3 = Gtk.Entry(); self.entry3.set_text(str(POS_STACK))
        button1 = Gtk.Button(label="Confirm"); button1.connect("clicked",self.on_confirm_stack)
        hbox = Gtk.HBox(); hbox.pack_start(label,True,True,0); hbox.pack_start(self.entry3,True,True,0); hbox.pack_start(button1,True,True,0)
        vbox.pack_start(hbox,True,False,0)

        frame_memory.add(vbox)

        # 设置信息：寄存器设置
        none = Gtk.Label("       ")
        frame_reg = Gtk.Frame.new("Register")
        frame_reg.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        vbox = Gtk.VBox()
        label = Gtk.Label("Number of Register:"); self.entry4 = Gtk.Entry(); self.entry4.set_text(str(NUM_REG))
        button1 = Gtk.Button(label="Confirm"); button1.connect("clicked",self.on_confirm_reg)
        hbox = Gtk.HBox(); hbox.pack_start(label,True,True,0); hbox.pack_start(self.entry4,True,True,0); hbox.pack_start(button1,True,True,0)
        vbox.pack_start(hbox,True,False,0)
        frame_reg.add(vbox)

        # 设置信息： 其他设置（虚拟机名，可显示在运行窗口的子标题中；开机后单步执行模式开关）
        frame_others = Gtk.Frame.new("Others")
        frame_others.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        vbox=Gtk.VBox()
        label = Gtk.Label("Host Name:"); self.entry5 = Gtk.Entry(); self.entry5.set_text(str(HOST_NAME))
        button1 = Gtk.Button(label="Confirm"); button1.connect("clicked",self.on_confirm_name)
        hbox = Gtk.HBox(); hbox.pack_start(label,True,True,0); hbox.pack_start(self.entry5,True,True,0); hbox.pack_start(button1,True,True,0)
        vbox.pack_start(hbox,True,False,0)
        frame_others.add(vbox)

        box = Gtk.VBox()
        box.pack_start(frame_memory,True,True,0)
        box.pack_start(frame_reg,True,True,0)
        box.pack_start(frame_others,True,True,0)
        self.add(box)

    def on_confirm_data(self,button):
        global LEN_MEM_DATA
        LEN_MEM_DATA = int(self.entry1.get_text())   

    def on_confirm_code(self,button):
        global LEN_MEM_CODE
        LEN_MEM_CODE = int(self.entry2.get_text())

    def on_confirm_stack(self,button):
        global POS_STACK
        POS_STACK = int(self.entry3.get_text())

    def on_confirm_reg(self,button):
        global NUM_REG
        NUM_REG = int(self.entry4.get_text())    
        
    
    def on_confirm_name(self,button):
        global HOST_NAME
        HOST_NAME = self.entry5.get_text()    
            

    # 返回键事件函数：关闭当前窗口，返回启动界面
    def on_clicked(self, button):
        self.destroy()
        Gtk.main_quit()
        start_window = StartWindow()
        start_window.connect("delete-event",Gtk.main_quit)
        start_window.show_all()
        Gtk.main()

#------------------------------------------------------------------------------------------------------------

#--------------------运行窗口：继承自Gtk.Window，功能：提供机器状态展示、虚拟机控制功能等-------------------------
class RunningWindow(Gtk.Window):
    # 一些重要的成员变量

    regs = []   # 寄存器控件组
    mem_data = [] # 内存数据区控件组
    mem_code = [] # 内存代码区控件组
    output_labels = [] # 显示区信息标签控件组
    entry = None # 输入框
    data_start = 0
    data_end = 99
    code_start = 0 + LEN_MEM_DATA
    code_end = 99 + LEN_MEM_DATA

    def __init__(self):
        Gtk.Window.__init__(self, title="Simple-VM")
        self.set_border_width(20)
        self.set_resizable(False)
        self.set_size_request(400,550)
        # 标题栏设置，增加子标题为虚拟机名
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Simple-VM"
        global HOST_NAME
        hb.set_subtitle(HOST_NAME)
        self.set_titlebar(hb)

        
        vbox = Gtk.VBox(spacing=6)
        self.add(vbox)


        # 机器状态显示区：分成四页，分别是数据区、代码区、寄存器区、虚拟机及程序输出信息区
        frame_device = Gtk.Frame.new("")
        frame_device.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        device_view = Gtk.Stack()
        device_view.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        device_view.set_transition_duration(1000)
        
        # 数据区视图,采用滚动布局
        md_box = Gtk.VBox()
        alignment = Gtk.Alignment.new(0,0,0,0)
        alignment.add(md_box)
        sw_data = Gtk.ScrolledWindow(); sw_data.set_size_request(200,200)
        sw_data.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw_data.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw_data.add(alignment)

        # 新增内存数据区查看范围设置
        self.data_entry1 = Gtk.Entry(); self.data_entry2 = Gtk.Entry()
        self.data_entry1.set_width_chars(8); self.data_entry2.set_width_chars(8)
        self.data_entry1.set_text(str(self.data_start)); self.data_entry2.set_text(str(self.data_end))
        data_scale_button = Gtk.Button("Confirm"); data_scale_button.connect("clicked",self.data_scale)
        temp_box = Gtk.HBox(); temp_box.pack_start(self.data_entry1,True,True,0); temp_box.pack_start(self.data_entry2,True,True,0)
        temp_box.pack_start(data_scale_button,True,True,0); md_box.pack_start(temp_box,True,True,0) 
        
        # 数据区布局
        md = Gtk.Label("Address"+"  "*10+"Value(DEC)"+"  "*10+"Value(HEX)") # 数据区第一行信息栏
        self.mem_data.append(md)
        md_box.pack_start(md,False,False,0)
        global MEM_DATA,LEN_MEM_DATA
        for i in range(100):
            md1 = Gtk.Label(hex(i)); md2 = Gtk.Label("0"); md3 = Gtk.Label(hex(0))

            self.mem_data.append([md1,md2,md3])
            # 固定布局，确认显示对齐
            MD = Gtk.Fixed()
            md1.set_xalign(0); md2.set_xalign(0); md3.set_xalign(0)
            MD.put(md1,0,0); MD.put(md2,150,0);MD.put(md3,300,0)
            md_box.pack_start(MD,True,True,0)

        device_view.add_titled(sw_data,"data","Memory-Data")
        

        # 代码区视图：采取滚动布局
        mc_box = Gtk.VBox()
        alignment = Gtk.Alignment.new(0,0,0,0)
        alignment.add(mc_box); sw_code = Gtk.ScrolledWindow()
        sw_code.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw_code.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw_code.add(alignment)

        # 新增内存代码区查看范围设置
        self.code_entry1 = Gtk.Entry(); self.code_entry2 = Gtk.Entry()
        self.code_entry1.set_width_chars(8); self.code_entry2.set_width_chars(8)
        self.code_entry1.set_text(str(self.code_start)); self.code_entry2.set_text(str(self.code_end))
        code_scale_button = Gtk.Button("Confirm"); code_scale_button.connect("clicked",self.code_scale)
        temp_box = Gtk.HBox(); temp_box.pack_start(self.code_entry1,True,True,0); temp_box.pack_start(self.code_entry2,True,True,0)
        temp_box.pack_start(code_scale_button,True,True,0); mc_box.pack_start(temp_box,True,True,0) 

        # 代码区布局
        mc = Gtk.Label("Address"+"  "*10+"Ins"+"  "*10+"op1"+"  "*10+"op2") # 代码区第一行为信息栏
        self.mem_code.append(mc)
        mc_box.pack_start(mc,True,True,0)
        global MEM_CODE,LEN_MEM_CODE
        for i in range(100):
            mc0 = Gtk.Label(hex(i+LEN_MEM_DATA))
            mc1 = Gtk.Label(str(MEM_CODE[i-1]['insName'])); mc2 = Gtk.Label(str(MEM_CODE[i-1]['op1'])); mc3 = Gtk.Label(str(MEM_CODE[i-1]['op2']))
            self.mem_code.append([mc0,mc1,mc2,mc3])
            # 采用固定布局，保证显示对齐
            MC = Gtk.Fixed()
            mc0.set_xalign(0); mc1.set_xalign(0); mc2.set_xalign(0); mc3.set_xalign(0)
            MC.put(mc0,0,0); MC.put(mc1,100,0); MC.put(mc2,200,0);MC.put(mc3,300,0)
            mc_box.pack_start(MC,True,True,0)
        
        device_view.add_titled(sw_code,"code","Memory-Code")

        # 寄存器视图：采用嵌套Box布局和Fixed布局
        label_reg = Gtk.Fixed()
        frame_reg = Gtk.Frame.new("")
        frame_reg.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        frame_reg.add(label_reg)
        global NUM_REG,PC_REG,SP_REG,CC_REG
        for i in range(NUM_REG):
            reg_row = Gtk.Box()
            for j in range(4):
                # 对于特殊寄存器，Simple-VM高亮显示
                if (len(self.regs) == PC_REG):
                    reg = Gtk.Label(); reg.set_markup("<span color=\"red\">PC: </span>")
                elif (len(self.regs) == SP_REG):
                    reg = Gtk.Label(); reg.set_markup("<span color=\"red\">SP: </span>")
                elif (len(self.regs) == CC_REG):
                    reg = Gtk.Label(); reg.set_markup("<span color=\"red\">CC: </span>")
                else:
                    reg = Gtk.Label("R"+str(len(self.regs) + 1))
                self.regs.append(reg)
                label_reg.put(reg,j * 100, i * 50)
                if (len(self.regs) == NUM_REG):
                    break
            if (len(self.regs) == NUM_REG):
                break
        
        device_view.add_titled(frame_reg, "reg", "Regsiter")
        
        # 显示区视图：采用滚动布局，对于不同的信息来源采用不同的颜色高亮
        mo_box = Gtk.VBox()
        alignment = Gtk.Alignment.new(0,0,0,0)
        alignment.add(mo_box); sw_code = Gtk.ScrolledWindow()
        sw_code.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw_code.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw_code.add(alignment)
        mo = Gtk.Label("Output Information")
        self.output_labels.append(mo)
        for i in range(1000):
            mo = Gtk.Label("")
            self.output_labels.append(mo)
            mo_box.pack_start(mo,False,False,0)
        device_view.add_titled(sw_code,"output","Output")

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(device_view)
        vbox.pack_start(stack_switcher,False,True,1)
        vbox.pack_start(device_view,False,True,0)
        
        # 功能按钮：单步多步切换、暂停继续切换、关机键、单步控制、运行频率、模拟中断按钮
        frame_buttons = Gtk.Frame.new("ToolKit")
        frame_buttons.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        buttons = Gtk.Grid()
        frame_buttons.add(buttons)
        buttons.set_row_spacing(30)
        buttons.set_column_spacing(60)

        # 单步按钮
        button1 = Gtk.ToggleButton(label="One Step")
        button1.connect("toggled",self.step_shift)
        
        # 关机按钮
        button2 = Gtk.Button(label="Power Off")
        button2.connect("clicked",self.on_quit_clicked)
        
        # 暂停按钮
        button3 = Gtk.Button(label="Pause")
        button3.connect("clicked",self.on_pause_clicked)
        
        # 频率按钮：PopOver控件作为二级按钮
        self.button4 = Gtk.Button(label="Frequency")
        self.button4.connect("clicked",self.on_frequency_clicked)
        vbox4 = Gtk.VBox()
        fre_0_1 = Gtk.ModelButton("0.1"); vbox4.pack_start(fre_0_1,False,True,0); fre_0_1.connect("clicked",self.on_fre_0_1_clicked)
        fre_1_0 = Gtk.ModelButton("1.0"); vbox4.pack_start(fre_1_0,False,True,0); fre_1_0.connect("clicked",self.on_fre_1_0_clicked)
        fre_2_0 = Gtk.ModelButton("2.0"); vbox4.pack_start(fre_2_0,False,True,0); fre_2_0.connect("clicked",self.on_fre_2_0_clicked)
        fre_5_0 = Gtk.ModelButton("5.0"); vbox4.pack_start(fre_5_0,False,True,0); fre_5_0.connect("clicked",self.on_fre_5_0_clicked)
        self.popover = Gtk.Popover()
        self.popover.add(vbox4)
        self.popover.set_position(Gtk.PositionType.LEFT)

        # 模拟中断按钮：采用PopOver控件作为二级按钮
        self.button5 = Gtk.Button(label="Interrupt")
        self.button5.connect("clicked",self.on_interrupt_clicked)
        vbox5 = Gtk.VBox()
        int1 = Gtk.ModelButton("INT1"); vbox5.pack_start(int1,False,True,0); int1.connect("clicked",self.on_int1_clicked)
        int2 = Gtk.ModelButton("INT2"); vbox5.pack_start(int2,False,True,0); int2.connect("clicked",self.on_int2_clicked)
        self.popover5 = Gtk.Popover()
        self.popover5.add(vbox5)
        self.popover5.set_position(Gtk.PositionType.LEFT)
        
        # 中断前进控制按钮
        self.button6 = Gtk.Button(label="Next")
        self.button6.set_sensitive(False)
        self.button6.connect("clicked",self.on_next_clicked)

        # 按钮布局，Grid布局
        buttons.attach(button1,0,0,1,1)
        buttons.attach(button3,1,0,1,1)
        buttons.attach(button2,2,0,1,1)
        buttons.attach(self.button6,0,1,1,1)
        buttons.attach(self.button4,1,1,1,1)
        buttons.attach(self.button5,2,1,1,1)
        buttons.set_size_request(100,100)
        vbox.pack_start(frame_buttons, True, False, 0)

        # 输入框，用Expander存储，可随时隐藏
        self.entry = Gtk.Entry()
        expand = Gtk.Expander.new("Input")
        expand.set_expanded(False)
        expand.add(self.entry)
        vbox.pack_start(expand,False,False,0)
        
        # 判断虚拟机是否运行信号，若信号有效，显示窗口
        global signal_run
        
        if (signal_run):
            self.show_all()

    # 两组范围确认按钮事件函数
    def data_scale(self, data_scale_button):
        self.data_start = int(self.data_entry1.get_text())
        self.data_end = int(self.data_entry2.get_text())
    
    def code_scale(self, code_scale_button):
        self.code_start = int(self.code_entry1.get_text())
        self.code_end = int(self.code_entry2.get_text())


    # 关机键按钮事件函数：设置虚拟机状态为关闭，关闭窗口
    def on_quit_clicked(self,widget):
        global is_end
        is_end = True
        Gtk.main_quit()
    
    # 运行频率按钮事件函数：将二级按钮显示
    def on_frequency_clicked(self,widget):
        self.popover.set_relative_to(self.button4)
        self.popover.show_all()
        self.popover.popup()

    # 频率二级按钮事件函数，改变虚拟机运行频率（指令间延时）
    def on_fre_0_1_clicked(self,widget):
        global frequency
        frequency = 0.1
    def on_fre_1_0_clicked(self,widget):
        global frequency
        frequency = 1.0
    def on_fre_2_0_clicked(self,widget):
        global frequency
        frequency = 2.0
    def on_fre_5_0_clicked(self,widget):
        global frequency
        frequency = 5.0
    
    # 模拟中断按钮事件函数，调用二级按钮
    def on_interrupt_clicked(self,widget):
        self.popover5.set_relative_to(self.button5)
        self.popover5.show_all()
        self.popover5.popup()

    # 用户选择中断序列，Simple-VM提供了两个预置中断代码，用户可以自行选择
    def on_int1_clicked(self,widget):
        global INT_NUMBER
        INT_NUMBER = 0
        global signal_int_happen,signal_int_run
        if (signal_int_run):
            # 如果当前已有中断信号，则抛出信息
            global label_output; label_output.append("<span color=\"red\">Interrupt has happened.</span>")
        else:
            # 否则将中断信号置为有效
            signal_int_happen = True

    def on_int2_clicked(self,widget):
        global INT_NUMBER
        INT_NUMBER = 1
        global signal_int_happen,signal_int_run
        if (signal_int_run):
            # 如果当前已有中断信号，则抛出信息
            global label_output; label_output.append("<span color=\"red\">Interrupt has happened.</span>")
        else:
            # 否则将中断信号置为有效
            signal_int_happen = True
    
    # 单步控制前进按钮事件函数：点击一下，虚拟机继续跑一次指令
    def on_next_clicked(self,widget):
        global mutex_one,signal_onestep
        if (signal_onestep):
                mutex_one = True
    
    # 暂停事件函数：改变虚拟机相关信号
    def on_pause_clicked(self, button3):
        global signal_pause
        # 根据虚拟机当前状态选择不同处理，若已暂停则继续，若正在运行则暂停
        if (button3.get_label() == "Pause"):
            button3.set_label("Continue")
            signal_pause = True        
        else:
            button3.set_label("Pause")
            signal_pause = False
 
    # 单步按钮事件函数：改变虚拟机相关信号
    def step_shift(self,button1):
        global signal_onestep
        if (button1.get_active()):
            signal_onestep = True
            self.button6.set_sensitive(True)
            self.button4.set_sensitive(False)
        else:
            signal_onestep = False
            self.button6.set_sensitive(False)
            self.button4.set_sensitive(True)
        
#------------------------------------------------------------------------------------------------------------

#########################################
#                                       #
#                                       #
#        虚拟机逻辑主体:逻辑函数          #
#                                       #
#                                       #
#########################################


# 虚拟机初始化函数
def VM_init():
    global LEN_MEM_DATA,LEN_MEM_CODE,MEM_DATA,MEM_CODE,REG,PC_REG,SP_REG,signal_jmp,INT_START,INT_END,INT_VECTOR

    # 初始化数据区为0
    for i in range(LEN_MEM_DATA):
        MEM_DATA.append(0)

    # 初始化代码区为None
    for i in range(LEN_MEM_CODE): 
        MEM_CODE.append({'insName':None,'op1':None,'op2':None})
    
    # 预置中断代码区
    intFile = open("intCode.txt","r").readlines()
    for i in range(INT_VECTOR[0],INT_VECTOR[0]+len(intFile)):
        temp = intFile[i - INT_VECTOR[0]].split()
        MEM_CODE[i-LEN_MEM_DATA-1] = {'insName':temp[0],'op1':temp[1],'op2':temp[2]}
        

    # 清空寄存器，设置SP为初始栈位置-1
    for i in range(NUM_REG):
        REG.append(0)
    REG[PC_REG] = 0
    REG[SP_REG] = POS_STACK - 1
    
    # 设置跳转信号为无效
    signal_jmp = False

# 虚拟机加载函数
def VM_load(filename):
    global MEM_CODE,REG
    file = open(filename,"r")
    insNum = 0
    for line in file.readlines():
        # 解析字符串
        temp_ins = line.strip().split(' ')
        # 构造临时指令结构
        ins = {'insName':None,'op1':None,'op2':None}
        ins['insName'] = temp_ins[0].upper()
        ins['op1'] = temp_ins[1]
        ins['op2'] = temp_ins[2]
        # 加载该指令到内存
        MEM_CODE[insNum] = ins
        insNum = insNum + 1


running_window = None
signal_iret = False

# 软件核心主函数
def app_main():
    running_window = RunningWindow()
    running_window.connect("delete-event",Gtk.main_quit)
    # 保存现场
    def save_scene():
        global MEM_DATA,REG,last_sp,SP_REG,signal_int_run,SP_REG
        # 记录保存现场的起点，以便恢复现场
        last_sp = REG[SP_REG]
        #print("Before INT",REG)
        # 调用PUSH指令，将寄存器信息压入堆栈
        for i in range(len(REG)):
            ins = {};
            ins['insName'] = "PUSH"; ins["op1"] = i + 1; ins["op2"] = "NULL"
            ins_exec(ins)
        MEM_DATA[last_sp+SP_REG+1] = last_sp
        # 开始执行中断程序，设置中断代码运行信号有效
        signal_int_run = True

    # 恢复现场
    def recover_scene():
        global MEM_DATA,REG,last_sp,SP_REG,signal_int_happen,signal_int_run
        # 将中断出现信号置无效
        signal_int_happen = False
        # 将寄存器信息重新返回
        sp = last_sp
        for i in range(len(REG)):
            REG[i] = MEM_DATA[sp+i + 1]
           # print(sp,sp+i,MEM_DATA[sp+i])
        # 关闭中断程序，设置中断运行信号无效
        #print("After INT",REG)
        signal_int_run = False
        output("Interrupt End")

    # 封装了一个在显示区输出字符串的函数
    def output(str):
        label_output.append(str)
    
    # 控制器
    def VM_run():
        global MEM_CODE,REG,PC_REG,signal_jmp,signal_pause,signal_onestep,mutex_one,frequency,signal_int_run,last_sp
        global SP_REG,MEM_DATA,INT_VECTOR,INT_NUMBER,CC_REG,is_end,signal_iret
        global error_happen,signal_int_run

        currentIns = MEM_CODE[REG[PC_REG]]
        
        while (currentIns['insName'] != 'HLT' and not is_end):
            # 阻塞更新接口线程
            GLib.idle_add(update)
            #if (signal_int_run):
            #    print("INT runnning:",REG)
            # 处理单步执行信号，并保证中途退出能够关闭界面
            while (signal_onestep and not mutex_one):
                print("")
                if (is_end):
                    break
            mutex_one = False

            # 处理暂停信号，并保证中途退出能够关闭界面
            while (signal_pause):
                print("")
                if (is_end):
                    break    

            # 在多步执行模式下，调节延时，以估计虚拟机运行频率  
            if (not signal_onestep and not signal_pause):
                time.sleep(frequency)
            

            #if (True):
            #    print("Currentins: ",currentIns)
            #    print("PC:",REG[PC_REG])
               
            
            # 执行指令
            ins_exec(currentIns)

            # 根据跳转信号，更新PC
            if (not signal_jmp):
                REG[PC_REG] = REG[PC_REG] + 1
            if (signal_iret):
                REG[PC_REG] = REG[PC_REG] - 1
                signal_iret = False
            signal_jmp = False

            # 读取下一条指令
            currentIns = MEM_CODE[REG[PC_REG]]


            if (signal_int_happen and not signal_int_run):
                output("Begin Interrupt")
                sp = REG[SP_REG]
                save_scene()
                # 初始化中断代码的寄存器信息
                for i in range(len(REG)):
                    REG[i] = 0
                REG[SP_REG] = sp + len(REG) + 1
                REG[PC_REG] = INT_VECTOR[INT_NUMBER] - LEN_MEM_DATA - 1
                currentIns = MEM_CODE[REG[PC_REG]]
            
        
        output("<span color=\"green\">Program Finished.</span>")
        update()
        #Gtk.main_quit()
    
    # 解析条件码寄存器，由于Simple-VM只有三个条件码，因此直接用十进制作为模拟，110表示前两个条件码有效，以此类推
    def extractCC(N):
        return [((N//100)%10),((N//10)%10),N%10]    

    # 运算器，负责执行单条指令
    def ins_exec(Ins):
        global REG,MEM_DATA,SP_REG,PC_REG,signal_jmp,CC_REG,error_happen,LEN_MEM_DATA,LEN_MEM_CODE,POS_STACK
        
        # 解析指令，获取指令名与操作数
        insName = Ins['insName']
        op1 = Ins['op1']
        op2 = Ins['op2']

       # 执行指令
        if (insName == 'RRMOV'):  
            [s,d] = [int(op1), int(op2)]
            if (d > len(REG) or s > len(REG) or d < 1 or s < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = REG[s - 1]
        elif (insName == "NOP"): 
            pass
        elif (insName == 'IRMOV'): 
            [s,d] = [int(op1), int(op2)]
            if (d > len(REG) or d < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = s
        elif (insName == 'RMMOV'):
            [s,d] = [int(op1), REG[int(op2) - 1]]
            if (s > len(REG) or d > LEN_MEM_DATA or d < 0 or s < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                MEM_DATA[d] = REG[s - 1]
        elif (insName == 'MRMOV'):
            [s,d] = [REG[int(op1) - 1], int(op2)]
            if (d > len(REG) or s > LEN_MEM_DATA or s < 0 or d < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = MEM_DATA[s]
        elif (insName == 'PUSH'):
            s = int(op1)
            if (s > len(REG) or s < 1):
                output("<span color=\"red\">Address Overflow</span>")
            elif (REG[SP_REG] >= LEN_MEM_DATA or REG[SP_REG] < POS_STACK - 1):
                output("<span color=\"red\">Stack Overflow</span>")
            else:
                REG[SP_REG] = REG[SP_REG] + 1
                MEM_DATA[REG[SP_REG]] = REG[s - 1]
        elif (insName == 'POP'):
            d = int(op1)
            if (d > len(REG) or d < 1):
                output("<span color=\"red\">Address Overflow</span>")
            elif (REG[SP_REG] >= LEN_MEM_DATA or REG[SP_REG] < POS_STACK):
                output("<span color=\"red\">Stack Overflow</span>")
            else:
                REG[d - 1] = MEM_DATA[REG[SP_REG]]
                REG[SP_REG] = REG[SP_REG] - 1
        elif (insName == 'INC'):
            d = int(op1)
            if (d > len(REG) or d < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = REG[d - 1] + 1
        elif (insName == 'DEC'):
            d = int(op1)
            if (d > len(REG) or d < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = REG[d - 1] - 1
        elif (insName == 'ADD'):
            [s,d] = [int(op1), int(op2)]
            if (d > len(REG) or s > len(REG) or d < 1 or s < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = REG[d - 1] + REG[s - 1]
        elif (insName == 'SUB'):
            [s,d] = [int(op1), int(op2)]
            if (d > len(REG) or s > len(REG) or d < 1 or s < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = REG[d - 1] - REG[s - 1]
        elif (insName == 'IMUL'):
            [s,d] = [int(op1), int(op2)]
            if (d > len(REG) or s > len(REG) or d < 1 or s < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = REG[d - 1] * REG[s - 1]
        elif (insName == 'DIV'):
            [s,d] = [int(op1), int(op2)]
            if (d > len(REG) or s > len(REG) or d < 1 or s < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = REG[d - 1] / REG[s - 1]
        elif (insName == "NOT"):
            d = int(op1)
            if (d > len(REG) or d < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = ~REG[d - 1]
        elif (insName == "XOR"):
            [s,d] = [int(op1), int(op2)]
            if (d > len(REG) or s > len(REG) or d < 1 or s < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = REG[d - 1] ^ REG[s - 1]
        elif (insName == "OR"):
            [s,d] = [int(op1), int(op2)]
            if (d > len(REG) or s > len(REG) or d < 1 or s < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = REG[d - 1]|REG[s - 1]
        elif (insName == "AND"):
            [s,d] = [int(op1), int(op2)]
            if (d > len(REG) or s > len(REG) or d < 1 or s < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = REG[d - 1]&REG[s - 1]
        elif (insName == "SAL"):
            [s,d] = [int(op1), int(op2)]
            if (d > len(REG) or s > len(REG) or d < 1 or s < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = REG[d - 1] << s
        elif (insName == "SAR"):
            [k,d] = [int(op1), int(op2)]
            if (d > len(REG) or s > len(REG) or d < 1 or s < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[d - 1] = REG[d - 1] >> k
        elif (insName == "JMP"):
            addr = int(op1)
            if (addr < 0 or addr > LEN_MEM_CODE):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                REG[PC_REG] = addr
                signal_jmp = True
        elif (insName == "JE"):
            addr = int(op1)
            CZ,LZ,GZ = extractCC(REG[CC_REG])
            if (CZ == 1):
                if (addr < 0 or addr > LEN_MEM_CODE):
                    output("<span color=\"red\">Address Overflow</span>")
                else:
                    REG[PC_REG] = addr
                    signal_jmp = True
        elif (insName == "JNE"):
            addr = int(op1)
            CZ,LZ,GZ = extractCC(REG[CC_REG])
            if (CZ == 0):
                if (addr < 0 or addr > LEN_MEM_CODE):
                    output("<span color=\"red\">Address Overflow</span>")
                else:
                    REG[PC_REG] = addr
                    signal_jmp = True
        elif (insName == "JL"):
            addr = int(op1)
            CZ,LZ,GZ = extractCC(REG[CC_REG])
            if (LZ == 1):
                if (addr < 0 or addr > LEN_MEM_CODE):
                    output("<span color=\"red\">Address Overflow</span>")
                else:
                    REG[PC_REG] = addr
                    signal_jmp = True
        elif (insName == "JLE"):
            addr = int(op1)
            CZ,LZ,GZ = extractCC(REG[CC_REG])
            if (LZ == 1 or CZ == 1):
                if (addr < 0 or addr > LEN_MEM_CODE):
                    output("<span color=\"red\">Address Overflow</span>")
                else:
                    REG[PC_REG] = addr
                    signal_jmp = True
        elif (insName == "JG"):
            addr = int(op1)
            CZ,LZ,GZ = extractCC(REG[CC_REG])
            if (GZ == 1):
                if (addr < 0 or addr > LEN_MEM_CODE):
                    output("<span color=\"red\">Address Overflow</span>")
                else:
                    REG[PC_REG] = addr
                    signal_jmp = True
        elif (insName == "JGE"):
            addr = int(op1)
            CZ,LZ,GZ = extractCC(REG[CC_REG])
            if (GZ == 1 or CZ == 1):
                if (addr < 0 or addr > LEN_MEM_CODE):
                    output("<span color=\"red\">Address Overflow</span>")
                else:
                    REG[PC_REG] = addr
                    signal_jmp = True
        elif (insName == "CMP"):
            [s,d] = [int(op1), int(op2)]
            if (d > len(REG) or s > len(REG) or d < 1 or s < 1):
                output("<span color=\"red\">Address Overflow</span>")
            else:
                if (REG[d-1] - REG[s-1] == 0):
                    REG[CC_REG] = 100
                elif (REG[d-1] - REG[s-1] < 0):
                    REG[CC_REG] = 10
                elif (REG[d-1] - REG[s-1] > 0):
                    REG[CC_REG] = 1
        elif (insName == "MOUT"):
            d = int(op1)
            if (d > len(REG) or d < 1 or REG[d-1] > LEN_MEM_DATA or REG[d-1] < 0) :
                output("<span color=\"red\">Address Overflow</span>")
            else:
                output("<span color=\"blue\">"+str(MEM_DATA[REG[d-1]])+"</span>")
        elif (insName == "INPUT"):
            d = int(op1)
            if (d > len(REG) or d < 1 or REG[d-1] > LEN_MEM_DATA or REG[d-1] < 0) :
                output("<span color=\"red\">Address Overflow</span>")
            else:
                s = ""
                while (len(s) <= 0 or s[-1] != '#'):
                    s = running_window.entry.get_text()
                MEM_DATA[REG[d-1]] = int(s[0:-1])
        elif (insName == "IRET"):
            recover_scene()
            global signal_iret
            signal_iret = True
        else:
            output("<span color=\"red\">insName Error:"+str(insName)+"</span>")

    # 更新接口程序，负责更新窗口信息
    def update():
        regs = running_window.regs
        mem_data = running_window.mem_data
        mem_code = running_window.mem_code
        output_labels= running_window.output_labels
        global REG,MEM_DATA,MEM_CODE,PC_REG,SP_REG,CC_REG,INT_START,INT_END,error_over

        # 更新显示区信息
        for i in range(1,len(label_output)):
            output_labels[i].set_markup(label_output[i])

        # 更新寄存器信息
        for i in range(len(regs)):
            if (i == PC_REG):
                s = "<span color=\"red\">PC: " + str(hex(REG[i] + LEN_MEM_DATA))+"</span>"
            elif (i == SP_REG):
                s = "<span color=\"red\">SP: " + str(REG[i])+"</span>"
            elif (i == CC_REG):
                s = "<span color=\"red\">CC: " + str(REG[i])+"</span>"
            else:
                s = "R"+str(i + 1)+": "+str(REG[i])
            regs[i].set_markup(s)

        # 更新数据区信息
        mem_data[0].set_markup("<b><span color=\"blue\">Address</span>"+" "*15+"<span color=\"blue\">Value(DEC)</span>"+"  "*8+"<span color=\"blue\">Value(HEX)</span></b>")
        start = running_window.data_start; end = running_window.data_end; end = start + 99
        for i in range(start,end+1):
            s0 = hex(i); s1 = str(MEM_DATA[i]); s2 = hex(MEM_DATA[i])
            if (i >= POS_STACK and i < POS_EXTEND):
                s0 = "<b><span color=\"green\">"+s0+"</span></b>"
                s1 = "<b><span color=\"green\">"+s1+"</span></b>"
                s2 = "<b><span color=\"green\">"+s2+"</span></b>"
            if (i >= POS_EXTEND):
                s0 = "<b><span color=\"red\">"+s0+"</span></b>"
                s1 = "<b><span color=\"red\">"+s1+"</span></b>"
                s2 = "<b><span color=\"red\">"+s2+"</span></b>"
            mem_data[i-start+1][0].set_markup(s0) 
            mem_data[i-start+1][0].set_xalign(0)
            mem_data[i-start+1][1].set_markup(s1) 
            mem_data[i-start+1][1].set_xalign(0)
            mem_data[i-start+1][2].set_markup(s2) 
            mem_data[i-start+1][2].set_xalign(0)

        # 更新代码区信息
        mem_code[0].set_markup("<b><span color=\"blue\">Address</span>"+" "*10+"<span color=\"blue\">Ins</span>"+"  "*10+"<span color=\"blue\">op1</span>"+"  "*10+"<span color=\"blue\">op2</span></b>")
        start = running_window.code_start; end = running_window.code_end; end = start + 99
        for i in range(start,end+1):
            s0 = hex(i); s1 = str(MEM_CODE[i-LEN_MEM_DATA-1]['insName']); s2 = str(MEM_CODE[i-LEN_MEM_DATA-1]['op1']); s3 = str(MEM_CODE[i-LEN_MEM_DATA-1]['op2'])
           
            if (i >= INT_START and i <= INT_END and REG[PC_REG] + LEN_MEM_DATA != i):
                s0 = "<b><span color=\"green\">"+s0+"</span></b>"
                s1 = "<b><span color=\"green\">"+s1+"</span></b>"
                s2 = "<b><span color=\"green\">"+s2+"</span></b>"
                s3 = "<b><span color=\"green\">"+s3+"</span></b>"
            if (REG[PC_REG]+LEN_MEM_DATA == i):
                s0 = "<b><span color=\"red\">"+s0+"</span></b>"
                s1 = "<b><span color=\"red\">"+s1+"</span></b>"
                s2 = "<b><span color=\"red\">"+s2+"</span></b>"
                s3 = "<b><span color=\"red\">"+s3+"</span></b>"
             
            mem_code[i-start+1][0].set_markup(s0) 
            mem_code[i-start+1][0].set_xalign(0)
            mem_code[i-start+1][1].set_markup(s1) 
            mem_code[i-start+1][1].set_xalign(0)
            mem_code[i-start+1][2].set_markup(s2) 
            mem_code[i-start+1][2].set_xalign(0)
            mem_code[i-start+1][3].set_markup(s3) 
            mem_code[i-start+1][3].set_xalign(0)


    running_window.show_all()
    thread = threading.Thread(target=VM_run)
    thread.daemon = True
    thread.start()


def main():
    GObject.threads_init()
    start_window = StartWindow()
    start_window.connect("delete-event",Gtk.main_quit)
    start_window.show_all()
    Gtk.main()
    if (signal_run):
        VM_init()
        VM_load(filename)
        app_main()
        Gtk.main()
        
if __name__ == "__main__":
    main()
 
