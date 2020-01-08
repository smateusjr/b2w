**PLANET API**

Gostaria de agradeçer a oportunidade e espero que a minha forma de pensar seja compativel com a B2w.

Pensei nos detalhes, mas não aprofundei neles por causa do tempo, tenho outras atividades na semana, exemplo: o Swagger, versionamento da API, classe de logs, etc. 

**Instalação:**
Python 3.7.3

Necessário:
- MongoDB
- Redis

#### Instalação simples usando o requirements.txt
pip install -r requirements.txt


#### Configuração
Na pasta "Code/configs" existe os templates necessários para a criação de 3 arquivos obrigatórios:

MongoDB - Criar a Database "starwars" e a colletion "planet".

config.ini - Configurações da API.
- Versionamento do arquivo utils
- Criação de novos Clients e Secret Ids e usuários de acesso à API (Deveria ser em outro servidor)
- Criação e configuração dos HTTP_CODES da API.

server.ini - Configurações do servidor.
- Configurações do tornado
- Configurações do swagger
- Configurações do redis
- Configurações do MongoDB
- Configurações da url da API SWAPI

config_unit_test.ini - Arquivo com o mock de usuários, senhas, clients e secrets da API.

#### Daemon
O arquivo service.sh.template é um shell usado para iniciar a aplicação como serviço.
Configurar e copiar para "/etc/init.d/planet" 

Configuração:

DIRVENV='~/.virtualenvs/b2w/'

#Caminho absoluto do diretório onde esta a virtualenv

DIRBASE='~/Documents/projects/b2w/Code/'

#Caminho absoluto do diretório onde esta o código da aplicação

Como usar service.sh:

*/etc/init.d/planet stop | start | restart | reload | status | help | unittest* 


#### Versionamento
Para criar uma versão nova da API basta criar uma nova pasta em "Code/application" com a versão desejada, exemplo "Code/application/v2" 
Também é possivel versionar o arquivo utils "Code/utils" com funções especificas para cada versão de API.

#### Unit Test

Todos os arquivos estão na pasta "Code/tests"
Pode ser configurado em uma IDE, usando o service.sh com o parâmetro "unittest" ou com a linha abaixo:

#python -m unittest discover -s /Users/smateus/Documents/projects/b2w/Code/tests -t /Users/smateus/Documents/projects/b2w/Code/tests

#### API
Nenhum parâmetro é obrigatório, assim ele usa as informações default dos arquivos .ini
O Swagger é iniciado junto com a aplicação na opção -doc, sendo acessado na url base da aplicação, exemplo:
http://localhost:8889  

python main.py -h
usage: main.py [-h] [-action {kill,reload,daemon}] [-doc] [-i INSTANCES]
               [-p PORT] [-t TEST]

optional arguments:
  -h, --help            show this help message and exit

  -doc, --docs          Load Documentation

  -i INSTANCES, --instances INSTANCES Number of instances

  -p PORT, --port PORT  Port Number

  -t TEST, --test TEST  Run in test Mode

Action options:
  -action {kill,reload,daemon} Select the action.

#### Envio de dados

Pode ser enviado via "Content Type json" ou via "x-www-form-urlencoded" 


#### Logs

2 tipos de Logs:
Esta em um formato onde podemos colocar em no logstach ou no newrelic

- access - Log com todos os acessos nivel de INFO 

- aplicação - Log de debug com passo a passo da requisição (request_id) 
