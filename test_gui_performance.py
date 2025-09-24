"""
Real GUI Performance Test
Tests the actual GUI application performance by monitoring the running system
"""

import time
import threading
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui_app import PoseDetectionGUI
from utils import logger, system_monitor


class GUIPerformanceMonitor:
    """Monitor GUI performance in real-time"""
    
    def __init__(self):
        self.monitoring = False
        self.fps_history = []
        self.start_time = None
        
    def start_monitoring(self, duration=30):
        """Start monitoring for specified duration"""
        self.monitoring = True
        self.start_time = time.time()
        self.fps_history = []
        
        def monitor_worker():
            while self.monitoring and self.start_time and (time.time() - self.start_time) < duration:
                fps = system_monitor.get_fps()
                runtime = system_monitor.get_runtime()
                self.fps_history.append(fps)
                
                print(f"Time: {runtime} | FPS: {fps:.2f}")
                time.sleep(1)  # Check every second
            
            self.stop_monitoring()
        
        monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
        monitor_thread.start()
        
        return monitor_thread
    
    def stop_monitoring(self):
        """Stop monitoring and show results"""
        self.monitoring = False
        
        if self.fps_history:
            avg_fps = sum(self.fps_history) / len(self.fps_history)
            max_fps = max(self.fps_history)
            min_fps = min(self.fps_history)
            
            print(f"\n=== Performance Test Results ===")
            print(f"Test Duration: {len(self.fps_history)} seconds")
            print(f"Average FPS: {avg_fps:.2f}")
            print(f"Maximum FPS: {max_fps:.2f}")
            print(f"Minimum FPS: {min_fps:.2f}")
            print(f"FPS Stability: {len([f for f in self.fps_history if f > 20])}/{len(self.fps_history)} good frames")
            
            # Analyze performance issues
            if avg_fps < 5:
                print("\n⚠️  SEVERE PERFORMANCE ISSUE DETECTED!")
                print("Possible causes:")
                print("- GUI thread blocking")
                print("- Heavy computation in main thread")
                print("- Memory leak or resource contention")
                print("- Threading synchronization issues")
            elif avg_fps < 15:
                print("\n⚠️  Performance needs improvement")
            else:
                print("\n✅ Performance is acceptable")


def test_gui_performance():
    """Test GUI performance by running the actual application"""
    print("Starting GUI Performance Test...")
    print("This will run the actual GUI application and monitor its performance.")
    print("Please start the system manually when the GUI opens.\n")
    
    monitor = GUIPerformanceMonitor()
    
    try:
        # Create GUI application
        app = PoseDetectionGUI()
        
        # Start monitoring after GUI is created
        print("GUI created. Starting performance monitoring...")
        monitor_thread = monitor.start_monitoring(duration=30)
        
        # Show instructions
        def show_instructions():
            import tkinter as tk
            instruction_window = tk.Toplevel(app.root)
            instruction_window.title("Test Instructions")
            instruction_window.geometry("400x200")
            
            instructions = """
Performance Test Instructions:

1. Click "啟動系統" to start the system
2. Let it run for 30 seconds
3. The test will automatically collect FPS data
4. Results will be shown in console

The test will run for 30 seconds.
            """
            
            tk.Label(instruction_window, text=instructions, justify=tk.LEFT).pack(padx=10, pady=10)
            tk.Button(instruction_window, text="OK", command=instruction_window.destroy).pack(pady=10)
        
        # Show instructions after a delay
        app.root.after(1000, show_instructions)
        
        # Run the GUI
        app.run()
        
    except Exception as e:
        print(f"Error during GUI performance test: {e}")
        logger.error(f"GUI performance test failed: {e}")
    finally:
        monitor.stop_monitoring()


if __name__ == "__main__":
    test_gui_performance()