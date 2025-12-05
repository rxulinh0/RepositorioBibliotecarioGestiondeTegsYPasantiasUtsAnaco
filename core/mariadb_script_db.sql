CREATE DATABASE IF NOT EXISTS BibliotecaMariaDB CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE BibliotecaMariaDB;

CREATE TABLE Usuarios (
    UsuarioID INT PRIMARY KEY AUTO_INCREMENT,
    NombreUsuario VARCHAR(100) NOT NULL UNIQUE,
    ContrasenaHash VARCHAR(256) NOT NULL 
);

CREATE TABLE Carreras (
    CarreraID INT PRIMARY KEY AUTO_INCREMENT,
    Nombre    VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE Autores (
    AutorID INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(150) NOT NULL,
    Apellido VARCHAR(150) NOT NULL,
    GuidGlobal CHAR(36) NOT NULL UNIQUE,
    FechaActualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY UQ_Autor_NombreCompleto (Nombre, Apellido) 
);


CREATE TABLE Libros (
    LibroID INT PRIMARY KEY AUTO_INCREMENT,
    ISBN VARCHAR(13) UNIQUE NOT NULL,
    Titulo VARCHAR(500) NOT NULL,
    Editorial VARCHAR(200) NULL,
    AnioPublicacion INT NULL,
    Ubicacion VARCHAR(100) NULL,
    CantidadDisponible INT NOT NULL DEFAULT 1,
    
    CarreraID INT,
    FOREIGN KEY (CarreraID) REFERENCES Carreras(CarreraID)
);

CREATE TABLE TEG (
    TEGID INT PRIMARY KEY AUTO_INCREMENT,
    GuidGlobal CHAR(36) NOT NULL UNIQUE,
    Titulo VARCHAR(500) NOT NULL,
    Resumen TEXT NULL, 
    AnioPublicacion INT NOT NULL,
    PalabrasClave VARCHAR(500) NULL,
    
    RutaArchivoPDF VARCHAR(1024) NOT NULL UNIQUE, 
    
    UsuarioAgregaID INT NOT NULL,
    CarreraID INT,
    FechaActualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (CarreraID)      REFERENCES Carreras(CarreraID),
    FOREIGN KEY (UsuarioAgregaID) REFERENCES Usuarios(UsuarioID)
);


CREATE TABLE TEGAutores (
    TEGID   INT NOT NULL,
    AutorID INT NOT NULL,
    
    PRIMARY KEY (TEGID, AutorID),
    
    FOREIGN KEY (TEGID)  REFERENCES TEG(TEGID) ON DELETE CASCADE,
    FOREIGN KEY (AutorID) REFERENCES Autores(AutorID) ON DELETE CASCADE
);

CREATE TABLE LibroAutores (
    LibroID INT NOT NULL,
    AutorID INT NOT NULL,
    
    PRIMARY KEY (LibroID, AutorID),
    FOREIGN KEY (LibroID) REFERENCES Libros(LibroID) ON DELETE CASCADE,
    FOREIGN KEY (AutorID) REFERENCES Autores(AutorID) ON DELETE CASCADE
);


-- Admin de ejemplo
INSERT IGNORE INTO Usuarios (NombreUsuario, ContrasenaHash)
VALUES ('Gian', '4321');
INSERT IGNORE INTO Carreras (Nombre) VALUES
('Electricidad: Mención Instalaciones Eléctricas (EMIE)'),
('Electricidad: Mención Mantenimiento (EMM)'),
('Electrónica (ELECTRO)'),
('Diseño de Obras Civiles (DOC)'),
('Diseño Gráfico (DG)'),
('Diseño Industrial (DI)'),
('Informática (INF)'),
('Seguridad Industrial (SI)'),
('Tecnología de la Construcción Civil (TCC)'),
('Tecnología Mecánica: Mención Fabricación (TMMF)'),
('Tecnología Mecánica: Mención Mantenimiento (TMMM)'),
('Administración: Mención Costos (AMC)'),
('Administración: Mención Ciencias Comerciales (AMCC)'),
('Administración: Mención Mercadotecnía (AMM)'),
('Publicidad (PUB)'),
('Relaciones Industriales (RELI)'),
('Riesgos y Seguros (RS)'),
('Secretaría (SECR)'),
('Turismo Mención: Hotelería (HOTEL)'),
('Turismo Mención: Servicios Turísticos (TMST)');

