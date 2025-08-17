import unittest
import importlib.util
from io import StringIO
import ast
import sys
import signal
import threading
import time
from contextlib import contextmanager

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("程式執行超時")

def run_with_timeout(func, timeout_seconds=5):
    """在指定時間內執行函數，超時則拋出異常"""
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func()
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)
    
    if thread.is_alive():
        # 如果線程還在運行，強制終止
        return TimeoutError(f"程式執行超過 {timeout_seconds} 秒")
    
    if exception[0]:
        return exception[0]
    
    return result[0]

def detect_encoding(file_path):
    """智能檢測檔案編碼"""
    # 嘗試常見編碼
    common_encodings = [
        'utf-8',
        'utf-8-sig',  # UTF-8 with BOM
        'big5',       # 繁體中文
        'gbk',        # 簡體中文
        'gb2312',     # 簡體中文
        'cp950',      # 繁體中文 (Windows)
        'cp936',      # 簡體中文 (Windows)
        'shift_jis',  # 日文
        'euc-jp',     # 日文
        'euc-kr',     # 韓文
        'latin-1',    # 西歐語言
        'iso-8859-1', # 西歐語言
    ]
    
    for encoding in common_encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue
    
    return 'utf-8'  # 預設使用 UTF-8

@contextmanager
def mock_input(input_values):
    """模擬輸入的上下文管理器"""
    import builtins
    
    if isinstance(input_values, str):
        input_values = [input_values]
    
    input_iter = iter(input_values)
    
    def mock_input_func(prompt=""):
        try:
            return next(input_iter)
        except StopIteration:
            return ""
    
    # 保存原始的 input 函數
    original_input = builtins.input
    
    try:
        # 替換 input 函數
        builtins.input = mock_input_func
        yield
    finally:
        # 恢復原始的 input 函數
        builtins.input = original_input

def load_student_code(file_path, input_values=None):
    """載入學生程式碼，可選地模擬輸入"""
    spec = importlib.util.spec_from_file_location("student_code", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def find_main_function(file_path):
    """自動檢測學生程式碼中的主要函數"""
    # 使用智能編碼檢測
    encoding = detect_encoding(file_path)
    
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()
    except Exception as e:
        # 如果還是失敗，嘗試二進位模式讀取並解碼
        try:
            with open(file_path, 'rb') as f:
                raw_content = f.read()
                # 嘗試移除 BOM
                if raw_content.startswith(b'\xef\xbb\xbf'):
                    raw_content = raw_content[3:]
                content = raw_content.decode('utf-8', errors='replace')
        except:
            return None
    
    try:
        tree = ast.parse(content)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        # 優先順序：solution > main > 第一個函數
        if 'solution' in functions:
            return 'solution'
        elif 'main' in functions:
            return 'main'
        elif functions:
            return functions[0]
        else:
            return None
    except:
        return None

def generate_test_cases(inputs, outputs, module, function_name):
    """動態建立unittest測試用例"""
    class TestCode(unittest.TestCase):
        pass

    for i, (input_data, expected_output) in enumerate(zip(inputs, outputs)):
        def test_case(input_data, expected_output, func_name):
            def test(self):
                if hasattr(module, func_name):
                    func = getattr(module, func_name)
                    try:
                        # 執行函數並獲取結果
                        result = func(input_data)
                        
                        # 標準化結果和期望輸出進行比較
                        result_str = str(result).strip()
                        expected_str = str(expected_output).strip()
                        
                        self.assertEqual(result_str, expected_str, f"測試案例 {i + 1} 失敗: 期望 '{expected_str}', 實際得到 '{result_str}'")
                        
                    except Exception as e:
                        self.fail(f"函數執行錯誤: {str(e)}")
                else:
                    self.fail(f"函數 '{func_name}' 不存在")
            return test
        
        setattr(TestCode, f"test_case_{i + 1}", test_case(input_data, expected_output, function_name))
    
    return TestCode

def run_test_cases(student_code, question_id, timeout_seconds=5):
    """執行測試用例，可設定超時時間"""
    try:
        # 載入學生程式碼模組
        module = load_student_code(student_code)
        
        # 檢測主要函數
        function_name = find_main_function(student_code)
        if not function_name:
            return "CE", False
        
        # 從資料庫獲取題目的輸入輸出範例
        from questions.models import Question
        try:
            question = Question.objects.get(id=question_id, is_approved=True)
            inputs = [line.strip() for line in question.input_example.strip().splitlines() if line.strip()]
            outputs = [line.strip() for line in question.output_example.strip().splitlines() if line.strip()]
        except Question.DoesNotExist:
            return "CE", False
        
        # 生成測試用例
        test_cases = generate_test_cases(inputs, outputs, module, function_name)
        
        # 使用超時機制執行測試
        def run_tests():
            stream = StringIO()
            runner = unittest.TextTestRunner(stream=stream, verbosity=2)
            suite = unittest.TestLoader().loadTestsFromTestCase(test_cases)
            result = runner.run(suite)
            return result, stream.getvalue()
        
        # 執行測試並設置超時
        test_result = run_with_timeout(run_tests, timeout_seconds)
        
        if isinstance(test_result, Exception):
            # 如果是超時異常
            if isinstance(test_result, TimeoutError):
                return "TLE", False
            else:
                # 其他異常，根據錯誤訊息判斷類型
                error_str = str(test_result).lower()
                if 'memory' in error_str or 'out of memory' in error_str:
                    return "MLE", False
                elif 'recursion' in error_str or 'stack overflow' in error_str:
                    return "RE", False
                elif 'syntax' in error_str or 'indentation' in error_str:
                    return "CE", False
                else:
                    return "RE", False
        
        result, output_text = test_result
        
        if result.wasSuccessful():
            return "AC", True  # Accepted
        else:
            return "WA", False  # Wrong Answer
        
    except SyntaxError as e:
        return "CE", False  # Compilation Error
    except IndentationError as e:
        return "CE", False  # Compilation Error
    except TimeoutError as e:
        return "TLE", False  # Time Limit Exceeded
    except MemoryError as e:
        return "MLE", False  # Memory Limit Exceeded
    except RecursionError as e:
        return "RE", False  # Runtime Error
    except Exception as e:
        # 根據錯誤訊息判斷錯誤類型
        error_str = str(e).lower()
        if 'timeout' in error_str or 'time limit' in error_str:
            return "TLE", False
        elif 'memory' in error_str or 'out of memory' in error_str:
            return "MLE", False
        elif 'recursion' in error_str or 'stack overflow' in error_str:
            return "RE", False
        elif 'syntax' in error_str or 'indentation' in error_str:
            return "CE", False
        else:
            return "RE", False