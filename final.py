#!/usr/bin/python
import math
import os
import random
import sys
import zlib



#FUNCOES/VARS AUXILIARES

#plot do nrz
AMPLITUDE_0_NRZ=[-5,-5,-5,-5]
AMPLITUDE_1_NRZ=[+5,+5,+5,+5]

#amplitudes usadas no codificador de linha (nrz) e no Modulador
AMPLITUDE_0=-5
AMPLITUDE_1=+5

#fases do BPSK
FASE_0='F0'
FASE_180='F180'

PATH_ARQUIVO_TEMPORARIO_NRZ='./tempnrz.txt'
PATH_ARQUIVO_TEMPORARIO_AMOSTRAS='./dadosAmostras.txt'
PATH_ARQUIVO_TEMPORARIO_AMOSTRAS_RUIDOSAS='./dadosAmostrasRuidosas.txt'
PATH_ARQUIVO_TEMPORARIO_AMOSTRAS_RECUPERADAS='./dadosAmostrasRecuperadas.txt' 
arquivoTemporarioNrz = open(PATH_ARQUIVO_TEMPORARIO_NRZ,'w')
arquivoTemporarioAmostras = open(PATH_ARQUIVO_TEMPORARIO_AMOSTRAS,'w')
arquivoTemporarioAmostrasRuidosas = open(PATH_ARQUIVO_TEMPORARIO_AMOSTRAS_RUIDOSAS,'w')
arquivoTemporarioAmostrasRecuperadas = open(PATH_ARQUIVO_TEMPORARIO_AMOSTRAS_RECUPERADAS,'w')

#tb usado no plot
def salvaDadosArquivo(arq,tempo,amp):
    if arq==None:
        sys.exit(0)

    if len(amp) != len(tempo):
        print "Invalid data",len(amp),len(tempo)
        sys.exit(0)

    for t,a in zip(tempo,amp):        
        arq.write(str(t)+" "+str(a)+"\n")

def geraTemposGnuplot(nAmplitudes):
    tempos=[]
    for i in range (nAmplitudes):
        tempos.extend([i,i+0.5,i+0.5,i+1])

    return tempos


def exibeGnuplot(pathArquivoDeDados,stringOriginal,title,amplitudeMinima,amplitudeMaxima):  
    os.system("gnuplot -persist -e \"set grid x2tics;set x2tics 1 format \'\' scale 0;set xtics 1;set xrange [0:"+str(len(stringOriginal))+"]; set yrange ["+amplitudeMinima+":"+amplitudeMaxima+"]; plot \'"+pathArquivoDeDados+"\' linecolor rgb \'blue\'with lines title \'"+title+" para string de bits "+stringOriginal+"\'\"") 

def exibeSinalModuladoGnuplot(pathArquivoDeDados,nAmostras,titulo):  
    os.system("gnuplot -persist -e \"set grid x2tics;set x2tics 100 format \'\' scale 0;set xtics 100;set xrange[0:"+str(nAmostras)+"] ;plot '"+pathArquivoDeDados+"' with lines title '"+titulo+"' \"") 


def amplitudesDiscretasToIntervalos(amplitudes):
    #converte as amplitudes em tempos de 4 amostras por intervalo
    #para o valor de 0 ou 1 , ou seja,  para 1 tempo por intervalo.
    #Exemplos: 
    #   1)[+5,+,5+,5+,5] (bit 1) retorna [+5]
    #   2)[+5,+5,+5,+5,-5,-5,-5,-5] (bits '10') retorna [+5,-5]


    amplitudeAtual = [] #le de 4 em 4
    amplitudesResultantes = []

    AMPLITUDE_0=-5
    AMPLITUDE_1=+5

    i=0
    while i < len(amplitudes):
        amplitudeAtual=amplitudes[i:i+4]
        if amplitudeAtual==AMPLITUDE_0_NRZ:
            amplitudesResultantes.append(AMPLITUDE_0)           
        else:
            amplitudesResultantes.append(AMPLITUDE_1)
        i+=4
    return amplitudesResultantes

def intervalosToAmplitudesDiscretas(intervalos):

    amplitudeAtual = [] #le de 4 em 4
    amplitudesResultantes = []

    AMPLITUDE_0=-5
    AMPLITUDE_1=+5

    i=0
    for a in intervalos:
        if a == AMPLITUDE_0:
            amplitudesResultantes+=AMPLITUDE_0_NRZ
        else:
            amplitudesResultantes+=AMPLITUDE_1_NRZ
            
    return amplitudesResultantes


#########################################################
#FUNCOES DO TRANSMISSOR/RECEPTOR
#########################################################
def leFonte(arquivoDados):
    texto=""
    for line in arquivoDados:
        texto+=line

    return texto

def codificadorFonte(texto):        
    return zlib.compress(texto,9)


def decodificadorFonte(stringDados):
    return zlib.decompress(stringDados)


#byte to bit: caixa utilizada entre codificador de fonte e de linha
def byteStringToBitString(stringDados):
    bitString=""

    #converte cada byte em uma string de bits
    for char in stringDados:
        
        bits=bin(ord(char))[2:]

        diferencaBits = 8-len(bits)
        while diferencaBits > 0:
            bits='0'+bits
            diferencaBits = 8-len(bits) 
        
        bitString+=bits       

    return bitString


def bitStringToByteString(stringBits):
    byteString=""
    i=0    
    while(i < len(stringBits)):
        byte=stringBits[i:i+8]
        byteString+=chr(int(byte,2))
        i+=8
    
    return byteString


def codificadorLinha(bitString):
    #NRZ

    i=0
    ampl=[]
    temp = []
    for bit in bitString:
        if int(bit) == 0:           
            ampl.extend(AMPLITUDE_0_NRZ)            
        else:
            ampl.extend(AMPLITUDE_1_NRZ)
    
    return amplitudesDiscretasToIntervalos(ampl) #ajustar para retornar diretamente 4 amostras


def decodificadorLinha(Amplitudes):
    #Decodifica NRZ 
    
    amplitudes = intervalosToAmplitudesDiscretas(Amplitudes) #formato anterior (de 4 amostras): ajustar
    AMPLITUDE = [] #le de 4 em 4
    bitsSaida = ""

    i=0
    while i < len(amplitudes):
        AMPLITUDE=amplitudes[i:i+4]
        if AMPLITUDE==AMPLITUDE_0_NRZ:
            bitsSaida+="0"
        else:
            bitsSaida+="1"
        i+=4
    return bitsSaida



def codificadorCanal(amplitudesCodificadorLinha):
    amplitudesCanal=amplitudesCodificadorLinha

    return amplitudesCanal


def decodificadorCanal(amplitudesCodificadorCanal):
    amplitudesLinha=amplitudesCodificadorCanal
    return amplitudesLinha


def moduladorBpsk(amplitudes):
    #gera a constelacao de pontos a partir 
    #dos diferentes valores de entrada.
    constelacao=[]
    amostras=[]

    for amplitude in amplitudes:
        if amplitude==AMPLITUDE_0:
            constelacao+=[FASE_0]
        else:
            constelacao+=[FASE_180]

    return constelacao


def demoduladorBpsk(constelacao):
    
    amplitudesResultantes=[]
    

    for fase in constelacao:
        if fase==FASE_0:
            amplitudesResultantes+=[AMPLITUDE_0]
        else:
            amplitudesResultantes+=[AMPLITUDE_1]

    return amplitudesResultantes


def geraAmostrasBpsk(fase):
    
    
    i=0

    #constantes da funcao seno
    N_AMOSTRAS=100   
    amplitude=AMPLITUDE_1 #amplitude do codificador de linha (nrz)

    amostra=[]


    if fase == FASE_0:
        for i in range(N_AMOSTRAS):            
            amostra+= [amplitude*math.sin((float(i)/N_AMOSTRAS)*2*math.pi)]            
    else:
        for i in range(N_AMOSTRAS):
            amostra+= [amplitude*math.sin((float(i)/N_AMOSTRAS)*2*math.pi+math.pi)]    
    return amostra



def fasesToAmostrasBpsk(constelacao):
    '''
        converte as n fases (ou constelacao) do dado a ser transmitido
        para a senoide correspondente , de modo que a senoide resultante 
        ,para cada fase, possui 100 amostras.
        O valor retornado eh um  vetor contendo todos os valores de cada
        amostra de cada fase

        Exemplo: 1) Com a amplitude = 5v , ['F0','F180'] resulta em 
                        [0,...,+5,...,0,...,-5,...,0] + [0,...,-5,...,0,...,+5,...,0]

    '''   
    amostras=[]
    for fase in constelacao:        
            amostras+=geraAmostrasBpsk(fase)
    
    return amostras


def obtemFaseAmostra(amostra):
    '''
        Processo reverso a geracao de amostra pela funcao
        geraAmostrasBpsk(...)

    '''
    i=0
    
    
    cristaEsquerda=amostra[0:50]
    cristaDireita=amostra[50:100]
    somaEsq=0
    somaDir=0

    #corrige ruido
    for a in cristaEsquerda:
        if a>AMPLITUDE_1:
            a=AMPLITUDE_1

        if a<AMPLITUDE_0:
            a=AMPLITUDE_0

        somaEsq+=a



    for a in cristaDireita:
        if a>AMPLITUDE_1:
            a=AMPLITUDE_1

        if a<AMPLITUDE_0:
            a=AMPLITUDE_0

        somaDir+=a



    if somaEsq < somaDir:
        return FASE_180
    else: return FASE_0


def ruidoNosso():    
    return random.uniform(AMPLITUDE_0*10,-AMPLITUDE_0*10)

def ruidoGaussiano():
    print 'gaussiano'

def amostrasToFasesBpsk(amostras):
    '''
        Processo reverso ao fasesToAmostrasBpsk()
    '''
    fases=[]
    i=0
    while(i<len(amostras)):
        amostra=amostras[i:i+100]
        fases+=[obtemFaseAmostra(amostra)]
        i+=100

    return fases



def ruido(amostras):
    '''
        Dado um conjunto de amostras,
        adiciona o ruido gaussiano nessas.

    '''
    amostrasRuidosas=amostras[:]
    for i in  range(len(amostrasRuidosas)):
        ruido=ruidoNosso()
        amostrasRuidosas[i]+=ruido

    return amostrasRuidosas



def ber(bitsRecebidos,bitsEnviados):
    if(len(bitsRecebidos) != len(bitsEnviados)):
        print "Erro: bitsEnviados de tamanhos diferentes"
        sys.exit(3)

    nBitsErrados=0

    for i in range(len(bitsEnviados)):
        if bitsRecebidos[i] != bitsEnviados[i]:
            nBitsErrados+=1

    #AJUSTAR BER: VER FUNCAO PARA DETERMINAR DIFERENCA ENTRE DUAS STRINGS
    print 'Bits Errados:',nBitsErrados,len(bitsRecebidos)
    return float(nBitsErrados)/len(bitsRecebidos)

###################################################
#Programa principal

#fonte de informacao
PATH_ARQUIVO_FONTE_INFORMACAO = "./fonte.txt"
arquivoFonteInformacao = open(PATH_ARQUIVO_FONTE_INFORMACAO,'r')



#TRANSMISSAO


#leitura da fonte: arquivo texto
fonteInformacao=leFonte(arquivoFonteInformacao)
print ">Fonte de Informacao<\n",fonteInformacao
print "Tamanho da fonte de informacao:",len(fonteInformacao),'bytes\n'

#codificacao da fonte: ZIP
textoZip = codificadorFonte(fonteInformacao);
print ">Texto codificado(zip)<\n:",textoZip
print "Tamanho do texto codificado:",len(textoZip),'bytes\n'


#codificador linha: NRZ
print ">Codificacao NRZ<\n"
bitString=byteStringToBitString(textoZip) #intermediario entre codificador de fonte e de linha: transformador de bytes codificados para bits
amplitudesNrz=codificadorLinha(bitString)
tempoNrz = geraTemposGnuplot(len(bitString))

print '-Bits\n',bitString,'\n','Total de bits: ',len(bitString),'\n'
print '-NRZ Voltagens por Intervalo de Tempo\n',amplitudesNrz,'\n','Total de voltagens: ',len(amplitudesNrz),'\n'


#plot do NRZ
salvaDadosArquivo(arquivoTemporarioNrz,tempoNrz[:10*4],intervalosToAmplitudesDiscretas(amplitudesNrz)[:10*4]) #plot NRT
exibeGnuplot(PATH_ARQUIVO_TEMPORARIO_NRZ,bitString[:10],"NRZ Bipolar",str(min(AMPLITUDE_0_NRZ)),str(max(AMPLITUDE_1_NRZ)+1)) #plot

#codificador canal: paridade (TO DO later)
amplitudesCodificadorCanal = amplitudesNrz

#modulador BPSK. 2 Etapas: Constelacao e Amostragem
constelacao = moduladorBpsk(amplitudesCodificadorCanal)

print ">Modulacao<\n"
print "-Constelacao:\n", constelacao,'\n'
#print '-Amostras:\n'
amostras = fasesToAmostrasBpsk(constelacao)
arquivoTemporarioAmostras.write(str(amostras[:1000]).replace('[','').replace(',','\n').replace(']',''))
exibeSinalModuladoGnuplot(PATH_ARQUIVO_TEMPORARIO_AMOSTRAS,len(amostras[:1000]),'Sinal Modulado BPSK')

print '>Ruido<\n'
amostrasRuidosas=ruido(amostras)
arquivoTemporarioAmostrasRuidosas.write(str(amostrasRuidosas[:1000]).replace('[','').replace(',','\n').replace(']',''))
exibeSinalModuladoGnuplot(PATH_ARQUIVO_TEMPORARIO_AMOSTRAS_RUIDOSAS,len(amostrasRuidosas[:1000]),'Sinal Modulado BPSK Com Ruido')


print '>Ber<\n'





#RECEPCAO



#demodulador
recConstelacao = amostrasToFasesBpsk(amostrasRuidosas)
recAmostras=fasesToAmostrasBpsk(recConstelacao)
arquivoTemporarioAmostrasRecuperadas.write(str(recAmostras[:1000]).replace('[','').replace(',','\n').replace(']',''))
exibeSinalModuladoGnuplot(PATH_ARQUIVO_TEMPORARIO_AMOSTRAS_RECUPERADAS,len(recAmostras[:1000]),'Sinal Demodulado BPSK')
#recAmplitudesCanal=demoduladorBpsk(recConstelacao)
recAmplitudesCanal=demoduladorBpsk(constelacao)
print '>Demodulacao<\n'
print 'Amostras apos demodulacao(simbolos da constelacao):\n',recConstelacao,'\n'
print 'Numero de simbolos recebidos:\n',len(recConstelacao),'\n'

print 'Demodulacao dos simbolos recebidos para niveis no codificador de canal\n',recAmplitudesCanal,'\n'
print 'Total de niveis recebidos: ',len(recAmplitudesCanal),'\n'

#decodificador canal: (TO DO)
recAmplitudesNrz=decodificadorCanal(recAmplitudesCanal)
print '>Decodificacao de niveis no canal, para niveis na codificacao de linha<\n',recAmplitudesNrz
print 'Total de niveis de codificacao de linha(NRZ):\n',len(recAmplitudesNrz)


#decodificador linha: NRZ
recBits = decodificadorLinha(recAmplitudesNrz)
recTextoZip = bitStringToByteString(recBits) #intermediario entre codificador de linha e codificador de fonte
print '>Decodificacao NRZ<\n'
print '-Bits:\n',recBits,'\nTotal de bits recebidos: ',len(recBits),'\n'
print '-Dados:\n',recTextoZip,'\nTotal de dados recebidos: ',len(recTextoZip),' bytes\n'

#ber
print 'BER:\n',ber(recBits,bitString)*100,'%'


#decodificador fonte
textoDecodificado=decodificadorFonte(recTextoZip)
print "Decodificador Fonte\n",textoDecodificado
print "Tamanho do texto decodificado:",len(textoDecodificado)


