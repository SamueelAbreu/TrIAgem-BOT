import sqlite3
import os

DB_FILE = "medicos.db"

# Remove o banco de dados antigo, se existir, para garantir um estado limpo
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# Conecta ao banco de dados (será criado se não existir)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Cria a tabela de médicos
cursor.execute("""
CREATE TABLE medicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_local TEXT NOT NULL,
    especialidade TEXT NOT NULL,
    endereco TEXT NOT NULL,
    telefone TEXT,
    nivel_urgencia TEXT NOT NULL -- 'alta', 'media', 'baixa'
)
""")

# Popula o banco de dados com médicos e locais fictícios
medicos = [
    # Alta Urgência (Hospitais e Pronto-Socorros)
    ('Hospital Central de Emergência', 'Pronto-Socorro', 'Av. da Saúde, 123, Centro', '(11) 91234-5678', 'alta'),
    ('Hospital Municipal', 'Emergência Geral', 'Rua das Ambulâncias, 456, Bairro Norte', '(21) 98765-4321', 'alta'),
    ('UPA 24 Horas', 'Atendimento de Urgência', 'Praça do Socorro, 789, Bairro Sul', '(31) 99887-7665', 'alta'),

    # Média Urgência (Clínicos Gerais e Especialistas)
    ('Clínica Geral Dr. House', 'Clínico Geral', 'Rua dos Diagnósticos, 101, Vila Madalena', '(41) 98877-6655', 'media'),
    ('Consultório Dr. Marcus Welby', 'Clínico Geral', 'Alameda dos Ipês, 202, Jardins', '(51) 97766-5544', 'media'),
    ('Clínica Otorrino Center', 'Otorrinolaringologista', 'Av. do Ouvido, 303, Moema', '(61) 96655-4433', 'media'),
    ('NeuroClínica', 'Neurologista', 'Rua da Mente, 404, Pinheiros', '(71) 95544-3322', 'media'),
    ('GastroCenter', 'Gastroenterologista', 'Travessa do Estômago, 505, Lapa', '(81) 94433-2211', 'media'),

    # Baixa Urgência (Postos de Saúde e Médicos de Família)
    ('Posto de Saúde Bem-Estar', 'Médico de Família', 'Rua da Comunidade, 606, Bairro Leste', '(91) 93322-1100', 'baixa'),
    ('UBS Família Feliz', 'Clínica Médica', 'Av. da Vizinhança, 707, Bairro Oeste', '(92) 92211-0099', 'baixa'),
    ('Clínica Cuida Bem', 'Médico de Família', 'Rua do Aconchego, 808, Centro Comunitário', '(93) 91100-9988', 'baixa'),
]

cursor.executemany("INSERT INTO medicos (nome_local, especialidade, endereco, telefone, nivel_urgencia) VALUES (?, ?, ?, ?, ?)", medicos)

conn.commit()
conn.close()

print(f"Banco de dados '{DB_FILE}' criado e populado com sucesso.")