# insert_request_info 함수 테스트
# read_request_info 함수 테스트 (데이터가 있는 경우)
# read_request_info 함수 테스트 (데이터가 없는 경우)

# pytest tests/ml/domain/service/test_execute_request_info_db.py
# pip install pytest

import pytest
from unittest.mock import MagicMock, patch
from src.ml.domain.service.execute_request_info_db import insert_request_info, read_request_info
from src.ml.domain.vo.request_info_vo import RequestInfoVO

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_get_db(mock_db):
    return MagicMock(return_value=iter([mock_db]))

@patch('src.ml.domain.service.execute_request_info_db.get_db')
def test_insert_request_info(mock_get_db, mock_db):
    # 테스트용 RequestInfoVO 객체 생성
    test_request_info = RequestInfoVO(some_field="test_value")
    
    # mock_get_db가 mock_db를 반환하도록 설정
    mock_get_db.return_value = mock_db
    
    # 함수 실행
    result = insert_request_info(test_request_info)
    
    # 검증
    assert mock_db.add.called
    assert mock_db.commit.called
    assert mock_db.refresh.called
    assert result == mock_db.refresh.return_value.id

@patch('src.ml.domain.service.execute_request_info_db.get_db')
def test_read_request_info(mock_get_db, mock_db):
    # 테스트용 데이터 설정
    test_id = 1
    test_data = '{"some_field": "test_value"}'
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(data=test_data)
    
    # mock_get_db가 mock_db를 반환하도록 설정
    mock_get_db.return_value = mock_db
    
    # 함수 실행
    result = read_request_info(test_id)
    
    # 검증
    assert result == test_data
    mock_db.query.assert_called_once()
    mock_db.query.return_value.filter.assert_called_once()

@patch('src.ml.domain.service.execute_request_info_db.get_db')
def test_read_request_info_not_found(mock_get_db, mock_db):
    # 테스트용 데이터 설정
    test_id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # mock_get_db가 mock_db를 반환하도록 설정
    mock_get_db.return_value = mock_db
    
    # 함수 실행
    result = read_request_info(test_id)
    
    # 검증
    assert result is None
    mock_db.query.assert_called_once()
    mock_db.query.return_value.filter.assert_called_once()