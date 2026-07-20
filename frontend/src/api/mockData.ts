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
