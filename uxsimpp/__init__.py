"""
UXsim++: Fast, simple, lightweight traffic simulator for Python

This package provides traffic simulation capabilities using C++ extensions via pybind11.
"""

import os
import sys
import importlib.util
import glob
import site

# # import C++ module: This should be unnessesary at this stage
# try:
#     # 通常のインポート方法を試す
#     from . import trafficppy
# except ImportError:
#     # インポートに失敗した場合、モジュールを探す
#     #emergency fallbacks. may be unnecessary
#     module_found = False
#     package_dir = os.path.dirname(__file__)
    
#     # 可能性のあるパスのリスト
#     possible_paths = [
#         # 1. 現在のパッケージディレクトリ内を検索
#         os.path.join(package_dir, "trafficppy.cp*-*.pyd"),
#         os.path.join(package_dir, "trafficppy.pyd"), #"trafficppy*.pyd"かも？
#         os.path.join(package_dir, "trafficppy.so"), #"trafficppy*.so"かも？
#     ]
    
#     # モジュールを探してインポート
#     for path_pattern in possible_paths:
#         if "*" in path_pattern:
#             matching_paths = glob.glob(path_pattern)
#             for path in matching_paths:
#                 if os.path.exists(path):
#                     try:
#                         spec = importlib.util.spec_from_file_location("trafficppy", path)
#                         if spec:
#                             trafficppy = importlib.util.module_from_spec(spec)
#                             spec.loader.exec_module(trafficppy)
#                             module_found = True
#                             #print(f"Found module at: {path}")
#                             break
#                     except Exception as e:
#                         #print(f"Error loading {path}: {e}")
#                         pass
#             if module_found:
#                 break
#         elif os.path.exists(path_pattern):
#             try:
#                 spec = importlib.util.spec_from_file_location("trafficppy", path_pattern)
#                 if spec:
#                     trafficppy = importlib.util.module_from_spec(spec)
#                     spec.loader.exec_module(trafficppy)
#                     module_found = True
#                     #print(f"Found module at: {path_pattern}")
#                     break
#             except Exception as e:
#                 #print(f"Error loading {path_pattern}: {e}")
#                 pass
    
#     if not module_found:
#         raise ImportError("Failed to import the C++ extension module. Sorry for the inconvenience. This package is still in the development stage. Please report to the developer.")

# .pyからの機能をインポート
from .uxsimpp import *

__version__ = "0.0.1"
__author__ = "Toru Seo"
__copyright__ = "Copyright (c) 2025 Toru Seo"
__license__ = "MIT License"


# temporal workaround for segmentation failure
import atexit
import gc
import io

def _safe_cleanup_and_exit():
    # 1. 標準出力／標準エラーのフラッシュ
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.flush()
        except Exception:
            pass

    # 2. open() されたファイルオブジェクトのクローズ
    for obj in gc.get_objects():
        if isinstance(obj, io.IOBase) and not obj.closed:
            try:
                obj.close()
            except Exception:
                pass

    # 3. （必要に応じて）データベース接続やキャッシュの明示的クローズ
    #    例: SQLAlchemy を使っている場合 engine.dispose() を呼ぶなど

    # 4. プロファイラやカバレッジツールのフラッシュ
    #    例: coverage.Coverage.current().save()

    # 最後に os._exit で即時終了
    os._exit(0)

# atexit ハンドラは「登録順の逆」で実行されるので、
# ここで登録しておくと他のハンドラのあとに _safe_cleanup_and_exit が呼ばれる可能性が高くなります。
atexit.register(_safe_cleanup_and_exit)