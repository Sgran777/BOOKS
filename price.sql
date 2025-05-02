CREATE TABLE book_price_analysis (
    isbn VARCHAR(13) NOT NULL COMMENT '国际标准书号',
    quality VARCHAR(20) NOT NULL COMMENT '新旧程度（标准化值）',
    source VARCHAR(20) NOT NULL COMMENT '数据来源',
    title VARCHAR(255) NOT NULL COMMENT '书名',
    -- 平台维度统计
    platform_avg DECIMAL(10,2) COMMENT '该平台平均价',
    platform_min DECIMAL(10,2) COMMENT '该平台最低价',
    platform_max DECIMAL(10,2) COMMENT '该平台最高价',
    platform_std DECIMAL(10,2) COMMENT '该平台标准差',
    -- 全局综合统计
    global_avg DECIMAL(10,2) COMMENT '全平台加权平均',
    global_min DECIMAL(10,2) COMMENT '全平台最低价',
    global_max DECIMAL(10,2) COMMENT '全平台最高价',
    -- 推荐价格
    suggest_price_min DECIMAL(10,2) COMMENT '推荐价格下限',
    suggest_price_max DECIMAL(10,2) COMMENT '推荐价格上限',
    -- 元数据
    sample_count INT COMMENT '样本数量',
    source_weight DECIMAL(5,3) COMMENT '平台权重',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (isbn, quality, source) -- 复合主键
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 comment '书籍价格分析表';




# 价格算法
-- 步骤1：创建带排序的临时表
DROP TEMPORARY TABLE IF EXISTS sorted_prices;
CREATE TEMPORARY TABLE sorted_prices AS
SELECT
    isbn,
    quality,
    source,
    current_price,
    ROW_NUMBER() OVER (
        PARTITION BY isbn, quality, source
        ORDER BY current_price
    ) AS row_num,
    COUNT(*) OVER (PARTITION BY isbn, quality, source) AS total
FROM books
WHERE current_price IS NOT NULL;

-- 步骤2：计算分位数（修正HAVING子句）
DROP TEMPORARY TABLE IF EXISTS quantiles;
CREATE TEMPORARY TABLE quantiles AS
SELECT
    isbn,
    quality,
    source,
    -- 计算Q1（第25百分位）
    MAX(CASE WHEN row_num = FLOOR((total + 1) * 0.25) THEN current_price END) AS q1,
    -- 计算Q3（第75百分位）
    MAX(CASE WHEN row_num = FLOOR((total + 1) * 0.75) THEN current_price END) AS q3,
    -- 获取样本量
    MAX(total) AS sample_size
FROM sorted_prices
GROUP BY isbn, quality, source
HAVING MAX(total) >= 5;  -- 关键修正点：使用聚合函数

-- 步骤3：添加索引优化
ALTER TABLE quantiles ADD INDEX idx_quant (isbn, quality, source);

-- 步骤4：执行异常值处理
UPDATE books b
JOIN quantiles q
    ON b.isbn = q.isbn
    AND b.quality = q.quality
    AND b.source = q.source
SET b.use_flag = 10
WHERE b.current_price < (q.q1 - 1.5*(q.q3 - q.q1))
   OR b.current_price > (q.q3 + 1.5*(q.q3 - q.q1));

-- 步骤5：验证结果
SELECT
    COUNT(*) AS total_records,
    SUM(IF(current_price IS NULL, 1, 0)) AS outliers,
    ROUND(100 * SUM(IF(current_price IS NULL, 1, 0)) / COUNT(*), 2) AS outlier_ratio
FROM books;


#测试
-- 检查典型分组的计算过程
SELECT *
FROM sorted_prices
WHERE isbn = '9787040599008'
  AND quality = '全新'
  AND source = '孔夫子'
ORDER BY current_price;

-- 验证分位数计算结果
SELECT
    isbn,
    quality,
    source,
    q1,
    q3,
    q3 - q1 AS iqr,
    sample_size
FROM quantiles
where isbn = 9787040599008;



-- 创建排序临时表
CREATE TEMPORARY TABLE platform_sorted AS
SELECT
    isbn,
    quality,
    source,
    title,
    current_price,
    ROW_NUMBER() OVER (PARTITION BY isbn, quality, source ORDER BY current_price) AS row_num,
    COUNT(*) OVER (PARTITION BY isbn, quality, source) AS total
FROM books
WHERE current_price IS NOT NULL;


# 将价格表的更新算法储存为过程
DELIMITER //
CREATE PROCEDURE RefreshPriceAnalysis()
BEGIN
    # 将利用算法处理后的数据存入表中
    -- 计算平台维度统计数据
    truncate table book_price_analysis;
    INSERT INTO book_price_analysis (
        isbn, quality, source, title,
        platform_avg, platform_min, platform_max, platform_std,
        suggest_price_min, suggest_price_max,
        sample_count, source_weight
    )
    SELECT
        p.isbn,
        p.quality,
        p.source,
        MAX(p.title) AS title,
        -- 基础统计
        AVG(p.current_price) AS platform_avg,
        MIN(p.current_price) AS platform_min,
        MAX(p.current_price) AS platform_max,
        STDDEV(p.current_price) AS platform_std,
        -- 手动计算IQR范围
        MAX(CASE
            WHEN row_num = FLOOR((total+1)*0.25) THEN current_price
        END) * 0.9 AS suggest_min,
        MAX(CASE
            WHEN row_num = FLOOR((total+1)*0.75) THEN current_price
        END) * 1.1 AS suggest_max,
        COUNT(*) AS sample_count,
        CASE p.source
            WHEN '孔夫子' THEN 0.73
            WHEN '当当' THEN 0.27
        END AS source_weight
    FROM platform_sorted p
    GROUP BY p.isbn, p.quality, p.source
    HAVING COUNT(*) >= 5;

    -- 全局统计字段
    UPDATE book_price_analysis a
    JOIN (
        SELECT
            isbn,
            quality,
            SUM(platform_avg * source_weight) AS weighted_avg,
            MIN(platform_min) AS global_min,
            MAX(platform_max) AS global_max
        FROM book_price_analysis
        GROUP BY isbn, quality
    ) t USING (isbn, quality)
    SET
        a.global_avg = t.weighted_avg,
        a.global_min = t.global_min,
        a.global_max = t.global_max,
        -- 综合建议价 = 加权平均 ±10%
        a.suggest_price_min = ROUND(t.weighted_avg * 0.9, 2),
        a.suggest_price_max = ROUND(t.weighted_avg * 1.1, 2);
END //
DELIMITER ;

-- 重新生成分析数据
CALL RefreshPriceAnalysis();