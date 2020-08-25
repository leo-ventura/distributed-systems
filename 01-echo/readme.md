# Servidor básico de echo
[server.py](./server.py) é o script que age como servidor, fazendo um bind no endereço passado como argumento (se nenhum endereço for passado, utiliza localhost:5000 como default).

[client.py](./client.py) age como o cliente, abrindo uma conexão com o servidor (também recebendo o host e a porta como argumento e utilizando o mesmo padrão de localhost:5000 como default), e enviando para o servidor o que recebe pela entrada padrão. Para encerrar a conexão, aperte CTRL D.


## Exemplo de execução
![image](https://user-images.githubusercontent.com/24783497/91204491-8f520e80-e6da-11ea-88d0-7c2213f80c33.png)
