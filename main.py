import requests, json, math, re, os
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep
from get_urls import base_builder
from dotenv import load_dotenv
load_dotenv()

USER = os.environ.get("USER")
PASS = os.environ.get("PASS")
HOST = os.environ.get("HOST")
PORT = os.environ.get("PORT")

PROXIES = { 
    "http": f"http://{USER}:{PASS}@{HOST}:{PORT}/",
    "https": f"http://{USER}:{PASS}@{HOST}:{PORT}/"
}

def get_list(page_no, url):
    new_url = url+f"?page={page_no}"
    print("URL:", new_url)
    response = requests.get(new_url)
    soup = BeautifulSoup(response.content, "html.parser")
    listings = soup.find_all("div", id="ProductBoxContainer")
    
    links = []
    print("Number of listings found:", len(listings))
    for listing in listings:
        link = "https://www.webstaurantstore.com"+listing.find("a")["href"]
        links.append(link)

    return links

def get_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    try:
        name = soup.find("h1", class_="page-header").text.strip()
    except:
        print("Sleeping for 90 seconds..........")
        sleep(90)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        name = soup.find("h1", class_="page-header").text.strip()
    subhead = soup.find("div", class_="product-subhead")

    # try:
    #     spans = subhead.find_all("span")
    #     rating = spans[0].text.strip().split("Rated ")[-1].split(" out")[0].strip()+"/5"
    #     total_reviews = ''.join(filter(lambda i: i.isdigit(), spans[1].text.strip()))
    #     item_number = spans[5].text.strip().upper()
    #     try:
    #         mfr_number = spans[7].text.strip()
    #     except:#if no mfr number
    #         mfr_number = ""
    # except:#if no review
    #     spans = subhead.find_all("span")
    #     rating = "No rating"
    #     total_reviews = "0"
    #     item_number = spans[4].text.strip().upper()
    #     try:
    #         mfr_number = spans[6].text.strip()
    #     except:#if no review and no mfr number
    #         mfr_number = ""

    try:
        rating = subhead.find("span", class_="sr-only").text.strip().split("Rated ")[-1].split(" out")[0].strip()+"/5"
        if subhead.find("span", class_="sr-only").text.strip() == "Item number":
            rating = "No rating"
            total_reviews = "0"
        else:
            total_reviews  = subhead.find("span", class_="product-subhead__rating-link ml-1").text.strip()
            total_reviews = ''.join(filter(lambda i: i.isdigit(), total_reviews))
    except:
        rating = "No rating"
        total_reviews = "0"
        
    item_number = subhead.find("span", class_="item-number").find("span", style="text-transform:uppercase").text.strip().upper()

    try:
        mfr_number = subhead.find("span", class_="mfr-number").find("span", style="text-transform:uppercase").text.strip()
    except:
        mfr_number = ""
    
    try:        
        right_sidebar = soup.find("div", id="subject")
        price = float(right_sidebar.find("p", class_="price").text.strip().split("/")[0].split("$")[-1].replace(",","").strip())
    except:
        price = ""

    try:
        details_div = soup.find("div", id="details-group")
        details = details_div.find("p").text.strip()
    except:
        details = ""

    try:
        upc_code = soup.find("div", class_="product__stat").find_all("span")[-1].text.strip()
    except:
        upc_code = ""

    try:
        brand = soup.find("a", class_="vendor-logo")["title"].strip()
    except:
        brand = ""

    images=soup.select('a[data-testid="image-dot"]')
    image_urls=[]
    for image in images:
        path = image.find("img")["src"].replace("thumbnails", "large")
        image_urls.append("https://cdnimg.webstaurantstore.com"+path)

    if len(image_urls) > 1:
        temp = image_urls[0]
        image_urls[0] = image_urls[1]
        image_urls[1] = temp

    try:
        overview = soup.find("ul", class_="highlights no-margin")
        overview_list = overview.find_all("li")

        overviews = [point.text.strip() for point in overview_list]
        overviews = '\n'.join([str(elem) for elem in overviews])
    except:
        overviews = ""

    try:
        product_variations = soup.find("div", id="ProductVariations").find_all("li")
        product_variations = [variation.text.strip() for variation in product_variations]
        product_variations = '\n'.join([str(elem) for elem in product_variations])
    except:
        product_variations = ""

    breadcrumbs = soup.find("ol", class_="breadcrumb").find_all("a")
    
    for breadcrumb in breadcrumbs:
        if "email" in breadcrumb.text:
            # print(breadcrumb.text)
            breadcrumbs.remove(breadcrumb)
       

    try:
        category = breadcrumbs[-1]['title'].strip()
    except KeyError:
        breadcrumbs.remove(breadcrumbs[len(breadcrumbs)-1])
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
    

def list_driver(page_start, cat_name, filename, org_url):
    urls = []
    i=page_start
    while True:
        print(f"Page: {i}")
        links = get_list(i, org_url)
        urls.append(links)
        i+=1
        if len(links) == 0:
            break
    new_lst = [item for sublist in urls for item in sublist]
    print("Total number of links:", len(new_lst))
    with open(f"tests/{cat_name}/lists/{filename}.json", "w") as f:
        json.dump(new_lst, f, indent=4)


def details_driver(cat_name, filename, continue_from):
    with open(f"tests/{cat_name}/lists/{filename}.json", "r") as f:
        links = json.load(f)
        
    all_details = []

    x = 1
    for link in links:
        #GD = Getting Details
        if x >= continue_from:
            print(f"GD | {x}/{len(links)} | {cat_name} > {filename} | {link}")
            details = get_details(link)
            all_details.append(details)
            
            with open(f"tests/{cat_name}/details/{filename}_details.json", "w") as f:
                json.dump(all_details, f, indent=4)
    
        x += 1

def json2xlsx(input, output):
    with open(input, "r") as f:
        details = json.load(f)

    df = pd.DataFrame(details)
    df.to_excel(output, index=False)

def get_total_pages(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    header = soup.find("h1").text.strip()
    total_pages = ''.join(filter(lambda i: i.isdigit(), header))
    total_pages = math.ceil(int(total_pages)/60)
    return total_pages

def main():
    base_url = "https://www.webstaurantstore.com"
    execute = True
    if execute:
        urls=[
                "https://www.webstaurantstore.com/office-products.html"
            ]


        for url in urls:
            # url = "https://www.webstaurantstore.com/15037/commercial-restaurant-ranges.html"
            cat_name = url.split("/")[-1].split(".")[0]

            base_builder(url, cat_name)

            print("\nBase Build... Done\n")

            with open(f"tests/{cat_name}/true_links/merged_true_links.json", "r") as f:
                links = json.load(f)
            
            for x in range(0, len(links)):
                filename  = links[x].split("/")[-1].split(".")[0]
                link_name = links[x]
                print(f"|========================| {cat_name} |========================|")
                print(f"{filename} | {link_name}")
                print(f"|==========================================================================================|\n")
            
                list_driver(1, cat_name, filename, links[x])
                details_driver(cat_name, filename, continue_from=1)
                # json2xlsx(filename)
    else:
        
        cat_name = "restaurant-tabletop-supplies"
        with open(f"tests/{cat_name}/true_links/merged_true_links.json", "r") as f:
                links = json.load(f)
        print(f"|========================| {cat_name} |========================|")
        print(links[5])
        print(f"|==============================================================================================|\n")

        filename  = links[50].split("/")[-1].split(".")[0]
        print(filename)
        details_driver(cat_name, filename, continue_from=2668)
            
def remove_dupes_from_lst_of_dct(lst_of_dct):
    return [dict(t) for t in {tuple(d.items()) for d in lst_of_dct}]

def merge_all_details():
    dirs = os.listdir("tests")
    dirs.pop(1)
    all_details = []
    x=1
    dirs=["office-products"]
    for dir in dirs:
        print(f"{x}/{len(dirs)}")
        if dir != ".DS_Store":
            files = os.listdir(f"tests/{dir}/details")
            for file in files:
                if file != ".DS_Store":
                    with open(f"tests/{dir}/details/{file}", "r") as f:
                        details = json.load(f)
                    all_details.extend(details)
        x+=1
    print(f"Length of file: {len(all_details)}")
    all_details = remove_dupes_from_lst_of_dct(all_details)
    print(f"Length of file After: {len(all_details)}")
    with open("done/all_details.json", "w") as f:
        json.dump(all_details, f, indent=4)
    # json2xlsx("done/all_details.json","done/all_details.xlsx")


if __name__ == "__main__":
    # main()
    # merge_all_details()
    
    pass
    
    