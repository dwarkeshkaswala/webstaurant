import requests, json, os
from bs4 import BeautifulSoup
from time import sleep

def remove_dupes(lst):
    lst = sorted(set(lst))
    return lst

def link_checker(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        prod_listing = soup.find("div", id="product_listing")
        if prod_listing:
            return True
        else:
            return False
    except:
        if "comhttps" in url:
            url = url.replace("https://www.webstaurantstore.comh", "h")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            prod_listing = soup.find("div", id="product_listing")
            if prod_listing:
                return True
            else:
                return False
        else:
            print(f"Error with {url}")
    
def get_links(url):

    try:
        # print(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        main_div = soup.find("div", id="main")
        photo_grids = main_div.select('div[data-testid="Photo Grid Categories"]')
        carousels = main_div.select('div[data-testid="enhanced-carousel-background"]')
    except:
        print("Sleeping for 90 seconds..........")
        sleep(90)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        main_div = soup.find("div", id="main")
        photo_grids = main_div.select('div[data-testid="Photo Grid Categories"]')
        carousels = main_div.select('div[data-testid="enhanced-carousel-background"]')

    links = []
    for photo_grid in photo_grids:
        for a in photo_grid.select("a"):
            if not "https://www.webstaurantstore.com" in a["href"].strip():
                links.append("https://www.webstaurantstore.com"+a["href"].strip())
            else:
                links.append(a["href"].strip())
    
    for carousel in carousels:
        for a in carousel.select("a"):
            if not "https://www.webstaurantstore.com" in a["href"].strip():
                links.append("https://www.webstaurantstore.com"+a["href"].strip())
            else:
                links.append(a["href"].strip())
                
    matchers = ['feature','?filter','new/?category', 'specials.html?', '/search', 'vendor', url]
    cleaned = [s for s in links if not any(xs in s for xs in matchers)]

    cleaned = remove_dupes(cleaned)

    true_links = []
    false_links = []
    temp_true = []

    for link in cleaned:
        
        status = link_checker(link)
        if status==True:
            true_links.append(link)
        else:
            false_links.append(link)
        
            

    return true_links, false_links

def driver(url, cat_name):

    if not os.path.exists(f"tests/{cat_name}/true_links"):
        os.makedirs(f"tests/{cat_name}/true_links")

    if not os.path.exists(f"tests/{cat_name}/false_links"):
        os.makedirs(f"tests/{cat_name}/false_links")

    if not os.path.exists(f"tests/{cat_name}/details"):
        os.makedirs(f"tests/{cat_name}/details")

    if not os.path.exists(f"tests/{cat_name}/lists"):
        os.makedirs(f"tests/{cat_name}/lists")

    try:
        files_dir = os.listdir(f'tests/{cat_name}/true_links')
        temp = [int(i.split("_")[2].split(".")[0]) for i in files_dir]
        x = max(temp)+1
    except:
        x = 1

    try:
        files_dir = os.listdir(f'tests/{cat_name}/false_links')
        temp = [int(i.split("_")[2].split(".")[0]) for i in files_dir]
        y = max(temp)+1
    except:
        y = 1

    true_links, false_links = get_links(url)

    if len(true_links) > 0:
        with open(f"tests/{cat_name}/true_links/true_links_{x}.json", "w") as f:
            json.dump(true_links, f, indent=4)
    if len(false_links) > 0:
        with open(f"tests/{cat_name}/false_links/false_links_{y}.json", "w") as f:
            json.dump(false_links, f, indent=4)
    

def looper(next_traversed_file_no, cat_name, org_url):
    while True:
        try:
            files_dir = os.listdir(f'tests/{cat_name}/false_links')
            temp = [int(i.split("_")[2].split(".")[0]) for i in files_dir]
            max_file_no = max(temp)+1
        except:
            print(f"{cat_name} | No further links found")
            break

        if next_traversed_file_no == max_file_no:
            break
        else:
            with open(f"tests/{cat_name}/false_links/false_links_{next_traversed_file_no}.json", "r") as f:
                false_links = json.load(f)
            
            m=1
            for link in false_links:
                if link == org_url:
                    continue
                print(f"{m}/{len(false_links)} | false_links_{next_traversed_file_no}.json | {link}")
                driver(link, cat_name)
                m+=1
            next_traversed_file_no += 1

def merge_json(cat_name):
    files_dir = os.listdir(f'tests/{cat_name}/true_links')
    final_lst = []
    for file in files_dir:
        with open(f"tests/{cat_name}/true_links/{file}", "r") as f:
            true_links = json.load(f)
        final_lst += true_links

    final_lst = remove_dupes(final_lst)
    with open(f"tests/{cat_name}/true_links/merged_true_links.json", "w") as f:
        json.dump(final_lst, f, indent=4)

    files_dir = os.listdir(f'tests/{cat_name}/false_links')
    final_lst = []
    for file in files_dir:
        with open(f"tests/{cat_name}/false_links/{file}", "r") as f:
            false_links = json.load(f)
        final_lst += false_links

    final_lst = remove_dupes(final_lst)
    with open(f"tests/{cat_name}/false_links/merged_false_links.json", "w") as f:
        json.dump(final_lst, f, indent=4)
        
    

def base_builder(url, cat_name):
    driver(url, cat_name)
    next_traversed_file_no = 1
    looper(next_traversed_file_no, cat_name, url)
    merge_json(cat_name)

if __name__ == "__main__":
    base_builder()