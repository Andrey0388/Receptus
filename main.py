import io
import sys
import sqlite3
import hashlib

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog


class RegisterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Загружаем дизайн
        uic.loadUi('register.ui', self)
        self.setWindowTitle('Register')
        self.signButton.clicked.connect(self.sign)
        self.signupButton.clicked.connect(self.signUp)

    def sign(self):
        name = self.nameEdit.text()
        password = self.passwordEdit.text()
        if name and password:
            # Хэшируем строки
            name = hashlib.sha1(name.encode("utf-8")).hexdigest()
            password = hashlib.sha1(password.encode("utf-8")).hexdigest()

            # Открываем базу данных и проверяем соотвествие name и password
            con = sqlite3.connect("recepts_db.sqlite")
            cur = con.cursor()
            result = cur.execute("""SELECT * FROM Users
                WHERE Name = ? and Password = ?""", (name, password,)).fetchall()
            if result:
                # Имя юзера
                UserName = result[0][0]
                # Пароль юзера
                UserPassword = result[0][1]
                # Доступ юзера
                UserKeys = result[0][2]
                self.Mm = MainWindow(UserName, UserPassword, UserKeys)
                self.Mm.show()
                self.close()
            else:
                self.statusbar.showMessage('Неверный логин или пароль!', 5000)
            con.close()
        else:
            self.statusbar.showMessage('Имя или пароль пустые!', 5000)

    def signUp(self):
        name = self.nameEdit.text()
        password = self.passwordEdit.text()
        # Открываем базу данных и добавляем нового юзера, если имя и пароль не пустые строки
        if name and password:
            # Хэшируем строки
            name = hashlib.sha1(name.encode("utf-8")).hexdigest()
            password = hashlib.sha1(password.encode("utf-8")).hexdigest()

            con = sqlite3.connect("recepts_db.sqlite")
            cur = con.cursor()
            # Только если данного пользователя не существует добавляем и подтверждаем
            result = cur.execute("""SELECT * FROM Users
                            WHERE Name = ?""", (name,)).fetchall()
            if not result:
                result1 = cur.execute("""INSERT INTO Users(Name,Password,Keys) VALUES(?,?,'1,2,3,4,5,6')""",
                                      (name, password,))
                con.commit()
                self.Uw = UraWindow()
                self.Uw.show()
            else:
                self.statusbar.showMessage('Этот логин занят!', 5000)
        else:
            self.statusbar.showMessage('Имя или пароль пустые!', 5000)
        con.close()


class MainWindow(QMainWindow):
    def __init__(self, UserName, UserPassword, UserKeys):
        super().__init__()
        # Загружаем дизайн
        uic.loadUi('recept.ui', self)
        self.setWindowTitle('Receptus')

        # Кнопка открывает окно с фильтрами
        self.filtresButton.clicked.connect(self.openFilters)

        # Кнопки добавить и удалить открывают окна добавления и удаления рецепта
        self.addButton.clicked.connect(self.addRecept)
        self.deleteButton.clicked.connect(self.deleteRecept)
        self.sendButton.clicked.connect(self.sendRecept)

        # Добавим юзера, его пароль и доступ юзера
        self.UserName = UserName
        self.UserPassword = UserPassword
        self.UserKeys = UserKeys

        # Кнопка обновить будет обновлять содержимое списка рецептов
        self.refreshButton.clicked.connect(self.refreshRecepts)
        # Сейчас список пустой поэтому заполним его с помощью обновления
        self.refreshRecepts()

        # По двойному нажатию открывается окно с рецептом
        self.recepts.doubleClicked.connect(self.openRecept)

    def openFilters(self):
        # UserKeys
        con = sqlite3.connect("recepts_db.sqlite")
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM Users
                                WHERE Name = ? and Password = ?""", (self.UserName, self.UserPassword,)).fetchall()
        self.UserKeys = result[0][2]
        if self.UserKeys:
            self.UserKeys = list(map(int, self.UserKeys.split(',')))
        else:
            self.UserKeys = list()

        # открываем окно фильтров
        self.ex1 = FiltersWindow(self.recepts, self.UserKeys)
        self.ex1.show()

    def openRecept(self):
        # В переменной item_name у нас будет индивидуальное название рецепта
        item_name = self.recepts.currentItem().text()
        # Откроем базу данных
        con = sqlite3.connect("recepts_db.sqlite")
        cur = con.cursor()
        # По названию найдем наш рецепт
        result = cur.execute("""SELECT * FROM Recepts
            WHERE Name = ?""", (item_name,)).fetchall()
        for id, name, category, recept in result:
            # Теперь можем открыть новое окно передав в него айди, имя, категорию и сам рецепт
            # Старое окно автоматически закрывается
            self.Rw = ReceptWindow(id, name, category, recept)
            self.Rw.show()
        con.close()

    def refreshRecepts(self):
        # UserKeys
        con = sqlite3.connect("recepts_db.sqlite")
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM Users
                                        WHERE Name = ? and Password = ?""",
                             (self.UserName, self.UserPassword,)).fetchall()
        self.UserKeys = result[0][2]
        if self.UserKeys:
            self.UserKeys = list(map(int, self.UserKeys.split(',')))
        else:
            self.UserKeys = list()

        # Добавляем в поле рецептов все рецепты из базы данных
        # только если у данного юзера права на той или иной рецепт
        self.recepts.clear()  # Если до этого тут были рецепты, то мы должны их убрать
        result = cur.execute("""SELECT * FROM Recepts""").fetchall()
        for id, name, category, recept in result:
            if id in self.UserKeys:
                self.recepts.addItem(name)
        con.close()

    def addRecept(self):
        # UserKeys
        con = sqlite3.connect("recepts_db.sqlite")
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM Users
                                WHERE Name = ? and Password = ?""", (self.UserName, self.UserPassword,)).fetchall()
        self.UserKeys = result[0][2]
        if self.UserKeys:
            self.UserKeys = list(map(int, self.UserKeys.split(',')))
        else:
            self.UserKeys = list()

        self.Aw = AddWindow(self.UserName, self.UserPassword, self.UserKeys)
        self.Aw.show()

    def deleteRecept(self):
        self.Dw = DeleteWindow(self.UserName, self.UserPassword, self.UserKeys)
        self.Dw.show()

    def sendRecept(self):
        self.Sw = SendWindow(self.UserName, self.UserPassword, self.UserKeys)
        self.Sw.show()


class FiltersWindow(QMainWindow):
    def __init__(self, recepts, UserKeys):
        super().__init__()
        # Загружаем дизайн
        uic.loadUi('filtres.ui', self)
        self.setWindowTitle('Filters')

        # Чтобы обращаться к списку рецептов из другого окна
        # передадим его при создании класса и запишем в отдельную перменную
        self.recepts = recepts

        # Доступ юзера
        self.UserKeys = UserKeys

        # На нажатие кнопки будут применяться выбранные фильтры
        self.filterButton.clicked.connect(self.filterActivation)

    def filterActivation(self):
        # Создадим условие которое будем дополнять исходя из выбранных чекбоксов
        condition = '''SELECT * FROM Recepts
    WHERE '''
        # если мы добавим что-то в условие изменим флаг на True
        flag = True
        # проверяем чекбоксы и добавляем соответсвующие условия в condition
        if self.checkBox_1.checkState():
            condition += "Category = 'Завтрак'"
            # условие изменилось, а значит флаг ставим True
            flag = False
        if self.checkBox_2.checkState():
            # Если мы до этого добавляли что-то в условие то нужно ставить разделитель OR
            if not flag:
                condition += ' OR '
            condition += "Category = 'Обед'"
            flag = False
        if self.checkBox_3.checkState():
            if not flag:
                condition += ' OR '
            condition += "Category = 'Ужин'"
            flag = False
        if self.checkBox_4.checkState():
            if not flag:
                condition += ' OR '
            condition += "Category = 'Напитки'"
            flag = False
        if self.checkBox_5.checkState():
            if not flag:
                condition += ' OR '
            condition += "Category = 'Десерты'"
            flag = False
        if self.checkBox_6.checkState():
            if not flag:
                condition += ' OR '
            condition += "Category = 'Салаты'"
            flag = False

        # Если фильтр изменялся, т. е. не пустой, ставим рецепты condition условием, иначе выводим все
        if not flag:
            # сначала очистим рецепты, а затем уже заполним используя condition
            self.recepts.clear()
            con = sqlite3.connect("recepts_db.sqlite")
            cur = con.cursor()
            result = cur.execute(condition).fetchall()
            for id, name, category, recept in result:
                if id in self.UserKeys:
                    self.recepts.addItem(name)
            con.close()
        else:
            self.recepts.clear()
            con = sqlite3.connect("recepts_db.sqlite")
            cur = con.cursor()
            result = cur.execute("""SELECT * FROM Recepts""").fetchall()
            for id, name, category, recept in result:
                if id in self.UserKeys:
                    self.recepts.addItem(name)
            con.close()


class ReceptWindow(QMainWindow):
    def __init__(self, id, name, category, recept):
        super().__init__()
        # Загружаем дизайн
        uic.loadUi('rec.ui', self)
        # Теперь настраиваем окно под рецепт
        self.setWindowTitle(name)
        self.nameRecept.setText(f'{name} ({category})')
        self.overRecept.setText(recept)


class UraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Загружаем дизайн
        uic.loadUi('ura.ui', self)
        self.setWindowTitle('Ura')
        self.closeButton.clicked.connect(self.closeWindow)

    def closeWindow(self):
        self.close()


class AddWindow(QMainWindow):
    def __init__(self, UserName, UserPassword, UserKeys):
        super().__init__()
        # Загружаем дизайн
        uic.loadUi('add.ui', self)
        self.setWindowTitle('AddRecept')
        self.createButton.clicked.connect(self.createRecept)

        # Добавим юзера
        self.UserName = UserName
        self.UserPassword = UserPassword
        self.UserKeys = UserKeys

    def createRecept(self):
        name = self.nameEdit.text()
        category = self.categoryBox.currentText()
        recept = self.receptEdit.toPlainText()
        # Открываем базу данных и добавляем новый рецепт, если имя и пароль не пустые строки
        if name and recept:
            # Если данный рецепт уже существует то добавлять его не надо
            con = sqlite3.connect("recepts_db.sqlite")
            cur = con.cursor()
            result = cur.execute("""SELECT * FROM Recepts
                            WHERE Name = ?""", (name,)).fetchall()
            if not result:
                # Добавляем новый рецепт и подтверждаем создание
                result1 = cur.execute("""INSERT INTO Recepts(Name,Category,Recept) VALUES(?,?,?)""",
                                      (name, category, recept,))
                con.commit()

                # Находим только что созданный в базе данных рецепт
                # и в переменную new_recept_key записываем выданный базой данных индивидуальный ей айди
                result2 = cur.execute("""SELECT * FROM Recepts WHERE Name = ?""", (name,)).fetchall()
                new_recept_key = result2[0][0]

                # Теперь у юзера будет доступ это его прошлые ключи и новый ключ
                new_keys = ','.join(list(map(str, self.UserKeys + [new_recept_key])))
                # Изменяем доступ юзера по имени и паролю (они не бывают идентичные для двух пользователей)
                result3 = cur.execute("""UPDATE Users SET Keys = ? WHERE Name = ? and Password = ?""",
                                      (new_keys, self.UserName, self.UserPassword,))
                con.commit()

                self.Uw = UraWindow()
                self.Uw.show()

                self.close()
            else:
                self.statusbar.showMessage('Такой рецепт уже существует! Измените название!', 5000)

            con.close()

        else:
            self.statusbar.showMessage('Название рецепта или рецепт пустые!', 5000)


class DeleteWindow(QMainWindow):
    def __init__(self, UserName, UserPassword, UserKeys):
        super().__init__()
        # Загружаем дизайн
        uic.loadUi('delete.ui', self)
        self.setWindowTitle('DeleteRecept')
        self.deleteButton.clicked.connect(self.deleteRecept)

        # Добавим юзера
        self.UserName = UserName
        self.UserPassword = UserPassword
        self.UserKeys = UserKeys

        # Заполним бокс рецептами
        con = sqlite3.connect("recepts_db.sqlite")
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM Recepts""").fetchall()
        for id, name, category, recept in result:
            # Теперь добаивм в бокс все доступные пользователю рецепты
            if id in self.UserKeys:
                self.deleteBox.addItem(name)
        con.commit()

    def deleteRecept(self):
        # Рецепт который хочет удалить пользователь
        delete_recept = self.deleteBox.currentText()
        if delete_recept:
            # Спрашиваем у пользователя подтверждение на удаление элементов
            valid = QMessageBox.question(self, '', "Действительно удалить рецепт " + delete_recept,
                                         QMessageBox.Yes, QMessageBox.No)
            # Если пользователь ответил утвердительно, удаляем доступ к данному рецепту.
            if valid == QMessageBox.Yes:
                con = sqlite3.connect("recepts_db.sqlite")
                cur = con.cursor()

                # id delete_recept
                result = cur.execute("""SELECT * FROM Recepts WHERE Name = ?""", (delete_recept,)).fetchall()
                id_delete_recept = result[0][0]
                # Новый доступ пользователя
                self.UserKeys.remove(id_delete_recept)
                new_keys = ','.join(list(map(str, self.UserKeys)))
                # Изменяем доступ юзера по имени и паролю (они не бывают идентичные для двух пользователей)
                result3 = cur.execute("""UPDATE Users SET Keys = ? WHERE Name = ? and Password = ?""",
                                      (new_keys, self.UserName, self.UserPassword,))
                con.commit()
                self.close()


class SendWindow(QMainWindow):
    def __init__(self, UserName, UserPassword, UserKeys):
        super().__init__()
        # Загружаем дизайн
        uic.loadUi('send.ui', self)
        self.setWindowTitle('SendRecept')
        self.sendButton.clicked.connect(self.sendRecept)

        # Добавим юзера
        self.UserName = UserName
        self.UserPassword = UserPassword
        self.UserKeys = UserKeys

        # Заполним бокс рецептами
        con = sqlite3.connect("recepts_db.sqlite")
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM Recepts""").fetchall()
        for id, name, category, recept in result:
            # Теперь добаивм в бокс все доступные пользователю рецепты
            if id in self.UserKeys:
                self.sendBox.addItem(name)
        con.commit()

    def sendRecept(self):
        # Рецепт который хочет отправить пользователь
        send_recept = self.sendBox.currentText()
        sUser = self.sendEdit.text()
        # Хэшируем строки
        sUser = hashlib.sha1(sUser.encode("utf-8")).hexdigest()
        # Открываем базу данных и проверяем на наличие данного пользователя
        con = sqlite3.connect("recepts_db.sqlite")
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM Users
                            WHERE Name = ?""", (sUser,)).fetchall()
        if result:
            # Доступ юзера
            if result[0][2]:
                UserKeys = result[0][2].split(",")
            else:
                UserKeys = list()
            # Спрашиваем у пользователя подтверждение на отправление элементов
            valid = QMessageBox.question(self, '', "Действительно отправить рецепт " + send_recept, QMessageBox.Yes,
                                         QMessageBox.No)
            # Если пользователь ответил утвердительно
            if valid == QMessageBox.Yes:
                # Находим в базе данных рецепт
                # и в переменную send_recept_key записываем выданный базой данных индивидуальный ей айди
                result2 = cur.execute("""SELECT * FROM Recepts WHERE Name = ?""", (send_recept,)).fetchall()
                send_recept_key = result2[0][0]
                if send_recept_key not in UserKeys:
                    # Теперь у юзера будет доступ это его прошлые ключи и новый ключ
                    new_keys = ','.join(list(map(str, UserKeys + [send_recept_key])))
                    # Изменяем доступ юзера по имени (он не бывает идентичный для двух пользователей)
                    result3 = cur.execute("""UPDATE Users SET Keys = ? WHERE Name = ?""",
                                          (new_keys, sUser,))
                    con.commit()

                self.Uw = UraWindow()
                self.Uw.show()

                self.close()
        else:
            self.statusbar.showMessage('Данного пользователя не существует!', 5000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    reg = RegisterWindow()
    reg.show()
    sys.exit(app.exec_())
