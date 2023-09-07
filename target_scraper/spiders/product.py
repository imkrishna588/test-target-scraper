import scrapy
from playwright.async_api import async_playwright
import re
import numpy as np
import time
from bs4 import BeautifulSoup
import json

class ProductSpider(scrapy.Spider):
    name = 'product'

    def __init__(self, url=None, *args, **kwargs):
        super(ProductSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]

    async def parse(self, response):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(response.url,  timeout=10000)
            time.sleep((20-10)*np.random.random()+5)
            page_content = await page.content()
            soup = BeautifulSoup(page_content, 'html.parser')

            tcin = response.url.split('-')[-1]
            upc =  re.search(r'"primary_barcode(.*?)primary_brand',str(response.body),  re.IGNORECASE | re.DOTALL).group(1).split('"')[2].replace('\\\\','')
            
            price_amount = soup.find('span',{'data-test': 'product-price'}).text
            currency = 'USD'
            description = soup.find('div',{'data-test': 'item-details-description'}).text
            bullets = soup.find('ul',{'direction': 'column'}).text
            specs = None
            ingredients = []
            
            specifications_element = await page.query_selector('text=Specifications')
            await specifications_element.click()
            
            await page.wait_for_selector('[data-test="item-details-specifications"]')
        
            specifications_element = await page.query_selector('[data-test="item-details-specifications"]')
            specifications_text = await specifications_element.inner_text()
            specifications_list = specifications_text.split('\n')

            await page.wait_for_selector('[data-test="questionsCountLink"]')
            question = await page.query_selector('[data-test="questionsCountLink"]')
            await question.click()
            
            await page.wait_for_selector('[data-test="question"]')
            question_elements = await page.query_selector_all('[data-test="question"]')
            question_data = {"questions": []}
            for question_element in question_elements:
                questions = await question_element.inner_text()
                print ('question_id ++++++++++++++++++++++++++',questions)

            yield {
            "url": response.url,
            "tcin": tcin,
            "upc": upc,
            "price_amount": price_amount,
            "currency": currency,
            "description": description,
            "specs": specs,
            "ingredients": ingredients,
            "bullets": bullets,
            "features": specifications_list
            }
                
            await browser.close()


        