import scrapy
import json
from scrapy import Request, Spider
from scrapy_splash.request import SplashRequest
from bilibili_crawl.items import VideoInfoItem, CommentItem

# Splash 爬取动态渲染的视频详情页
lua_script = """
            function main(splash, args)
                assert(splash:go(args.url))
                assert(splash:wait(10))
                splash.scroll_position = {x=0, y=5000}
                assert(splash:wait(5))
                return splash:html()
            end
            """


class BiliSpiderSpider(scrapy.Spider):
    name = 'bili_spider'
    allowed_domains = ['www.bilibili.com', 'space.bilibili.com', 'api.bilibili.com']
    video_list_url = 'https://api.bilibili.com/x/space/arc/search?mid={mid}&ps=30&tid=0&pn={page}&keyword=&order=pubdate&jsonp=jsonp'
    video_detail_url = 'https://www.bilibili.com/video/{bvid}'

    def start_requests(self):
        """请求 api 生成用户投稿的视频列表"""
        mids = self.settings.get('TARGET_USER_CONFIG').keys()
        for mid in mids:
            page = self.settings.get('TARGET_USER_CONFIG').get(mid)
            start_page, end_page = page[0], page[1]
            yield Request(
                url=self.video_list_url.format(mid=mid, page=start_page),
                callback=self.parse_video_list,
                meta={'mid': mid, 'page': start_page, 'end': end_page}
            )

    def parse_video_list(self, response):
        """解析视频列表，提取视频的信息"""
        result = json.loads(response.text)
        mid = response.meta.get('mid')
        # 提取视频信息
        if result.get('data').get('list').get('vlist'):
            video_list = result.get('data').get('list').get('vlist')
            for video in video_list:
                item = VideoInfoItem()
                item['mid'] = mid
                item['aid'] = video.get('aid')
                item['bvid'] = video.get('bvid')
                item['title'] = video.get('title')
                item['author'] = video.get('author')
                item['comment'] = video.get('comment')
                item['description'] = video.get('description')
                item['pic'] = video.get('pic')
                item['play'] = video.get('play')
                yield item

                # 生成视频详情页的请求
                bvid = video.get('bvid')
                url = self.video_detail_url.format(bvid=bvid)
                yield SplashRequest(
                    url=url, callback=self.parse_video_detail,
                    endpoint='execute',
                    args={'lua_source': lua_script},
                    meta={'bvid': bvid}
                )

            # 请求下一页视频列表
            present_page = response.meta.get('page')
            end_page = response.meta.get('end')
            if present_page < end_page:
                next_page = present_page + 1
                yield Request(
                    url=self.video_list_url.format(mid=mid, page=next_page),
                    callback=self.parse_video_list,
                    meta={'mid': mid, 'page': next_page, 'end': end_page}
                )

    def parse_video_detail(self, response):
        """解析视频的评论信息"""
        reply_list = response.xpath('.//p[@class="text"]')
        bvid = response.meta.get('bvid')
        if reply_list:
            item = CommentItem()
            item_list = []
            for reply in reply_list:
                reply_item = ''.join(reply.xpath('./text()').extract()).strip()
                item_list.append(reply_item)
            item['bvid'] = bvid
            item['reply'] = item_list
            yield item
            print('>>>>>>> {bvid} 完成 <<<<<<<'.format(bvid=bvid))
        else:
            print('>>>>>>> {bvid} 失败 <<<<<<<'.format(bvid=bvid))
