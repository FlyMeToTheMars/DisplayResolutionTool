# 显示器分辨率调节工具 / Display Resolution Tool

Windows下的显示器分辨率调节工具，支持多显示器管理和刷新率设置

A Windows display resolution utility with multi-monitor support and refresh rate control



## 一图看懂本工具 / UI


![程序运行界面截图](https://raw.githubusercontent.com/FlyMeToTheMars/DisplayResolutionTool/main/demo.png)

## 软件使用场景 / Software application contexts

多显示器用户如果有CS老玩家爱用1280 960 或者1440 1080分辨率的玩家，使用win默认的调整要么麻烦，要么有时候调整完刷新率自己变成60，要么有时候在多显示器环境无法准确识别哪个显示器，所以有了这个软件。

## 功能特性 / Features

- ✅ 多显示器支持 / Multi-display support
- ✅ 分辨率与刷新率组合选择 / Resolution & refresh rate combinations
- ✅ 管理员权限自动获取 / Automatic admin privilege escalation
- ✅ 现代图形界面 / Modern GUI interface
- ✅ 设置持久化保存 / Persistent setting storage
- ✅ 错误友好提示 / User-friendly error handling

## 使用 / Usage

解压release，管理员打开直接使用

或者自己编译

把源代码中的文件下载

```python
python resolution_tool.py
```

使用PyInstaller生成独立可执行文件：

```bash
pyinstaller --onefile --windowed --manifest resolution_gui.manifest resolution_tool.py
```

## 

## 注意事项 / Notes
1. 首次运行需要允许管理员权限
2. 修改分辨率可能导致屏幕短暂黑屏
3. 部分老旧显示器可能不支持高刷新率
4. 建议在更改分辨率前关闭全屏应用程序
5. 需求比较个性化，所以在别的机器上测试过，如果使用有问题可以提issue

## 贡献 / Contributing
欢迎提交Issue和Pull Request：
- 报告问题请包含操作系统版本和显示器型号
- 新功能建议请描述使用场景

Welcome to submit issues and PRs:
- Include OS version and monitor model when reporting issues
- Describe usage scenarios for feature requests

## 许可证 / License
[MIT](LICENSE) © flymetothemars
