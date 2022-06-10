from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QGraphicsScene, QGraphicsPixmapItem

from IPMCL import setting, accounts, l_current
from Launcher.Microsoft.Login import start_auth, launch_login
from Launcher.Minecraft.launch import launch
from Deploy.Path import add, create
from Deploy.Minecraft import installer
from Deploy.Minecraft.Manifest import Manifest
from Request.fdownload import fdownload
from .Windows import main

from PIL import Image
from PIL.ImageQt import ImageQt

from io import BytesIO

from loguru import logger

import os
import sys
import asyncio
import threading


def account_names():
    """
    获取所有保存的用户名
    :return: 用户名列表
    """
    names = list()

    for account in accounts:
        names.append(accounts[account]["name"])

    return names


def get_account(name):
    """
    通过ID获取账户UUID（不是游戏UUID）
    :param name: ID
    :return: UUID
    """
    return [k for k, v in accounts.items() if v["name"] == name]


class GUI(QMainWindow, main.Ui_IPMCL):
    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)
        self.setupUi(self)

        self.c_vn = str()  # 准备跨方法变量

        # 添加存储的路径
        self.version_sel_3.addItems(setting["Paths"])

        # 获取原版游戏版本
        self.version_install_sel.addItems(Manifest().all)

        # 添加保存账户
        self.accounts_sel.addItems(account_names())

        # 设置当前的账户为选择账户
        try:
            self.accounts_sel.setCurrentText(accounts[setting["Launch"]["Select"]]["name"])
        except KeyError:
            pass

        # 添加当前选择路径所安装的游戏版本
        try:
            self.game_version_sel.addItems(os.listdir(os.path.join(setting["Launch"]["CurrentPath"], "versions")))
        except KeyError:
            pass

        # 从远端获取皮肤并绑定头像更新函数
        self.skin_update_thread = SkinUpdateThread()
        self.skin_update_thread.sig.connect(self.skin)

        # 开始获取皮肤
        self.skin_update_thread.start()

        logger.info(l_current["Launcher"]["GUI"]["Log"]["Ready"])

    # 在这个类中下面的所有后台操作都应该由线程接手
    def MicrosoftLogin(self):
        logger.info(l_current["Launcher"]["GUI"]["Log"]["LoginStart"])
        MSLogin_Thread(win=self).start()

    def Launch(self):
        if self.version_sel_3.currentText() != "":
            game_path = self.version_sel_3.currentText()
        elif "CurrentPath" not in setting["Launch"]:
            QMessageBox.warning(self,
                                l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
                                l_current["Launcher"]["GUI"]["PopUp"]["Unselect"]["Path"])
        else:
            game_path = setting["Launch"]["CurrentPath"]

        if self.game_version_sel.currentText() != "":
            version_name = self.game_version_sel.currentText()
        else:
            QMessageBox.warning(self,
                                l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
                                l_current["Launcher"]["GUI"]["PopUp"]["Unselect"]["Version"])

        if self.accounts_sel.currentText() != "":
            account = get_account(self.accounts_sel.currentText())
        else:
            QMessageBox.warning(self,
                                l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
                                l_current["Launcher"]["GUI"]["PopUp"]["Unselect"]["Account"])



        try:
            self.c_vn = version_name

            logger.info(l_current["Launcher"]["GUI"]["Log"]["LaunchStart"].format(
                path=game_path,
                version_name=version_name,
                account=account,
                offline=self.offline_che_3.isChecked()
            ))

            self.launch_thread = Launch_Thread(
                base_path=game_path,
                version_name=version_name,
                account=account,
                offline=self.offline_che_3.isChecked()
            )

            self.launch_thread.sig.connect(self.launch_success)

            self.launch_thread.start()
        except UnboundLocalError:
            pass

    def InstallF(self):
        if self.version_sel_3.currentText() != "":
            game_path = self.version_sel_3.currentText()
        elif "CurrentPath" not in setting["Launch"]:
            QMessageBox.warning(self,
                                l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
                                l_current["Launcher"]["GUI"]["PopUp"]["Unselect"]["Path"])
        else:
            game_path = setting["Launch"]["CurrentPath"]

        if self.version_install_sel.currentText() != "":
            game_version = self.version_install_sel.currentText()
        else:
            QMessageBox.warning(self,
                                l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
                                l_current["Launcher"]["GUI"]["PopUp"]["Unselect"]["Version"])

        if self.version_name_inp.text() == "":
            version_name = None
        else:
            version_name = self.version_name_inp.text()

        if version_name is None:
            self.c_ivn = game_version
        else:
            self.c_ivn = version_name

        if game_path != "" and game_version != "":
            self.install_thread = InstallF_Thread(
                base_path=game_path,
                version=game_version,
                version_name=version_name,
                win=self)

            self.install_thread.sig.connect(self.install_success)

            self.install_thread.start()

            QMessageBox.information(
                self,
                l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
                l_current["Launcher"]["GUI"]["PopUp"]["Success"]["Install"].format(version_name=self.c_ivn)
            )

    def SavePath(self):
        # dame
        answer = is_mc_path = None

        if not os.path.isdir(s=self.path_inp.text()):
            QMessageBox.information(self,
                                    l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
                                    l_current["Launcher"]["GUI"]["PopUp"]["Fail"]["Path"]["Dir"])
            return False

        if os.path.exists(self.path_inp.text()):
            is_mc_path = True

            for folder in ["versions", "libraries", "assets"]:
                if not os.path.exists(os.path.join(self.path_inp.text(), folder)):
                    answer = QMessageBox.warning(
                        self,
                        l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
                        l_current["Launcher"]["GUI"]["PopUp"]["Fail"]["Path"]["MinecraftDir"],
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                    )

                    is_mc_path = False
                    break

        else:
            answer = QMessageBox.warning(self,
                                         l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
                                         l_current["Launcher"]["GUI"]["PopUp"]["Fail"]["Path"]["Exist"],
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if str(answer) == "16384":
            CreatePath_Thread(base_path=self.path_inp.text()).start()

            logger.info(l_current["Launcher"]["GUI"]["Log"]["Path"]["Create"].format(path=self.path_inp.text()))

            QMessageBox.information(self,
                                    l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
                                    l_current["Launcher"]["GUI"]["PopUp"]["Success"]["Path"]["Create"])

        elif is_mc_path:
            AddPath_Thread(base_path=self.path_inp.text()).start()

            logger.info(l_current["Launcher"]["GUI"]["Log"]["Path"]["Add"].format(path=self.path_inp.text()))

            QMessageBox.information(self,
                                    l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
                                    l_current["Launcher"]["GUI"]["PopUp"]["Success"]["Path"]["Add"])

        elif str(answer) == "65536":
            QMessageBox.information(self,
                                    l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
                                    l_current["Launcher"]["GUI"]["PopUp"]["Success"]["Path"]["Cancel"])

        self.version_sel_3.clear()
        self.version_sel_3.addItems(setting["Paths"])

    def ReloadSkin(self):
        logger.info(l_current["Launcher"]["GUI"]["Log"]["SkinRStart"].format(path=self.path_inp.text()))

        setting["Launch"]["Select"] = get_account(self.accounts_sel.currentText())[0]

        self.skin_update_thread.start()

    def skin(self):
        logger.info(l_current["Launcher"]["GUI"]["Log"]["SkinReloaded"].format(path=self.path_inp.text()))

        img = ImageQt(self.sender().head_img)

        scene = QGraphicsScene()  # 创建场景
        scene.addItem(QGraphicsPixmapItem(QPixmap.fromImage(img)))

        self.skin_img.setScene(scene)

    def launch_success(self):
        QMessageBox.information(
            self,
            l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
            l_current["Launcher"]["GUI"]["PopUp"]["Success"]["Launch"].format(version_name=self.c_vn)
        )

    def install_success(self):
        QMessageBox.information(
            self,
            l_current["Launcher"]["GUI"]["PopUp"]["Title"]["Info"],
            l_current["Launcher"]["GUI"]["PopUp"]["Success"]["Installed"].format(version_name=self.c_ivn)
        )


class MSLogin_Thread(threading.Thread):
    def __init__(self, win):
        threading.Thread.__init__(self)
        self.win = win

    def run(self):
        asyncio.run(start_auth())

        self.win.accounts_sel.clear()
        self.win.accounts_sel.addItems(account_names())


class CreatePath_Thread(threading.Thread):
    def __init__(self, base_path):
        threading.Thread.__init__(self)
        self.base_path = base_path

    def run(self):
        create(home_path=self.base_path)


class AddPath_Thread(threading.Thread):
    def __init__(self, base_path):
        threading.Thread.__init__(self)
        self.base_path = base_path

    def run(self):
        add(home_path=self.base_path)


class InstallF_Thread(QThread):
    sig = pyqtSignal()

    def __init__(self, base_path, version, win, version_name=None):
        super(InstallF_Thread, self).__init__()
        self.base_path = base_path
        self.version = version
        self.version_name = version_name
        self.win = win

    def run(self):
        installer(home_path=self.base_path, version=self.version, version_name=self.version_name)

        self.win.game_version_sel.clear()
        self.win.game_version_sel.addItems(os.listdir(os.path.join(setting["Launch"]["CurrentPath"], "versions")))

        self.sig.emit()


class Launch_Thread(QThread):
    sig = pyqtSignal()

    def __init__(self, base_path, version_name, account, offline):
        super(Launch_Thread, self).__init__()

        self.base_path = base_path
        self.version_name = version_name
        self.account = account
        self.offline = offline

    def run(self):

        if not self.offline:
            account_data = asyncio.run(launch_login(self.account[0]))
        else:
            account_data = [
                accounts[self.account[0]]["name"],
                accounts[self.account[0]]["uuid"],
                "OFFLINE_MODE",
            ]

        launch(game_directory=self.base_path,
               version_name=self.version_name,
               auth_access_token=account_data[2],
               auth_player_name=account_data[0],
               auth_uuid=account_data[1])

        self.sig.emit()


class SkinUpdateThread(QThread):
    sig = pyqtSignal()

    def __init__(self):
        super(SkinUpdateThread, self).__init__()

    def run(self):
        try:
            self.img = Image.open(BytesIO(asyncio.run(fdownload(accounts[setting["Launch"]["Select"]]["skin_url"]))))

            self.head_img = Image.new(mode="RGBA", size=(68, 68))

            self.head_layer1 = self.img.crop((8, 8, 16, 16)).resize((64, 64), Image.NEAREST)
            self.head_layer2 = self.img.crop((40, 8, 48, 16)).resize((68, 68), Image.NEAREST)

            self.head_img.paste(self.head_layer1,
                                (2, 2))

            self.head_img.paste(self.head_layer2,
                                (0, 0),
                                self.head_layer2)

            self.sig.emit()
        except KeyError:
            pass


app = QApplication(sys.argv)

main_window = GUI()


def start():
    main_window.show()

    sys.exit(app.exec_())
