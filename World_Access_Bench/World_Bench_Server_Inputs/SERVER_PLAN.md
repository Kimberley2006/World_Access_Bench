# 固定的服务器执行计划

## 1. 输入与后端绑定

输入清单是tasks.jsonl、sources.jsonl、generation/jobs.jsonl及splits目录。后台模型固定为MiniMax-H3-Base-Ref2VA、Wan2.1-T2V-1.3B+FlowEdit、Wan2.1-T2V-1.3B+FlowAlign。ReCamMaster不承担固定机位的物体时空编辑主任务。

H3使用原版Ref2VA，不加入其他项目的target筛帧或source冻结等实验修改。Wan复用1.3B权重，需要视频编辑实现和兼容的权重格式。公开参考：

- https://github.com/MiniMax-AI/MiniMax-H3
- https://github.com/KyujinHan/Awesome-Training-Free-WAN2.1-Editing

服务器应记录实际checkout commit和checkpoint SHA；这些地址只是实现来源，不代表仓库安装或模型适配已经完成。代码是否支持长序列、GPU内存预算和当前依赖需在服务器确认。公开Wan示例存在固定16 FPS导出，须改为遵守明确的时间映射。

## 2. 批量生成

每任务每方法两个种子，共1662个自然编辑候选。source描述只能根据源片；target描述准确表达任务，不能补造事件或放宽时间、位置要求。给所有方法相同的公开任务信息，记录提示转换。

每次运行保存原任务ID、方法、种子、实际参数、输出视频、哈希、宽高、帧数、实际PTS、时长和运行成本。保留成功和失败输出，不凭主观质量挑最好一次。错误和不支持项单独记录；输出失败不等于物理违规。原样本不修改对照及慢放/冻结只进入diagnostics。

生成状态：planned_not_generated → running → generated / execution_error / unsupported。生成完成不等于标注完成。现有jobs里的planned_output_path是目标路径，actual_video_path为空时文件并不存在。

## 3. 逐条件自动标注

按照protocols/ANNOTATION_PROTOCOL.md，两套独立标注流程检查实际源—结果视频对。方法身份、随机种子、已知变体配方、其他标注答案对首次AI判断隐藏。程序测量只提供可验证的辅助证据，不能仅由文件名或生成方法生成物理标签。

各条件覆盖指令实现、内容保留、物理规则、时间连贯性。保存所有原始判断与证据，复查分歧。无法解决的条件明确登记uncertain及原因，不能填充成负例。物理上不适用的规则使用not_applicable，不强行标通过。

## 4. 覆盖与补采

统计每条物理规则、任务类别、生成方法和split上的可判定率、通过/违规/无法判断分布。训练集缺少可判定正/负样本时可以按预先登记的策略补采，并使用新的job_id保留过程。验证/测试不根据成功或失败结果挑样本或平衡比例。不要在测试集调标注阈值。

如果某规则没有足够可判定样本，明确报告该规则未形成有效训练/评测覆盖；不得仅为达到文件数量宣布完成。不能把粗糙扰动识别表现解释为物理规律理解。

## 5. 最终验收与导出

必须先通过：所有正式条目有可解码文件和对应哈希；任务版本一致；所有必需条件已经判断（没有尚未检查的null）；uncertain/not_applicable有理由；规则适用性与判定一致；事件区间在实际结果PTS范围内；生成错误不混入物理负例；源场景和内容重复没有跨划分交叉；生成配方和参考答案没有泄漏进模型输入。

最终输出final/train.jsonl、validation.jsonl、test.jsonl和dataset_report.json。每条保留source/result路径、任务条件、逐条件标签、证据和监督掩码；各任务分开统计，不用单一总分隐藏缺失。生成方法、诊断配方、违规区间与AI参考理由只能作为审计/标签，不是评测器输入。

数据集定义为AI silver。测试结果衡量与自动参考的一致性；没有人工金标或可独立验证物理状态时，不宣称人工物理判断准确率。既有源场景分组隔离不代表底模预训练或历史调参污染已排除。
