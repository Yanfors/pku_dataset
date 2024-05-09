import _thread
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
import json

result = {}
error_count = {}
threadLock = _thread.allocate_lock()

count = 0


def _do_fun(fn, id, arg, arg2):
    global result
    try:
        ret = fn(arg, arg2)
        with threadLock:
            result[id] = ret
            print('线程', id, '完成任务', result[id])
            # 如果不是错误的 存下来。
            if result[id] is not None and result[id] is not None and result[id] is not {} and len(result[id]) > 0:
                with open('./data_0508_2_single/save_json_' + str(id) + '.json', encoding='utf-8', mode='w') as f:
                    json.dump(result[id], f, indent=2)
    except Exception:
        if id not in error_count: error_count[id] = 0
        error_count[id] += 1
        if error_count[id] > 3:
            result[id] = "ERROR"
        else:
            traceback.print_exc()
            time.sleep(0.5)
            return _do_fun(fn, id, arg, arg2)


def wait_multi_task(fn, args: dict, multi=20, timeout: int = 600):
    pool = ThreadPoolExecutor(multi)
    for k, q in args.items():
        result[k] = False
        pool.submit(_do_fun, fn, k, q, k)
    has_pass = False
    ts = time.time()
    start_time = time.time()
    last_size = 0
    # same = 0
    # cache_count = 0
    while not has_pass:
        has_pass = True
        ok_count = 0
        for k, v in result.copy().items():
            if v is False:
                has_pass = False
            else:
                ok_count += 1
        # if cache_count == ok_count:
        #     same += 1
        # if same >= 300:
        #     print('卡住, 打印该 count 后的V')
        #     for k, v in result.copy().items():
        #         if k < cache_count:
        #             continue
        #         print(k, '->', v)
        #     print('提前结束.')
        #     pool.shutdown(wait=False)
        #     return {}
        # cache_count = ok_count
        print(f"ok:{ok_count}/{len(args)}  {int(ok_count * 100 / len(args))}%  speed: {'nan' if ok_count == 0 else (time.time() - start_time) / ok_count} item/s", end="\n", flush=True)
        if time.time() - ts > timeout:
            has_pass = True
        if last_size != ok_count:
            ts = time.time()
        last_size = ok_count
        time.sleep(0.5)
    ret = result.copy()
    result.clear()
    pool.shutdown(wait=False)
    return ret
