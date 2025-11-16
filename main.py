import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
import logging

from config.config_manager import ConfigManager
from crawler.news_crawler import NewsCrawler
from analyzer.news_analyzer import NewsAnalyzer
from analyzer.frequency_analyzer import FrequencyAnalyzer
from models.news import News
from notifier.notification_manager import NotificationManager
from utils.logger import setup_logger
from utils.file_manager import FileManager

# 设置日志
logger = setup_logger(__name__)


def generate_all_news_with_content(all_news: List[News], output_dir: Path) -> str:
    """生成带正文内容的全部新闻报告"""
    
    # 按平台分组
    platform_news = {}
    for news in all_news:
        platform = news.source
        if platform not in platform_news:
            platform_news[platform] = []
        platform_news[platform].append(news)
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全部新闻内容 - TrendRadar</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 28px;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
            padding: 15px;
            background: #f7fafc;
            border-radius: 8px;
            flex-wrap: wrap;
        }}
        .stat-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}
        .platform-section {{
            margin: 30px 0;
            padding: 20px;
            background: #f9fafb;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .platform-title {{
            font-size: 20px;
            color: #1a202c;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .news-count {{
            background: #667eea;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 14px;
        }}
        .news-card {{
            background: white;
            border-radius: 8px;
            margin: 15px 0;
            border: 1px solid #e2e8f0;
            overflow: hidden;
            transition: all 0.3s;
        }}
        .news-card:hover {{
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
        }}
        .news-header {{
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            cursor: pointer;
            background: linear-gradient(to right, #f8f9fa, #ffffff);
            transition: background 0.3s;
        }}
        .news-header:hover {{
            background: linear-gradient(to right, #e9ecef, #f8f9fa);
        }}
        .news-rank {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: bold;
            min-width: 50px;
            text-align: center;
            font-size: 16px;
        }}
        .news-rank.top {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        .news-title-area {{
            flex: 1;
        }}
        .news-title {{
            color: #2d3748;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .news-meta {{
            display: flex;
            gap: 15px;
            font-size: 13px;
            color: #718096;
        }}
        .news-hot {{
            color: #f56565;
            font-weight: bold;
        }}
        .expand-icon {{
            color: #667eea;
            font-size: 20px;
            transition: transform 0.3s;
        }}
        .news-card.expanded .expand-icon {{
            transform: rotate(180deg);
        }}
        .news-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.5s ease-out;
            background: #ffffff;
        }}
        .news-card.expanded .news-content {{
            max-height: 2000px;
            transition: max-height 0.5s ease-in;
        }}
        .news-body {{
            padding: 20px;
            border-top: 1px solid #e2e8f0;
        }}
        .news-text {{
            color: #4a5568;
            line-height: 1.8;
            font-size: 15px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .news-link {{
            display: inline-block;
            margin-top: 15px;
            padding: 8px 16px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 14px;
            transition: all 0.3s;
        }}
        .news-link:hover {{
            background: #764ba2;
            transform: translateX(5px);
        }}
        .filter-bar {{
            margin: 20px 0;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            padding: 10px 18px;
            background: white;
            border: 2px solid #667eea;
            color: #667eea;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
            font-weight: 500;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: #667eea;
            color: white;
        }}
        .expand-all-btn {{
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.3s;
            margin-left: auto;
        }}
        .expand-all-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📰 全部新闻内容</h1>
        <p style="color: #718096; margin-top: 10px;">
            生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 点击新闻卡片查看详情
        </p>
        
        <div class="stats">
            <div class="stat-item">
                <span>📊 新闻总数:</span>
                <span class="stat-number">{len(all_news)}</span>
            </div>
            <div class="stat-item">
                <span>🏢 平台数量:</span>
                <span class="stat-number">{len(platform_news)}</span>
            </div>
            <button class="expand-all-btn" onclick="toggleAll()">
                <span id="toggle-text">展开全部</span>
            </button>
        </div>
        
        <div class="filter-bar">
            <button class="filter-btn active" onclick="showAll()">全部平台</button>
"""
    
    # 添加平台筛选按钮
    for platform in platform_news.keys():
        html_content += f'            <button class="filter-btn" onclick="filterPlatform(\'{platform}\')">{platform}</button>\n'
    
    html_content += "        </div>\n"
    
    # 生成每个平台的新闻卡片
    for platform, news_list in sorted(platform_news.items(), key=lambda x: len(x[1]), reverse=True):
        html_content += f"""
        <div class="platform-section" data-platform="{platform}">
            <div class="platform-title">
                🔥 {platform}
                <span class="news-count">{len(news_list)} 条</span>
            </div>
"""
        
        # 按排名排序
        sorted_news = sorted(news_list, key=lambda x: x.rank if x.rank else 999)
        
        for idx, news in enumerate(sorted_news):
            rank_class = "top" if news.rank and news.rank <= 10 else ""
            rank_text = f"#{news.rank}" if news.rank else "—"
            hot_text = f"🔥 {news.hot}" if news.hot else ""
            
            # 提取新闻描述（优先使用 desc，其次 content，最后显示默认文本）
            content = ""
            if hasattr(news, 'desc') and news.desc:
                content = news.desc
            elif hasattr(news, 'content') and news.content:
                content = news.content
            else:
                content = "暂无详细内容，请点击下方链接查看原文"
            
            # 转义 HTML 特殊字符
            content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            title = news.title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            html_content += f"""
            <div class="news-card" id="card-{platform}-{idx}">
                <div class="news-header" onclick="toggleCard('{platform}-{idx}')">
                    <span class="news-rank {rank_class}">{rank_text}</span>
                    <div class="news-title-area">
                        <div class="news-title">{title}</div>
                        <div class="news-meta">
                            <span>📅 {news.pub_date or '未知时间'}</span>
                            <span class="news-hot">{hot_text}</span>
                        </div>
                    </div>
                    <span class="expand-icon">▼</span>
                </div>
                <div class="news-content">
                    <div class="news-body">
                        <div class="news-text">{content}</div>
                        <a href="{news.url}" target="_blank" class="news-link">
                            🔗 查看原文
                        </a>
                    </div>
                </div>
            </div>
"""
        
        html_content += "        </div>\n"
    
    # 添加 JavaScript 交互功能
    html_content += """
    <script>
        // 切换单个卡片
        function toggleCard(id) {
            const card = document.getElementById('card-' + id);
            card.classList.toggle('expanded');
        }
        
        // 展开/收起全部
        let allExpanded = false;
        function toggleAll() {
            const cards = document.querySelectorAll('.news-card');
            const button = document.getElementById('toggle-text');
            
            allExpanded = !allExpanded;
            
            cards.forEach(card => {
                if (allExpanded) {
                    card.classList.add('expanded');
                } else {
                    card.classList.remove('expanded');
                }
            });
            
            button.textContent = allExpanded ? '收起全部' : '展开全部';
        }
        
        // 显示所有平台
        function showAll() {
            document.querySelectorAll('.platform-section').forEach(el => {
                el.style.display = 'block';
            });
            setActiveButton(0);
        }
        
        // 筛选平台
        function filterPlatform(platform) {
            document.querySelectorAll('.platform-section').forEach(el => {
                if (el.dataset.platform === platform) {
                    el.style.display = 'block';
                } else {
                    el.style.display = 'none';
                }
            });
            
            const buttons = document.querySelectorAll('.filter-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        function setActiveButton(index) {
            const buttons = document.querySelectorAll('.filter-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            buttons[index].classList.add('active');
        }
    </script>
</body>
</html>
"""
    
    # 保存文件
    all_news_file = output_dir / "all_news_content.html"
    with open(all_news_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"✅ 带内容的全部新闻报告已生成: {all_news_file}")
    return str(all_news_file)


async def main():
    """主函数"""
    try:
        logger.info("=" * 50)
        logger.info("TrendRadar 热点新闻监控系统启动")
        logger.info("=" * 50)
        
        # 加载配置
        config = ConfigManager()
        
        # 检查是否启用爬虫
        if not config.get_crawler_config().get("enable_crawler", True):
            logger.warning("爬虫功能已禁用，程序退出")
            return
        
        # 初始化组件
        file_manager = FileManager()
        output_dir = file_manager.get_output_dir()
        
        # 创建爬虫
        crawler = NewsCrawler(config)
        
        # 爬取新闻
        logger.info("开始爬取新闻...")
        all_news = await crawler.crawl_all()
        
        if not all_news:
            logger.warning("未获取到任何新闻，程序退出")
            return
        
        logger.info(f"成功爬取 {len(all_news)} 条新闻")
        
        # 生成带内容的全部新闻报告
        logger.info("生成全部新闻内容页面...")
        generate_all_news_with_content(all_news, output_dir)
        
        # 初始化分析器
        frequency_analyzer = FrequencyAnalyzer(config)
        news_analyzer = NewsAnalyzer(config)
        
        # 加载频率词
        frequency_words = frequency_analyzer.load_frequency_words()
        if not frequency_words:
            logger.warning("未配置频率词，将生成全部新闻报告")
        else:
            logger.info(f"已加载 {len(frequency_words)} 个频率词")
        
        # 分析新闻
        logger.info("开始分析新闻...")
        hot_news = news_analyzer.analyze(all_news, frequency_words)
        
        logger.info(f"匹配到 {len(hot_news)} 条热点新闻")
        
        # 生成报告
        report_mode = config.get_report_config().get("mode", "current")
        logger.info(f"当前报告模式: {report_mode}")
        
        # 生成 HTML 报告
        from report.report_generator import ReportGenerator
        report_generator = ReportGenerator(config)
        
        if report_mode == "daily":
            # 日报模式
            report_file = report_generator.generate_daily_report(hot_news, all_news, output_dir)
            logger.info(f"日报已生成: {report_file}")
            
        elif report_mode == "current":
            # 当前榜单模式
            report_file = report_generator.generate_current_report(hot_news, all_news, output_dir)
            logger.info(f"当前榜单已生成: {report_file}")
            
        elif report_mode == "incremental":
            # 增量模式
            report_file = report_generator.generate_incremental_report(hot_news, all_news, output_dir)
            logger.info(f"增量报告已生成: {report_file}")
        
        else:
            logger.warning(f"未知的报告模式: {report_mode}，使用默认 current 模式")
            report_file = report_generator.generate_current_report(hot_news, all_news, output_dir)
        
        # 发送通知
        if config.get_notification_config().get("enable_notification", False):
            logger.info("开始发送通知...")
            notification_manager = NotificationManager(config)
            await notification_manager.send_notifications(hot_news, report_file)
            logger.info("通知发送完成")
        else:
            logger.info("通知功能已禁用，跳过发送")
        
        logger.info("=" * 50)
        logger.info("TrendRadar 运行完成")
        logger.info("=" * 50)
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # 运行主程序
    asyncio.run(main())
