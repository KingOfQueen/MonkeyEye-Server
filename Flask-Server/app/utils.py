# *-* coding: utf-8 *-*
import time
from datetime import datetime

mobile_code = {}
isValid = lambda x, y: len(x) == y and x.isdigit()


# 检查短信验证码, 10分钟内有效
def checkSmsNum(mobile, code):
    print mobile_code
    if isValid(mobile, 11) and isValid(code, 6):
        info = mobile_code.get(mobile, None)
        if info != None and info.get('code', '0') == int(code):
            now = datetime.now()
            if (now - info.get('lasttime')).seconds < 600:
                mobile_code.pop(mobile)
                return 'Pass'

            return 'Expired Code'

    return 'Invalid Args'


#  每格一个小时删除已过期的手机信息
def _popExpiredItems():
    expired = []
    for mobile in mobile_code:
        now = datetime.now()
        # 验证码已过期
        if (now - mobile_code.get(mobile).get('lasttime')).seconds > 600:
            expired.append(mobile)

    # 删除已过期的手机信息
    for mobile in expired:
        mobile_code.pop(mobile)

    time.sleep(3600)
    _popExpiredItems()

# 定时器，新开线程，避免阻塞主进程
from threading import Timer
Timer(0, _popExpiredItems).start()
