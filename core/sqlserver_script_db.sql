------------------------------------------------------------
-- Crear base de datos (SQL Server)
------------------------------------------------------------
IF DB_ID(N'BibliotecaMariaDB') IS NULL
BEGIN
    CREATE DATABASE BibliotecaMariaDB;
END
GO

USE BibliotecaMariaDB;
GO

------------------------------------------------------------
-- Tablas
------------------------------------------------------------

-- Usuarios
IF OBJECT_ID(N'dbo.Usuarios', N'U') IS NOT NULL
    DROP TABLE dbo.Usuarios;
GO

CREATE TABLE dbo.Usuarios (
    UsuarioID       INT IDENTITY(1,1) PRIMARY KEY,
    NombreUsuario   VARCHAR(100) NOT NULL UNIQUE,
    ContrasenaHash  VARCHAR(256) NOT NULL
);
GO

-- Carreras
IF OBJECT_ID(N'dbo.Carreras', N'U') IS NOT NULL
    DROP TABLE dbo.Carreras;
GO

CREATE TABLE dbo.Carreras (
    CarreraID INT IDENTITY(1,1) PRIMARY KEY,
    Nombre    VARCHAR(150) NOT NULL UNIQUE
);
GO

-- Autores
IF OBJECT_ID(N'dbo.Autores', N'U') IS NOT NULL
    DROP TABLE dbo.Autores;
GO

CREATE TABLE dbo.Autores (
    AutorID   INT IDENTITY(1,1) PRIMARY KEY,
    Nombre    VARCHAR(150) NOT NULL,
    Apellido  VARCHAR(150) NOT NULL,
    CONSTRAINT UQ_Autor_NombreCompleto UNIQUE (Nombre, Apellido)
);
GO

-- Libros
IF OBJECT_ID(N'dbo.Libros', N'U') IS NOT NULL
    DROP TABLE dbo.Libros;
GO

CREATE TABLE dbo.Libros (
    LibroID            INT IDENTITY(1,1) PRIMARY KEY,
    ISBN               VARCHAR(13) NOT NULL UNIQUE,
    Titulo             VARCHAR(500) NOT NULL,
    Editorial          VARCHAR(200) NULL,
    AnioPublicacion    INT NULL,
    Ubicacion          VARCHAR(100) NULL,
    CantidadDisponible INT NOT NULL DEFAULT 1,

    CarreraID          INT NULL,
    CONSTRAINT FK_Libros_Carreras
        FOREIGN KEY (CarreraID) REFERENCES dbo.Carreras(CarreraID)
);
GO

-- TEG
IF OBJECT_ID(N'dbo.TEG', N'U') IS NOT NULL
    DROP TABLE dbo.TEG;
GO

CREATE TABLE dbo.TEG (
    TEGID            INT IDENTITY(1,1) PRIMARY KEY,
    Titulo           VARCHAR(500) NOT NULL,
    Resumen          NVARCHAR(MAX) NULL,
    AnioPublicacion  INT NOT NULL,
    PalabrasClave    VARCHAR(500) NULL,

    RutaArchivoPDF   VARCHAR(1024) NOT NULL UNIQUE,

    UsuarioAgregaID  INT NOT NULL,
    CarreraID        INT NULL,

    CONSTRAINT FK_TEG_Carreras
        FOREIGN KEY (CarreraID) REFERENCES dbo.Carreras(CarreraID),
    CONSTRAINT FK_TEG_Usuarios
        FOREIGN KEY (UsuarioAgregaID) REFERENCES dbo Usuarios(UsuarioID)
);
GO

-- TEGAutores
IF OBJECT_ID(N'dbo.TEGAutores', N'U') IS NOT NULL
    DROP TABLE dbo.TEGAutores;
GO

CREATE TABLE dbo.TEGAutores (
    TEGID   INT NOT NULL,
    AutorID INT NOT NULL,

    CONSTRAINT PK_TEGAutores PRIMARY KEY (TEGID, AutorID),

    CONSTRAINT FK_TEGAutores_TEG
        FOREIGN KEY (TEGID) REFERENCES dbo.TEG(TEGID) ON DELETE CASCADE,
    CONSTRAINT FK_TEGAutores_Autores
        FOREIGN KEY (AutorID) REFERENCES dbo.Autores(AutorID) ON DELETE CASCADE
);
GO

-- LibroAutores
IF OBJECT_ID(N'dbo.LibroAutores', N'U') IS NOT NULL
    DROP TABLE dbo.LibroAutores;
GO

CREATE TABLE dbo.LibroAutores (
    LibroID INT NOT NULL,
    AutorID INT NOT NULL,

    CONSTRAINT PK_LibroAutores PRIMARY KEY (LibroID, AutorID),
    CONSTRAINT FK_LibroAutores_Libros
        FOREIGN KEY (LibroID) REFERENCES dbo.Libros(LibroID) ON DELETE CASCADE,
    CONSTRAINT FK_LibroAutores_Autores
        FOREIGN KEY (AutorID) REFERENCES dbo.Autores(AutorID) ON DELETE CASCADE
);
GO

------------------------------------------------------------
-- Datos iniciales (equivalente a INSERT IGNORE)
------------------------------------------------------------

-- Admin de ejemplo
IF NOT EXISTS (SELECT 1 FROM dbo.Usuarios WHERE NombreUsuario = 'Gian')
BEGIN
    INSERT INTO dbo.Usuarios (NombreUsuario, ContrasenaHash)
    VALUES ('Gian', '4321');
END
GO

-- Carreras
IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Electricidad: Mencin Instalaciones Elctricas (EMIE)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Electricidad: Mencin Instalaciones Elctricas (EMIE)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Electricidad: Mencin Mantenimiento (EMM)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Electricidad: Mencin Mantenimiento (EMM)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Electrnica (ELECTRO)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Electrnica (ELECTRO)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Diseo de Obras Civiles (DOC)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Diseo de Obras Civiles (DOC)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Diseo Grfico (DG)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Diseo Grfico (DG)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Diseo Industrial (DI)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Diseo Industrial (DI)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Informtica (INF)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Informtica (INF)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Seguridad Industrial (SI)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Seguridad Industrial (SI)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Tecnologa de la Construccin Civil (TCC)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Tecnologa de la Construccin Civil (TCC)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Tecnologa Mecnica: Mencin Fabricacin (TMMF)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Tecnologa Mecnica: Mencin Fabricacin (TMMF)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Tecnologa Mecnica: Mencin Mantenimiento (TMMM)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Tecnologa Mecnica: Mencin Mantenimiento (TMMM)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Administracin: Mencin Costos (AMC)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Administracin: Mencin Costos (AMC)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Administracin: Mencin Ciencias Comerciales (AMCC)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Administracin: Mencin Ciencias Comerciales (AMCC)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Administracin: Mencin Mercadotecna (AMM)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Administracin: Mencin Mercadotecna (AMM)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Publicidad (PUB)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Publicidad (PUB)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Relaciones Industriales (RELI)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Relaciones Industriales (RELI)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Riesgos y Seguros (RS)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Riesgos y Seguros (RS)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Secretara (SECR)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Secretara (SECR)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Turismo Mencin: Hotelera (HOTEL)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Turismo Mencin: Hotelera (HOTEL)');

IF NOT EXISTS (SELECT 1 FROM dbo.Carreras WHERE Nombre = 'Turismo Mencin: Servicios Tursticos (TMST)')
    INSERT INTO dbo.Carreras (Nombre) VALUES ('Turismo Mencin: Servicios Tursticos (TMST)');
GO
