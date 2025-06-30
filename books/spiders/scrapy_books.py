import scrapy
from scrapy.http import Response


class ScrapyBooksSpider(scrapy.Spider):
    name = "scrapy_books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response):
        for book in response.css(".image_container a::attr(href)").getall():
            absolute_url = response.urljoin(book)
            yield scrapy.Request(absolute_url, callback=self.parse_book)

        next_page = response.css(".next").css("a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: Response):
        title = response.css("h1::text").get()

        table = {}
        rows = response.css("table.table-striped tr")
        for row in rows:
            key = row.css("th::text").get()
            value = row.css("td::text").get()
            table[key] = value

        price = float(table.get("Price (incl. tax)", "0").replace("£", ""))
        amount_in_stock = int(
            table.get("Availability", "").split()[-2].replace("(", "")
        )
        upc = table.get("UPC", "")

        rating_word = response.css("p.star-rating").attrib["class"].split()[-1]
        rating_converter = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        rating = rating_converter.get(rating_word, 0)

        category = response.css("ul.breadcrumb li a::text").getall()[-1]

        description = response.css(".product_page>p::text").get()

        result_dict = {
            "title": title,
            "price": price,
            "amount_in_stock": amount_in_stock,
            "category": category,
            "rating": rating,
            "description": description,
            "upc": upc,
        }

        yield result_dict
