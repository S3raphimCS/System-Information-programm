from importlib import import_module
import shutil
from PyQt5 import QtCore, QtGui, QtWidgets
from time import sleep
import sys
import os
import psutil
import PySide2
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QWidget
import PySide2extn
from PySide2extn.RoundProgressBar import roundProgressBar
from PySide2extn.SpiralProgressBar import spiralProgressBar
from interface import *
from qt_material import *
import datetime
import platform
import webbrowser
from pathlib import Path

class WorkerSignals(QtCore.QObject):

        finished = QtCore.Signal()
        error = QtCore.Signal(tuple)
        result = QtCore.Signal(object)
        progress = QtCore.Signal(int)


class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.kwargs['progress_callback'] = self.signals.progress

    QtCore.Slot()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            exctype, value = sys.exc_info()[:2]
        else:
            pass

        finally:
            pass


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        apply_stylesheet(app, theme='dark_red.xml')

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint) #Убрать Знак "Закрыть"


        self.shadow = QtWidgets.QGraphicsDropShadowEffect(self) #Эффект тени
        self.shadow.setBlurRadius(50)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)

        self.ui.centralwidget.setGraphicsEffect(self.shadow) #Подключение эффекта тени для окна

        self.setWindowIcon(QtGui.QIcon(':/icons/usefull_png/airplay.png')) #Иконка окна

        self.setWindowTitle('ARCANE') #Название окна

        QtWidgets.QSizeGrip(self.ui.size_grip)

        self.ui.minimize_window_button.clicked.connect(lambda: self.showMinimized())
        self.ui.closewindow_button.clicked.connect(lambda: self.close())
        self.ui.rebuild_window_button.clicked.connect(lambda: self.restore_or_maximize_window())

        #Поправление рамок на странице Сетей
        self.ui.tableWidget_4.setMinimumHeight(185)
        self.ui.tableWidget_5.setMinimumHeight(185)
        self.ui.tableWidget_6.setMinimumHeight(185)
        self.ui.tableWidget_7.setMinimumHeight(185)
        self.ui.network_page.setContentsMargins(9,9,9,12)


        self.ui.cpu_pic.setStyleSheet('border-bottom: 2px solid;'
                                      'border-bottom-color: white;')

        
        self.ui.label.setText("Эта работа не увидела бы свет без этих 10 литров кваса. Благодарю за помощь в разработке: индусов, континент Habr'a и Илью. Привет Артему")
        

        #Переход на CPU
        self.ui.cpu_pic.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.cpu_page))
        self.ui.pushButton_7.clicked.connect(lambda: self.ui.cpu_pic.click())
        #Переход на Battery
        self.ui.battery_pic.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.battery_page))
        self.ui.pushButton_8.clicked.connect(lambda: self.ui.battery_pic.click())
        #Переход на System info
        self.ui.system_pic.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.system_page))
        self.ui.pushButton_9.clicked.connect(lambda: self.ui.system_pic.click())
        #Переход на Activity
        self.ui.activities_pic.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.activity_page))
        self.ui.pushButton_10.clicked.connect(lambda: self.ui.activities_pic.click())
        #Переход на Storage
        self.ui.storage_pic.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.storage_page))
        self.ui.pushButton_11.clicked.connect(lambda: self.ui.storage_pic.click())
        #Переход на Sensors
        self.ui.sensor_pic.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.sensor_page))
        self.ui.pushButton_12.clicked.connect(lambda: self.ui.sensor_pic.click())
        #Переход на Network
        self.ui.network_pic.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.network_page))
        self.ui.pushButton_13.clicked.connect(lambda: self.ui.network_pic.click())
        #Переход на страницу ВК
        self.ui.vk_button.clicked.connect(lambda: webbrowser.open('https://vk.com/s3raphim'))
        #Переход на WA
        self.ui.wa_button.clicked.connect(lambda: webbrowser.open('https://web.whatsapp.com/send/?phone=79241037379'))
        #self.ui.vk_button.clicked.connect(lambda: webbrowser.open_new_tab('vk.com/s3raphim'))

        self.old_pos = None

        self.ui.header_frame.mouseDoubleClickEvent

        self.ui.menu_button.clicked.connect(lambda: self.slideLeftMenu())
        self.ui.pushButton.clicked.connect(lambda: self.slideRightMenu())

        
         # Activities buttons
        self.ui.pushButton_2.clicked.connect(lambda: self.activity_type_check('suspend'))
        self.ui.pushButton_3.clicked.connect(lambda: self.activity_type_check('resume'))
        self.ui.pushButton_4.clicked.connect(lambda: self.activity_type_check('terminate'))
        self.ui.pushButton_5.clicked.connect(lambda: self.activity_type_check('kill'))

        for el in self.ui.menu_frame.findChildren(QtWidgets.QPushButton):
            if el == self.ui.pushButton_7:
                el = self.ui.cpu_pic
            elif el == self.ui.pushButton_8:
                el = self.ui.battery_pic
            elif el == self.ui.pushButton_9:
                el = self.ui.system_pic
            elif el == self.ui.pushButton_10:
                el = self.ui.activities_pic
            elif el == self.ui.pushButton_11:
                el = self.ui.storage_pic
            elif el == self.ui.pushButton_12:
                el = self.ui.sensor_pic
            elif el == self.ui.pushButton_13:
                el = self.ui.network_pic
            el.clicked.connect(self.applyButtonStyle)


        self.threadpool = QtCore.QThreadPool()


        self.ui.available_ram.setStyleSheet('color: rgb(6,233,38)')
        self.ui.used_ram.setStyleSheet('color: rgb(6,201,233)')
        self.ui.free_ram.setStyleSheet('color: rgb(233,6,201)')
        

        self.show() 


        #Main functions
        #self.battery()
        #self.cpu_and_ram()
        #self.system_info()
        self.activities() 
        self.storage()
        self.sensors()
        self.network()
        self.psutil_thread()

    #Close confirm
    def closeEvent(self, e):

        result = QtWidgets.QMessageBox.question(self, 'Подтверждение', 'Вы действительно хотите выйти?', 
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

            
        if result == QtWidgets.QMessageBox.Yes:
            e.accept()
            QtWidgets.QWidget.closeEvent(self, e)
        else: e.ignore()
            

    def psutil_thread(self):
        worker = Worker(self.cpu_and_ram)

        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        self.threadpool.start(worker)

        battery_worker = Worker(self.battery)

        battery_worker.signals.result.connect(self.print_output)
        battery_worker.signals.finished.connect(self.thread_complete)
        battery_worker.signals.progress.connect(self.progress_fn)

        self.threadpool.start(battery_worker)

        process_worker = Worker(self.activities)

        process_worker.signals.result.connect(self.print_output)
        process_worker.signals.finished.connect(self.thread_complete)
        process_worker.signals.progress.connect(self.progress_fn)

        self.threadpool.start(process_worker)

        system_info_worker = Worker(self.system_info)

        system_info_worker.signals.result.connect(self.print_output)
        system_info_worker.signals.finished.connect(self.thread_complete)
        system_info_worker.signals.progress.connect(self.progress_fn)

        self.threadpool.start(system_info_worker)

        process_check_worker = Worker(self.process_check_thread)

        process_check_worker.signals.result.connect(self.print_output)
        process_check_worker.signals.finished.connect(self.thread_complete)
        process_check_worker.signals.progress.connect(self.progress_fn)

        self.threadpool.start(process_check_worker)


    def process_check_thread(self, progress_callback):
        while self.pid_count == len(psutil.pids()):
            sleep(5)
        self.activities()
        self.process_check_thread(progress_callback)

    def print_output(self, s):
        print(s)
    
    
    def thread_complete(self):
        print('Thread complete')


    def progress_fn(self, n):
        print('%d%% done' % n)


    def network(self):
        #netstat
        for i in psutil.net_if_stats():
            z = psutil.net_if_stats()
            rowPosition = self.ui.tableWidget_4.rowCount()
            self.ui.tableWidget_4.insertRow(rowPosition)

            self.create_table_widget(rowPosition, 0, i, 'tableWidget_4')
            self.create_table_widget(rowPosition, 1, str(z[i].isup), 'tableWidget_4')
            self.create_table_widget(rowPosition, 2, str(z[i].duplex), 'tableWidget_4')
            self.create_table_widget(rowPosition, 3, str(z[i].speed), 'tableWidget_4')
            self.create_table_widget(rowPosition, 4, str(z[i].mtu), 'tableWidget_4')

        #netIO
        for i in psutil.net_io_counters(pernic=True):
            z = psutil.net_io_counters(pernic=True)
            rowPosition = self.ui.tableWidget_5.rowCount()
            self.ui.tableWidget_5.insertRow(rowPosition)

            self.create_table_widget(rowPosition, 0, i, 'tableWidget_5')
            self.create_table_widget(rowPosition, 1, str(z[i].bytes_sent), 'tableWidget_5')
            self.create_table_widget(rowPosition, 2, str(z[i].bytes_recv), 'tableWidget_5')
            self.create_table_widget(rowPosition, 3, str(z[i].packets_sent), 'tableWidget_5')
            self.create_table_widget(rowPosition, 4, str(z[i].packets_recv), 'tableWidget_5')
            self.create_table_widget(rowPosition, 5, str(z[i].errin), 'tableWidget_5')
            self.create_table_widget(rowPosition, 6, str(z[i].errout), 'tableWidget_5')
            self.create_table_widget(rowPosition, 7, str(z[i].dropin), 'tableWidget_5')
            self.create_table_widget(rowPosition, 8, str(z[i].dropout), 'tableWidget_5')

        #net addresses
        for i in psutil.net_if_addrs():
            z = psutil.net_if_addrs()
            for j in z[i]:
                rowPosition = self.ui.tableWidget_6.rowCount()
                self.ui.tableWidget_6.insertRow(rowPosition)

                self.create_table_widget(rowPosition, 0, str(i), 'tableWidget_6')
                self.create_table_widget(rowPosition, 1, str(j.family), 'tableWidget_6')
                self.create_table_widget(rowPosition, 2, str(j.address), 'tableWidget_6')
                self.create_table_widget(rowPosition, 3, str(j.netmask), 'tableWidget_6')
                self.create_table_widget(rowPosition, 4, str(j.broadcast), 'tableWidget_6')
                self.create_table_widget(rowPosition, 5, str(j.ptp), 'tableWidget_6')
        
        #net connections
        for i in psutil.net_connections():
            z = psutil.net_connections()
            rowPosition = self.ui.tableWidget_7.rowCount()
            self.ui.tableWidget_7.insertRow(rowPosition)

            if 'win' in str(sys.platform):
                self.create_table_widget(rowPosition, 0, 'Not supported', 'tableWidget_7')
            else:
                self.create_table_widget(rowPosition, 0, str(i.fd), 'tableWidget_7')
            self.create_table_widget(rowPosition, 1, str(i.family), 'tableWidget_7')
            self.create_table_widget(rowPosition, 2, str(i.type), 'tableWidget_7')
            self.create_table_widget(rowPosition, 3, str(i.laddr), 'tableWidget_7')
            self.create_table_widget(rowPosition, 4, str(i.raddr), 'tableWidget_7')
            self.create_table_widget(rowPosition, 5, str(i.status), 'tableWidget_7')


    def sensors(self):
        if 'linux' in sys.platform:
            for i in psutil.sensors_temperarures():
                for j in psutil.sensors_temperatures()[i]:
                    rowPosition = self.ui.tableWidget_3.rowCount()
                    self.ui.tableWidget_3.insertRow(rowPosition)

                    self.create_table_widget(rowPosition, 0, i, 'tableWidget_3')
                    self.create_table_widget(rowPosition, 1, j.label, 'tableWidget_3')
                    self.create_table_widget(rowPosition, 2, str(j.current), 'tableWidget_3')
                    self.create_table_widget(rowPosition, 3, str(j.high), 'tableWidget_3')
                    self.create_table_widget(rowPosition, 4, str(j.critical), 'tableWidget_3')

                    temp_per = (j.current / j.high) * 100

                    progressBar = QtWidgets.QProgressBar(self.ui.tableWidget_3)
                    progressBar.setObjectName(u'progressBar')
                    progressBar.setValue(temp_per)
        else:
            rowPosition = self.ui.tableWidget_3.rowCount()
            self.ui.tableWidget_3.insertRow(rowPosition)
            
            self.create_table_widget(rowPosition, 0, 'Not supported', 'tableWidget_3')
            self.create_table_widget(rowPosition, 1, 'N/A', 'tableWidget_3')
            self.create_table_widget(rowPosition, 2, 'N/A', 'tableWidget_3')
            self.create_table_widget(rowPosition, 3, 'N/A', 'tableWidget_3')
            self.create_table_widget(rowPosition, 4, 'N/A', 'tableWidget_3')


    def storage(self):
        storage = psutil.disk_partitions(all = False)

        for el in storage:
            rowPosition = self.ui.tableWidget_2.rowCount()
            self.ui.tableWidget_2.insertRow(rowPosition)
            self.create_table_widget(rowPosition, 0, el.device, 'tableWidget_2')
            self.create_table_widget(rowPosition, 1, el.mountpoint, 'tableWidget_2')
            self.create_table_widget(rowPosition, 2, el.fstype, 'tableWidget_2')
            self.create_table_widget(rowPosition, 3, el.opts, 'tableWidget_2')

            if 'linux' in str(sys.platform):
                self.create_table_widget(rowPosition, 4, el.maxfile, 'tableWidget_2')
                self.create_table_widget(rowPosition, 5, el.maxpath, 'tableWidget_2')
            else:
                self.create_table_widget(rowPosition, 4, 'Not supported', 'tableWidget_2')
                self.create_table_widget(rowPosition, 5, 'Not supported', 'tableWidget_2')

            disk_usage = shutil.disk_usage(el.mountpoint)

            self.create_table_widget(rowPosition, 6, (str(f'{(disk_usage.total / (1024 * 1024 * 1024)):.2f}') + ' GB'), 'tableWidget_2')
            self.create_table_widget(rowPosition, 8, (str(f'{(disk_usage.free / (1024 * 1024 * 1024)):.2f}') + ' GB'), 'tableWidget_2')
            self.create_table_widget(rowPosition, 7, (str(f'{(disk_usage.used / (1024 * 1024 * 1024)):.2f}') + ' GB'), 'tableWidget_2')

            
            full_disk = (disk_usage.used / disk_usage.total) * 100
            progressBar = QtWidgets.QProgressBar(self.ui.tableWidget_2)
            progressBar.setObjectName(u'progressBar')
            progressBar.setValue(full_disk)
            self.ui.tableWidget_2.setCellWidget(rowPosition, 9, progressBar)
            

    def create_table_widget(self, rowPosition, columnPosition, text, tableName):
        qtablewidgetitem = QtWidgets.QTableWidgetItem()

        getattr(self.ui, tableName).setItem(rowPosition, columnPosition, qtablewidgetitem)
        qtablewidgetitem = getattr(self.ui, tableName).item(rowPosition, columnPosition)

        qtablewidgetitem.setText(text)


    def activities(self):
        self.ui.tableWidget.setRowCount(0)
        for x in psutil.pids():
            rowPosition = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(rowPosition)
            try:
                process = psutil.Process(x)
                self.create_table_widget(rowPosition, 0, str(process.pid), 'tableWidget')
                self.create_table_widget(rowPosition, 1, process.name(), 'tableWidget')
                self.create_table_widget(rowPosition, 2, process.status(), 'tableWidget')
                self.create_table_widget(rowPosition, 3, str(datetime.datetime.utcfromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S')), 'tableWidget')
            except Exception as error:
                print(error)
        self.pid_count = len(psutil.pids())
        self.ui.search_line.textChanged.connect(self.findName)
        self.ui.pushButton_6.clicked.connect(self.findName)
    

    def findName(self):
        name = str(self.ui.search_line.text().lower())
        for row in range(int(self.ui.tableWidget.rowCount())):
            try:
                item = self.ui.tableWidget.item(row, 1)
                self.ui.tableWidget.setRowHidden(row, name not in str(item.text().lower()))
            except:
                print('Ошибка в FindName')


    def system_info(self, progress_callback):
        while True:
            time = datetime.datetime.now().strftime("%I:%M:%S %p")
            self.ui.system_time.setText(str(time))
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            self.ui.system_date.setText(str(date))
            self.ui.machine.setText(platform.machine())
            self.ui.system_version.setText(platform.version())
            self.ui.platform.setText(platform.platform())
            self.ui.system.setText(platform.system())
            self.ui.processor.setText(platform.processor())
            sleep(1)


    def cpu_and_ram(self, progress_callback):
        
        while True:
            #RAM Calculating
            totalRam = psutil.virtual_memory()[0]
            totalRam = totalRam / (1024 * 1024 * 1024)
            self.ui.total_ram.setText(str(f'{totalRam:.2f}' + ' GB'))

            availableRam = psutil.virtual_memory()[1]
            availableRam = availableRam / (1024 * 1024* 1024)
            self.ui.available_ram.setText(str(f'{availableRam:.2f}' + ' GB'))


            ramUsed = psutil.virtual_memory()[3]
            ramUsed = ramUsed / (1024 * 1024 * 1024)
            self.ui.used_ram.setText(str(f'{ramUsed:.2f}' + ' GB'))


            freeRam = psutil.virtual_memory()[4]
            freeRam = freeRam / (1024 * 1024 * 1024)
            self.ui.free_ram.setText(str(f'{freeRam:.2f}' + ' GB'))


            #CPU Calculating
            cpulogical = psutil.cpu_count()
            self.ui.cpu_log.setText(str(cpulogical))

            cpuper = psutil.cpu_percent()
            self.ui.cpu_per.setText(str(cpuper) + '%')

            cpuphys = psutil.cpu_count(logical = False)
            self.ui.cpu_phys.setText(str(cpuphys))

            self.ui.cpu_usage.rpb_setMaximum(100)

            self.ui.cpu_usage.rpb_setValue(cpuper)

            self.ui.cpu_usage.rpb_setBarStyle('Hybrid2')

            self.ui.cpu_usage.rpb_setLineColor((255, 30, 99))

            self.ui.cpu_usage.rpb_setPieColor((45, 74, 83))

            self.ui.cpu_usage.rpb_setTextFormat('Percentage')

            self.ui.cpu_usage.rpb_setTextFont('Century Gothic')

            self.ui.cpu_usage.rpb_setLineWidth(15)

            self.ui.cpu_usage.rpb_setPathWidth(15)

            self.ui.cpu_usage.rpb_setLineCap('RoundCap')

            self.ui.ram_usage.spb_setMinimum((0,0,0))

            self.ui.ram_usage.spb_setMaximum((totalRam, totalRam, totalRam))

            self.ui.ram_usage.spb_setValue((availableRam, ramUsed, freeRam))

            self.ui.ram_usage.spb_lineColor(((6,233,38), (6,201,233), (233,6,201)))

            self.ui.ram_usage.spb_setInitialPos(('West', 'West', 'West'))

            self.ui.ram_usage.spb_lineWidth(15)

            self.ui.ram_usage.spb_setGap(15)

            self.ui.ram_usage.spb_lineStyle(('SolidLine', 'SolidLine', 'SolidLine'))

            self.ui.ram_usage.spb_lineCap(('RoundCap', 'RoundCap', 'RoundCap'))

            self.ui.ram_usage.spb_setPathHidden(True)

            sleep(1)


    def secondstohour(self, sec):
        mm, ss = divmod(sec, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d {H:M:S}" % (hh, mm, ss)


    def battery(self, progress_callback):   #Проверка функциональности батареи и инфа о ней
        while True:
            batt = psutil.sensors_battery()

            if not hasattr(psutil, 'sensors_battery'):
                self.ui.battery_status.setText('Платформа не поддерживается')


            if batt is None:
                self.ui.battery_status.setText('Батарея не установлена')

            else:
            
                if batt.power_plugged:
                    self.ui.battery_charge.setText(str(round(batt.percent, 2))+'%')
                    self.ui.battery_timeleft.setText('N/A')
                    if batt.percent < 100:
                        self.ui.battery_status.setText('Charging')
                    else:
                        self.ui.battery_status.setText('Fully Charged')
                    self.ui.battery_plugged.setText('Yes')

                else:
                    self.ui.battery_charge.setText(str(round(batt.percent,2)) + '%')
                    self.ui.battery_timeleft.setText(self.secondstohour(batt.secsleft))
                    if batt.percent < 100:
                        self.ui.battery_status.setText('Discharging')
                    else:
                        self.ui.battery_status.setText('Fully Charged')
                    self.ui.battery_plugged.setText('No')

            self.ui.battery_usage.rpb_setMaximum(100)

            if batt == None:
                self.ui.battery_usage.rpb_setValue(666)
            else:
                self.ui.battery_usage.rpb_setValue(batt.percent)

            self.ui.battery_usage.rpb_setBarStyle('Hybrid2')

            self.ui.battery_usage.rpb_setLineColor((255, 30, 99))

            self.ui.battery_usage.rpb_setPieColor((45,74,83))

            self.ui.battery_usage.rpb_setTextColor((255,255,255))

            self.ui.battery_usage.rpb_setInitialPos('West')

            self.ui.battery_usage.rpb_setTextFormat('Percentage')

            self.ui.battery_usage.rpb_setLineWidth(15)

            self.ui.battery_usage.rpb_setPathWidth(15)

            self.ui.battery_usage.rpb_setLineCap('RoundCap')

            sleep(1)
        

    def applyButtonStyle(self):
        for el in self.ui.menu_frame.findChildren(QtWidgets.QPushButton):
            if el.objectName() != self.sender().objectName():
                el.setStyleSheet('border-bottom: 2px solid;'
                                 'color: rgb(0,0,0);'
                                 'font: 14pt "Century Gothic')


        self.sender().setStyleSheet('border-bottom: 2px solid;'
                                    'border-color: rgb(255, 255, 255);'
                                    'color: white;'
                                    'font: 14pt "Century Gothic"'
                                    )
        return 


    def slideLeftMenu(self):
        width = self.ui.left_main_frame.width()

        if width == 40:
            newWidth = 200
        else:
            newWidth = 40

        self.animation = QtCore.QPropertyAnimation(self.ui.left_main_frame, b'minimumWidth')
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()

    def slideRightMenu(self):
        width = self.ui.right_main_frame.width()

        if width == 40:
            newWidth = 200
            self.ui.label.setStyleSheet('color: (255,255,255);')
            self.ui.label_18.setStyleSheet('color: (255, 255, 255);')
            
        else:
            newWidth = 40
            self.ui.label.setStyleSheet('color: black;')
            self.ui.label_18.setStyleSheet('color: black;')

        self.animation = QtCore.QPropertyAnimation(self.ui.right_main_frame, b'minimumWidth')
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()
    

    def restore_or_maximize_window(self):
        if self.isMaximized():
            self.showNormal()
        else: 
            self.showMaximized()

    def mousePressEvent(self, event):
       if event.button() == QtGui.Qt.LeftButton:
           self.old_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtGui.Qt.LeftButton:
            self.old_pos = None

    def mouseMoveEvent(self, event):
        if not self.old_pos:
            return

        delta = event.pos() - self.old_pos
        self.move(self.pos() + delta)
    
    def mouseDoubleClickEvent(self, event):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    
    def delete_row(self):
        row = self.ui.tableWidget.currentRow()
        if row > -1:
            self.ui.tableWidget.removeRow(row)
            self.ui.tableWidget.selectionModel().clearCurrentIndex()
            self.ui.tableWidget.setRowCount(0)


    def activity_type_check(self, type):
        if type == 'suspend':
            psutil.Process(int(self.ui.tableWidget.item(self.ui.tableWidget.currentItem().row(), self.ui.tableWidget.currentItem().column()).text())).suspend()
            self.ui.tableWidget.item(self.ui.tableWidget.currentItem().row(), 2).setText('stopped')
        elif type == 'resume':
            psutil.Process(int(self.ui.tableWidget.item(self.ui.tableWidget.currentItem().row(), self.ui.tableWidget.currentItem().column()).text())).resume()
            self.ui.tableWidget.item(self.ui.tableWidget.currentItem().row(), 2).setText('running')
        elif type == 'terminate':
            psutil.Process(int(self.ui.tableWidget.item(self.ui.tableWidget.currentItem().row(), self.ui.tableWidget.currentItem().column()).text())).terminate()
            self.ui.search_line.setText('')
            self.ui.tableWidget.setRowCount(0)
            self.activities()
        elif type == 'kill':
            psutil.Process(int(self.ui.tableWidget.item(self.ui.tableWidget.currentItem().row(), self.ui.tableWidget.currentItem().column()).text())).kill()
            self.delete_row()
            self.ui.search_line.setText('')
            self.activities()
            

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
    



