# Run in a shell with: scrapy shell

fetch("https://www.upc.edu/")
print(response.text)
response.css("img").extract_first()
response.css("a").extract_first()