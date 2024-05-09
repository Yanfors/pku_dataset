# PKU DATASET

---

## Quick Start
1. 将 ```datasource``` 文件夹中的 ```easy_question_3.json``` 替换为你的数据集，本项目提供的为示例数据集。
2. 配置你的Python环境，本项目使用 ```Python 3.11``` 使用到的第三方库有 ```requests openai```。
3. ```python stage_2.py``` 运行本项目。等待并发进行完毕后，你可以在 ```data_0508_2_single``` 中找到每一条处理的 json, 可以在 ```data_0508_2``` 中找到所有处理好的json，以及分类出来的 exactly json。

## 项目结构
1. ```stage_2.py``` 为主函数Python文件，其中包含了数据集的去重、断点重续、GPT问题构造以及询问、并发处理构造、打包json以及分类json。
2. ```stage_2_tool.py``` 为工具类Python文件，其中包含了GPT询问、GPT返回数据处理、等其他的一些常用函数。
3. ```multi_tool.py``` 为并发工具类Python文件，其中包含了并发处理GPT询问以及每条json处理后的保存、处理速度的计算等。
4. ```verify_data.py``` 为清洗统计数据Python文件，其中包含了对 ```stage_2.py``` 文件执行出来的数据进行清洗分类并统计脏数据、计算数据的exactly率。
