# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field


class BilibiliCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class VideoInfoItem(scrapy.Item):
    """视频信息"""
    col = 'video_info'
    mid = Field()   # 用户id
    aid = Field()    # av号
    bvid = Field()    # bv号
    title = Field() # 标题
    author = Field()    # 作者
    comment = Field()   # 评论数
    description = Field()   # 描述
    pic = Field()   # 封面
    play = Field()  # 播放数
    crawled_at = Field()    # 爬取时间


class CommentItem(scrapy.Item):
    """评论信息"""
    col = 'comment'
    bvid = Field()  # bv号
    reply = Field() # 评论内容
    crawled_at = Field()  # 爬取时间
