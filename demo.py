# -*- coding: UTF-8 -*-
import utils
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
import time
import requests

# http://171.106.48.55:8899/legalsystem/ReportServer?reportlet=ktgg/ktgglist.cpt&fbdm=450000
# http://171.106.48.55:8899/legalsystem/web/ktgg.jsp?webid=1032253163
# http://yggx.gxcourt.gov.cn/
while True:
    try:
        ips = utils.getProxy()
        proxies = {}
        print("换代理")
        proxies["http"] = ips[0]
        proxies["https"] = ips[1]

        proxy = Proxy(
            {
                'proxyType': ProxyType.MANUAL,
                'httpProxy': ips[2]  # 代理ip和端口
            }
        )

        desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
        # 把代理ip加入到技能中
        proxy.add_to_capabilities(desired_capabilities)
        driver = webdriver.Chrome(
            desired_capabilities=desired_capabilities
        )
        driver.set_page_load_timeout(5)
        driver.set_script_timeout(5)
        # #
        # r = requests.get("http://171.106.48.55:8899/legalsystem/ReportServer?reportlet=ktgg/ktgglist.cpt&fbdm=450000",
        #                  proxies=proxies)
        # print(r.content)
        driver.get("http://171.106.48.55:8899/legalsystem/ReportServer?reportlet=ktgg/ktgglist.cpt&fbdm=450000")
        time.sleep(20)
        print driver.page_source
    except Exception as e:
        driver.quit()
        print e
    else:
        break
