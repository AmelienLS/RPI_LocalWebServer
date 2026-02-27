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

CREATE TABLE IF NOT EXISTS sortie_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_ecran INTEGER NOT NULL,
    libelle TEXT NOT NULL,
    personne TEXT NOT NULL,
    personne_rangement TEXT,
    sortie_ts TEXT NOT NULL,
    rangement_ts TEXT,
    lavee INTEGER,
    FOREIGN KEY (ref_ecran) REFERENCES serigraphie (ref_ecran)
);

CREATE INDEX IF NOT EXISTS idx_sortie_logs_ref ON sortie_logs (ref_ecran, rangement_ts);
CREATE INDEX IF NOT EXISTS idx_sortie_logs_date ON sortie_logs (sortie_ts);

INSERT OR IGNORE INTO users (identifiant, prenom, nom, admin) VALUES ('admin', 'amélien', 'larade', 1);
