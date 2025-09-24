"""
GUI測試檔案
獨立測試Tkinter GUI界面功能
"""

import sys
import os
import time
import threading

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import tkinter as tk
    from gui_app import PoseDetectionGUI
    from messages import Messages
    GUI_AVAILABLE = True
except ImportError as e:
    print(f"導入失敗: {e}")
    print("GUI測試需要tkinter和其他依賴")
    GUI_AVAILABLE = False


def test_gui_init():
    """測試GUI初始化"""
    print("=== 測試GUI初始化 ===")
    
    if not GUI_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        # 創建根視窗但不運行mainloop
        root = tk.Tk()
        root.withdraw()  # 隱藏視窗
        
        print("✓ Tkinter根視窗創建成功")
        
        # 測試基本組件
        frame = tk.Frame(root)
        label = tk.Label(frame, text="測試標籤")
        button = tk.Button(frame, text="測試按鈕")
        
        print("✓ 基本Tkinter組件創建成功")
        
        root.destroy()
        print("✓ GUI初始化測試完成")
        return True
        
    except Exception as e:
        print(f"❌ GUI初始化測試失敗: {e}")
        return False


def test_gui_components():
    """測試GUI組件"""
    print("\n=== 測試GUI組件 ===")
    
    if not GUI_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        root = tk.Tk()
        root.withdraw()
        
        # 測試各種組件
        components = [
            ("Frame", lambda: tk.Frame(root)),
            ("Label", lambda: tk.Label(root, text="測試")),
            ("Button", lambda: tk.Button(root, text="測試")),
            ("Entry", lambda: tk.Entry(root)),
            ("Text", lambda: tk.Text(root)),
            ("Listbox", lambda: tk.Listbox(root)),
            ("Canvas", lambda: tk.Canvas(root)),
            ("Scale", lambda: tk.Scale(root)),
            ("Checkbutton", lambda: tk.Checkbutton(root)),
        ]
        
        for name, creator in components:
            try:
                widget = creator()
                print(f"✓ {name} 組件創建成功")
            except Exception as e:
                print(f"❌ {name} 組件創建失敗: {e}")
                return False
        
        root.destroy()
        print("✓ GUI組件測試完成")
        return True
        
    except Exception as e:
        print(f"❌ GUI組件測試失敗: {e}")
        return False


def test_messages_integration():
    """測試訊息系統整合"""
    print("\n=== 測試訊息系統整合 ===")
    
    try:
        # 測試訊息獲取
        print("測試訊息獲取...")
        
        title = Messages.GUI_TEXTS['title']
        print(f"✓ GUI標題: {title}")
        
        instructions = Messages.get_all_instructions()
        print(f"✓ 動作說明: {instructions[:50]}...")
        
        for action, key in Messages.ACTION_KEYS.items():
            success_msg = Messages.get_success_message(action)
            print(f"✓ {action} -> {key}: {success_msg}")
        
        print("✓ 訊息系統整合測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 訊息系統整合測試失敗: {e}")
        return False


def test_gui_layout():
    """測試GUI佈局"""
    print("\n=== 測試GUI佈局 ===")
    
    if not GUI_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        root = tk.Tk()
        root.withdraw()
        
        # 測試網格佈局
        main_frame = tk.Frame(root)
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 測試各種佈局組件
        control_frame = tk.LabelFrame(main_frame, text="控制面板")
        control_frame.grid(row=0, column=0, sticky="ew")
        
        video_frame = tk.LabelFrame(main_frame, text="視頻顯示")
        video_frame.grid(row=1, column=0, sticky="nsew")
        
        status_frame = tk.LabelFrame(main_frame, text="狀態信息")
        status_frame.grid(row=2, column=0, sticky="ew")
        
        print("✓ 網格佈局創建成功")
        
        # 測試權重配置
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        print("✓ 權重配置成功")
        
        root.destroy()
        print("✓ GUI佈局測試完成")
        return True
        
    except Exception as e:
        print(f"❌ GUI佈局測試失敗: {e}")
        return False


def test_gui_variables():
    """測試GUI變數"""
    print("\n=== 測試GUI變數 ===")
    
    if not GUI_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        root = tk.Tk()
        root.withdraw()
        
        # 測試各種變數類型
        bool_var = tk.BooleanVar()
        string_var = tk.StringVar()
        int_var = tk.IntVar()
        double_var = tk.DoubleVar()
        
        # 測試變數操作
        bool_var.set(True)
        assert bool_var.get() == True
        print("✓ BooleanVar 測試通過")
        
        string_var.set("測試文字")
        assert string_var.get() == "測試文字"
        print("✓ StringVar 測試通過")
        
        int_var.set(42)
        assert int_var.get() == 42
        print("✓ IntVar 測試通過")
        
        double_var.set(3.14)
        assert double_var.get() == 3.14
        print("✓ DoubleVar 測試通過")
        
        root.destroy()
        print("✓ GUI變數測試完成")
        return True
        
    except Exception as e:
        print(f"❌ GUI變數測試失敗: {e}")
        return False


def test_gui_events():
    """測試GUI事件處理"""
    print("\n=== 測試GUI事件處理 ===")
    
    if not GUI_AVAILABLE:
        print("跳過測試：缺少必要依賴")
        return False
    
    try:
        root = tk.Tk()
        root.withdraw()
        
        # 測試事件處理
        event_triggered = False
        
        def test_callback():
            nonlocal event_triggered
            event_triggered = True
        
        button = tk.Button(root, text="測試", command=test_callback)
        
        # 模擬按鈕點擊
        button.invoke()
        
        if event_triggered:
            print("✓ 按鈕事件處理成功")
        else:
            print("❌ 按鈕事件處理失敗")
            return False
        
        # 測試變數回調
        callback_triggered = False
        
        def var_callback(*args):
            nonlocal callback_triggered
            callback_triggered = True
        
        test_var = tk.StringVar()
        test_var.trace('w', var_callback)
        test_var.set("觸發回調")
        
        if callback_triggered:
            print("✓ 變數回調處理成功")
        else:
            print("❌ 變數回調處理失敗")
            return False
        
        root.destroy()
        print("✓ GUI事件處理測試完成")
        return True
        
    except Exception as e:
        print(f"❌ GUI事件處理測試失敗: {e}")
        return False


def run_all_tests():
    """運行所有測試"""
    print("開始GUI測試...")
    print("=" * 50)
    
    tests = [
        test_gui_init,
        test_gui_components,
        test_messages_integration,
        test_gui_layout,
        test_gui_variables,
        test_gui_events,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ 測試 {test_func.__name__} 執行失敗: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("測試結果摘要:")
    print(f"通過: {sum(results)}/{len(results)}")
    
    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✓ 通過" if result else "❌ 失敗"
        print(f"{i+1}. {test_func.__name__}: {status}")
    
    overall_success = all(results)
    print(f"\n整體測試結果: {'✓ 全部通過' if overall_success else '❌ 有失敗項目'}")
    
    return overall_success


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)