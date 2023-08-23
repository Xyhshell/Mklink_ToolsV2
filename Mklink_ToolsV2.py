#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
@author: jingmo
@file:   Mklink_ToolsV2.py
@time:   2022/04/01 15:35:24
"""

import ctypes
import os
import os.path
import shutil
import tkinter as tk
import zipfile
from time import sleep
from tkinter import filedialog


demo = """
MKLINK [[/D] | [/H] | [/J]] Link Target

/D      创建目录符号链接。默认为文件符号链接。
/H      创建硬链接而非符号链接。
/J       创建目录联接。
Link    指定新的符号链接名称。
Target  指定新链接引用的路径(相对或绝对)。

"""

# 实际实现流程
r"""
mklink /d
        （软链接指向的新文件路径（实际文件存储位置），要求不存在且由于局限于软件目录的指向，文件名 【待定*】）

         （实际文件存储位置，来源使用热剪切（压缩源数据，创建链接后解压缩））
"""


# 获取源文件路径 / 压缩文件 / 删除源文件 / 创建软链接
def get_old_filepath():
    global old_path

    old_file_path = filedialog.askdirectory(title="选择文件的初始储存位置：")
    if old_file_path != '':
        print("文件的初始储存位置：", old_file_path)
        leble01.config(text=old_file_path, font=("微软雅黑", 10), fg="green", )

        old_path = old_file_path
    else:
        print('* 未获取文件夹')
        exit()


# 获取新文件路径 / 并定为文件存储位置
def get_new_filepath():
    global new_path
    
    new_file_path = filedialog.askdirectory(title="选择文件最终储存位置：")
    if new_file_path != '':
        print("文件映射位置：", new_file_path)
        leble02.config(text=new_file_path, font=("微软雅黑", 10), fg="green", )
        
        new_path = new_file_path
    else:
        print('* 未获取文件夹')
        exit()


# 压缩文件夹
def zip_dir(dirname, zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else:
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))
    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        zf.write(tar, arcname)
    zf.close()


# 解压缩文件夹
def unzip_dir(loding_zip, post_file):
    z = zipfile.ZipFile(fr"{loding_zip}", 'r')
    z.extractall(path=fr"{post_file}")
    z.close()


# 压缩文件夹 线程
def zip_file(old_path, new_file_name):
    zip_dir(dirname=old_path, zipfilename=f"./{new_file_name}.zip")


# 解压缩文件夹 线程
def unzip_file(new_file_name, new_file_path):
    unzip_dir(loding_zip=f"./{new_file_name}.zip", post_file=new_file_path)


# 删除源文件
def del_file(old_path):
    shutil.rmtree(old_path)  # 递归删除文件夹


# 创建软链接
def mklink_main(cmd1, cmd2, _user):
    if user == "admin":
        cmd_main = f'mklink /D "{cmd1}" "{cmd2}"'
        print("管理员执行：", cmd_main)
        os.popen(cmd_main)
    else:
        cmd_main = f'mklink /J "{cmd1}" "{cmd2}"'
        print("普通用户执行：", cmd_main)
        os.popen(cmd_main)


# 执行函数
def click_up():
    global old_path, new_path
    # 接收全局变量 old_path, new_path 先进行判空：
    if old_path and new_path is not None:
        print("已获取参数：", old_path, new_path)

        # 定义新文件名
        new_file_name = str(old_path).split("/")[-1]

        # 压缩文件夹至程序运行目录
        zip_file(old_path=old_path, new_file_name=new_file_name)

        # 删除源文件夹
        del_file(old_path=old_path)

        # 创建软链接
        mklink_main(cmd1=old_path, cmd2=new_path, _user=user)

        # 解压缩文件夹至新文件夹
        unzip_file(new_file_name=new_file_name, new_file_path=new_path)

        # 很重要， 执行点击操作后需要 释放该值，避免重复操作！
        old_path = None
        leble01.config(text="", font=("微软雅黑", 10), fg="green", )

        new_path = None
        leble02.config(text="", font=("微软雅黑", 10), fg="green", )

        print("* 已操作完成！")
    else:
        # 很重要， 执行点击操作后需要 释放该值，避免重复操作！
        old_path = None
        leble01.config(text="", font=("微软雅黑", 10), fg="green", )

        new_path = None
        leble02.config(text="", font=("微软雅黑", 10), fg="green", )

        print("* 路径参数获取错误，请重新选择！")


# 解除软链接
def rmdir_main_del(cmd1, _user):
    if user == "admin":
        cmd_main = f'rmdir "{cmd1}"'
        print("管理员解除映射：", cmd_main)
        os.popen(cmd_main)
    else:
        cmd_main = f'rmdir "{cmd1}"'
        print("普通用户解除映射：", cmd_main)
        os.popen(cmd_main)


# 解除函数
def click_del():
    """:cvar
    1. 获取传入的源地址，映射地址 ！
    2.打包压缩映射文件 !
    3.利用rmdir 删除源地址的mklink链接（唯一且只有映射可删）
    4.解压缩打包文件至源文件地址
    5.删除映射地址所有文件
    """
    global old_path, new_path
    # 接收全局变量 old_path, new_path 先进行判空：
    if old_path and new_path is not None:
        print("已获取参数：", old_path, new_path)

        # 定义新文件名
        new_file_name = str(old_path).split("/")[-1]

        # 压缩文件夹至程序运行目录
        zip_file(old_path=new_path, new_file_name=new_file_name)

        # 创建软链接
        rmdir_main_del(cmd1=old_path, _user=user)
        sleep(2)
        # 解压缩文件夹至新文件夹
        unzip_file(new_file_name=new_file_name, new_file_path=old_path)

        # 删除源文件夹
        del_file(old_path=new_path)

        # 很重要， 执行点击操作后需要 释放该值，避免重复操作！
        old_path = None
        leble01.config(text="", font=("微软雅黑", 10), fg="green", )
        new_path = None
        leble02.config(text="", font=("微软雅黑", 10), fg="green", )
        print("* 已操作完成！")
    else:
        # 很重要， 执行点击操作后需要 释放该值，避免重复操作！
        old_path = None
        leble01.config(text="", font=("微软雅黑", 10), fg="green", )
        new_path = None
        leble02.config(text="", font=("微软雅黑", 10), fg="green", )
        print("* 路径参数获取错误，请重新选择！")


# # 管理员权限检测
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


# 绘制简单ui / tkinter库
if __name__ == '__main__':
    old_path = None
    new_path = None

    if is_admin():
        user = "admin"
        mods_text = "管理员模式 MkLink /D"
    else:
        user = ""
        mods_text = "普通模式 MkLink /J"
        
    os.popen('mode con cols=50 lines=10')
    root_main = tk.Tk()
    root_main.withdraw()

    main_root = tk.Tk()
    main_root.title(f"MkLink 软链接操作器GuiV2.1 By:Jingmo ->运行模式：{mods_text}")

    main_root.resizable(width=False, height=False)
    screenwidth = main_root.winfo_screenwidth()
    screenheight = main_root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (580, 310, (screenwidth - 580) / 2, (screenheight - 310) / 2)
    main_root.geometry(size)

    # V2 运行模式判定
    mods = tk.Label(main_root, text=mods_text, font=("微软雅黑", 10), fg="red")
    mods.place(x=380, y=155, width=205, height=40)

    leble_ = tk.Label(main_root, text="源文件地址:", font=("微软雅黑", 12), fg="blue")
    leble_.place(x=12, y=2, width=100, height=40)

    leble01 = tk.Label(main_root, text="源文件地址 (-请选择-)", font=("微软雅黑", 10), fg="silver")
    leble01.place(x=7, y=32, width=454, height=40)

    leble_0 = tk.Label(main_root, text="映射地址:", font=("微软雅黑", 12), fg="blue")
    leble_0.place(x=12, y=75, width=100, height=40)

    leble02 = tk.Label(main_root, text="映射地址 (-请选择-)", font=("微软雅黑", 10), fg="silver")
    leble02.place(x=7, y=105, width=454, height=40)

    but01 = tk.Button(main_root, text="选择文件夹", font=("微软雅黑", 12), fg="green", command=get_old_filepath)
    but01.place(x=473, y=35, width=106, height=40)

    but02 = tk.Button(main_root, text="选择文件夹", font=("微软雅黑", 12), fg="green", command=get_new_filepath)
    but02.place(x=473, y=107, width=106, height=40)

    but03 = tk.Button(main_root, text="设置\n软链接\n (∩,∩)", font=("微软雅黑", 16), fg="red", command=click_up)
    but03.place(x=420, y=190, width=150, height=99)

    # 新增解除软链接
    but04 = tk.Button(main_root, text="解除\n软链接", font=("微软雅黑", 16), command=click_del)
    but04.place(x=310, y=190, width=100, height=99)

    leble_2 = tk.Label(main_root, text=demo, anchor='e', justify='left', font=("微软雅黑", 9), fg="grey")
    leble_2.place(x=2, y=160, width=300, height=160)

    main_root.mainloop()
