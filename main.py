#!/bin/python3
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
import DimCondUI
from dimcond import dimcond


class UserInterface(QtWidgets.QMainWindow, DimCondUI.Ui_DimensionadorDeCondutores):
    def __init__(self):
        # This is needed here for variable and method access
        super().__init__()
        self.setupUi(self)  # Initialize a design
        self.pushButton.clicked.connect(self.mostrarcalculo)
    
    def execdimcond(self):

        msgerr = ''
        try:
            corrente = float(self.lineEdit.text().replace(",","."))
        except:
            msgerr = msgerr + "\nCampo: 'Corrente' contem caractere inválido"
        try:
            temperarura = float(self.lineEdit_2.text().replace(",","."))
            if not 4 < temperarura < 81:
                msgerr = msgerr + "\nCampo: 'Temperatura' contem valor fora do limite"
        except:
            msgerr = msgerr + "\nCampo: 'Temperatura' contem caractere inválido"
        try:
            comprimento = float(self.lineEdit_3.text().replace(",","."))
        except:
            msgerr = msgerr + "\nCampo: 'Comprimento do condutor' contem caractere inválido"
        try:
            numcirc = int(self.lineEdit_4.text())
        except:
            msgerr = msgerr + "\nCampo: 'Circuitos simultâneos' contem caractere inválido"
        try:
            tensaonom = float(self.lineEdit_5.text().replace(",","."))
        except:
            msgerr = msgerr + "\nCampo: 'Tensão nominal do circuito' contem caractere inválido"
        try:
            quedarelativa = float(self.lineEdit_6.text().replace(",","."))
        except:
            msgerr = msgerr + "\nCampo: 'Queda relativa de tensão' contem caractere inválido"
        #try:
        #   correntedecurto = 0
        # except:
        #     msgerr = msgerr + "\nCampo: 'Corrente de curto' contem caractere inválido"
        numcond =           int(self.comboBox.currentText())
        material =          self.comboBox_2.currentText()
        isolacao =          self.comboBox_3.currentText()
        metodo =            self.comboBox_4.currentText()
        tipoamb =           self.comboBox_5.currentText()
        try:
            correntedisjuntor = int(self.comboBox_7.currentText())
        except:
            correntedisjuntor = str(self.comboBox_7.currentText())
        tipcirc =           self.comboBox_6.currentText()
        if material == 'Cobre':
            material = 'cobre'
        elif material == 'Alumínio':
            material = 'aluminio'
        if isolacao == 'PVC':
            isolacao = 'pvc'
        elif isolacao == 'EPR/XLPE':
            isolacao = 'epr'
        dictcorrmet = {'A1': 'a1','A2': 'a2','B1': 'b1','B2': 'b2','C': 'c','D': 'd','E': 'e','F (2 Justapostos)': 'f1','F (3 Justapostos, trio)': 'f2','F (3 Justapostos, plano)': 'f3','G': 'g'}
        metodo = dictcorrmet[metodo]
        if tipoamb == 'Ar':
            tipoamb = 'ar'
        elif tipoamb == 'Solo':
            tipoamb = 'solo'
        if tipcirc == 'Força':
            tipcirc = 'forca'
        elif tipcirc == 'Iluminação':
            tipcirc = 'iluminacao'
        elif tipcirc == 'Controle':
            tipcirc = 'controle'
        estado, resultado = dimcond(corrente,metodo,material,isolacao,numcond,temperarura,tipoamb,tipcirc,comprimento,numcirc,tensaonom,quedarelativa,correntedisjuntor)
        if estado:
            secaodim, correntedim, correntedisjuntor = resultado
        else:
            msgerr = msgerr + '\n' + resultado
        if not msgerr == '':
            QMessageBox.warning(self, "Entrada inválida", msgerr,QMessageBox.Ok)
            return False
        return(secaodim, correntedim, correntedisjuntor)

    def mostrarcalculo(self):
        try:
            secaodim, correntedim, correntedisjuntor = self.execdimcond()
            textValue = 'Seção nominal: {secao} mm²\nCorrente máxima: {corrente} A\nDisjuntor: {correntedisjuntor}'.format(secao=secaodim, corrente=correntedim,correntedisjuntor=correntedisjuntor)
            QMessageBox.information(self, 'Resultado', textValue,QMessageBox.Ok)
        except:
            pass

def main():
    app = QtWidgets.QApplication(sys.argv)  # New instance of `QApplication`
    window = UserInterface()  # Create an object of class ExampleApp
    window.show()  # Show a window
    app.exec_()  # Run the app


if __name__ == '__main__':
    main()