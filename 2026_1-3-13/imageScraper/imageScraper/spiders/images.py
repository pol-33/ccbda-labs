import scrapy
from urllib.parse import urljoin

class ImagesSpider(scrapy.Spider):
    name = "images"
    allowed_domains = ["www.upc.edu"]
    start_urls = ["https://www.upc.edu/en/"]
    unique_images = []

    def closed(self, cause):
        self.unique_images.sort()
        print(self.unique_images)

    def parse(self, response):
        # Extract image URLs
        for img in response.css("img"):
            image_src = img.attrib.get('src') or img.attrib.get('data-src')  # Fallback to 'data-src'
            if image_src is not None:
                full_image_url = urljoin(response.url, image_src)
                yield {
                    'img_url': full_image_url,
                    'appears_url': response.url,
                    'depth': response.meta.get('depth', 0)
                }
                if full_image_url not in self.unique_images:
                    self.unique_images.append(full_image_url)
        
        # Extract and follow hyperlinks
        for link in response.css('a::attr(href)').getall():
            # Ensure the link is absolute
            absolute_link = urljoin(response.url, link)
            # Follow the link and call the parse method recursively
            if absolute_link and absolute_link.startswith('https://'):  # Validating full link
                yield scrapy.Request(url=absolute_link, callback=self.parse)

        

    
