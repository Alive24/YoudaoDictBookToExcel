import xml.dom.minidom
import pandas as pd
import os
import sys
import getopt
from multiprocessing import Pool
import logging
import requests
from bs4 import BeautifulSoup

### 创建初始全局变量
global_logger = logging.getLogger()
global devMode
global config 

### 初始化参数
devMode = False
config = {
    "inputPath" : "./input",
    "outputPath" : "./output"
}


def loadConfig(configJson={}):
    global config
    previousConfig = config
    print("loadConfig")
    ### 此处进行操作
    updatedConfig = previousConfig
    config = updatedConfig

def YoudaoXMLToExcel(filename):
    try:
        sourceXMLPath = os.path.join(config["inputPath"], filename)
        targetXLSXPath = os.path.join(config["outputPath"], filename.split('.')[0] + ".xlsx")
    except Exception as error:
        global_logger.exception("Failed to prepare for XMLToExceL", error)
    try:
        dom = xml.dom.minidom.parse(sourceXMLPath)
        wordTags = dom.getElementsByTagName("word")
        words = [wordTags[i].firstChild.data for i in range(len(wordTags))]
        transTags = dom.getElementsByTagName("trans")
        trans = [(transTags[i].firstChild.data if transTags[i].firstChild is not None else resetTranslationViaYoudao(wordTags[i].firstChild.data)) for i in range(len(transTags))]
        itemDict = {'words': words, 'trans': trans}
        df = pd.DataFrame(itemDict)  
        with pd.ExcelWriter(targetXLSXPath) as Writer:
            df.to_excel(Writer, 'Sheet1', index=False, header=False)
    except Exception as error:
        global_logger.exception("Failed to parse in XMLToExceL", error)

def resetTranslationViaYoudao(word, lang="eng"):
    try:
        r = requests.get('http://www.youdao.com/w/%s/%s' %(lang, word)) # 向有道词典请求资源
        html = r.text
        soup = BeautifulSoup(html, 'html.parser') # 结构化文本soup
        transContainer = soup.find(name='div', attrs={'class': 'trans-container'}) # 获取中文释义所在的标签
        trans = transContainer.find("ul")
        print(trans.get_text()) # 获取标签内文本
        return trans.get_text()
    except Exception as error:
        global_logger.exception("Failed to getTranslation in XMLToExceL, returning empty string", error)
        return ""


def prepareJobList():
    print("prepareJobList")

def coordinator():
    pool = Pool(6)
    pool.map(XMLToExcel, filenames)
    pool.close()
    pool.join()

def main(args=[]):
    print(args)

def devMain(args=[]):
    testXMLFilename = "英语生词 2021-02-28.xml"
    YoudaoXMLToExcel(testXMLFilename)
    # resetTranslationViaYoudao("test")

if __name__ == "__main__":

    ### 读取配置文件
    loadConfig()
    ### 解析入口参数
    try:
        opts, args = getopt.getopt(sys.argv[1:],"",["dev"])
    except getopt.GetoptError as error:
        global_logger.exception("Failed to parse opts and args", error)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('help msg')
            sys.exit()
        elif opt in ("--dev"):
            devMode = True
    ### 入口
    if devMode == True:
        ### 开发模式入口
        devMain()
    else:
        ### 常规入口
        main()