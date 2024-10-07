# 拼音输入法——基于字的二、三元模型

## 目录结构

```
.
├── corpus
├── data
│   ├── answer.txt
│   ├── input.txt
│   └── output.txt
├── judge.py
├── main.py
├── readme.md
├── requirements.txt
├── res
└── src
    ├── alphabet
    │   ├── 拼音汉字表.txt
    │   └── 一二级汉字表.txt
    ├── const.py
    ├── main_oj.py
    ├── predict2g.py
    ├── predict3g.py
    ├── stat.py
    ├── train2g.py
    └── train3g.py
```

**文件目录以及格式**

`corpus` ：语料库文件目录

`data`：测试输入、测试输出、标准输出文件目录

`src`：源代码文件目录

`res`：模型数据文件目录

`src/alphabet`：拼音汉字表目录

## 使用基于字的二元模型或三元模型

```bash
python main.py [-h] [-3] [-a ALPHA]
```

参数说明：

+ `-3`：选择使用三元模型，默认使用二元模型
+ `-a`：输入 alpha 参数，默认为`1e-6`
+ `-h`：查看参数说明

首次运行时，会自动进行语料库训练，训练数据会存放在 `res` 目录下。

当训练数据存在时，再次运行，程序会自动加载训练数据，不再重复训练。

## 重新训练语料库

如果需要重新训练语料库，需要删除 `res` 目录下的所有文件，把待训练语料库放入 `corpus` 目录，再执行上面的命令即可自动训练并生成预测结果。

**注意**：语料库请使用 `utf-8` 或 `gbk` 编码（两种编码均支持，但建议 `utf-8`）。