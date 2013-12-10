#!/usr/bin/python
#Universidade Federal do Rio Grande do Sul -  Instituto de Informatica
#Departamento de Informatica Aplicada - Comunicacao de Dados INF01005
#Professores: Juergen Rochol e Cristiano Both
#Aluno: Mario Cesar Gasparoni Junior
#2013-2

######################################################################
#
#Script de decodificacao Manchester Diferencial (mark) e NRZ.
#Requisitos: python (recomendavel versao 2.7) e gnuplot-x11
#
#Entrada: arquivo de entrada com valores de tempo(t) e voltagem/amplitude(a)
#       no formato "t a\n",cada
#Saida: string de bits correspondente a decodificacao
#
#Exemplo:
#   ./decodificadorManchesterDiferencial arquivo1.txt
#
#Exemplo de formato do arquivo de entrada:
#   0 -5
#   0.5 -5
#   0.5 5
#   1 5
#   1 -5
#   1.5 -5
#   1.5 5
#   2 5
#   2 5
#   2.5 5
#   2.5 -5
#   3 -5
#   3 -5
#
######################################################################

import math
import os
import random
import sys

FASE_0_MANCH_DIF=[-5,-5,+5,+5]
FASE_1_MANCH_DIF=[+5,+5,-5,-5]

THRESHOLD = 2.5

RUIDO = []
FATOR_RUIDO = math.sqrt(8)


def geraRuido(tamanho):
    #ruido resultado tb eh uma lista de fases
    ruido =[]
    for i in range(tamanho):
        fase=[]
        for j in range(len(FASE_0_MANCH_DIF)):            
            fase.append(FATOR_RUIDO*random.uniform(0,1))        
        ruido.append(fase)

    return ruido 

def aplicaRuido(sinal,ruido):
    resultado=[]

    for i in range(len(sinal)):
        faseSinal=sinal[i]
        faseRuido=ruido[i]
        novaFase=[]

        for j in range(len(FASE_0_MANCH_DIF)):
           novaFase.append(faseSinal[j]+faseRuido[j])
        
        resultado.append(novaFase)

    return resultado 


def corrigeFase(fase):
    amplitudeMinima = min(FASE_0_MANCH_DIF)
    amplitudeMaxima = max(FASE_1_MANCH_DIF)

    resultado=[]
    for amp in fase:
        if amp < (-THRESHOLD):
            resultado.append(amplitudeMinima)
        if amp > THRESHOLD:
            resultado.append(amplitudeMaxima)
        

    return resultado


        
def bitCorrespondenteAFase(FASE):
          
    if corrigeFase(FASE) == FASE_0_MANCH_DIF:
        return 0
    if corrigeFase(FASE) == FASE_1_MANCH_DIF:
        return 1
    else:
        return "error"
    

def parseiaEntradaManchester(PATH):
    #retorna lista de fases

    try:
        arquivoManch = open(PATH,'r')
    except IOError:
        print "No input file"
        sys.exit(0)

    i=0    
    resultado=[]
    FASE_ATUAL=[]

    for line in arquivoManch:
            tokens=line.split()
            FASE_ATUAL.append(int(tokens[1]))
            i+=1
            if(i==4):
                resultado.append(FASE_ATUAL)
                FASE_ATUAL=[]
                i=0

                 
    arquivoManch.close()
    return resultado       

def decodificaFases(fases):
    
    resultado=[]
    
    #primeira fase
    resultado.append(bitCorrespondenteAFase(fases[0]))
       
    for i in range(1,len(fases)):
        if corrigeFase(fases[i]) == corrigeFase(fases[i-1]):
            resultado.append(0)
        if corrigeFase(fases[i]) != corrigeFase(fases[i-1]):
            resultado.append(1)

    return resultado
        

#Programa principal

if len(sys.argv) > 1:
    print "uso: decodificadorManchester.py <arquivo>"
    PATH_ARQUIVO_MANCH_DIF = sys.argv[1]

else:      
    PATH_ARQUIVO_MANCH_DIF = "tempmanchdif.txt"

tempoNrz=[]
amplitudesNrz=[]

tempoManchester=[]
amplitudesManchester = []
stringBits = []
stringBitsRuido = []

#obtem as fases e parseia
sinalOriginal = parseiaEntradaManchester(PATH_ARQUIVO_MANCH_DIF)
ruido = geraRuido(len(sinalOriginal))
sinalRuidoso=aplicaRuido(sinalOriginal,ruido)

stringBits = decodificaFases(sinalOriginal)
stringBitsRuido = decodificaFases(sinalRuidoso)
  
print "Decodificacao do sinal sem ruido" 
print stringBits
print "Decodificacao do sinal com ruido AWGN"
print stringBitsRuido



