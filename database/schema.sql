CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    identifiant TEXT UNIQUE NOT NULL,
    admin INTEGER NOT NULL CHECK(admin IN (0, 1))
);

CREATE TABLE IF NOT EXISTS serigraphie (
    ref_ecran INTEGER PRIMARY KEY,
    libelle TEXT NOT NULL,
    pcb INTEGER,
    fab TEXT NOT NULL,
    n_fab TEXT,
    type TEXT NOT NULL,
    n TEXT NOT NULL UNIQUE,
    sorti INTEGER DEFAULT 0,
    lave INTEGER DEFAULT 1
);
