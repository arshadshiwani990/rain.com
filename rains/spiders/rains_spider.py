import scrapy
import json
import html
import re
import re
class RainsSpiderSpider(scrapy.Spider):
    name = "rains_spider"
    allowed_domains = ["rains.com"]
    # start_urls = ["https://www.rains.com/collections/bags"]

    def start_requests(self):
        
        yield scrapy.Request('https://www.rains.com/collections/bags',callback=self.parse_category)
    def parse_category(self,response):


        product_links=response.xpath('//div[@class="px-4 pt-4"]//p/a/@href').extract()
        for product_link in product_links:
        
            product_link='https://www.rains.com/'+product_link
            print(product_link)
            yield scrapy.Request(product_link,callback=self.parse_product)
    
    def remove_html_tags(self,text):
    # Regular expression to match HTML tags
        clean_text = re.sub(r'<.*?>', ' ', text)
        return clean_text

    def parse_product(self, response):
        # Extract and parse JSON data from the page
        
        
        
        # Extract data between 'lsData.product' and 'window.lsData.cart'
        raw_data = response.xpath('//script[contains(text(),"lsData.product")]/text()').get()
        
        if not raw_data:
            print("No data found")
            return

        # Extract JSON part
        data = raw_data.split('lsData.product')[1].split('window.lsData.cart')[0]
        data = data.replace(' = {', '{').strip()
        
        # Clean escaped characters
        decoded_data = html.unescape(data)
        decoded_data = decoded_data.replace('\/', '/')
        
        # Remove trailing semicolons and ensure proper JSON format
        decoded_data = re.sub(r';$', '', decoded_data).strip()

        try:
            json_data = json.loads(decoded_data)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print("Data causing issue:", decoded_data)

        title=json_data.get('title')
        price=json_data.get('price')
        Vendor=json_data.get('vendor')
        variants=json_data.get('variants')
        Description=json_data.get('description')
        
        feature=response.xpath('//p[contains(text(),"Features")]/following-sibling::ul/li//text()').extract()
        feature='\n'.join(feature)
        print(feature)
        item={}
        item['RAW Title']=title
        item['Vendor']=Vendor
        item['URL']=response.url
        item['RAW Price']=round((float(price)/100),2)
        item['Description']=self.remove_html_tags(Description)
        item['feature']=self.remove_html_tags(feature)
        item['currency']=response.xpath('//meta[@property="og:price:currency"]/@content').get()
       
        
        j=1
        i=1
        variants=json_data.get('variants')
        for variant in variants:
            
            if i==1:
                
                key='Variant '+str(j)+' Name'
                item[key]=variant.get('title')
                medias=json_data.get('media')
             
                for media in medias[:10]:
                    
                    value='Image '+str(i)+' URL'
                    item[value]=media.get('src')
                    
                    value='Image '+str(i)+' alt text'
                    item[value]=media.get('alt')
            
                    i=i+1
            else:
                key='Variant '+str(j)+' Name'
                item[key]=variant.get('title')
         

                # key='Image '+str(j)+' alt text'
                key='Image '+str(j)+' url'
                item[key]=variant.get('featured_image').get('src')
                
                
                key='Image '+str(j)+' alt text'
                item[key]=variant.get('featured_image').get('alt')
                
            j=j+1
        
        yield item