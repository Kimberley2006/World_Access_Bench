# 发布到指定仓库

目标：`https://github.com/Kimberley2006/World_Access_Bench.git`。

本目录是待提交内容；此文件不代表已经推送。使用已获该仓库写权限的 GitHub 账号操作。

1. 克隆目标仓库，检查已有内容及仓库指令；将本目录内容合入工作区。不要覆盖已有不同内容，也不要强制推送。
2. 提交并推送这些文本文件。视频和压缩包不加入 Git。
3. 安装并登录 GitHub CLI 后，在已推送的提交上创建 Release，将两个原始 ZIP 作为资产上传；若该标签已存在，先核对已有资产，不盲目替换。

```bash
gh release create inputs-2026-10-25 \
  /path/to/World_Bench_Server_Inputs_Main.zip \
  /path/to/World_Bench_Server_Inputs_Diagnostic_Videos.zip \
  --repo Kimberley2006/World_Access_Bench \
  --target <已推送的提交SHA> \
  --title 'World Access Bench: fixed server inputs' \
  --notes-file RELEASE_NOTES.md
```

4. 用新工作目录运行 `python3 tools/download_data.py`，再执行输入校验，确认远端文件可完整恢复。私有仓库使用 `gh release download` 下载两个资产，再用脚本本地模式核验。

GitHub CLI 命令中的路径和提交 SHA 必须替换成真实值。
