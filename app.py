import boto3
from flask import Flask, request, redirect, url_for, render_template, Response
import os

app = Flask(__name__)

# --- Configuração do Boto3 para o LocalStack ---
# A chave é apontar o endpoint_url para o nosso container LocalStack
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',  # Pode ser qualquer valor
    aws_secret_access_key='test', # Pode ser qualquer valor
    region_name='us-east-1'
)

BUCKET_NAME = 'meu-balde-de-arquivos'

@app.route('/')
def index():
    """
    Página inicial que lista os arquivos do bucket e mostra o formulário de upload.
    """
    files = []
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents']]
    except Exception as e:
        print(f"Erro ao listar arquivos: {e}")
        # Se o bucket não existir, podemos tentar criá-lo
        try:
            s3_client.create_bucket(Bucket=BUCKET_NAME)
        except Exception as create_error:
            print(f"Erro ao criar bucket: {create_error}")

    return render_template('index.html', files=files)


@app.route('/upload', methods=['POST'])
def upload():
    """
    Rota para fazer o upload de um arquivo para o S3.
    """
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        try:
            s3_client.upload_fileobj(
                file,
                BUCKET_NAME,
                file.filename,
                ExtraArgs={'ContentType': file.content_type} # Importante para o navegador saber o tipo do arquivo
            )
        except Exception as e:
            print(f"Erro no upload: {e}")
            return "Erro no upload!", 500

    return redirect(url_for('index'))


@app.route('/download/<filename>')
def download(filename):
    """
    Rota para baixar um arquivo do S3.
    """
    try:
        file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=filename)
        return Response(
            file_obj['Body'].read(),
            mimetype=file_obj['ContentType'],
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    except Exception as e:
        print(f"Erro no download: {e}")
        return "Arquivo não encontrado!", 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)