# World Access Bench

面向视频编辑结果的物理评测数据构建项目。当前版本固定了输入、任务和场景分组划分，供服务器执行生成与自动标注。

**当前是服务器输入版本，不是已完成的评测器训练集。正式模型输出为 0 条，正式物理标签为 0 条。**

| 划分 | 源视频 | 场景组 | 编辑任务 | 计划生成结果 |
|---|---:|---:|---:|---:|
| 训练 | 48 | 38 | 135 | 810 |
| 验证 | 9 | 6 | 23 | 138 |
| 测试 | 40 | 32 | 119 | 714 |
| 合计 | 97 | 76 | 277 | 1,662 |

每任务六个自然编辑候选：MiniMax-H3-Base-Ref2VA、Wan2.1-T2V-1.3B + FlowEdit、Wan2.1-T2V-1.3B + FlowAlign，各用两个种子。另含 194 条慢放/冻结诊断视频；诊断视频和历史局部程序标签不得自动作为正式物理负例。

## 取得完整输入

Git 保存任务、划分、协议、证据索引和脚本。MP4 与历史证据图保存在 Release 的两个数据包中，文件大小及 SHA-256 见 [release-assets.json](release-assets.json)。发布者上传资产后运行：

```bash
python3 tools/download_data.py
python3 World_Bench_Server_Inputs/tools/verify_inputs.py
```

尚未发布 Release，或已经下载两个 ZIP 时，可直接从本地目录恢复：

```bash
python3 tools/download_data.py --archive-dir /path/to/archives
python3 World_Bench_Server_Inputs/tools/verify_inputs.py
```

脚本先校验全部压缩包，再解压；现有同名文件内容不同会停止，防止覆盖修改。私有仓库请先通过已登录的 GitHub 工具下载资产，然后使用本地模式。

## 在服务器继续

阅读 [START_HERE.md](World_Bench_Server_Inputs/START_HERE.md) 和 [SERVER_PLAN.md](World_Bench_Server_Inputs/SERVER_PLAN.md)。依据服务器真实模型路径、代码版本和权重补齐 `generation/backends.json`，执行生成、双路 AI 标注、证据复查及验收，之后才能构建 `final/train.jsonl`、`validation.jsonl`、`test.jsonl`。

生成计划不能当作已完成训练样本；未评估字段保留空值；证据不足不能标为物理失败。AI 标签需保留来源，不得称为人工真值。ReCamMaster 可用于独立机位实验，当前不属于六个正式对象编辑候选。

源视频来源、排除记录和历史审查记录见 `sources.jsonl` 与 `provenance/`；第三方视频和代码仍适用各自原始条款，本仓库不重新授予其许可。历史记录中的工作区路径只用于追溯，服务器执行使用当前相对路径。

## 发布布局

- Git：本目录的文本、清单、协议和脚本。
- Release `inputs-2026-10-25`：`World_Bench_Server_Inputs_Main.zip` 与 `World_Bench_Server_Inputs_Diagnostic_Videos.zip`，合计约 627 MB。
- 数据状态：[PACKAGE_STATUS.json](World_Bench_Server_Inputs/PACKAGE_STATUS.json)。

发布操作说明见 [PUBLISH.md](PUBLISH.md)。
