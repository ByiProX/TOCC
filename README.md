# ThoughtWorks2018SpringDEV
---
项目地址
https://github.com/ByiProX/ThoughtWorks2018SpringDEV

---
本项目使用**Python3.6.4**完成

使用到的工具包有 sys, unittest

运行环境管理工具 virtualenv

*非必要使用 virtualenv，若该项目无法运行(一般python3下均可运行)，可以尝试使用virtualenv。使用方法为在该项目目录下，终端运行*

```python3
source venv/bin/activate # bash shell启动方法

source venv/bin/activate.fish # fish shell启动方法

deactivate # 关闭方法

```


## 1.程序的运行方法：
**终端定位到check.py所在的目录下并输入 *python3 check.py filename signal_index* ，比如：**
```python
python3 check.py signal.txt 2
```


**详细描述如下,在终端中分别执行以下命令：**

```python
python3 check.py signal.txt 2

python3 check.py signal.txt 4

python3 check.py signal.txt 100

python3 check.py signal.txt 3

python3 check.py signal 2    # 非正常输入

python3 check.py signal.txt  # 非正常输入

```

**以上命令行中运行结果如下：**

![Screen Shot 2018-01-16 at 22.19.56.jpg](http://upload-images.jianshu.io/upload_images/2952111-e89d2da94a0e50d7.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


#### 可以看到输出结果符合题目要求 ####

---

## 2.单元测试运行方法


**单元测试内容包括**

- 项目中所有方法函数的测试，包括返回值类型测试以及返回值的测试
- 不同信号文件内容的测试，包括常规测试以及各种边缘测试。比如消息内容格式不符的测试、无人机前一条消息坐标计算值不匹配的测试等

具体测试案例文件位于 *./testcase/* 目录下

**测试运行方法为：终端定位到unit_test.py所在的目录下并输入运行**
```python
python3 unit_test.py
```

![Screen Shot 2018-01-17 at 17.28.47.png](http://upload-images.jianshu.io/upload_images/2952111-bf45462579b17e51.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

#### 经检验全部案例均通过测试

---
