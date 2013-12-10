Exemplo de execucao do codificacador e decodificador
requisitos: -python (abaixo da versao 3)
            -gnuplot-x11 

Manchester:
    Codificacao:

        ./codificadorManchester.py 100101010

        #A codificacao gera o arquivo de saida tempmanchdif.txt

    Decodificacao:

        ./decodificadorManchester.py
        
        #caso desejes utilizar o arquivo gerado pelo codificador
        #ou:
        
        ./decodificadorManchester <arquivo>
        
        #caso desejes utilizar um outro arquivo para codificacao
        

Manchester Diferencial:
    Codificacao:

        ./codificadorManchesterDiferencial.py 100101010

        #A codificacao gera o arquivo de saida tempmanchdif.txt

    Decodificacao:

        ./decodificadorManchesterDiferencial.py
        
        #caso desejes utilizar o arquivo gerado pelo codificador
        #ou:
        
        ./decodificadorManchesterDiferencial <arquivo>
        
        #caso desejes utilizar um outro arquivo para codificacao
        
