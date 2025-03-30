import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select


#调用API获取要举报的新闻id
def fetch_news_id():

    '''
    get news id from API
    '''


    news_id = 100
    refute_news(news_id)


#在数据库中查询该新闻的相关信息
def get_news_info(news_id):
    news_info = {}

    '''
    get news info from database
    '''

    return news_info


def refute_news(news_id = None):

    news_info = get_news_info(news_id)

    REFUTATION_URL = r"https://www.piyao.org.cn/xxjbrk.htm"

    #初始化非新闻数据库信息
    phone_number = "1145141919810"

    #初始化默认新闻信息
    new_title = "新闻标题"
    new_type = "时事政治"
    new_content = "新闻内容"
    new_url = "新闻链接"
    new_platform = "社交媒体平台"

    if news_info:
        new_title = news_info.get("news_title", new_title)
        new_type = news_info.get("hash_tag", new_type)
        new_content = news_info.get("news_content", new_content)
        new_url = news_info.get("url", new_url)
        new_platform = news_info.get("platform", new_platform)

    driver = webdriver.Edge()
    # 打开网页
    driver.get(REFUTATION_URL)


    # 显式等待元素加载（CSS 选择器定位）
    img_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'div.nextTep > img')  

        )
    )
    # 点击下一步
    img_element.click()






    # 显式等待页面加载
    wait = WebDriverWait(driver, 10)

    # 填写标题
    title_textarea = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div.bt textarea")
    ))
    title_textarea.send_keys(new_title)


    # 选择地域（省）
    option = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//select[@class="selt1"]/option[@data-code="1561100000"]')
    ))
    option.click()




    category_select = Select(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select.selt3"))))
    category_select.select_by_visible_text(new_type)  # 直接匹配选项文本



    # 填写内容
    content_textarea = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div.nr textarea")
    ))
    content_textarea.send_keys()

    # 填写链接
    link_textarea = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div.lj textarea")
    ))
    link_textarea.send_keys(new_url)

    # 填写标签
    tag_textarea = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div.bq textarea")
    ))
    tag_textarea.send_keys(new_platform)

    # 填写手机号码
    phone_input = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div.shoj input[type='number']")
    ))
    phone_input.send_keys(phone_number)


    '''
    # 提交表单
    submit_button = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "div.submit img")
    ))
    submit_button.click()'''

    # 等待提交完成（可根据实际需求调整）
    time.sleep(30000)

    # 关闭浏览器
    driver.quit()
















