# -*- coding: utf-8 -*-
import scrapy
import re
from copy import deepcopy
from pyquery import PyQuery as pq
from sunning.items import SunningItem

class SuningSpider(scrapy.Spider):
    name = 'suning'
    allowed_domains = ['suning.com']
    start_urls = ['https://book.suning.com/']

    def parse(self, response):
        # 获取大分类的分组
        div_list = response.xpath("//div[@class='menu-list']/div[@class='menu-item']")
        # 和大分类呼应的中间分类组
        div_sub_list = response.xpath("//div[@class='menu-list']/div[@class='menu-sub']")
        # print(div_sub_list)
        for div in div_list:
            item = SunningItem()
            # 大分类的名字 文学艺术、少儿、人文、
            item['parent_type'] = div.css('h3 a::text').extract_first()
            # 当前大分类的所有的中间分类的位置
            current_sub_div = div_sub_list[div_list.index(div)]

            # 获取中间分类的分组 例：文学艺术中：小说、青春文学、艺术、动漫
            p_list = current_sub_div.css('.submenu-left .submenu-item')
            # print(p_list)
            for p in p_list:
                # print(p)
                # 中间分类的名字,小说、青春文学、艺术、动漫
                # item["m_cate{}".format(p_list.index(p))] = p.xpath("./a/text()").extract_first()
                item["m_cate"] = p.xpath("./a/text()").extract_first()
                # 获取小分类中的小分组
                li_list = p.xpath("./following-sibling::ul[1]/li")
                # print(li_list)
                for li in li_list:
                    # print(li.css('a::attr(href)').extract_first())
                    # 小分类的名字
                    item["s_cate"] = li.css("a::text").extract_first()
                    # 小分类的URL地址
                    item["s_href"] = li.css("a::attr(href)").extract_first()
                    # print(item["s_href"])
                    # print(item["s_href"])

                    # 请求图书的列表页
                    yield scrapy.Request(
                        url=item["s_href"],
                        callback=self.parse_book_list,
                        # scrapy框架底层实现了多线程，所以item传递时，为避免数据覆盖错位情况，需要使用deepcopy()传递下去。
                        meta={"item": deepcopy(item)}
                    )

    def parse_book_list(self, response):
        item = response.meta['item']
        lis_list = response.css('.filter-results .clearfix li')
        for li in lis_list:
            item['book_name'] = li.css('.res-info .sell-point a::text').extract_first().strip()
            item["book_href"] = 'https:' + li.css('.res-info .sell-point a::attr(href)').extract_first()
            # print(item)
            yield scrapy.Request(
                url=item["book_href"],
                callback=self.parse_book,
                # scrapy框架底层实现了多线程，所以item传递时，为避免数据覆盖错位情况，需要使用deepcopy()传递下去。
                meta={"item": deepcopy(item)}
            )

        # next_url=response.xpath('//*[@id="nextPage"]/@href').extract_first()
        # doc=pq(response.text)
        # next_url=doc('.').attr('href')
        cur_url = 'https://list.suning.com' + response.css('#bottom_pager > a.cur + a::attr(href)').extract_first()
        # print(item)
        #print('下一页url为:',cur_url)
        # 循环该中间分类的小分组的图书列表
        yield scrapy.Request(url=cur_url, callback=self.parse_book_list, meta={"item": deepcopy(item)})

    def parse_book(self, response):  # 获取图书详细信息
        item = response.meta['item']
        # 图书价格由js生成
        # item["book_price"] = re.findall('"netPrice":"(.*?)"', response.body.decode())
        #item["book_public"] = response.css('.i-header + span::text').extract_first()
        yield item
