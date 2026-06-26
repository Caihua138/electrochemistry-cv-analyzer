# Electrochemistry CV Analyzer

电化学循环伏安法(CV)数据自动分析工具，专门用于分析电催化反应（OER/ORR/HER）的关键参数。

## 功能特性

### 支持的反应类型
- **OER (Oxygen Evolution Reaction)**: 析氧反应
- **ORR (Oxygen Reduction Reaction)**: 氧还原反应  
- **HER (Hydrogen Evolution Reaction)**: 析氢反应

### 自动计算的参数

#### 1. 电势校正 (Potential Correction)
- 自动转换参考电极至可逆氢电极 (RHE)
- 基于Nernst方程：$$E_{RHE} = E_{ref} + E°_{ref} + 0.0592 \times \text{pH}$$
- 支持多种参考电极：Hg/HgO, Ag/AgCl, SCE等

#### 2. ORR参数计算
- **Onset Potential (起始电位)**: 电流密度达到 -0.1 mA/cm² 时的电位
- **On-Half Potential (半反应电位)**: 限制电流密度达到峰值50%时的电位
- **Limited Current Density (极限电流密度)**: 指定电位范围内的平均最��值
- **Tafel Slope (Tafel斜率)**: 对数刻度上电流-电势关系的斜率
  
#### 3. OER/HER参数计算
- **Overpotential (过电势)**: 实际电势与理论电势的差值（取绝对值）
- **Onset Potential**: 电流明显增大时的电位
- **Tafel Slope**: 自动识别线性增长区间

## 使用方法

### 安装依赖
```bash
pip install -r requirements.txt
```

### 基础用法
```python
from src.cv_analyzer import CVAnalyzer

# 初始化分析器
analyzer = CVAnalyzer(
    reaction_type='ORR',  # 'OER', 'ORR', 'HER'
    reference_electrode='Hg/HgO',
    pH=14,
    electrode_area=0.1256  # cm²
)

# 加载和分析单个文件
results = analyzer.analyze_file('data/sample.csv')
print(results)

# 批量处理
batch_results = analyzer.batch_analyze('data/')
```

### 电势校正
```python
# 使用Nernst方程校正
corrected_potential = analyzer.correct_potential(
    measured_potential=0.155,
    ref_electrode='Hg/HgO',
    pH=14
)
# 输出: 1.1 V vs RHE
```

## 数据格式

输入CSV文件应包含三列：
```
T(Seconds),E(V),I(A/cm2)
2.20E+02,1.56E-01,8.07E-06
2.20E+02,1.56E-01,7.76E-06
...
```

## 项目结构

```
electrochemistry-cv-analyzer/
├── src/
│   ├── __init__.py
│   ├── data_loader.py           # CSV/Excel数据读取
│   ├── potential_corrector.py   # 电势校正(Nernst方程)
│   ├── cv_analyzer.py           # 核心分析引擎
│   ├── parameter_calculator.py  # 参数计算(OER/ORR/HER)
│   └── plotter.py               # 数据可视化
├── tests/
│   ├── test_loader.py
│   ├── test_corrector.py
│   ├── test_analyzer.py
│   └── test_calculator.py
├── examples/
│   └── example_usage.py
├── data/
│   └── sample_orr.csv           # 示例数据
├── results/
│   └── (输出结果文件夹)
├── requirements.txt
├── README.md
└── main.py
```

## 参考信息

### Nernst方程
电势校正公式：
$$E_{RHE} = E_{measured} + E°_{ref} + \frac{0.0592}{n} \times \text{pH}$$

其中：
- $E°_{Hg/HgO}$ = 0.945 V (1M NaOH, pH=14)
- $E°_{Ag/AgCl}$ = 0.197 V (3M KCl)
- $E°_{SCE}$ = 0.241 V

### 参数定义

**ORR (Oxygen Reduction Reaction)**
- 反应类型：还原反应
- 电流符号：负值
- 电位范围：1.2 ~ 0.0 V vs RHE
- 起始电位定义：j = -0.1 mA/cm²

**OER (Oxygen Evolution Reaction)**
- 反应类型：氧化反应
- 电流符号：正值
- 电��范围：0.0 ~ 2.0 V vs RHE
- 起始电位定义：电流明显增大

**HER (Hydrogen Evolution Reaction)**
- 反应类型：还原反应
- 电流符号：负值
- 电位范围：0.0 ~ -1.0 V vs RHE
- 起始电位定义：电流明显增大

## 输出结果

分析完成后，程序生成JSON格式的结果文件：

```json
{
  "filename": "sample_orr.csv",
  "reaction_type": "ORR",
  "electrode_area_cm2": 0.1256,
  "reference_electrode": "Hg/HgO (1M NaOH)",
  "pH": 14,
  "potential_correction_V": 0.945,
  "parameters": {
    "onset_potential_V_vs_RHE": 0.95,
    "on_half_potential_V_vs_RHE": 0.75,
    "limited_current_density_mA_cm2": -5.2,
    "tafel_slope_mV_dec": 85.3
  },
  "analysis_timestamp": "2026-06-26T10:30:45"
}
```

## 许可证

MIT

## 作者

Caihua138
