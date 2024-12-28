import xmlrpc.client

def get_supervisor_processes_status(rpc_url: str = "http://127.0.0.1:9001/RPC2"):
    """
    Supervisor에 등록된 모든 프로세스 정보를 조회한다.
    
    :param rpc_url: Supervisor XML-RPC 주소 (기본값: http://127.0.0.1:9001/RPC2)
    :return: [
        {
          'name': '프로세스명',
          'pid': 1234,
          'state': 'RUNNING' or 'STOPPED' 등,
          'statename': 'RUNNING' or 'STOPPED' 등 (문자열 형태),
          'description': '프로세스 요약 정보',
          ...
        },
        ...
    ]
    """
    try:
        server = xmlrpc.client.ServerProxy(rpc_url)
        # Supervisor 전체 프로세스 정보 가져오기
        process_info_list = server.supervisor.getAllProcessInfo()
        
        # process_info_list는 아래와 같은 딕셔너리들의 리스트입니다.
        # [
        #   {
        #     'name': '프로세스명',
        #     'group': '그룹명',
        #     'start': 1693632599,
        #     'stop': 0,
        #     'now': 1693632676,
        #     'state': 20,               # 내부 상태 코드
        #     'statename': 'RUNNING',    # 사람이 읽기 쉬운 상태명
        #     'spawnerr': '',
        #     'exitstatus': 0,
        #     'logfile': '/path/to/log',
        #     'stdout_logfile': '/path/to/stdout/log',
        #     'stderr_logfile': '/path/to/stderr/log',
        #     'pid': 1234,
        #     'description': 'pid 1234, uptime 5:20:01'
        #   },
        #   ...
        # ]

        # 필요한 정보만 추려서 반환 구조화
        status_list = []
        for info in process_info_list:
            status_list.append({
                'name': info.get('name'),
                'pid': info.get('pid'),
                'state': info.get('statename'),      # RUNNING, STOPPED 등
                'description': info.get('description'),
            })
        
        return status_list

    except Exception as e:
        print(f"Supervisor에 연결 중 오류가 발생했습니다: {e}")
        return []

if __name__ == "__main__":
    # 예시 호출
    processes = get_supervisor_processes_status()
    for proc in processes:
        print(f"[{proc['state']}] {proc['name']} (PID: {proc['pid']}) - {proc['description']}")
