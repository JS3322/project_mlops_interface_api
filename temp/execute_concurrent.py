import concurrent.futures
import time


# 임의의 함수 정의 (실제 작업은 이곳에 구현)
def execute_preprocess(task_id):
    print(f"Task {task_id}: Preprocessing...")
    time.sleep(1)  # 작업이 시간이 걸리는 것을 가정


def execute_train(task_id):
    print(f"Task {task_id}: Training...")
    time.sleep(1)


def execute_test(task_id):
    print(f"Task {task_id}: Testing...")
    time.sleep(1)


def execute_task(task_id):
    execute_preprocess(task_id)
    execute_train(task_id)
    execute_test(task_id)
    return f"Task {task_id} completed."


def main(count, core_count):
    tasks = list(range(1, count + 1))

    with concurrent.futures.ProcessPoolExecutor(max_workers=core_count) as executor:
        results = list(executor.map(execute_task, tasks))

    for result in results:
        print(result)


if __name__ == "__main__":
    count = 200  # 총 task 수
    core_count = 4  # 사용할 코어 수

    main(count, core_count)
