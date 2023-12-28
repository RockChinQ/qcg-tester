# qcg-tester
QChatGPT 测试套件

## 环境变量

```
TEST_DIRS 测试目录列表，以:分隔
BRANCH 分支名称
COMMIT 提交哈希
OPENAI_API_KEY OpenAI API Key
OPENAI_REVERSE_PROXY OpenAI API 反向代理
```

## 本地运行

```bash
pip install -r requirements.txt
```

设置以上的环境变量，若要进行所有测试，把`TEST_DIRS`设置为`src`。

运行：

```bash
python main.py
```

测试报告将输出在控制台。  
覆盖率报告生成在`report/coverage`目录下。
