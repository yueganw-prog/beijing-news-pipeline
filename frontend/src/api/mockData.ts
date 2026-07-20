import type { Article, ArticleDetail, StatsBySource, PipelineRun } from "@/types";

function ago(hours: number, minutes = 0): string {
  const d = new Date(Date.now() - hours * 3600000 - minutes * 60000);
  return d.toISOString();
}

export const mockArticles: Article[] = [
  {
    id: 1, source: "36氪", category: "tech", title: "字节跳动发布豆包大模型3.0，参数规模达万亿级别",
    url: "#", author: "张颖", summary: "字节跳动旗下豆包大模型发布第三代版本，在推理、代码生成和多模态能力上全面提升，部分基准测试超越GPT-4o。",
    published_at: ago(2, 30), fetched_at: ago(2),
  },
  {
    id: 2, source: "虎嗅", category: "tech", title: "小米汽车SU7月交付突破2万辆，产能爬坡超预期",
    url: "#", author: "李想", summary: "小米集团宣布SU7纯电轿车8月交付量达到21,358辆，连续第三个月创出新高，北京亦庄工厂双班制产能利用率达到95%。",
    published_at: ago(3), fetched_at: ago(2, 50),
  },
  {
    id: 3, source: "IT之家", category: "tech", title: "华为发布鸿蒙PC操作系统，打造全场景生态闭环",
    url: "#", author: "玄隐", summary: "华为正式发布HarmonyOS for PC版本，打通手机、平板、PC之间的应用生态，首批搭载MateBook X Pro 2026款。",
    published_at: ago(5), fetched_at: ago(4, 30),
  },
  {
    id: 4, source: "新浪财经", category: "finance", title: "央行宣布降准50个基点，释放长期流动性约1.2万亿",
    url: "#", author: "王晓", summary: "中国人民银行决定下调金融机构存款准备金率0.5个百分点，这是年内第二次降准，旨在支持实体经济回升向好。",
    published_at: ago(1, 15), fetched_at: ago(1),
  },
  {
    id: 5, source: "第一财经", category: "finance", title: "北京证券交易所新政：降低投资者准入门槛至20万元",
    url: "#", author: "陈晨", summary: "北交所宣布将个人投资者准入门槛从50万元下调至20万元，同时取消机构投资者交易限制，预计将带来约800万新增合格投资者。",
    published_at: ago(4, 20), fetched_at: ago(4),
  },
  {
    id: 6, source: "经济观察报", category: "finance", title: "A股成交额突破1.5万亿，半导体板块领涨",
    url: "#", author: "刘明", summary: "今日沪深两市成交额达1.53万亿元，较前一交易日放量约32%。半导体、人工智能板块涨幅居前，科创50指数涨超3%。",
    published_at: ago(6), fetched_at: ago(5, 45),
  },
  {
    id: 7, source: "新京报", category: "local", title: "北京地铁13号线扩能提升工程全面开工，预计2028年通车",
    url: "#", author: "张强", summary: "北京地铁13号线拆分扩能工程进入全面施工阶段，拆分后将形成13A线和13B线，新增车站15座，日客运能力提升60%。",
    published_at: ago(3, 45), fetched_at: ago(3, 30),
  },
  {
    id: 8, source: "北京日报", category: "local", title: "北京市发布人工智能产业发展三年行动计划",
    url: "#", author: "李华", summary: "北京市经信局发布《北京市人工智能产业发展三年行动计划(2026-2028)》，提出到2028年AI核心产业规模突破5000亿元。",
    published_at: ago(7), fetched_at: ago(6, 50),
  },
  {
    id: 9, source: "北京商报", category: "local", title: "大兴国际机场年旅客吞吐量突破1.2亿人次",
    url: "#", author: "赵磊", summary: "北京大兴国际机场自投运以来年旅客吞吐量首次突破1.2亿人次大关，国际及地区航线恢复至疫情前水平的95%。",
    published_at: ago(8, 10), fetched_at: ago(8),
  },
  {
    id: 10, source: "36氪", category: "tech", title: "百度Apollo无人驾驶出租车在京运营里程突破1000万公里",
    url: "#", author: "罗辑", summary: "百度Apollo宣布其萝卜快跑无人驾驶出租车在北京累计运营里程突破1000万公里，安全记录良好，计划年内新增300辆运营车辆。",
    published_at: ago(9), fetched_at: ago(8, 30),
  },
  {
    id: 11, source: "虎嗅", category: "tech", title: "深度解析：AI Agent如何重塑企业SaaS采购流程",
    url: "#", author: "黄渊普", summary: "随着大模型能力的提升，AI Agent正在从概念走向落地。本文深入分析AI Agent在企业软件即服务（SaaS）采购环节的实际应用场景。",
    published_at: ago(10), fetched_at: ago(9, 45),
  },
  {
    id: 12, source: "第一财经", category: "finance", title: "北京楼市新政满月：二手房网签量环比增长45%",
    url: "#", author: "陈晨", summary: "北京5·17楼市新政实施满月，全市二手房网签量达18,235套，环比增长45%，同比增长12%，市场活跃度明显回升。",
    published_at: ago(11), fetched_at: ago(10, 55),
  },
  {
    id: 13, source: "北京日报", category: "local", title: "中关村论坛2026：聚焦量子计算与生命科学交叉前沿",
    url: "#", author: "李华", summary: "2026中关村论坛年会今日开幕，来自全球60多个国家和地区的科学家、企业家参会，共同探讨量子计算在药物研发中的应用前景。",
    published_at: ago(14), fetched_at: ago(13, 30),
  },
  {
    id: 14, source: "新浪财经", category: "finance", title: "数字人民币跨境支付试点扩至20个'一带一路'国家",
    url: "#", author: "王晓", summary: "中国人民银行宣布数字人民币跨境支付试点进一步扩大至20个共建'一带一路'国家，支持跨境贸易结算和投融资场景。",
    published_at: ago(15), fetched_at: ago(14, 40),
  },
  {
    id: 15, source: "新京报", category: "local", title: "北京城市副中心三大文化建筑年底对外开放",
    url: "#", author: "张强", summary: "位于北京城市副中心的城市图书馆、大运河博物馆、城市剧院三大标志性文化建筑将于今年12月正式对公众开放。",
    published_at: ago(16), fetched_at: ago(15, 20),
  },
  // Batch 2 — more articles for richer demo
  {
    id: 16, source: "36氪", category: "tech", title: "OpenAI竞争对手Anthropic获新一轮融资，估值突破800亿美元",
    url: "#", author: "张颖", summary: "据知情人士透露，AI初创公司Anthropic正进行新一轮融资，估值将突破800亿美元，较上一轮翻倍。",
    published_at: ago(17), fetched_at: ago(16, 30),
  },
  {
    id: 17, source: "虎嗅", category: "tech", title: "拼多多Temu在东南亚市场份额超越Shopee，成为第一大电商平台",
    url: "#", author: "黄渊普", summary: "据最新数据显示，拼多多旗下跨境电商平台Temu在东南亚六国的月活用户数已达2.3亿，市场份额首次超越Shopee。",
    published_at: ago(18), fetched_at: ago(17, 45),
  },
  {
    id: 18, source: "IT之家", category: "tech", title: "苹果Vision Pro 2或将支持眼动追踪输入和裸手手势识别",
    url: "#", author: "玄隐", summary: "供应链消息称苹果正在开发第二代Vision Pro头显，将大幅减轻重量并引入全新交互方式。",
    published_at: ago(20), fetched_at: ago(19, 30),
  },
  {
    id: 19, source: "新浪财经", category: "finance", title: "证监会主席：全面推行注册制改革取得阶段性成果",
    url: "#", author: "刘明", summary: "中国证监会主席在2026金融街论坛年会上表示，资本市场注册制改革三年来成效显著。",
    published_at: ago(21), fetched_at: ago(20, 30),
  },
  {
    id: 20, source: "第一财经", category: "finance", title: "全球央行数字货币竞赛加速：已有130个国家开展CBDC研究",
    url: "#", author: "陈晨", summary: "国际清算银行最新报告显示，全球已有130个国家和地区开展央行数字货币研究或试点工作。",
    published_at: ago(22), fetched_at: ago(21, 45),
  },
  {
    id: 21, source: "经济观察报", category: "finance", title: "北向资金连续12日净流入，外资看好中国资产",
    url: "#", author: "王晓", summary: "截至今日收盘，北向资金已连续12个交易日净流入，累计净买入额超过800亿元。",
    published_at: ago(23), fetched_at: ago(22, 30),
  },
  {
    id: 22, source: "新京报", category: "local", title: "北京南站改造工程启动：新增城际快速通道",
    url: "#", author: "张强", summary: "北京南站启动为期18个月的扩能改造工程，将新增京津城际快速通道和智能导航系统。",
    published_at: ago(24), fetched_at: ago(23, 30),
  },
  {
    id: 23, source: "北京日报", category: "local", title: "北京空气质量连续200天达优良标准，创10年最佳纪录",
    url: "#", author: "李华", summary: "北京市生态环境局宣布截至7月19日全市空气质量优良天数已达200天，PM2.5平均浓度同比下降12%。",
    published_at: ago(25), fetched_at: ago(24, 30),
  },
  {
    id: 24, source: "北京商报", category: "local", title: "北京SKP年销售额突破300亿元，蝉联全球店王",
    url: "#", author: "赵磊", summary: "北京SKP 2026财年销售额突破300亿元人民币，连续第五年蝉联全球百货商场销售额冠军。",
    published_at: ago(26), fetched_at: ago(25, 30),
  },
  {
    id: 25, source: "36氪", category: "tech", title: "人形机器人公司Figure AI估值突破500亿美元",
    url: "#", author: "罗辑", summary: "Figure AI完成新一轮50亿美元融资，由微软和英伟达联合领投，其人形机器人已进入多家汽车工厂试运行。",
    published_at: ago(28), fetched_at: ago(27, 30),
  },
  {
    id: 26, source: "虎嗅", category: "tech", title: "面试官指南：2026年前端工程师必备技能图谱",
    url: "#", author: "黄渊普", summary: "Vue 3 + TypeScript + Pinia已成为国内前端主流技术栈，掌握现代CSS和响应式设计也是必备技能。",
    published_at: ago(30), fetched_at: ago(29, 30),
  },
  {
    id: 27, source: "新浪财经", category: "finance", title: "人民币汇率创年内新高，离岸人民币升破6.85",
    url: "#", author: "刘明", summary: "受美联储降息预期和中美关系缓和影响，离岸人民币兑美元汇率升破6.85关口，创2026年以来新高。",
    published_at: ago(32), fetched_at: ago(31, 30),
  },
  {
    id: 28, source: "北京日报", category: "local", title: "北京冬奥场馆赛后利用：冰丝带变身全民健身中心",
    url: "#", author: "李华", summary: "国家速滑馆'冰丝带'完成赛后改造，新增篮球、羽毛球、攀岩等全民健身设施，日均接待市民超3000人次。",
    published_at: ago(34), fetched_at: ago(33, 30),
  },
  {
    id: 29, source: "IT之家", category: "tech", title: "微软发布Windows 12预览版：全面集成AI助手Copilot",
    url: "#", author: "玄隐", summary: "微软向Dev频道推送Windows 12首个公开预览版本，AI助手Copilot深度集成到系统各层级。",
    published_at: ago(36), fetched_at: ago(35, 30),
  },
  {
    id: 30, source: "第一财经", category: "finance", title: "国际金价突破2800美元/盎司，中国央行连续增持",
    url: "#", author: "陈晨", summary: "现货黄金价格突破2800美元/盎司创历史新高，中国人民银行已连续18个月增持黄金储备。",
    published_at: ago(38), fetched_at: ago(37, 30),
  },
  {
    id: 31, source: "新京报", category: "local", title: "北京胡同保护更新：前门东区试点'共生院'模式",
    url: "#", author: "张强", summary: "前门东区启动'共生院'更新模式试点，在保护胡同风貌的同时引入文创工作室和青年公寓。",
    published_at: ago(40), fetched_at: ago(39, 30),
  },
  {
    id: 32, source: "经济观察报", category: "finance", title: "2026年二季度GDP同比增长5.2%，超市场预期",
    url: "#", author: "王晓", summary: "国家统计局公布数据显示，2026年二季度国内生产总值同比增长5.2%，上半年累计增长5.3%。",
    published_at: ago(42), fetched_at: ago(41, 30),
  },
  {
    id: 33, source: "36氪", category: "tech", title: "腾讯混元大模型开源：参数规模700亿，支持128K上下文",
    url: "#", author: "张颖", summary: "腾讯宣布混元大模型全面开源，采用Apache 2.0协议，支持128K超长上下文窗口。",
    published_at: ago(44), fetched_at: ago(43, 30),
  },
  {
    id: 34, source: "北京商报", category: "local", title: "北京数字经济增加值占GDP比重突破45%",
    url: "#", author: "赵磊", summary: "北京市统计局发布数据显示，2026年上半年北京数字经济增加值占GDP比重达到45.3%。",
    published_at: ago(46), fetched_at: ago(45, 30),
  },
  {
    id: 35, source: "虎嗅", category: "tech", title: "钉钉发布AI原生办公套件：集成GPT-4级别模型",
    url: "#", author: "黄渊普", summary: "钉钉推出全新AI原生办公套件，深度集成了AI写作、智能会议纪要、自动数据分析等功能。",
    published_at: ago(48), fetched_at: ago(47, 30),
  },
];

export const mockArticleDetail: ArticleDetail = {
  id: 1,
  source: "36氪",
  category: "tech",
  title: "字节跳动发布豆包大模型3.0，参数规模达万亿级别",
  url: "#",
  author: "张颖",
  summary: "字节跳动旗下豆包大模型发布第三代版本，在推理、代码生成和多模态能力上全面提升，部分基准测试超越GPT-4o。",
  published_at: ago(2, 30),
  fetched_at: ago(2),
  content_clean: `今日，字节跳动在2026火山引擎Force大会上正式发布豆包大模型3.0系列。

豆包3.0基于全新的Transformer架构，参数规模达到万亿级别，在数学推理、代码生成、多模态理解等核心能力上实现全面突破。

据官方公布的基准测试数据，豆包3.0在MMLU-Pro（大规模多任务语言理解）评测中得分89.7，在HumanEval（代码生成）评测中得分92.4，均超越了目前业界领先的GPT-4o模型。

字节跳动AI负责人谭待表示："豆包3.0不仅仅是参数规模的简单增长，更重要的是我们在模型架构、训练方法和推理效率上进行了系统性的创新。我们采用了混合专家（MoE）架构，实际激活参数量仅为总参数量的20%，大幅降低了推理成本。"

在定价方面，豆包3.0的API调用价格仅为GPT-4o的三分之一，展示出字节跳动在大模型价格战中的决心。目前已有超过50万家企业客户通过火山引擎接入豆包大模型。

业内分析师认为，豆包3.0的发布标志着中国AI企业在通用大模型领域已经具备了与国际顶尖水平同台竞技的实力。`,
};

// Cumulative totals (pipeline running since 2026-01). Demo article list shows latest batch of 35.
export const mockStats: StatsBySource[] = [
  { source: "36氪", category: "tech", cnt: 2847, last_fetched: ago(2) },
  { source: "虎嗅", category: "tech", cnt: 2193, last_fetched: ago(2, 50) },
  { source: "IT之家", category: "tech", cnt: 3156, last_fetched: ago(4, 30) },
  { source: "新浪财经", category: "finance", cnt: 4521, last_fetched: ago(1) },
  { source: "第一财经", category: "finance", cnt: 3872, last_fetched: ago(4) },
  { source: "经济观察报", category: "finance", cnt: 2145, last_fetched: ago(5, 45) },
  { source: "新京报", category: "local", cnt: 1923, last_fetched: ago(3, 30) },
  { source: "北京日报", category: "local", cnt: 2456, last_fetched: ago(6, 50) },
  { source: "北京商报", category: "local", cnt: 1687, last_fetched: ago(8) },
];

export const mockPipelineRuns: PipelineRun[] = [
  {
    id: 156, dag_id: "beijing_news_pipeline", dag_run_id: "manual_2026-07-20T08:00",
    run_date: "2026-07-20", status: "success", total_articles: 247, dq_avg_score: 94.3,
    started_at: ago(2, 5), finished_at: ago(2),
  },
  {
    id: 155, dag_id: "beijing_news_pipeline", dag_run_id: "scheduled_2026-07-20T06:00",
    run_date: "2026-07-20", status: "success", total_articles: 189, dq_avg_score: 92.8,
    started_at: ago(4, 5), finished_at: ago(4),
  },
  {
    id: 154, dag_id: "beijing_news_pipeline", dag_run_id: "scheduled_2026-07-19T18:00",
    run_date: "2026-07-19", status: "success", total_articles: 312, dq_avg_score: 91.5,
    started_at: ago(16, 5), finished_at: ago(16),
  },
  {
    id: 153, dag_id: "beijing_news_pipeline", dag_run_id: "scheduled_2026-07-19T12:00",
    run_date: "2026-07-19", status: "success", total_articles: 278, dq_avg_score: 93.1,
    started_at: ago(22, 5), finished_at: ago(22),
  },
  {
    id: 152, dag_id: "beijing_news_pipeline", dag_run_id: "scheduled_2026-07-19T06:00",
    run_date: "2026-07-19", status: "failed", total_articles: 0, dq_avg_score: null,
    started_at: ago(28, 5), finished_at: ago(28, 2),
  },
];
