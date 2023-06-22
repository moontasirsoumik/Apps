import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from ui import Ui_MainWindow
from PyQt5 import QtCore
from fbprophet import Prophet
import matplotlib.pyplot as plt
import yfinance as yf
import seaborn as sns


class Main_feed(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(__class__, self).__init__()
        self.setupUi(self)
        self.showNormal()

        self.predict_pushButton.clicked.connect(
            lambda: self.predict_btn_clicked())
        self.analyze_pushButton.clicked.connect(
            lambda: self.analyze_btn_clicked())
        self.plot_pushButton.clicked.connect(lambda: self.plot_btn_clicked())

        self.show_seasonality_btn = False
        self.show_accuracy_btn = False

        self.qt_initiator()
        self.conversion()
        self.analyze()

    def qt_initiator(self):
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")
        self.crypto_comboBox.addItem("")

        self.training_comboBox.addItem("")
        self.training_comboBox.addItem("")
        self.training_comboBox.addItem("")
        self.training_comboBox.addItem("")
        self.training_comboBox.addItem("")
        self.training_comboBox.addItem("")

        self.predicted_comboBox.addItem("")
        self.predicted_comboBox.addItem("")
        self.predicted_comboBox.addItem("")
        self.predicted_comboBox.addItem("")
        self.predicted_comboBox.addItem("")
        self.predicted_comboBox.addItem("")

        self.currency_comboBox.addItem("")
        self.currency_comboBox.addItem("")
        self.currency_comboBox.addItem("")

        _translate = QtCore.QCoreApplication.translate

        self.crypto_comboBox.setItemText(0, _translate("MainWindow", "BTC"))
        self.crypto_comboBox.setItemText(1, _translate("MainWindow", "ETH"))
        self.crypto_comboBox.setItemText(2, _translate("MainWindow", "BNB"))
        self.crypto_comboBox.setItemText(3, _translate("MainWindow", "USDT"))
        self.crypto_comboBox.setItemText(4, _translate("MainWindow", "SOL1"))
        self.crypto_comboBox.setItemText(5, _translate("MainWindow", "ADA"))
        self.crypto_comboBox.setItemText(6, _translate("MainWindow", "XRP"))
        self.crypto_comboBox.setItemText(7, _translate("MainWindow", "DOT1"))
        self.crypto_comboBox.setItemText(8, _translate("MainWindow", "USDC"))
        self.crypto_comboBox.setItemText(9, _translate("MainWindow", "HEX"))
        self.crypto_comboBox.setItemText(10, _translate("MainWindow", "DOGE"))
        self.crypto_comboBox.setItemText(11, _translate("MainWindow", "AVAX"))
        self.crypto_comboBox.setItemText(12, _translate("MainWindow", "SHIB"))
        self.crypto_comboBox.setItemText(13, _translate("MainWindow", "CRO"))
        self.crypto_comboBox.setItemText(14, _translate("MainWindow", "LUNA1"))
        self.crypto_comboBox.setItemText(15, _translate("MainWindow", "LTC"))
        self.crypto_comboBox.setItemText(16, _translate("MainWindow", "UNI3"))
        self.crypto_comboBox.setItemText(17, _translate("MainWindow", "LINK"))
        self.crypto_comboBox.setItemText(18, _translate("MainWindow", "MATIC"))
        self.crypto_comboBox.setItemText(19, _translate("MainWindow", "BCH"))
        self.crypto_comboBox.setItemText(20, _translate("MainWindow", "ALGO"))
        self.crypto_comboBox.setItemText(21, _translate("MainWindow", "MANA"))
        self.crypto_comboBox.setItemText(22, _translate("MainWindow", "AXS"))
        self.crypto_comboBox.setItemText(23, _translate("MainWindow", "EGLD"))
        self.crypto_comboBox.setItemText(24, _translate("MainWindow", "VET"))

        self.training_comboBox.setItemText(
            0, _translate("MainWindow", "1 month"))
        self.training_comboBox.setItemText(
            1, _translate("MainWindow", "2 months"))
        self.training_comboBox.setItemText(
            2, _translate("MainWindow", "3 months"))
        self.training_comboBox.setItemText(
            3, _translate("MainWindow", "6 months"))
        self.training_comboBox.setItemText(
            4, _translate("MainWindow", "1 year"))
        self.training_comboBox.setItemText(
            5, _translate("MainWindow", "All Data"))

        self.predicted_comboBox.setItemText(
            0, _translate("MainWindow", "1 week"))
        self.predicted_comboBox.setItemText(
            1, _translate("MainWindow", "2 weeks"))
        self.predicted_comboBox.setItemText(
            2, _translate("MainWindow", "3 weeks"))
        self.predicted_comboBox.setItemText(
            3, _translate("MainWindow", "1 month"))
        self.predicted_comboBox.setItemText(
            4, _translate("MainWindow", "3 months"))
        self.predicted_comboBox.setItemText(
            5, _translate("MainWindow", "6 months"))

        self.currency_comboBox.setItemText(0, _translate("MainWindow", "EUR"))
        self.currency_comboBox.setItemText(1, _translate("MainWindow", "MYR"))
        self.currency_comboBox.setItemText(2, _translate("MainWindow", "USD"))
        self.predict_pushButton.setText(_translate("MainWindow", "Predict"))

    def conversion(self):
        from google_currency import convert
        x = convert('usd', 'myr', 1)

        num = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']
        conv = '0'
        for i in x:
            for p in num:
                if i == p:
                    conv = conv + i

        self.c = float(conv)

        x = convert('usd', 'eur', 1)

        num = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']
        conv = '0'
        for i in x:
            for p in num:
                if i == p:
                    conv = conv + i

        self.ec = float(conv)

    def analyze(self):
        self.main_label.setText("Starting App, Please wait")
        self.sub_label.setText("")
        QApplication.processEvents()

        self.currency = self.currency_comboBox.currentText()

        self.y = ['BTC', 'ETH', "BNB", "USDT", "SOL1", "ADA", "XRP", "USDC", "DOT1", "HEX", "DOGE", "AVAX",
                  "SHIB", "CRO", "LUNA1", "LTC", "UNI3", "LINK", "MATIC", "BCH", "ALGO", "MANA", "AXS", "EGLD", "VET"]
        copy_date = True
        for x in self.y:
            df = yf.download(f'{x}-USD')
            df.reset_index(inplace=True)
            df = df[['Date', 'Adj Close']]
            df.columns = ['Date', f'{x}']
            df.reset_index()
            df.set_index('Date', inplace=True)
            if copy_date == True:
                self.df2 = df
                copy_date = False
            else:
                self.df2[f'{x}'] = df[f'{x}']

        self.main_label.setText("Welcome to Crypto Currency Predictor")
        self.sub_label.setText("")
        QApplication.processEvents()

    def predict_btn_clicked(self):
        self.crypto = self.crypto_comboBox.currentText()

        self.training_weekly_seasonality = False
        self.training_yearly_seasonality = False

        if self.training_comboBox.currentText() == '1 month':
            self.training = 30
            self.training_weekly_seasonality = True
        elif self.training_comboBox.currentText() == '2 months':
            self.training = 60
            self.training_weekly_seasonality = True
        elif self.training_comboBox.currentText() == '3 months':
            self.training = 90
            self.training_weekly_seasonality = True
        elif self.training_comboBox.currentText() == '6 months':
            self.training = 180
            self.training_weekly_seasonality = True
        elif self.training_comboBox.currentText() == '1 year':
            self.training = 365
            self.training_yearly_seasonality = True
        elif self.training_comboBox.currentText() == 'All Data':
            self.training = -1
            self.training_yearly_seasonality = True

        if self.predicted_comboBox.currentText() == '1 week':
            self.predicted = 7
        elif self.predicted_comboBox.currentText() == '2 weeks':
            self.predicted = 14
        elif self.predicted_comboBox.currentText() == '3 weeks':
            self.predicted = 21
        elif self.predicted_comboBox.currentText() == '1 month':
            self.predicted = 30
        elif self.predicted_comboBox.currentText() == '3 months':
            self.predicted = 90
        elif self.predicted_comboBox.currentText() == '6 months':
            self.predicted = 180

        self.currency = self.currency_comboBox.currentText()

        QApplication.processEvents()
        self.main_label.setText("Predicting, Please wait")
        self.sub_label.setText("")

        self.prediction()

    def prediction(self):
        QApplication.processEvents()

        if self.show_seasonality_btn == False:
            self.seasonality_pushButton = QtWidgets.QPushButton(
                self.centralwidget)
            self.seasonality_pushButton.setMaximumSize(QtCore.QSize(250, 22))
            font = QtGui.QFont()
            font.setPointSize(12)
            self.seasonality_pushButton.setFont(font)
            self.seasonality_pushButton.setObjectName("seasonality_pushButton")
            self.verticalLayout_2.addWidget(self.seasonality_pushButton)
            self.seasonality_pushButton.setText("Show Seasonality")
            self.seasonality_pushButton.clicked.connect(
                lambda: self.seasonality_btn_clicked())
            self.show_seasonality_btn = True

        if self.show_accuracy_btn == False:
            self.accuracy_pushButton = QtWidgets.QPushButton(
                self.centralwidget)
            self.accuracy_pushButton = QtWidgets.QPushButton(
                self.centralwidget)
            self.accuracy_pushButton.setMaximumSize(QtCore.QSize(250, 22))
            font = QtGui.QFont()
            font.setPointSize(12)
            self.accuracy_pushButton.setFont(font)
            self.accuracy_pushButton.setObjectName("accuracy_pushButton")
            self.verticalLayout_2.addWidget(self.accuracy_pushButton)
            self.accuracy_pushButton.setText("Check Accuracy")
            self.accuracy_pushButton.clicked.connect(
                lambda: self.accuracy_btn_clicked())
            self.show_accuracy_btn = True

        self.seasonality_pushButton.setText("Show Seasonality")
        self.accuracy_pushButton.setText("Check Accuracy")

        df_p = self.df2.copy()
        df_p.reset_index(inplace=True)
        df_p = df_p[['Date', f'{self.crypto}']]

        if self.currency == 'MYR':
            df_p[f'{self.crypto}'] = self.c*df_p[f'{self.crypto}']
        elif self.currency == 'EUR':
            df_p[f'{self.crypto}'] = self.ec*df_p[f'{self.crypto}']

        if self.currency == 'MYR':
            df_p[f'{self.crypto}'] = self.c*df_p[f'{self.crypto}']

        df_p.columns = ['ds', 'y']
        if self.training != -1:
            df_p = df_p.tail(self.training)
        model = Prophet(weekly_seasonality=self.training_weekly_seasonality,
                        yearly_seasonality=self.training_yearly_seasonality)
        model.fit(df_p)
        model.component_modes

        future_dates = model.make_future_dataframe(periods=self.predicted)
        prediction = model.predict(future_dates)
        prediction.tail()
        fig = model.plot(prediction)
        model.plot(prediction, uncertainty=True)
        fig.savefig('1.jpg')
        fig = model.plot_components(prediction)
        fig.savefig('2.jpg')
        self.main_label.setPixmap(QtGui.QPixmap('1.jpg'))
        self.sub_label.setText(
            f"Showing predicted data using training data. y-axis represents price in {self.currency}, x-axis represents time")
        self.d = df_p.copy()
        self.p = prediction.copy()

    def seasonality_btn_clicked(self):
        QApplication.processEvents()

        if self.seasonality_pushButton.text() == "Show Seasonality":
            self.main_label.setPixmap(QtGui.QPixmap('2.jpg'))
            self.seasonality_pushButton.setText("Show Prediction")
            self.accuracy_pushButton.setText("Check Accuracy")
            if self.training_weekly_seasonality == True:
                self.sub_label.setText(
                    f"Showing trend and weekly seasonality of the price of {self.crypto}")
            elif self.training_yearly_seasonality == True:
                self.sub_label.setText(
                    f"Showing trend and yearly seasonality of the price of {self.crypto}")

        elif self.seasonality_pushButton.text() == "Show Prediction":
            self.main_label.setPixmap(QtGui.QPixmap('1.jpg'))
            self.seasonality_pushButton.setText("Show Seasonality")
            self.sub_label.setText(
                f"Showing predicted data using training data. y-axis represents price in {self.currency}, x-axis represents time")

    def analyze_btn_clicked(self):
        QApplication.processEvents()
        self.main_label.setText("Analyzing, Please wait")
        self.sub_label.setText("")
        self.correlation()

    def correlation(self):
        QApplication.processEvents()

        self.showMaximized()
        plt.figure(figsize=(15, 11))
        sns.set(font_scale=0.7)
        df3 = self.df2.pct_change().corr(method="pearson")
        sns_plot = sns.heatmap(df3, annot=True, cmap="coolwarm")
        sns.despine(bottom=True, left=True)

        fig = sns_plot.get_figure()
        fig.savefig("3.jpg")
        self.main_label.setPixmap(QtGui.QPixmap('3.jpg'))
        self.sub_label.setText(
            f"Showing correlation heatmap of all available crypto currencies (Fullscreen view recommended)")

    def plot_btn_clicked(self):
        QApplication.processEvents()
        self.main_label.setText("Plotting, Please wait")
        self.sub_label.setText("")
        self.plot()

    def plot(self):
        import matplotlib.pyplot as plt
        import seaborn as sns

        QApplication.processEvents()
        y = ['BTC', 'ETH', "BNB", "USDT", "SOL1", "ADA", "XRP", "USDC", "DOT1", "HEX", "DOGE", "AVAX",
             "SHIB", "CRO", "LUNA1", "LTC", "UNI3", "LINK", "MATIC", "BCH", "ALGO", "MANA", "AXS", "EGLD", "VET"]
        self.currency = self.currency_comboBox.currentText()

        if self.currency == 'MYR':
            df3 = self.df2.copy()
            for x in y:
                df3[f'{x}'] = self.c*df3[f'{x}']

        if self.currency == 'EUR':
            df3 = self.df2.copy()
            for x in y:
                df3[f'{x}'] = self.ec*df3[f'{x}']

        if self.currency == 'USD':
            df3 = self.df2.copy()

        plt.figure(figsize=(15, 8))
        fig = sns.lineplot(data=df3).get_figure()
        fig.savefig("4.jpg")
        self.main_label.setMinimumSize(QtCore.QSize(1300, 730))
        self.main_label.setPixmap(QtGui.QPixmap('4.jpg'))
        self.sub_label.setText(
            "Showing prices of all crypto currency in a lineplot")

    def accuracy_btn_clicked(self):
        self.main_label.setText("Checking Accuracy, Please wait")
        self.sub_label.setText("")
        QApplication.processEvents()
        self.accuracy()

    def accuracy(self):
        if self.accuracy_pushButton.text() == "Check Accuracy":
            self.accuracy_pushButton.setText("Show Prediction")
            self.seasonality_pushButton.setText("Show Seasonality")
            df_a = self.p.copy()

            df_a.drop(df_a.tail(self.predicted).index, inplace=True)

            da = self.d["y"].copy()
            df_a[f'{self.crypto}'] = da.values
            pp = df_a[['ds', 'yhat_lower',
                       'yhat_upper', 'yhat', f'{self.crypto}']]

            x = int(len(pp))
            acc = 0
            for q in range(x):
                if (pp.at[q, f'{self.crypto}'] < pp.at[q, 'yhat_lower']) or (pp.at[q, f'{self.crypto}'] > pp.at[q, 'yhat_upper']):
                    acc += 1

            acc = (100 - (acc/x)*100)
            self.main_label.setText(
                f"Accuracy for {self.crypto} is: \n {round(acc,2)}%")
            self.sub_label.setText(
                f"Accuracy may vary with every try. If accuracy is below your expectation, try predicting again")

        elif self.accuracy_pushButton.text() == "Show Prediction":
            self.main_label.setPixmap(QtGui.QPixmap('1.jpg'))
            self.accuracy_pushButton.setText("Check Accuracy")
            self.sub_label.setText(
                f"Showing predicted data using training data. y-axis represents price in {self.currency}, x-axis represents time")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    feed = Main_feed()
    sys.exit(app.exec_())
