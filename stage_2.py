from stage_2_tool import *
import json
from multi_tool import wait_multi_task

# 得到每条数据的 short context  & evaluation form GPT 3.5

# 断点重续Setting
count = 1
start_index = count - 1

if __name__ == "__main__":
    # 去重数据集
    array = []
    with open('./datasource/easy_question_3.json', encoding='utf-8', mode='r') as f:
        array = json.load(f)
    print('去重前', len(array))
    s = {}
    uni_set = []
    for js in array:
        k = str(js['properties']['doi']) + str(js['question'])
        if k in s:
            continue
        s[k] = js
        uni_set.append(js)
    s.clear()
    array = uni_set
    print('数据数量：', len(array))

    # 询问函数
    def func(js, idx):
        # 1 . 根据问题得到答案
        system_answer = "Please play the role of a medical researcher and follow the instructions to answer the corresponding questions based on the following reference content."
        question1 = f"""        
                        question: {js['question']}
                        instruction 1:Give the shortest reference to the context paragraph that is sufficient to answer the question
                        instruction 2:Please organize the context and the shortest reference context according to the following format '[answer:(your answer),shortest_context:(your answer of shortest context)]'
                        reference:  
                        """
        # 构造 reference
        for k, v in js['raw_context'].items():
            question1 += 'article ' + str(k) + ':' + str(v) + ';\n'
        
        # Debug 输出
        print(system_answer,question1)
        # 询问GPT3.5
        response = gpt_ask_no_stream(text=question1, prompt=system_answer)
        
        # 出现问题则重试两次 两次如果都失败直接放弃该条数据
        try:
            temp_dict = split_respeonse1(response)
            js['short_context'] = temp_dict['shortest_context']
        except:
            try:
                response = gpt_ask_no_stream(text=question1, prompt=system_answer)
                temp_dict = split_respeonse1(response)
                js['short_context'] = temp_dict['shortest_context']
            except:
                return {}
        
        # Debug 输出
        print(js['short_context'])

        # 循环进行判断 最多问两次GPT他觉得最短的上下文
        cnt = 0
        over = False
        while cnt <= 2:
            # 2. 循环判断 ，是否为最短上下文，GPT 回答 yes for终止，回答no ，替换新的short context
            system_context = "Please act as a medical researcher and follow the instructions to determine whether the given short context is the shortest paragraph in the long context that is enough to answer the question."
            js['Long_context'] = ''
            for k, v in js['raw_context'].items():
                js['Long_context'] += 'article ' + str(k) + ':' + str(v) + ';\n'

            context_judger = f"""
                        question: {js['question']}
                        instruction 1:If your answer is yes, don’t add anything to your answer.The format is as follows:[Context_judge:Yes]
                        instruction 2:If your answer is No, please give the shortest context you think is sufficient to answer the question. 
                                     The format is as follows:[Context_judge:No,new_short_context:(the shortest context you think is sufficient to answer the question)]
                        reference:  long_context:{js['Long_context']};
                                    short_context:{js['short_context']}
                    """
            response = gpt_ask_no_stream(text=context_judger, prompt=system_context)
            try:
                temp_dict = split_respeonse2(response)
                if temp_dict['Context_judge'] == 'Yes':
                    break
                else:
                    print(temp_dict)
                    cnt += 1
                    js['short_context'] = temp_dict['new_short_context']
            except:
                try:
                    response = gpt_ask_no_stream(text=context_judger, prompt=system_context)
                    temp_dict = split_respeonse2(response)

                    if temp_dict['Context_judge'] == 'Yes':
                        break
                    else:
                        print(temp_dict)
                        cnt += 1
                        js['short_context'] = temp_dict['new_short_context']
                except:
                    over = True
                    break
        
        # try 两次均为失败 返回空字典表示放弃该条数据
        if over:
            return {}

        # 3. 使用 GPT3.5 评估 结果如何,在json中加入新的 evaluation_35:字段

        system_answer_judger = """
                Please act as an impartial judge and evaluate the quality of the responses provided by AI assistant to the user question displayed below.    
                Your return should be based on the question, context, and the AI assistant’s answer
                Your return can only be in one of the following three situations:
                If you think the context has the information needed to answer the question, but the answer does not fit the facts or context, answer 'bad answer'; 
                if you think the information in the context is irrelevant to the question, answer 'bad context'; 
                if you think the context contains enough information and the answer is consistent with common sense and context, please answer 'exactly'
                """
        answer_juger_context = f"""
                question: {js['question']}
                context:{js['short_context']}
                response:{js['raw_answer']}
                """
        
        # 将评估结果嵌入js中
        response = gpt_ask_no_stream(text=answer_juger_context, prompt=system_answer_judger)
        js['evaluation_35'] = str(response)

        return js


    # 构造并发字典
    all_dict = {}
    cnt = 1
    for i in range(len(array)):
        if i < start_index:
            cnt += 1
            continue
        all_dict[cnt] = array[i]
        cnt += 1

    # 并发求结果
    ret = wait_multi_task(func, all_dict, multi=12, timeout=6000)

    # 处理存储，将所有结果保存并分类出 exactly 数据
    save_array = []
    save_exactly = []
    for k, v in ret.items():
        if v is not None and v is not False and len(v.items()) > 0:
            save_array.append(v)
            if str(v['evaluation_35']).lower() == 'exactly':
                v['evaluation_35'] = str(v['evaluation_35']).lower()
                save_exactly.append(v)

    # 这里是跑完所有的以后将所有的json打到一个文件里
    with open('./data_0508_2/dataset_final.json', encoding='utf-8', mode='w') as f:
        json.dump(save_array, f, indent=2)
    with open('./data_0508_2/dataset_final_exactly.json', encoding='utf-8', mode='w') as f:
        json.dump(save_exactly, f, indent=2)