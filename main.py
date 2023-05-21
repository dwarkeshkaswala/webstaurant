import requests, json, math, re
import pandas as pd
from bs4 import BeautifulSoup

def get_list(page_no, search_term, url):
    
    new_url = url+f"/search/{search_term}.html?page={page_no}"
    response = requests.get(new_url)
    soup = BeautifulSoup(response.content, "html.parser")
    listings = soup.find_all("div", id="ProductBoxContainer")
    
    links = []
    print("Number of listings found:", len(listings))
    for listing in listings:
        link = url+listing.find("a")["href"]
        links.append(link)
    
    return links

def get_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    name = soup.find("h1", class_="page-header").text.strip()
    subhead = soup.find("div", class_="product-subhead")

    try:
        spans = subhead.find_all("span")
        rating = spans[0].text.strip().split("Rated ")[-1].split(" out")[0].strip()+"/5"
        total_reviews = ''.join(filter(lambda i: i.isdigit(), spans[1].text.strip()))
        item_number = spans[5].text.strip().upper()
        try:
            mfr_number = spans[7].text.strip()
        except:#if no mfr number
            mfr_number = ""
    except:#if no review
        spans = subhead.find_all("span")
        rating = "No rating"
        total_reviews = "0"
        item_number = spans[4].text.strip().upper()
        try:
            mfr_number = spans[6].text.strip()
        except:#if no review and no mfr number
            mfr_number = ""

    right_sidebar = soup.find("div", id="subject")
    price = right_sidebar.find("p", class_="price").text.strip()

    details_div = soup.find("div", id="details-group")
    details = details_div.find("p").text.strip()

    upc_code = soup.find("div", class_="product__stat").find_all("span")[-1].text.strip()

    brand = soup.find("a", class_="vendor-logo")["title"].strip()

    images=soup.select('a[data-testid="image-dot"]')
    image_urls=[]
    for image in images:
        path = image.find("img")["src"].replace("thumbnails", "large")
        image_urls.append("https://cdnimg.webstaurantstore.com"+path)

    temp = image_urls[0]
    image_urls[0] = image_urls[1]
    image_urls[1] = temp

    overview = soup.find("ul", class_="highlights no-margin")
    overview_list = overview.find_all("li")

    overviews = [point.text.strip() for point in overview_list]
    overviews = '\n'.join([str(elem) for elem in overviews])

    try:
        product_variations = soup.find("div", id="ProductVariations").find_all("li")
        product_variations = [variation.text.strip() for variation in product_variations]
        product_variations = '\n'.join([str(elem) for elem in product_variations])
    except:
        product_variations = ""

    breadcrumbs = soup.find("ol", class_="breadcrumb").find_all("a")
    category = breadcrumbs[-1]['title'].strip()

    breadcrumbs = breadcrumbs[::-1]
    sub_category = ""

    for breadcrumb in breadcrumbs:
        if not breadcrumb['title'].strip() == category and not breadcrumb['title'].strip() == "WebstaurantStore":
            sub_category = breadcrumb['title'].strip() + " > " + sub_category

    sub_category = sub_category[:-3]
    
    # print("Image URLs:", image_urls)
    # print("Name:", name)
    # print("Brand:", brand)
    # print("Rating:", rating)
    # print("Total Reviews:", total_reviews)
    # print("Item Number:", item_number)
    # print("MFR Number:", mfr_number)
    # print("Price:", price)
    # print("Details:", details)
    # print("UPC Code:", upc_code)
    # print("Overview:", overviews)
    # print("Product Variations:", product_variations)
    # print("URL:", url)
    # print("Category:", category)
    # print("Sub Category:", sub_category)

    product_details_dict = {
        "name": name,
        "brand": brand,
        "rating": rating,
        "total_reviews": total_reviews,
        "item_number": item_number,
        "mfr_number": mfr_number,
        "price": price,
        "details": details,
        "upc_code": upc_code,
        "overview": overviews,
        "product_variations": product_variations,
        "url": url,
        "category": category,
        "sub_category": sub_category
    }

    x = 1
    var_name = f"image_{x}"

    for image in image_urls:
        var_name = f"image_{x}"
        exec(f"{var_name} = '{image}'")
        product_details_dict[var_name] = image
        x += 1

    return product_details_dict
    

def list_driver(page_start, page_end, filename):
    urls = []
    for i in range(page_start, page_end):
        print("Page:", i)
        links = get_list(i, filename)
        urls.append(links)
    new_lst = [item for sublist in urls for item in sublist]
    print("Total number of links:", len(new_lst))
    with open(f"{filename}.json", "w") as f:
        json.dump(new_lst, f, indent=4)


def details_driver(filename):
    with open(f"{filename}.json", "r") as f:
        links = json.load(f)
        
    all_details = []

    x = 1
    for link in links:
        print(f"{x}/{len(links)} | {link}")
        details = get_details(link)
        all_details.append(details)
        
        
        with open(f"{filename}_details.json", "w") as f:
            json.dump(all_details, f, indent=4)
    
        if x==5:
            break

        x += 1

def json2xlsx(filename):
    with open(f"{filename}_details.json", "r") as f:
        details = json.load(f)

    df = pd.DataFrame(details)
    df.to_excel(f"{filename}_details.xlsx", index=False)

def get_total_pages(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    header = soup.find("h1").text.strip()
    total_pages = ''.join(filter(lambda i: i.isdigit(), header))
    total_pages = math.ceil(int(total_pages)/60)
    return total_pages

def main():
    url = "https://www.webstaurantstore.com"
    filename = "restaurant-equipment"
    total_pages = get_total_pages(f"{url}/search/{filename}.html")

    print("Total Pages:", total_pages)
    # list_driver(1, total_pages, filename)
    # details_driver(filename)
    # json2xlsx(filename)
    
if __name__ == "__main__":
    main()