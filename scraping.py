from com.dtmilano.android.viewclient import ViewClient
from ppadb.client import Client as AdbClient
import os
import time
import logging

logging.basicConfig(level=logging.INFO)

"""

"""


def connect():
    client = AdbClient(host="127.0.0.1", port=5037)  # Default is "127.0.0.1" and 5037
    try:
        device = client.device("52106b2bfcbe14a5")
    except:
        os.system("adb start-server")
        device = client.device("52106b2bfcbe14a5")
    logging.info("Connected to device")
    return device


def open_app(device, vc, app):
    logging.info("Opening app")
    device.shell("monkey -p " + app + " -c android.intent.category.LAUNCHER 1")
    time.sleep(10)
    logging.info("App opened")
    logging.info("Clicking on the explore tab")
    vc.dump(window=-1)
    vc.findViewWithTextOrRaise("Explore").touch()
    time.sleep(5)
    logging.info("Clicking on the people tab")
    vc.dump(window=-1)
    vc.findViewWithTextOrRaise("People").touch()


def extractData(device, vc):
    data = dict()
    views = vc.dump(window=-1)
    for view in views:
        if view.getUniqueId() == "id/no_id/5":
            ##print("Name:", view.getText())
            data["name"] = view.getText()
        if view.getUniqueId() == "id/no_id/4":
            data["TYPE"] = view.getText()
        if view.getUniqueId() == "id/no_id/6":
            data["Job Title"] = view.getText()
        if view.getUniqueId() == "id/no_id/9":
            data["Description"] = view.getText()
        if view.getUniqueId() == "id/no_id/10":
            data["Pays"] = view.getText()
        if view.getUniqueId() == "id/no_id/11":
            data["Domaine"] = view.getText()
    data["Share expertise about"] = list()
    data["Wants to learn"] = list()
    for i in range(2):
        scrollDown(device)
        time.sleep(1)
        views = vc.dump(window=-1)
        textList = []
        for view in views:
            if view.getText() != None and view.getText() != "":
                textList.append(view.getText())
        logging.info("Text list: " + str(textList))
        ## get all elements after element that contains "Share expertise" and before "WANTS TO LEARN"
        for i in range(len(textList)):
            if "SHARE" in textList[i]:
                for j in range(i + 1, len(textList)):
                    if "WANTS TO LEARN" in textList[j]:
                        break
                    logging.info("Adding " + textList[j] + " to the list")
                    data["Share expertise about"].append(textList[j])
        ## Same but with "WANTS TO LEARN"
        for i in range(len(textList)):
            if "WANTS" in textList[i]:
                for j in range(i + 1, len(textList)):
                    if "INTERACTIONS" in textList[j] or "PEOPLE SIMILAR" in textList[j]:
                        break
                    data["Wants to learn"].append(textList[j])
        ##print(data["Wants to learn"])
        print(data)
    return data


def scrollDown(device):
    logging.info("Scrolling down")
    device.shell("input swipe 520 1800 520 1000")


def boucle(device, vc):
    ## tap on x, y
    logging.info("Clicking on first tile")
    device.shell("input tap 520 713")
    time.sleep(2)
    data = extractData(device, vc)
    ## return to the previous page
    logging.info("Returning to the previous page")
    device.shell("input keyevent KEYCODE_BACK")
    time.sleep(2)
    logging.info("Scrolling down")
    device.shell("input swipe 520 1032 520 735")


def getAppList(device):
    appList = device.shell("pm list packages")
    return appList


def main(device, vc):
    apps = getAppList(device)
    apps = apps.split("\n")
    quatarApp = None
    for app in apps:
        if "summit" in app:
            quatarApp = app.split(":")[1]
    if quatarApp:
        open_app(device, quatarApp)


def test(device, vc):
    vc.dump(window=-1)
    ## print the tree
    views = vc.dump(window=-1)
    ## print the tree in a more readable way
    for view in views:
        print("Text:", view.getText())
        print("Resource ID:", view.getUniqueId())
        print("Bounds:", view.getBounds())
        print("Visibility:", view.getVisibility())


if __name__ == "__main__":
    device = connect()
    vc = ViewClient(*ViewClient.connectToDeviceOrExit(), autodump=False)

    extractData(device, vc)
