#!/usr/bin/python
import math
import os
import random
import reedsolomon
import sys
import zlib



#CONSTANTES
DEBUG = 0
PLOT = 1

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
    os.system("gnuplot -persist -e \"set grid x2tics;set x2tics 1 format '' scale 0;set xtics 1; plot '"+pathArquivoDeDados+"' linecolor rgb 'blue' with lines title '"+title+" para string de bits "+stringOriginal+"'\"") 

def exibeSinalModuladoGnuplot(pathArquivoDeDados,nAmostras,titulo):  
    os.system("gnuplot -persist -e \"set grid x2tics;set x2tics 100 format '' scale 0;set xtics 100;set xrange[0:"+str(nAmostras)+"] ;plot '"+pathArquivoDeDados+"' with lines title '"+titulo+"' \"") 


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




def fecEncode(stringDados):
    '''
        Utilizando Codificacao Reed Solomon.
        Entrada: String de dados provenientes do codificador de fonte
        Saida: String com os dados originais juntamente com a redundancia do Reed Solomon

    '''
    
    mRS = reedsolomon.ReedSolomon()
    dadoCodificado = mRS.RSEncode(stringDados,len(stringDados))
    return "".join(map(chr,dadoCodificado))

def fecDecode(stringDadosCodificados):
    '''
        Processo reverso ao fecEncode()
    '''    

    mRS = reedsolomon.ReedSolomon()
    dadosCodificados = map(ord,stringDadosCodificados)
    dadosDecodificados = mRS.RSDecode(dadosCodificados,len(dadosCodificados)/2)

    if(not dadosDecodificados):
        if DEBUG:
            print 'Nao foi possivel corrigir erros'
        return ''

    else:
        return "".join(map(chr,dadosDecodificados[:len(dadosDecodificados)/2]))  




def codificadorLinha(bitString):
    #nrz

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

def heuristica(valorAmostra):


    if valorAmostra>AMPLITUDE_1:
	    return AMPLITUDE_1

    if valorAmostra< AMPLITUDE_1 /2 and valorAmostra > 0:
	    return 0

    if valorAmostra<AMPLITUDE_0:
	    return AMPLITUDE_0

    if valorAmostra> AMPLITUDE_0 /2 and valorAmostra < 0:
	    return 0

    return valorAmostra

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
        somaEsq+=heuristica(a)

    for a in cristaDireita:
        somaDir+=heuristica(a)

    if somaEsq < somaDir:
        return FASE_180
    else: return FASE_0


def ruidoNosso():  
    multiplicador=2.75
    #multiplicador=10
    return random.uniform(AMPLITUDE_0*multiplicador,-AMPLITUDE_0*multiplicador)

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
        if DEBUG:
            print "Erro: bitsEnviados de tamanhos diferentes"
        return 1

    nBitsErrados=0

    for i in range(len(bitsEnviados)):
        if bitsRecebidos[i] != bitsEnviados[i]:
            nBitsErrados+=1

    
    #if DEBUG:
    print 'Bits Errados:',nBitsErrados, '/',len(bitsRecebidos)
    
    return float(nBitsErrados)/len(bitsRecebidos)



###################################################
#Programa principal

#fonte de informacao
PATH_ARQUIVO_FONTE_INFORMACAO = "./fonte3.txt"
arquivoFonteInformacao = open(PATH_ARQUIVO_FONTE_INFORMACAO,'r')



#TRANSMISSAO


#leitura da fonte: arquivo texto
fonteInformacao=leFonte(arquivoFonteInformacao)
if DEBUG:
    print ">Fonte de Informacao<\n",fonteInformacao
    print "Tamanho da fonte de informacao:",len(fonteInformacao),'bytes\n'

#codificacao da fonte: ZIP
textoZip = codificadorFonte(fonteInformacao)
#textoZip = 'MASDFGHIJKL'
if DEBUG:
    print ">Texto codificado(zip)<\n:",textoZip
    print "Tamanho do texto codificado:",len(textoZip),'bytes\n'

#FEC: Reed Solomon
if DEBUG:
    print ">Codificacao FEC(ReedSolomon)<\n"
stringSolomon = fecEncode(textoZip)

#codificador linha: NRZ
if DEBUG:
    print ">Codificacao NRZ<\n"

bitString=byteStringToBitString(stringSolomon) #intermediario entre codificador de fonte e de linha: transformador de bytes codificados para bits
amplitudesNrz=codificadorLinha(bitString)
tempoNrz = geraTemposGnuplot(len(bitString))

if DEBUG:
    print '-Bits\n',bitString,'\n','Total de bits: ',len(bitString),'\n'
    print '-NRZ Voltagens por Intervalo de Tempo\n',amplitudesNrz,'\n','Total de voltagens: ',len(amplitudesNrz),'\n'


#plot do NRZ
if PLOT:
    salvaDadosArquivo(arquivoTemporarioNrz,tempoNrz[:10*4],intervalosToAmplitudesDiscretas(amplitudesNrz)[:10*4]) #plot NRT
    arquivoTemporarioNrz.close()
    exibeGnuplot(PATH_ARQUIVO_TEMPORARIO_NRZ,bitString[:10],"NRZ Bipolar",str(min(AMPLITUDE_0_NRZ)),str(max(AMPLITUDE_1_NRZ)+1)) #plot

#codificador canal: paridade (TO DO later)
amplitudesCodificadorCanal = amplitudesNrz

#modulador BPSK. 2 Etapas: Constelacao e Amostragem
constelacao = moduladorBpsk(amplitudesCodificadorCanal)

if DEBUG:
    print ">Modulacao<\n"
    print "-Constelacao:\n", constelacao,'\n'
#print '-Amostras:\n'
amostras = fasesToAmostrasBpsk(constelacao)

if PLOT:
    arquivoTemporarioAmostras.write(str(amostras[:1000]).replace('[','').replace(',','\n').replace(']',''))
    exibeSinalModuladoGnuplot(PATH_ARQUIVO_TEMPORARIO_AMOSTRAS,len(amostras[:1000]),'Sinal Modulado BPSK')

if DEBUG:
    print '>Ruido<\n'
amostrasRuidosas=ruido(amostras)

if PLOT:
    arquivoTemporarioAmostrasRuidosas.write(str(amostrasRuidosas[:1000]).replace('[','').replace(',','\n').replace(']',''))
    exibeSinalModuladoGnuplot(PATH_ARQUIVO_TEMPORARIO_AMOSTRAS_RUIDOSAS,len(amostrasRuidosas[:1000]),'Sinal Modulado BPSK Com Ruido')




#RECEPCAO

#demodulador
recConstelacao = amostrasToFasesBpsk(amostrasRuidosas)
recAmostras=fasesToAmostrasBpsk(recConstelacao) #plot das amostras recuperadas

if PLOT:
    arquivoTemporarioAmostrasRecuperadas.write(str(recAmostras[:1000]).replace('[','').replace(',','\n').replace(']',''))
    exibeSinalModuladoGnuplot(PATH_ARQUIVO_TEMPORARIO_AMOSTRAS_RECUPERADAS,len(recAmostras[:1000]),'Sinal Demodulado BPSK')
#recAmplitudesCanal=demoduladorBpsk(recConstelacao)
recAmplitudesCanal=demoduladorBpsk(recConstelacao)
if DEBUG:
    print '>Demodulacao<\n'
    print 'Amostras apos demodulacao(simbolos da constelacao):\n',recConstelacao,'\n'
    print 'Numero de simbolos recebidos:\n',len(recConstelacao),'\n'

    print 'Demodulacao dos simbolos recebidos para niveis no codificador de canal\n',recAmplitudesCanal,'\n'
    print 'Total de niveis recebidos: ',len(recAmplitudesCanal),'\n'

#decodificador canal: (TO DO)
recAmplitudesNrz=decodificadorCanal(recAmplitudesCanal)
if DEBUG:
    print '>Decodificacao de niveis no canal, para niveis na codificacao de linha<\n',recAmplitudesNrz
    print 'Total de niveis de codificacao de linha(NRZ):\n',len(recAmplitudesNrz)


#decodificador linha: NRZ
recBits = decodificadorLinha(recAmplitudesNrz)


recStringSolomon = bitStringToByteString(recBits) #intermediario entre codificador de linha e codificador de fonte
if DEBUG:
    print '>Decodificacao NRZ<\n'
    print '-Dados Reed Solomon:\n',recStringSolomon
    print 'Bits:\n',recBits,'\nTotal de bits recebidos: ',len(recBits),'\n'

#ber
print '>BER Canal<\n *Canal: ',ber(recBits,bitString)*100,'%'


#FEC
recTextoZip = fecDecode(recStringSolomon)
if DEBUG:
    print ">Decodificacao FEC<\n"
    #print recTextoZip


print '>BER Apos Reed Solomon<\n *RS:',ber(byteStringToBitString(recTextoZip),byteStringToBitString(textoZip))*100,'%'

#decodificador fonte
try:
    textoDecodificado=decodificadorFonte(recTextoZip)
except:
    print 'Dados corrompidos'
    sys.exit(3)
#textoDecodificado=recTextoZip #remover essa linha e descomentar a acima

if DEBUG:
    print "Decodificador Fonte\n",textoDecodificado
    print "Tamanho do texto decodificado:",len(textoDecodificado)

print 'Dados recebidos com sucesso.'

arquivoFonteInformacao.close()
arquivoTemporarioAmostras.close()
arquivoTemporarioNrz.close()

