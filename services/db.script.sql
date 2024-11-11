CREATE DATABASE estoque;
GO

USE estoque;
GO

-- Criação da tabela categoria
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='categoria' AND xtype='U')
CREATE TABLE categoria (
    categoria_id INT NOT NULL IDENTITY(1,1),
    nome VARCHAR(80) NOT NULL CONSTRAINT CHK_Nome CHECK (nome IN ('classe', 'material')),
    PRIMARY KEY (categoria_id)
);
GO

-- Criação da tabela classes
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='classes' AND xtype='U')
CREATE TABLE classes (
    id_classe INT NOT NULL IDENTITY(1,1),
    nome_classe VARCHAR(80) NOT NULL,
    categoria_id INT NOT NULL,
    PRIMARY KEY (id_classe),
    FOREIGN KEY (categoria_id) REFERENCES categoria(categoria_id)
);
GO

-- Criação da tabela material
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='material' AND xtype='U')
CREATE TABLE material (
    id_material INT NOT NULL IDENTITY(1,1),
    nome_material VARCHAR(80) NOT NULL CONSTRAINT CHK_Nome_Material CHECK (nome_material IN ('material_paciente')),
    categoria_id INT NOT NULL,
    PRIMARY KEY (id_material),
    FOREIGN KEY (categoria_id) REFERENCES categoria(categoria_id)
);
GO

-- Criação da tabela item
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='item' AND xtype='U')
CREATE TABLE item (
    id_item INT NOT NULL IDENTITY(1,1),
    nome VARCHAR(80) NOT NULL,
    categoria_id INT NOT NULL,
    data_criacao DATETIME DEFAULT GETDATE(),
    id_classe INT,
    id_material INT,
    PRIMARY KEY (id_item),
    FOREIGN KEY (categoria_id) REFERENCES categoria(categoria_id),
    FOREIGN KEY (id_classe) REFERENCES classes(id_classe),
    FOREIGN KEY (id_material) REFERENCES material(id_material)
);
GO

-- Criação da tabela saldoestoque
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='saldoestoque' AND xtype='U')
CREATE TABLE saldoestoque (
    saldo_estoque_id INT NOT NULL IDENTITY(1,1),
    id_item INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 0,
    PRIMARY KEY (saldo_estoque_id),
    FOREIGN KEY (id_item) REFERENCES item(id_item)
);
GO

-- Criação da tabela tipomov
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tipomov' AND xtype='U')
CREATE TABLE tipomov (
    tipo_mov_id INT NOT NULL IDENTITY(1,1),
    tipo VARCHAR(200) NOT NULL CONSTRAINT CHK_TipoMov CHECK (tipo IN ('entrada', 'saida')),
    PRIMARY KEY (tipo_mov_id)
);
GO

-- Criação da tabela moviestoque
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='moviestoque' AND xtype='U')
CREATE TABLE moviestoque (
    movimentacao_id INT NOT NULL IDENTITY(1,1),
    id_item INT NOT NULL,
    tipo_mov_id INT NOT NULL,
    quantidade DECIMAL(10,2) NOT NULL,
    data_movi DATETIME DEFAULT GETDATE(),
    PRIMARY KEY (movimentacao_id),
    FOREIGN KEY (id_item) REFERENCES item(id_item),
    FOREIGN KEY (tipo_mov_id) REFERENCES tipomov(tipo_mov_id)
);
GO

-- Inserindo dados de tipos de saídas
INSERT INTO tipomov (tipo) VALUES
('entrada'),
('saida');
GO

-- Inserindo dados de nome na tabela categoria
INSERT INTO categoria (nome) VALUES
('classe'),
('material');
GO

-- Inserindo dados de nome na tabela material
INSERT INTO material (nome_material, categoria_id) VALUES
('material_paciente', 2);
GO

-- Trigger para atualizar o saldo de estoque após uma movimentação
IF OBJECT_ID ('update_saldo_estoque', 'TR') IS NOT NULL
DROP TRIGGER update_saldo_estoque;
GO

CREATE TRIGGER update_saldo_estoque
ON moviestoque
AFTER INSERT
AS
BEGIN
    -- Inicia uma transação explícita
    BEGIN TRANSACTION;

    -- Verifica saldo insuficiente para saídas e lança uma exceção
    IF EXISTS (
        SELECT 1
        FROM saldoestoque s
        JOIN inserted i ON s.id_item = i.id_item
        WHERE i.tipo_mov_id = 2
        AND i.quantidade > s.quantidade
    )
    BEGIN
        ROLLBACK TRANSACTION;  -- Reverte a transação se não houver saldo suficiente
        THROW 50000, 'Estoque insuficiente para saída.', 1;
        RETURN;
    END;

    -- Atualiza o saldo existente para entradas
    UPDATE s
    SET s.quantidade = s.quantidade + i.quantidade
    FROM saldoestoque s
    JOIN inserted i ON s.id_item = i.id_item
    WHERE i.tipo_mov_id = 1;  -- Entrada

    -- Atualiza o saldo existente para saídas
    UPDATE s
    SET s.quantidade = s.quantidade - i.quantidade
    FROM saldoestoque s
    JOIN inserted i ON s.id_item = i.id_item
    WHERE i.tipo_mov_id = 2;  -- Saída

    -- Insere novos itens no saldoestoque caso eles não existam ainda
    INSERT INTO saldoestoque (id_item, quantidade)
    SELECT i.id_item, 
           CASE 
               WHEN i.tipo_mov_id = 1 THEN i.quantidade  -- Entrada
               ELSE 0  -- Saída
           END
    FROM inserted i
    WHERE NOT EXISTS (
        SELECT 1 FROM saldoestoque s WHERE s.id_item = i.id_item
    );

    -- Confirma a transação após todas as operações
    COMMIT TRANSACTION;
END;
GO

-- Criação da tabela entradasaida
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='entradasaida' AND xtype='U')
CREATE TABLE entradasaida (
    tipo_entrada_saida_id INT NOT NULL IDENTITY(1,1),
    tipo_entrada_saida_nome VARCHAR(100) NOT NULL 
        CONSTRAINT CHK_TipoSaiEnt CHECK (tipo_entrada_saida_nome IN ('balanco', 'devolucao', 'paciente', 'perda', 'nota_fiscal')),
    PRIMARY KEY(tipo_entrada_saida_id)
);
GO

-- Criação da tabela informacoes
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='informacoes' AND xtype='U')
CREATE TABLE informacoes (
    informacoes_id INT NOT NULL IDENTITY(1,1),
    tipo_entrada_saida_id INT NOT NULL,
    numero_nota INT,
    devolucao_obs VARCHAR(500),
    paciente_nome VARCHAR(500),
    motivo_perda VARCHAR(200),
    PRIMARY KEY(informacoes_id),
    FOREIGN KEY (tipo_entrada_saida_id) REFERENCES entradasaida (tipo_entrada_saida_id)
);
GO

-- Alterações na tabela moviestoque para adicionar coluna e chave estrangeira
IF COL_LENGTH('moviestoque', 'tipo_entrada_saida_id') IS NULL
BEGIN
    ALTER TABLE moviestoque
        ADD tipo_entrada_saida_id INT NOT NULL;

    ALTER TABLE moviestoque
        ADD CONSTRAINT FK_MovimentoEntradaSaida
        FOREIGN KEY (tipo_entrada_saida_id) REFERENCES entradasaida (tipo_entrada_saida_id);
END;
GO

-- Inserindo dados na tabela entradasaida
INSERT INTO entradasaida (tipo_entrada_saida_nome) VALUES
('balanco'),
('devolucao'),
('paciente'),
('perda'),
('nota_fiscal');
GO

ALTER TABLE moviestoque
ADD informacoes_id INT NOT NULL
GO

ALTER TABLE moviestoque
ADD CONSTRAINT Fk_informacoes_id
FOREIGN KEY (informacoes_id)
REFERENCES informacoes (informacoes_id)
GO

ALTER TABLE informacoes
ADD lote_nota VARCHAR(15),
	data_nota DATE
GO
