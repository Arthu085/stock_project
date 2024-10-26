CREATE database estoque;

USE estoque;

-- Criação da tabela categoria
CREATE TABLE categoria (
    categoria_id INT NOT NULL IDENTITY(1,1),
    nome VARCHAR(80) NOT NULL CONSTRAINT CHK_Nome CHECK (nome IN ('classe', 'material')),
    PRIMARY KEY (categoria_id)
);

-- Criação da tabela classes
CREATE TABLE classes (
    id_classe INT NOT NULL IDENTITY(1,1),
    nome_classe VARCHAR(80) NOT NULL,
    categoria_id INT NOT NULL,
    PRIMARY KEY (id_classe),
    FOREIGN KEY (categoria_id) REFERENCES categoria(categoria_id)
);

-- Criação da tabela material
CREATE TABLE material (
    id_material INT NOT NULL IDENTITY(1,1),
    nome_material VARCHAR(80) NOT NULL CONSTRAINT CHK_Nome_Material CHECK (nome_material IN ('material_paciente')),
    categoria_id INT NOT NULL,
    PRIMARY KEY (id_material),
    FOREIGN KEY (categoria_id) REFERENCES categoria(categoria_id)
);

-- Criação da tabela item
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

-- Criação da tabela saldoestoque
CREATE TABLE saldoestoque (
    saldo_estoque_id INT NOT NULL IDENTITY(1,1),
    id_item INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 0,
    PRIMARY KEY (saldo_estoque_id),
    FOREIGN KEY (id_item) REFERENCES item(id_item)
);

-- Criação da tabela tipomov
CREATE TABLE tipomov (
    tipo_mov_id INT NOT NULL IDENTITY(1,1),
    tipo VARCHAR(200) NOT NULL CONSTRAINT CHK_TipoMov CHECK (tipo IN ('entrada', 'saida')),
    PRIMARY KEY (tipo_mov_id)
);

-- Criação da tabela moviestoque
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

-- Inserindo dados de tipos de saídas
INSERT INTO tipomov (tipo) VALUES
('entrada'),
('saida')
GO

-- Inserindo dados de nome na tabela categoria
INSERT INTO categoria (nome) VALUES
('classe'),
('material')
GO

-- Inserindo dados de nome na tabela material
INSERT INTO material (nome_material, categoria_id) VALUES
('material_paciente', 2)
GO

-- Trigger para atualizar o saldo de estoque após uma movimentação
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