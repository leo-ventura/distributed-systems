# Contador de palavras distribuído e concorrente
Nesse laboratório continuamos a implementação do laboratório anterior, mas utilizando concorrência (por meio de threads) e aceitando também leitura de diferentes descritores (como socket e stdin).

Para isso, foram desenvolvidos os seguintes módulos:

## Servidor
 - [server.py](./server.py) é o script que age como servidor, fazendo um bind no endereço passado como argumento (se nenhum endereço for passado, utiliza `localhost:5000` como default).
Nele é realizada toda a lógica de processamento.
 - [wordCounter.py](./wordCounter.py) é o módulo responsável pelo processamento das palavras recebidas pelo servidor, nele é gerado o dicionário com as palavras mais frequentes do arquivo passado.
 - [fileReader.py](./fileReader.py) é o módulo de leitura de arquivo. Retorna o conteúdo do arquivo passado ou gera uma exceção se o arquivo não existir.
 - [serverSocket.py](./serverSocket.py) é o encapsulador do socket do servidor. Nele mantemos a lógica de interação do socket com clientes, iniciando uma nova thread quando um novo cliente é recebido e o método `ready` é chamado.
 - [StdinWrapper.py](./StdinWrapper.py) é o encapsulador da entrada padrão. O utilizamos para lidar com o que o administrador do servidor digita pela entrada padrão do servidor. Assim como no `serverSocket`, lidamos com a entrada padrão do administrador quando o método `ready` é chamado.

## Cliente
 - [client.py](./client.py) age como o cliente, abrindo uma conexão com o servidor (também recebendo o host e a porta como argumento e utilizando o mesmo padrão de `localhost:5000` como default), e enviando para o servidor o que recebe pela entrada padrão. Para encerrar a conexão, aperte CTRL D. Além disso, o cliente também será responsável por receber a entrada do usuário com os arquivos que devem ser utilizados para a contagem de palavras.

## Exemplo de execução
![image](https://user-images.githubusercontent.com/24783497/93278088-10606b00-f79a-11ea-8506-cc89c0083bcb.png)
