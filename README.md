[依赖下载]

pip install -r requirements.txt

[运行]

python -m python_tester [品种] [策略]

品种目前支持
'BTC'
'China300'

策略
'turtle_100"

你也可以输入'turtle_[突破周期]'来自定义你的海龟策略 如
python -m python_tester China300 turtle_100

这将会运行对于China300，100高点突破的海龟策略
