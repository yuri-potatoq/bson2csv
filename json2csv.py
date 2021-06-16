import argparse
import csv
import logging

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger('main')


class QuestionParser:
    def __init__(
        self, db_name: str = None, filename: str = 'quesions',
        db_host: str = 'localhost', collection: str = 'questions'
    ):
        self.filename = filename
        self.db_host = db_host
        self.db_name = db_name
        self.collection = collection
        self.db = None
        self.connection = None
        self.cursor = None
    
    def connect_on_db(self):
        try:        
            self.connection = MongoClient(
                host=self.db_host, port=27016,
                username='admin', password='admin',
                authSource='admin')

            self.db = self.connection.get_database(self.db_name)

            logger.debug(f"Conectado em {self.db.name}")

        except ConnectionFailure as err:
            logger.error(
                'Erro ao conectar no banco.\n'
                f'db_name: {self.db_name}\n'
                f'db_host: {self.db_host}\n'
                f'err_details: {err.args}\n')

        finally:
            ...

    def __enter__(self):
        self.connect_on_db()

        self.cursor = self.db[self.collection].find()

        return self
        
    def __exit__(self, _type, _value, _traceback):
        self.connection.close()


# set parser para kwargs #
parser = argparse.ArgumentParser(description="""
    Script para parsear modelo de objeto BSON em CSV.
""")


# declara argumentos necessário para o script # 
parser.add_argument('--filename', help="Nome do arquivo CSV alvo.")
parser.add_argument('--db', help="Nome da database no SGDB")
parser.add_argument('--collection', help="Nome da coleção alvo a ser consumida.")
parser.add_argument('--db-host', help="Endereço no qual o banco se encontra.")

with QuestionParser(db_name='sea-point') as parser:
    field_names = [
        'Nota',
        'Avaliação',
        'Por que você escolheu a SEA TELECOM?',
        'outros-1',
        'Oque mais você gostou?',
        'outros-2',
        'Oque menos você gostou?'
        'outros-3',
    ]
    with open(parser.filename + '.csv', 'w') as csv_fp:
        csv_writer = csv.writer(
            csv_fp, delimiter=',',
            quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

        # escreve o cabeçalho no csv #
        csv_writer.writerow(field_names)

        # escreve cada uma dos documentos em uma row #
        for document in parser.cursor:
            answers = [value['answer']['selection']for value in document['values']]
            extra_answers = [value['answer']['text'] for value in document['values']]

            csv_writer.writerow([
                document['satisfactionLevel'],  # nota
                document['satisfactionAnswer'],  # avaliação
                answers[0], extra_answers[0],
                answers[1], extra_answers[1],
                answers[2], extra_answers[2]
            ])
