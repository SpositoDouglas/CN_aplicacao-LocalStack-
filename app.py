import boto3
from flask import Flask, request, redirect, url_for, render_template, Response, session, flash
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Chave secreta para gerenciar sessões de usuário (em produção, use um valor mais seguro)
app.secret_key = 'chave-ultra-secreta'


s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',  # Pode ser qualquer valor
    aws_secret_access_key='test', # Pode ser qualquer valor
    region_name='us-east-1'
)

dynamodb_client = boto3.client(
    'dynamodb',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

BUCKET_NAME = 'meu-balde-de-arquivos'
USER_TABLE_NAME = 'usuarios'

def criar_tabela_usuarios_se_nao_existir():
    try:
        existing_tables = dynamodb_client.list_tables()['TableNames']
        if USER_TABLE_NAME not in existing_tables:
            print(f"Tabela '{USER_TABLE_NAME}' não encontrada. Criando...")
            dynamodb_client.create_table(
                TableName=USER_TABLE_NAME,
                KeySchema=[
                    {'AttributeName': 'email', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'email', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
            waiter = dynamodb_client.get_waiter('table_exists')
            waiter.wait(TableName=USER_TABLE_NAME)
            print(f"Tabela '{USER_TABLE_NAME}' criada com sucesso.")
        else:
            print(f"Tabela '{USER_TABLE_NAME}' já existe.")
    except Exception as e:
        print(f"Erro ao verificar/criar tabela de usuários: {e}")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            response = dynamodb_client.get_item(
                TableName=USER_TABLE_NAME,
                Key={'email': {'S': email}}
            )

            if 'Item' in response:
                user_data = response['Item']
                hashed_password = user_data['password']['S']

                if check_password_hash(hashed_password, password):
                    session['user_email'] = email
                    flash('Login realizado com sucesso!', 'success')
                    return redirect(url_for('index'))
                
                else:
                    flash('E-mail ou senha incorretos.', 'danger')

            else:
                flash('E-mail ou senha incorretos.', 'danger')

        except Exception as e:
            flash(f'Erro ao fazer login: {e}', 'danger')
            
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        try:
            dynamodb_client.put_item(
                TableName=USER_TABLE_NAME,
                Item={
                    'email': {'S': email},
                    'password': {'S': hashed_password}
                },
                ConditionExpression='attribute_not_exists(email)'
            )
            flash('Conta criada com sucesso! Faça o login.', 'success')
            return redirect(url_for('login'))
        except dynamodb_client.exceptions.ConditionalCheckFailedException:
            flash('Este e-mail já está cadastrado.', 'danger')
        except Exception as e:
            flash(f'Erro ao criar conta: {e}', 'danger')

        return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    files = []
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents']]
    except Exception as e:
        print(f"Erro ao listar arquivos: {e}")

    return render_template('index.html', files=files, user_email=session['user_email'])


@app.route('/upload', methods=['POST'])
def upload():
    if 'user_email' not in session:
        return redirect(url_for('login'))
        
    if 'file' not in request.files or request.files['file'].filename == '':
        flash('Nenhum arquivo selecionado!', 'warning')
        return redirect(url_for('index'))

    file = request.files['file']
    try:
        s3_client.upload_fileobj(
            file,
            BUCKET_NAME,
            file.filename,
            ExtraArgs={'ContentType': file.content_type}
        )
        flash(f'Arquivo "{file.filename}" enviado com sucesso!', 'success')
    except Exception as e:
        flash(f"Erro no upload: {e}", 'danger')

    return redirect(url_for('index'))


@app.route('/download/<filename>')
def download(filename):
    if 'user_email' not in session:
        return redirect(url_for('login'))

    try:
        file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=filename)
        return Response(
            file_obj['Body'].read(),
            mimetype=file_obj['ContentType'],
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    except Exception as e:
        return "Arquivo não encontrado!", 404

if __name__ == '__main__':
    criar_tabela_usuarios_se_nao_existir()
    app.run(debug=True, port=5001)