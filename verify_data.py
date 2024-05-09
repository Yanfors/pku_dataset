import json
import os

# 数据清洗 和 计算数据的正确率和脏数据条数

# array = []

# for root, dirs, files in os.walk('./data_new'):
#     for file in files:
#         file_path = os.path.join(root, file)
#         with open(file_path, mode='r', encoding='utf-8') as f:
#             js = json.load(f)
#             if len(js) > 0:
#                 array.append(js)

# new_array = []
# for i in range(100):
#     new_array.append(array[i])

# with open('./data_source/dataset_100.json', mode='w', encoding='utf-8') as f:
#     json.dump(new_array, f, indent=2)

success = []

mark = 0

array = []

cnt = 0

for root, dirs, files in os.walk('./data_0508_2_single'):
    for file in files:
        file_path = os.path.join(root, file)
        with open(file_path, mode='r', encoding='utf-8') as f:
            js = json.load(f)
            array.append(js)

for j in array:
    if len(j) <= 0:
        mark += 1
        continue
    j['evaluation_35'] = str(j['evaluation_35']).lower()
    if j['evaluation_35'] == 'exactly' or j['evaluation_35'] == 'yes':
        j['evaluation_35'] = 'exactly'
        success.append(j)
    elif j['evaluation_35'] == 'bad context' or j['evaluation_35'] == 'bad answer':
        continue
    else:
        # miry.append(j)
        mark += 1

print('总共跑出', len(array))
print('脏数据', mark)
print('exactly', len(success))

two = []

d = set()

with open('./data_0508/dataset_final_exactly.json', mode='r', encoding='utf-8') as f:
    all_j = json.load(f)
    for j in all_j:
        k = str(j['properties']['doi']) + str(j['question'])
        d.add(k)
        two.append(j)


for s in success:
    k = str(s['properties']['doi']) + str(s['question'])
    if k not in d:
        two.append(s)

print('exactly', len(two))
with open('./data_0508/dataset_final_all_exactly.json', mode='w', encoding='utf-8') as f:
    json.dump(two, f, indent=2)