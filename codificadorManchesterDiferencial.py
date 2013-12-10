#!/usr/bin/python
#Universidade Federal do Rio Grande do Sul -  Instituto de Informatica
#Departamento de Informatica Aplicada - Comunicacao de Dados INF01005
#Professores: Juergen Rochol e Cristiano Both
#Aluno: Mario Cesar Gasparoni Junior
#2013-2

######################################################################
#
#Script de codificacao Manchester Diferencial (mark) e NRZ.
#Requisitos: python (recomendavel versao 2.7) e gnuplot-x11
#
#Entrada: uma string de bits
#Saida: Graficos contendo a codificacao Manchester Diferencial (mark) 
#   e NRZ correspondentes a string de bits passada na entrada
#
#Exemplo:
#   ./codificadorManchesterDiferencial 10010101
######################################################################


import sys
import os

FASE_0_MANCH_DIF=[-5,-5,+5,+5]
FASE_1_MANCH_DIF=[+5,+5,-5,-5]

AMPLITUDE_0_NRZ=[0,0,0,0]
AMPLITUDE_1_NRZ=[+5,+5,+5,+5]



def transicionaFase(f):
    resultado=[]
    for elem in f:
        resultado.append(elem*-1)

    return resultado       
    

def parseiaDadosEntradaManchester(sBits):
    i=0
    amp=[]
    tem = []

    #primeiro bit
    if int(sBits[0]) == 0:
        faseAtual = FASE_0_MANCH_DIF
    else:
        if int(sBits[0]) == 1:
            faseAtual = FASE_1_MANCH_DIF
        else:
            print "Invalid bit string"
            sys.exit(0)

    amp.extend(faseAtual) 
    tem.extend([i,i+0.5,i+0.5,i+1])        
    i+=1 
        
    for j in range(0,len(sBits) -2): 
        if int(sBits[j+1]) == 1:
            faseAtual=transicionaFase(faseAtual)
            amp.extend(faseAtual) 
            tem.extend([i,i+0.5,i+0.5,i+1])        
            i+=1
        else:
            if int(sBits[j+1]) == 0:
                amp.extend(faseAtual)
                tem.extend([i,i+0.5,i+0.5,i+1])
                i+=1
            else:
                print "Invalid bit string"
                sys.exit(0)
            
        
    #ultimo bit
    if int(sBits[len(sBits)-1]) == 1:
        amp.extend(FASE_1_MANCH_DIF) 
    else:
        if int(sBits[len(sBits)-1]) == 0:
            amp.extend(FASE_0_MANCH_DIF)
        else:
            print "Invalid bit string"
            sys.exit(0)
    
    tem.extend([i,i+0.5,i+0.5,i+1])
    return tem,amp


def parseiaDadosEntradaNrz(sBits):
    i=0
    ampl=[]
    temp = []
    for bit in sBits:    
        if int(bit) == 0:
            ampl.extend(AMPLITUDE_0_NRZ)
            temp.extend([i,i+0.5,i+0.5,i+1])        
            i+=1
        else:
            ampl.extend(AMPLITUDE_1_NRZ)
            temp.extend([i,i+0.5,i+0.5,i+1])
            i+=1

    
    return temp,ampl
 

def salvaDadosArquivo(arq,tempo,amp):
    if arq==None:
        sys.exit(0)

    if len(amp) != len(tempo):
        print "Invalid data",len(amp),len(tempo)
        sys.exit(0)

    for t,a in zip(tempo,amp):        
        arq.write(str(t)+" "+str(a)+"\n")
    
def exibeGnuplot(pathArquivoDeDados,stringOriginal,title,amplitudeMinima,amplitudeMaxima):
    os.system("gnuplot -persist -e \"set grid x2tics;set x2tics 1 format \'\' scale 0;set xtics 1;set xrange [0:"+str(len(stringOriginal))+"]; set yrange ["+amplitudeMinima+":"+amplitudeMaxima+"]; plot \'"+pathArquivoDeDados+"\' linecolor rgb \'blue\' with lines title \'"+title+" para string de bits "+stringOriginal+"\'\"")    
    

    

#Programa principal

PATH_ARQUIVO_TEMPORARIO_NRZ='tempnrzdif.txt'
PATH_ARQUIVO_TEMPORARIO_MANCH_DIF='tempmanchdif.txt'

arquivoTemporarioNrz = open(PATH_ARQUIVO_TEMPORARIO_NRZ,'w')
arquivoTemporarioManch = open(PATH_ARQUIVO_TEMPORARIO_MANCH_DIF,'w')

if len(sys.argv) < 2:
    print "uso: codificadorManchester.py \"sequencia_de_bits\""
    sys.exit(0) 


stringBits = sys.argv[1]
tempoNrz=[]
amplitudesNrz=[]

tempoManchester=[]
amplitudesManchester = []

tempoNrz,amplitudesNrz=parseiaDadosEntradaNrz(stringBits)
tempoManchester,amplitudesManchester=parseiaDadosEntradaManchester(stringBits)

salvaDadosArquivo(arquivoTemporarioNrz,tempoNrz,amplitudesNrz)
salvaDadosArquivo(arquivoTemporarioManch,tempoManchester,amplitudesManchester)

arquivoTemporarioNrz.close()
arquivoTemporarioManch.close()

exibeGnuplot(PATH_ARQUIVO_TEMPORARIO_MANCH_DIF,stringBits,"Manchester diferencial (mark) ",str(min(FASE_0_MANCH_DIF)-1),str(max(FASE_1_MANCH_DIF)+1))
exibeGnuplot(PATH_ARQUIVO_TEMPORARIO_NRZ,stringBits,"NRZ Unipolar",str(min(AMPLITUDE_0_NRZ)-1),str(max(AMPLITUDE_1_NRZ)+1))


#os.remove(PATH_ARQUIVO_TEMPORARIO_MANCH_DIF)
#os.remove(PATH_ARQUIVO_TEMPORARIO_NRZ)
