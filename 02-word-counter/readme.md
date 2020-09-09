# Contador de palavras distribuído
[server.py](./server.py) é o script que age como servidor, fazendo um bind no endereço passado como argumento (se nenhum endereço for passado, utiliza `localhost:5000` como default).
Além disso, ele também é encarregado de fazer todo o processamento necessário.
Ou seja, ele é responsável por pegar os nomes de arquivos passados, pedir para a camada 3 o conteúdo do arquivo se ele existir, e retornar a string a ser mostrada ao usuário no cliente.

[client.py](./client.py) age como o cliente, abrindo uma conexão com o servidor (também recebendo o host e a porta como argumento e utilizando o mesmo padrão de `localhost:5000` como default), e enviando para o servidor o que recebe pela entrada padrão. Para encerrar a conexão, aperte CTRL D.
Além disso, o cliente também será responsável por receber a entrada do usuário com os arquivos que devem ser utilizados para a contagem de palavras.

## Exemplo de execução
![image](https://user-images.githubusercontent.com/24783497/92542708-e6e69300-f21f-11ea-9832-732a60787f3e.png)
