# ACMC_Oracle

ACMC_Oracle 是一个基于图结构传播、代表性排序与人机交互约束投票的聚类实验项目。

当前项目主入口为 `run_ACMC.py`，支持：

- 常规批处理流程
- 半异步流程开关 `use_asy`
- 置信度更新开关 `isUpdate`

## 项目结构

```text
ACMC_Oracle/
├── a_DMCons.py
├── b_ranking_allocation.py
├── c_neighborhood_initialization.py
├── d_influence_model_propagation.py
├── e_neighborhood_learning.py
├── run_ACMC.py
├── ensemble/
│   ├── a_pre_cluster.py
│   ├── b_construct_query_list.py
│   ├── c_iteration_stage_user_vote.py
│   ├── c_iteration_stage_user_vote_asy.py
│   └── user.py
├── datasets/
└── result/
```

## 运行环境

- Python `3.10` 或 `3.11`
- 建议使用虚拟环境 `venv`

## 需要安装的包

运行 `run_ACMC.py` 及其依赖模块时，实际需要的第三方包如下：

- `numpy`
- `scipy`
- `scikit-learn`
- `networkx`
- `pandas`
- `matplotlib`

其中：

- `numpy`：数值计算、扰动矩阵、统计计算
- `scipy`：欧氏距离计算
- `scikit-learn`：`NearestNeighbors`、`LabelEncoder`、`adjusted_rand_score`
- `networkx`：图结构构建与遍历
- `pandas`：被 `a_DMCons.py` 导入
- `matplotlib`：被 `a_DMCons.py` 导入

标准库模块如 `csv`、`os`、`math`、`threading`、`time`、`random` 无需额外安装。

## 安装方式

### 1. 创建虚拟环境

```bash
python -m venv .venv
```

Windows 激活：

```bash
.venv\Scripts\activate
```

### 2. 安装依赖

```bash
pip install numpy scipy scikit-learn networkx pandas matplotlib
```

如果你希望一次性安装，也可以自行创建 `requirements.txt`，内容可写为：

```txt
numpy
scipy
scikit-learn
networkx
pandas
matplotlib
```

然后执行：

```bash
pip install -r requirements.txt
```

## 如何运行

主运行文件：

```bash
python run_ACMC.py
```

当前 `run_ACMC.py` 默认入口参数位于文件末尾：

```python
if __name__ == '__main__':
    output_path = 'result/'
    dataset_source, repetitions_times = 'banknote', 1

    run_ACMC(
        output_path,
        'ACMC',
        dataset_source,
        repetitions_times,
        error_span=0.00,
        min_users_n=1,
        max_users_n=1,
        isUpdate=True,
        use_asy=False
    )
```

## `run_ACMC` 参数说明

```python
run_ACMC(
    output_path,
    algo_name,
    dataset_source,
    repetitions_times,
    error_span,
    min_users_n,
    max_users_n,
    isUpdate=True,
    use_asy=False
)
```

- `output_path`：结果输出根目录
- `algo_name`：算法名称占位参数，当前不会参与结果目录命名
- `dataset_source`：数据目录名称，例如 `banknote`、`haberman`、`k_test`
- `repetitions_times`：重复实验次数
- `error_span`：用户统一错误率
- `min_users_n`：每次约束查询最少分配用户数
- `max_users_n`：每次约束查询最多分配用户数
- `isUpdate`：是否开启置信度更新机制
- `use_asy`：是否启用半异步版本

## 数据目录说明

当前代码会从以下目录读取数据：

```text
datasets/<dataset_source>/
```

例如：

- `datasets/banknote/banknote.csv`
- `datasets/haberman/haberman.csv`
- `datasets/k_test/*.csv`

请注意：

- 当前仓库中同时存在 `dataset/` 和 `datasets/`
- `run_ACMC.py` 现在使用的是 `datasets/`
- 如果你准备运行某个数据源，请确认对应文件已经放在 `datasets/<dataset_source>/` 下

## 输出结果

结果默认输出到：

```text
result/26_07_02/<dataset_source>/
```

每个数据集下会包含：

- 每次实验的 `*_result.csv`
- 运行时间文件 `time/*_runtime.csv`

## 核心流程

算法整体流程如下：

1. 从数据文件读取特征与标签
2. 对数据加入极小扰动
3. 构建骨架图并计算代表性排序
4. 初始化邻域
5. 传播得到预测标签
6. 基于不确定性选择待查询点
7. 通过用户投票更新邻域
8. 重复迭代直到结束

如果 `use_asy=True`，则在投票阶段启用半异步流程。

如果 `isUpdate=False`，则关闭用户置信度更新，仅保留固定用户错误率行为。

## 常见问题

### 1. 运行时报找不到数据文件

请检查：

- `dataset_source` 是否写对
- 数据是否放在 `datasets/<dataset_source>/`

### 2. 运行时报缺少依赖

请确认已安装：

```bash
pip install numpy scipy scikit-learn networkx pandas matplotlib
```

### 3. 如何切换半异步版本

把：

```python
use_asy=False
```

改成：

```python
use_asy=True
```

### 4. 如何关闭置信度更新

把：

```python
isUpdate=True
```

改成：

```python
isUpdate=False
```

## 说明

当前 README 以当前仓库中的实际代码结构和 `run_ACMC.py` 为准。
