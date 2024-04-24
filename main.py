from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import pypub
import os
from urllib import request
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PIL import Image

class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("baskerville", "i", 12)
        self.cell(0, 10, f"Page {self.page_no()} / {{nb}}", align="C")

def getNovel(url, option):
    #OPTIONS
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_argument("log-level=3")

    #DRIVER
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    wait = WebDriverWait(driver, 20, poll_frequency=5)

    driver.get(url)

    # GET INFO NOVEL
    novel = []
    chapter_number = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".header-stats span strong"))).text
    title_novel = wait.until(ec.presence_of_element_located((By.CLASS_NAME, "novel-title"))).text

    print("Getting", title_novel, "novel...")
    print("It has", chapter_number, "chapters")

    #GET IMAGE COVER
    cover = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".cover img")))
    res = request.URLopener()
    res.addheader("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)")
    res.retrieve(cover.get_attribute("src"), title_novel)
    im = Image.open(title_novel)
    im.save(title_novel + ".png")
    os.remove(title_novel)

    #ENTER CHAPTERS PAGE
    element = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "chapter-latest-container")))
    driver.execute_script("arguments[0].scrollIntoView(true)", element)
    element.click()

    element = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".chapter-list li")))
    driver.execute_script("arguments[0].scrollIntoView(true)", element)
    element.click()

    if option == "1":
        getPDF(driver, wait, chapter_number, title_novel)
    else:
        getEPUB(driver, wait, chapter_number, title_novel)

def getPDF(driver, wait, chapter_number, title_novel):

    #CREATE PDF OBJECT
    pdf = PDF("P", "mm", "Letter")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.image(title_novel + ".png", x=0, y= 0, w=pdf.w, h=pdf.h)
    pdf.add_font("baskerville", "", "fonts/libreBaskerville-Regular.ttf")
    pdf.add_font("baskerville", "b", "fonts/libreBaskerville-Bold.ttf")
    pdf.add_font("baskerville", "i","fonts/LibreBaskerville-Italic.ttf")
    pdf.set_margin(15)

    number = 1
    while True:
        pdf.add_page()
        
        #GET NOVEL CONTENT
        chapter_title = wait.until(ec.presence_of_element_located((By.CLASS_NAME, "chapter-title"))).text
        chapter = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "#chapter-container p")))

        print("Getting", chapter_title)
        print(str(number) + "/" + chapter_number, "----", (number*100)/int(chapter_number), "% ----")

        #CHAPTER TITLE
        pdf.set_font("baskerville", "b", 20)
        pdf.cell(0, 15, chapter_title + "\n", align="C", new_y=YPos.NEXT, new_x=XPos.LMARGIN)
        pdf.cell(0, 5, "", new_y=YPos.NEXT, new_x=XPos.LMARGIN)

        #CHAPTER CONTENT
        pdf.set_font("baskerville", "", 15)
        for p in chapter:
            pdf.multi_cell(pdf.w - (15 * 2), 6, "     " + p.text + "\n")

        # SEE IF THERE ARE MORE CHAPTERS
        classButton = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "nextchap")))

        if "isDisabled" in classButton.get_attribute("class"):
            break
        else:
            driver.execute_script("arguments[0].scrollIntoView(true)", classButton)
            classButton.click()
            number += 1

    print(title_novel, "download completed")

    if not(os.path.exists("novels")):
        os.mkdir("novels")
    pdf.output(os.path.join("novels", title_novel + ".pdf"))
    os.remove(title_novel + ".png")

def getEPUB(driver, wait, chapter_number, title_novel):
    epub = pypub.Epub(title_novel, cover=title_novel + ".png")
     # GET EVERY CHAPTER
    number = 1
    while True:
        chapter_title = wait.until(ec.presence_of_element_located((By.CLASS_NAME, "chapter-title"))).text
        chapter = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "#chapter-container p")))

        print("Getting", chapter_title)
        print(str(number) + "/" + chapter_number, "----", (number*100)/int(chapter_number), "% ----")
        paragraphs = ""

        for p in chapter:
            paragraphs += p.text + "\n"

        chapter = pypub.create_chapter_from_text(paragraphs, chapter_title)
        epub.add_chapter(chapter)

        # SEE IF THERE ARE MORE CHAPTERS
        classButton = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "nextchap")))
        
        if "isDisabled" in classButton.get_attribute("class"):
            break
        else:
            driver.execute_script("arguments[0].scrollIntoView(true)", classButton)
            classButton.click()
            number += 1
    
    print(title_novel, "download completed")

    if not(os.path.exists("novels")):
        os.mkdir("novels")
    epub.create(os.path.join(os.getcwd(), "novels", title_novel))
    os.remove(title_novel + ".png")


#GET LINK
url = input("Welcome, enter the link of the novel you want to collect from LightNovelPub: \n")
urlCheck = url.find("https://lightnovelpub.vip/novel/")
while urlCheck == -1:
    print("\nError! This is not a URL from LightNovelPub! \n")
    url = input("Enter the link of the novel again: \n")
    urlCheck = url.find("https://lightnovelpub.vip/novel/")

#GET FORMAT
option = input("\n1) PDF \n2) EPUB \n\nIn what format do you want the novel?: ")
while int(option) not in [1,2]:
    print("\nError! This option does not exist! \n")
    option = input("1) PDF \n2) EPUB \n\nIn what format do you want the novel?: ")

getNovel(url, option)