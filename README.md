## 📋 Pré-requisitos
* [Docker e Docker Desktop](https://www.docker.com/products/docker-desktop/)
* [Python 3.8+](https://www.python.org/downloads/)
* [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## 2. Crie e Ative o Ambiente Virtual
```bash
# Criar o ambiente virtual
python3 -m venv venv

# Ativar o ambiente
source venv/bin/activate
```

## 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

## 4. Configure o AWS CLI para o LocalStack
```bash
aws configure
```

Preencha os prompts da seguinte forma:

    AWS Access Key ID [None]: test

    AWS Secret Access Key [None]: test

    Default region name [None]: us-east-1

    Default output format [None]: json

## Estrutura do Projeto
```bash
.
├── app.py              # Lógica principal do backend Flask
├── requirements.txt    # Dependências do Python
├── static/
│   └── background.jpg  # Imagem de fundo da aplicação
└── templates/
    └── index.html      # Estrutura HTML e CSS da página
```

# Como executar a Aplicação
## 1. Inicie o Contêiner do LocalStack
Em um terminal, execute o seguinte comando Docker para iniciar os serviços da AWS localmente. Mantenha este terminal aberto.

```bash
docker run --rm -it -p 4566:4566 -p 4510-4559:4510-4559 localstack/localstack
```


## 2. Crie o Bucket S3
Em um novo terminal (com o ambiente virtual ativado), crie o bucket que a aplicação usará.
```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://meu-balde-de-arquivos
```

## 2. Execute a Aplicação Flask
Ainda no segundo terminal, inicie o servidor web.
```bash
python3 app.py
```
## 4. Acesse a Aplicação

Abra seu navegador e acesse o seguinte endereço: http://localhost:5001














