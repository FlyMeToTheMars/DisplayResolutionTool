import ctypes
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from ctypes import wintypes
from collections import defaultdict

# ============== 管理员权限检查 ==============
def require_admin():
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, None, 1)
        sys.exit()

# ============== Windows常量定义 ==============
DISPLAY_DEVICE_ACTIVE = 0x1
CDS_UPDATEREGISTRY = 0x00000001
DM_PELSWIDTH = 0x00080000
DM_PELSHEIGHT = 0x00100000
DM_DISPLAYFREQUENCY = 0x00400000

# ============== 结构体定义 ==============
class DISPLAY_DEVICEW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128)
    ]

class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmPositionX", ctypes.c_long),
        ("dmPositionY", ctypes.c_long),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
        ("dmColor", ctypes.c_short),
        ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short),
        ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short),
        ("dmFormName", wintypes.WCHAR * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
    ]

# ============== API初始化 ==============
user32 = ctypes.WinDLL("user32.dll")
user32.EnumDisplayDevicesW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.POINTER(DISPLAY_DEVICEW),
    wintypes.DWORD
]
user32.EnumDisplaySettingsW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.POINTER(DEVMODEW)
]
user32.ChangeDisplaySettingsExW.argtypes = [
    wintypes.LPCWSTR,
    ctypes.POINTER(DEVMODEW),
    wintypes.HWND,
    wintypes.DWORD,
    ctypes.c_void_p
]

# ============== 功能函数 ==============
def list_displays():
    displays = []
    index = 0
    while True:
        dev = DISPLAY_DEVICEW()
        dev.cb = ctypes.sizeof(DISPLAY_DEVICEW)
        if not user32.EnumDisplayDevicesW(None, index, ctypes.byref(dev), 0):
            break
        if dev.StateFlags & DISPLAY_DEVICE_ACTIVE:
            displays.append(dev.DeviceName)
        index += 1
    return displays

def get_supported_modes(device_name):
    mode_dict = defaultdict(list)
    index = 0
    while True:
        dm = DEVMODEW()
        dm.dmSize = ctypes.sizeof(DEVMODEW)
        if not user32.EnumDisplaySettingsW(device_name, index, ctypes.byref(dm)):
            break
        if dm.dmPelsWidth > 0 and dm.dmPelsHeight > 0:
            key = (dm.dmPelsWidth, dm.dmPelsHeight)
            mode_dict[key].append(dm.dmDisplayFrequency)
        index += 1
    return {
        k: sorted(list(set(v)), reverse=True)
        for k, v in mode_dict.items()
    }

def set_resolution(display_name, width, height, refresh):
    dm = DEVMODEW()
    dm.dmSize = ctypes.sizeof(DEVMODEW)
    dm.dmFields = DM_PELSWIDTH | DM_PELSHEIGHT | DM_DISPLAYFREQUENCY
    dm.dmPelsWidth = width
    dm.dmPelsHeight = height
    dm.dmDisplayFrequency = refresh
    result = user32.ChangeDisplaySettingsExW(
        display_name,
        ctypes.byref(dm),
        None,
        CDS_UPDATEREGISTRY,
        None
    )
    error_map = {
        0: "成功",
        -1: "需要重启",
        -2: "不支持的分辨率",
        -5: "权限不足",
        -6: "显卡驱动拒绝"
    }
    return result == 0, error_map.get(result, f"未知错误代码: {result}")

# ============== GUI界面类 ==============
class ResolutionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("显示器分辨率调节工具 by flymetothemars")
        self.geometry("600x500")  # 增加窗口高度
        self.resizable(False, True)  # 允许垂直调整
        self.current_display = None
        self.mode_data = {}
        self.configure_style()
        self.create_widgets()
        self.load_displays()

    def configure_style(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TLabel', padding=5, font=('微软雅黑', 9))
        self.style.configure('TButton', padding=8, font=('微软雅黑', 9))
        self.style.configure('TCombobox', padding=5, font=('微软雅黑', 9))
        self.style.configure('Treeview', rowheight=25, font=('微软雅黑', 9))
        self.style.configure('Treeview.Heading', font=('微软雅黑', 10, 'bold'))

    def create_widgets(self):
        # 显示器选择
        self.display_frame = ttk.LabelFrame(self, text="显示器选择")
        self.display_frame.pack(pady=5, padx=10, fill="x")
        self.display_combo = ttk.Combobox(self.display_frame, state="readonly")
        self.display_combo.pack(pady=5, fill="x", padx=5)
        self.display_combo.bind("<<ComboboxSelected>>", self.on_display_select)

        # 分辨率选择
        self.res_frame = ttk.LabelFrame(self, text="分辨率选择")
        self.res_frame.pack(pady=5, padx=10, fill="both", expand=True)
        self.res_tree = ttk.Treeview(
            self.res_frame,
            columns=("width", "height"),
            show="headings",
            height=10  # 减少显示行数
        )
        self.res_tree.heading("width", text="宽度")
        self.res_tree.heading("height", text="高度")
        self.res_tree.column("width", width=280, anchor="center")
        self.res_tree.column("height", width=280, anchor="center")
        self.res_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.res_tree.bind("<<TreeviewSelect>>", self.on_resolution_select)

        # 刷新率选择
        self.refresh_frame = ttk.Frame(self)
        self.refresh_frame.pack(pady=5, padx=10, fill="x")
        ttk.Label(self.refresh_frame, text="刷新率:").pack(side="left", padx=5)
        self.refresh_combo = ttk.Combobox(
            self.refresh_frame,
            state="readonly",
            width=15
        )
        self.refresh_combo.pack(side="left", padx=5)

        # 操作按钮（关键修复：调整pack顺序）
        self.btn_frame = ttk.Frame(self)
        self.btn_frame.pack(pady=10, padx=20, fill="x", side="bottom")  # 固定底部
        self.apply_btn = ttk.Button(
            self.btn_frame,
            text="应用设置",
            command=self.apply_resolution,
            width=15
        )
        self.apply_btn.pack(side="left", expand=True)
        self.refresh_btn = ttk.Button(
            self.btn_frame,
            text="刷新列表",
            command=self.refresh_all,
            width=15
        )
        self.refresh_btn.pack(side="right", expand=True)

    def load_displays(self):
        try:
            displays = list_displays()
            self.display_combo["values"] = [f"显示器 {i+1} ({d})" for i, d in enumerate(displays)]
            if displays:
                self.display_combo.current(0)
                self.current_display = displays[0]
                self.load_resolutions()
        except Exception as e:
            self.show_error("显示器枚举失败", str(e))

    def load_resolutions(self):
        self.res_tree.delete(*self.res_tree.get_children())
        self.refresh_combo.set('')
        self.refresh_combo["values"] = []
        try:
            self.mode_data = get_supported_modes(self.current_display)
            for (w, h) in sorted(self.mode_data.keys(), key=lambda x: (-x[0], -x[1])):
                self.res_tree.insert("", "end", values=(w, h))
        except Exception as e:
            self.show_error("分辨率获取失败", str(e))

    def on_display_select(self, event):
        if self.display_combo.current() >= 0:
            displays = list_displays()
            self.current_display = displays[self.display_combo.current()]
            self.load_resolutions()

    def on_resolution_select(self, event):
        selected = self.res_tree.selection()
        if selected:
            item = self.res_tree.item(selected[0])
            w, h = item["values"]
            refresh_rates = self.mode_data.get((w, h), [])
            self.refresh_combo["values"] = refresh_rates
            if refresh_rates:
                self.refresh_combo.current(0)

    def apply_resolution(self):
        if not self.current_display:
            self.show_warning("请先选择显示器")
            return
        selected_res = self.res_tree.selection()
        if not selected_res:
            self.show_warning("请选择分辨率")
            return
        if not self.refresh_combo.get():
            self.show_warning("请选择刷新率")
            return
        try:
            w, h = self.res_tree.item(selected_res[0])["values"]
            refresh = int(self.refresh_combo.get())
            success, msg = set_resolution(self.current_display, w, h, refresh)
            if success:
                messagebox.showinfo("成功", f"已设置为 {w}x{h}@{refresh}Hz\n屏幕可能短暂闪烁")
            else:
                self.show_error("设置失败", msg)
        except Exception as e:
            self.show_error("设置异常", str(e))

    def refresh_all(self):
        self.load_displays()

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def show_warning(self, message):
        messagebox.showwarning("提示", message)

if __name__ == "__main__":
    require_admin()
    app = ResolutionApp()
    app.mainloop()
