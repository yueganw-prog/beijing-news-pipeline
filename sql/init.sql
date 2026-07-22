-- ============================================================
-- Beijing News Pipeline — 业务表初始化
-- 由 PostgreSQL docker-entrypoint-initdb.d 自动执行
-- ============================================================

-- 1. 文章表（核心业务数据）
CREATE TABLE IF NOT EXISTS articles (
    id              BIGSERIAL       PRIMARY KEY,
    source          VARCHAR(128)    NOT NULL,       -- 来源标识，如 36kr / huxiu / bjnews
    category        VARCHAR(64)     NOT NULL,       -- tech / finance / local
    title           TEXT            NOT NULL,
    url             TEXT            NOT NULL UNIQUE,
    author          VARCHAR(256)    DEFAULT '',
    summary         TEXT            DEFAULT '',
    content_raw     TEXT            DEFAULT '',      -- 原始正文（Markdown / HTML）
    content_clean   TEXT            DEFAULT '',      -- 清洗后纯文本
    published_at    TIMESTAMPTZ,                     -- 文章发布时间
    fetched_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    minio_bucket    VARCHAR(128),                    -- 文章归档的 MinIO bucket
    minio_key       VARCHAR(512),                    -- 文章归档的 MinIO 对象 key
    language        VARCHAR(16)     DEFAULT 'zh',
    metadata        JSONB           DEFAULT '{}'::JSONB,  -- 扩展字段（阅读量 / 标签等）
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_articles_source     ON articles (source);
CREATE INDEX idx_articles_category   ON articles (category);
CREATE INDEX idx_articles_published  ON articles (published_at DESC);
CREATE INDEX idx_articles_fetched    ON articles (fetched_at DESC);

-- 2. 数据质量结果表（每个 DAG 任务记录 DQ 打分）
CREATE TABLE IF NOT EXISTS dq_results (
    id              BIGSERIAL       PRIMARY KEY,
    dag_run_id      VARCHAR(256)    NOT NULL,       -- Airflow DAG run ID
    task_id         VARCHAR(256)    NOT NULL,       -- 任务标识
    source          VARCHAR(128)    NOT NULL,
    category        VARCHAR(64)     NOT NULL,
    total_rows      INT             DEFAULT 0,      -- 该批次文章总数
    null_title      INT             DEFAULT 0,      -- 标题为空数
    null_url        INT             DEFAULT 0,
    null_content    INT             DEFAULT 0,
    dup_url_count   INT             DEFAULT 0,      -- URL 重复数
    min_content_len INT             DEFAULT 0,      -- 最短正文长度
    avg_content_len NUMERIC(10,2)   DEFAULT 0,      -- 平均正文长度
    score           NUMERIC(5,2),                   -- 综合质量分 (0-100)
    details         JSONB           DEFAULT '{}'::JSONB,  -- 详细检查结果
    checked_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_dq_dag_run  ON dq_results (dag_run_id);
CREATE INDEX idx_dq_source   ON dq_results (source);
CREATE INDEX idx_dq_score    ON dq_results (score DESC);

-- 3. 管道运行记录表（每次 DAG 执行的状态追踪）
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id              BIGSERIAL       PRIMARY KEY,
    dag_id          VARCHAR(256)    NOT NULL DEFAULT 'beijing_news_pipeline',
    dag_run_id      VARCHAR(256)    NOT NULL UNIQUE,
    run_date        DATE            NOT NULL,       -- 业务日期
    status          VARCHAR(32)     NOT NULL DEFAULT 'running',  -- running / success / failed / partial
    started_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    finished_at     TIMESTAMPTZ,
    total_sources   INT             DEFAULT 0,      -- 计划采集源数
    success_sources INT             DEFAULT 0,      -- 成功采集源数
    total_articles  INT             DEFAULT 0,      -- 采得文章数
    dq_avg_score    NUMERIC(5,2),                   -- 本轮平均 DQ 分
    error_message   TEXT            DEFAULT '',      -- 错误信息汇总
    minio_archive   JSONB           DEFAULT '{}'::JSONB,  -- MinIO 归档路径
    metadata        JSONB           DEFAULT '{}'::JSONB,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pipeline_run_date  ON pipeline_runs (run_date DESC);
CREATE INDEX idx_pipeline_status    ON pipeline_runs (status);

-- 4. 更新时间自动触发
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_articles_updated_at') THEN
        CREATE TRIGGER trg_articles_updated_at
            BEFORE UPDATE ON articles
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_pipeline_runs_updated_at') THEN
        CREATE TRIGGER trg_pipeline_runs_updated_at
            BEFORE UPDATE ON pipeline_runs
            FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
END;
$$;

-- 5. 滚动视图：最近 7 天文章摘要（对 Metabase 友好）
CREATE OR REPLACE VIEW v_articles_last_7d AS
SELECT
    id, source, category, title, url, author,
    LEFT(content_clean, 200) AS content_excerpt,
    published_at, fetched_at, language
FROM articles
WHERE fetched_at >= NOW() - INTERVAL '7 days'
ORDER BY fetched_at DESC;

-- 6. 按源/分类统计（Metabase 可用）
CREATE OR REPLACE VIEW v_source_stats AS
SELECT
    source,
    category,
    COUNT(*)              AS article_count,
    MIN(fetched_at)       AS first_fetched,
    MAX(fetched_at)       AS last_fetched,
    AVG(LENGTH(content_clean))::INT AS avg_content_len
FROM articles
GROUP BY source, category;

-- 7. 管道运行概览视图
CREATE OR REPLACE VIEW v_pipeline_summary AS
SELECT
    run_date,
    status,
    total_sources,
    success_sources,
    total_articles,
    dq_avg_score,
    started_at,
    finished_at,
    EXTRACT(EPOCH FROM (finished_at - started_at))::INT AS duration_seconds
FROM pipeline_runs
ORDER BY run_date DESC;
