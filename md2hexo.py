# coding=utf-8
# 基于conda env:py35

# 功能说明
# 将vnote的md格式转为hexo的md格式，生成类似下面的文件前缀(同时，删除文件正文首行的title)  
# ---
# title: 01_原因
# date: 2019-11-30 00:00:01
# categories:['xx','yy']
# tags:['ff','zz']
# comments: true
# toc: true
# 
# ---

# 用法说明和举例
# 用法 python md2hexo 目录
#   递归查询目录下所有md文件，生成md文件的前缀信息
# 用法 python md2hexo ./目录1/目录2/文件.md(x)
#   生成文件的前缀，此时文件的cate=目录1,目录2
# 用法 python md2hexo 文件.md

# 生成文件的前缀，此时文件的cate=空
import sys
import os
import time
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')


# 时间戳转换
def TimeStampToTime(timestamp):
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)


def getFileDatetime(fullFilePath):
    return TimeStampToTime(os.path.getctime(fullFilePath))


def getFileCategories(fullFilePath):
    return filter(lambda x: x != '.' and x != '/' and x != '', fullFilePath.split('/')[:-1])


class MdArticle(object):
    # 从文件中初始化
    def __init__(self, fullFilePath=''):
        self.fullFilePath = fullFilePath
        self.title = ''
        self.date = ''
        self.categories = ''
        self.tags = ''
        self.data = []
        if self.fullFilePath.strip():
            # 操作文件
            with open(self.fullFilePath, 'r+') as f:
                endLineNum = 0
                lines = f.readlines()
                if len(lines) > 0 and lines[0] == '---\n':
                    for i in range(1, len(lines)):
                        if lines[i] != '---\n':
                            if lines[i].startswith('title: '):
                                self.title = lines[i][7:].strip()
                            elif lines[i].startswith('date: '):
                                self.date = lines[i][6:].strip()
                            elif lines[i].startswith('categories: '):
                                self.categories = lines[i][12:].strip()
                            elif lines[i].startswith('tags: '):
                                self.tags = lines[i][5:].strip()
                        else:
                            endLineNum = i
                            break
                # 拼接新文件
                if endLineNum == 0:
                    self.data.extend(lines[0:])
                else:
                    self.data.extend(lines[endLineNum + 1:])
                f.close()
        return

    # 填充修改自身信息
    def fillInfo(self):
        (filePath, fullFileName) = os.path.split(self.fullFilePath)
        (fileName, fileExtension) = os.path.splitext(fullFileName)

        self.title = fileName
        if not self.date:
            self.date = getFileDatetime(self.fullFilePath)
        self.categories = str(list(getFileCategories(self.fullFilePath)))
        return

    # 保存到文件中
    def save(self):
        # 获得文章date和tags(优先使用原有数据)
        filePrefixLines = ['---\n']
        # 文件名，填充title
        filePrefixLines.append('title: %s  \n' % self.title)
        # 文件创建时间，填充date
        filePrefixLines.append('date: %s  \n' % self.date)
        # 文件相对路径，填充categories
        filePrefixLines.append('categories: %s  \n' % str(self.categories))
        filePrefixLines.append('tags: %s  \n' % str(self.tags))
        # 收尾
        filePrefixLines.append('toc: true  \n')
        if self.title.find('[密]') > -1:
            filePrefixLines.append('password: xxxxyyyy  \n')
        filePrefixLines.append('\n---\n')
        # 标题也重新生成,标题不重新生成
        # filePrefixLines.append('# %s\n' % self.title)
        filePrefixLines.extend(self.data)

        # 操作文件
        with open(self.fullFilePath, 'r+') as f:
            f.truncate()
            f.writelines(filePrefixLines)
            f.flush()
            f.close()
        return


# 处理单文件
def handleFile(fullFilePath):
    if not fullFilePath.endswith('.md'):
        return
    print(fullFilePath)

    mdArticle = MdArticle(fullFilePath)
    mdArticle.fillInfo()
    mdArticle.save()


# 处理目录
def handleDir(fileDir):
    # for root, dirs, files in os.walk(fileDir):
    #     for file in files:
    #         print(os.path.join(root, file))
    allFullFilePath = [os.path.join(root, file) for root, dirs, files in os.walk(fileDir) for file in files]
    [handleFile(fullFilePath) for fullFilePath in allFullFilePath]


# fullFilePath = '/home/john/abc.md'
# handleFile(fullFilePath)
# fileDir = './test1/test2/'
# handleDir(fileDir)
# fullFilePath = 'abc.md'
# handleFile(fullFilePath)


print('params:'+str(sys.argv[1:]))
for param in sys.argv[1:]:
    if os.path.isdir(param):
        handleDir(param)
    elif os.path.isfile(param):
        handleFile(param)
