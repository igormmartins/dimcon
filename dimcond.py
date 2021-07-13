import numpy as np
from bdd import bdd
import os, sys
# try:
#     path = sys._MEIPASS
# except:
#   path = os.path.abspath('.')


#Função geral do dimensionamento dos condutores:
def dimcond(corrente,metodo = 'b2',material = 'cobre',isolacao = 'pvc',numcond = 2,temperarura = 30, tipoamb = 'ar',tipcirc = 'forca',comprimento = 15, numcirc = 1, tensaonom = 220, quedarelativa = 5, correntedisjuntor = 50):
    fatorcorracum = 1
    if numcond == 4:
        fatorcorracum = 1/0.86
    #constantes
    def metodoparaindice(metodo,numcond): #funcao pra calcular o indice da coluna da tabela da norma
        inddict = {'a1': 1, 'a2': 3, 'b1': 5, 'b2': 7, 'c': 9, 'd': 11, 'e': 13, 'f1': 15, 'f2': 16, 'f3': 17, 'g': 19} #relacao baseada no indice superior das colunas
        if metodo in inddict: #se o metodo digitado exite no dicionario da linha anterior executa a proxima linha
            if numcond == 2 or numcond == 3 or numcond == 4: #se o numero de condutores for igual a 2 ou 3 executa a proxima linha
                if numcond == 4:
                    numcond -= -1
                if metodo == 'f1' or metodo == 'f2' or metodo == 'f3': #se o metodo for um dos F
                    indice = inddict[metodo] #associa o indice diretamente do dicionario
                else: #se não
                    indice = inddict[metodo] + (numcond - 2) #aplica um metodo para encontrar o indice da coluna da tabela. numcond - 2 + indice do dicionario é igual ao indice geral da tabela
            else: #se o numero de condutores for diferente de 2 ou 3 executa a proxima linha
                return(False,'numero de condutores inválido') #diz pro usuario que digitou algo errado e retorna false para desencadear uma falha de execução do código a fim de interroper a execução
            return(indice) #se tudo estiver de acordo, retorna o indice da coluna
        return(False,'Método não existente no banco de dados') #retorna false para desencadear uma falha de execução do código a fim de interroper a execução
    tabela =  bdd[material+isolacao]#importa a tabela selecionada nas 3 linhas anteriores para a variavel
    tabelatemps = bdd['temp'] #Importa a tabela com correcao de temperatura
    tipolintempref = {'ar': 0, 'solo': 2} #dicionario que define o indice da tabela a ser importado referente ao ambiente de instalacao a ser aplicada em um metodo
    fatagrup = [[1,2,3,4,5,6,7,8,11,15,19,20],[1, 0.80, 0.70, 0.65, 0.60, 0.57, 0.54, 0.52, 0.50, 0.45, 0.41, 0.38]] #Parte simplificada das tabelas de fotor de agrupamento
    disjval = [2,4,6,10,16,25,32,40,50,63,70,80,100,125,150,160,175,180,200,225,250,300,315,350,400,450,500,600,630,700,800,1000,1250]
    for i in range(len(fatagrup[0])): #percorre os numeros de circuitos da parte simplificada do fator de agrupamento da linha anterior
        if fatagrup[0][i] >= numcirc: #se o numero de circuitos introduzidos pelo usuario for menor ou igual ao do fator de agrupamento 
            fatagrupun = fatagrup[1][i] #associa a correcao respectiva à variavel
            break #a execução do loop é interrompida
    rescob = 0.0162 #resistividade do cobre adequada às unidades m/mm^2
    resalum = 0.028 #resistividade do aluminio adequada às unidades m/mm^2
    if numcond == 2: corrquedatensao = numcond #Correção do calculo de queda de tensão para circuitos bifásicos
    elif numcond == 3 or numcond == 4: corrquedatensao = 3**(1/2) #Correção do calculo de queda de tensão para circuitos trifásicos
    if material == 'cobre': #se o material for cobre
        secaominima = (corrente*rescob*comprimento*corrquedatensao)/(tensaonom*quedarelativa*0.01) #calcula a secao minima baseada na corrente, resistividade do condutor, comprimento do circuito, tensao nominal e a queda relativa percential de tensão
    if material == 'aluminio': #se o material for aliminio
        secaominima = (corrente*resalum*comprimento*corrquedatensao)/(tensaonom*quedarelativa*0.01) #calcula a secao minima baseada na corrente, resistividade do condutor, comprimento do circuito, tensao nominal e a queda relativa percential de tensão
    fatork = {'cobrepvc': 115, 'aluminiopvc': 76, 'cobrepvc300': 103, 'aluminiopvc300': 68,'cobreepr': 143, 'aluminioepr': 94} #dicionario contendo os fatores K de curto circuito

    #Aplicação dos metodos com as contantes e variaveis pré definidas
    #aplicacao de fatores de correcao de temperatura e fator de agrupamento e a obtencao da secao pelos metodos de corrente das tabelas da norma
    indice = metodoparaindice(metodo,numcond) #calcula o indice da coluna da tabela de correntes usando a funcao ja citada
    tempsref = np.array(tabelatemps)[:,0] #adquire a primeira coluna da tabela de correcao de temperatura, em uma linha
    for i in range(len(tempsref)): #para i no comprimento da coluna de temperatura
        if float(tempsref[i]) >= temperarura: #se a temperatura atual (do loop) for maior que a introduzida pelo usuario
            if isolacao == 'pvc': #se a isolacao for pvc
                valortemp = float(np.array(tabelatemps)[:,(tipolintempref[tipoamb]+1)][i]) #obtem o valor de correcao respectivo
                if valortemp == 0: #se for 0 (0 significa que a isolacao nao suporta, forma encontrada para dizer isto ao programa de maiera facil) executa a proxima linha
                    return(False,'Isolação de PVC não suporta esta temperatura\n') #diz que nao suporta a temperatura digitada
                fatorcorracum = fatorcorracum/(valortemp*fatagrupun) #calcula a corrente corrigida pelo fator de agrupamento e a de temperatura para o pvc
            elif isolacao == 'epr':fatorcorracum = fatorcorracum/(float(np.array(tabelatemps)[:,(tipolintempref[tipoamb]+2)][i])*fatagrupun) #calcula a corrente corrigida pelo fator de agrupamento e a de temperatura se a isolacao for epr
            break #a execução do loop é interrompida
    selecao = np.array(tabela)[:,indice] #associa a coluna selecionada com o indice ja calculado à variavel
    for i in range(len(selecao)): #percorre a coluna importada
        if float(selecao[i]) >= corrente*fatorcorracum: #se a corrente inserida pelo usuario for menor ou igual a atual do loop que percorre a coluna
            break #a execução do loop é interrompida
    #aplicacao do metodo da secao minima
    if tipcirc == 'forca': #se os cabos serao de um circuito de forca
        if material == 'cobre': #se o material for cobre
            if float(np.array(tabela)[:,0][i]) < 2.5: #se a secao selecionada pelo metodo anterior for menor que a secao minima
                i = 4 #seleciona o indice da secao minima na respectiva tabela
            elif material ==   'aluminio': #se o material for aluminio
                if float(np.array(tabela)[:,0][i]) < 16: #se a secao selecionada pelo metodo anterior for menor que a secao minima
                    i = 0 #seleciona o indice da secao minima na respectiva tabela
    if tipcirc == 'iluminacao': #se os cabos serao de um circuito de iluminacao
        if material == 'cobre': #se o material for cobre
            if float(np.array(tabela)[:,0][i]) < 1.5: #se a secao selecionada pelo metodo anterior for menor que a secao minima
                i = 3 #seleciona o indice da secao minima na respectiva tabela
            elif material ==   'aluminio': #se o material for aluminio
                if float(np.array(tabela)[:,0][i]) < 16: #se a secao selecionada pelo metodo anterior for menor que a secao minima
                    i = 0 #seleciona o indice da secao minima na respectiva tabela
    if tipcirc == 'controle': #se os cabos serao de um circuito de controle
        if material == 'cobre': #se o material for cobre
            if float(np.array(tabela)[:,0][i]) < 0.5: #se a secao selecionada pelo metodo anterior for menor que a secao minima
                i = 0 #seleciona o indice da secao minima na respectiva tabela
            elif material ==   'aluminio': #se o material for aluminio
                if float(np.array(tabela)[:,0][i]) < 16: #se a secao selecionada pelo metodo anterior for menor que a secao minima
                    print("A norma não especifica uma seção mínima, no entanto aproximando para o mínimo.") #diz que nao suporta
                    i = 0 #e seleciona o indice da secao minima na respectiva tabela
    #aplicacao do metodo de queda de tensão
    if secaominima > float(np.array(tabela)[:,0][i]): #se a secao selecionada pelo metodo anterior for menor que a secao minima calculada para este metodo
        for i in range(len(selecao)): #percorre a coluna das secoes nominais da norma
            seccorr = float(np.array(tabela)[:,0][i]) #associa a secao atual do loop à variavel
            if seccorr >= secaominima: #se a secao atual for maior que a secao minima
                break #a execução do loop é interrompida
    # # #aplicacao do metodo de curto circuito
    # nomtabcorrcurt = material+isolacao #constroi o indice a ser consultado no dicionario com as strings
    # if float(np.array(tabela)[:,0][i]) > 300: #se a secao selecionada pelo metodo anterior for maior que 300
    #     nomtabcorrcurt = nomtabcorrcurt + '300' #adiciona ao indice a ser consultado no dicionario com as strings 300
    # novasecao = (correntedecurto*0.223606797749979*1000)/fatork[nomtabcorrcurt] #calcula a nova secao baseada na corrente de curto*√0,05s ÷ pelo fator obtido do dicionario
    # if novasecao > float(np.array(tabela)[:,0][i]): #se a secao selecionada pelo metodo anterior for menor que a secao minima calculada para este metodo
    #     for i in range(len(selecao)): #percorre a coluna das secoes nominais da norma
    #         seccorr = float(np.array(tabela)[:,0][i]) #associa a secao atual do loop à variavel 
    #         if seccorr >= novasecao: #se a secao atual for maior que a secao minima
    #             break #a execução do loop é interrompida
    # #Verificação da corrente dos disjuntores devido a terem seus valores tabelados
    if correntedisjuntor == 'Auto':
        for j in disjval:
            if j >= (corrente):
                correntedisjuntor = j
                break
        if correntedisjuntor == 'Auto':
            correntedisjuntor = disjval[-1]
    try:
        while int(float(np.array(tabela)[:,indice][i])/fatorcorracum) < correntedisjuntor: #Enquanto a corrente encontrada for menor que a do disjuntor indicado
            i = i + 1 #Ecolhe a proxima seção
    except:
        return(False,'Método/Isolação não suporta a corrente selecionada')
    #a variavel i contem o indice da coluna de secoes nominaos a ser mostrado
    return(True,[np.array(tabela)[:,0][i],int(float(np.array(tabela)[:,indice][i])/fatorcorracum),correntedisjuntor])


if __name__ == '__main__':
    #variaveis
    corrente = 1100 #max 1000
    material = 'cobre' #cobre ou aluminio
    isolacao = 'pvc' #pvc ou epr
    metodo = 'b1' #a1, a2, b1...
    numcond = 2 #2 ou 3. No caso do metodo G 2 equivale ao metodo horizontal e 3 ao vertical. No método F é ignorado.
    temperarura = 30 #de 5 a 80
    tipoamb = 'ar' #ar ou solo
    tipcirc = 'forca' #força, iluminacao ou controle
    comprimento = 15 #comprimento do condutor
    numcirc = 1 #numero de circuitos simultaneos para calculo simplificado do fator de agrupamento
    tensaonom = 220 #Tensão nominal do circuito em volts
    quedarelativa = 5 #queda de tensão máxima permitida em %
    correntedisjuntor = 'Auto' #Corrente do disjuntor a ser ligado em série com o fio

    estado, resultado = dimcond(corrente,metodo,material,isolacao,numcond,temperarura,tipoamb,tipcirc,comprimento,numcirc,tensaonom,quedarelativa,correntedisjuntor)
    secaodim, correntedim, correntedisjuntor = resultado

    print('\n\nCondutor de:',secaodim, 'mm2') #mostra a secao nominal selecionada
    print('Corente máxima de:', correntedim, 'A') #mostra a secao nominal selecionada
    print('Corrente de disjuntor:{}\n\n'.format(correntedisjuntor))