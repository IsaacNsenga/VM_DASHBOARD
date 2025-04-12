-- Création de la base de données dashboard
CREATE DATABASE dashboard
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_general_ci;

-- Création de la table des Superviseurs
CREATE TABLE superviseur (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prenom VARCHAR(50),
    nom VARCHAR(50),
    adresse_mail VARCHAR(100) UNIQUE,
    numero_telephone VARCHAR(20) UNIQUE
) ENGINE=InnoDB;

-- Création de la table des Coachs Mobiles (CM)
CREATE TABLE coach_mobile (
    numero_mpos VARCHAR(20) UNIQUE,
    reg_user_name VARCHAR(50),
    noms_prenoms VARCHAR(100),
    numero_cni VARCHAR(30),
    id_superviseur INT,
    PRIMARY KEY (numero_mpos),
    FOREIGN KEY (id_superviseur) REFERENCES superviseur(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Table pour enregistrer toutes les SIMs enregistrées par jour
CREATE TABLE all_sim (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_mpos VARCHAR(50) UNIQUE,
    date_releve DATE NOT NULL UNIQUE,
    total_sim INT NOT NULL,
    FOREIGN KEY (numero_mpos) REFERENCES coach_mobile(numero_mpos) ON DELETE CASCADE
);

-- Table pour les SIMs acceptées par jour
CREATE TABLE accepted_sim (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_mpos VARCHAR(50),
    date_releve DATE NOT NULL,
    total_accepted INT NOT NULL,
    FOREIGN KEY (numero_mpos) REFERENCES coach_mobile(numero_mpos) ON DELETE CASCADE
);

-- Table pour les Gross Add SIM par jour
CREATE TABLE gross_add_sim (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_mpos VARCHAR(50) UNIQUE ,
    date_releve DATE NOT NULL UNIQUE ,
    total_gross_add INT NOT NULL,
    FOREIGN KEY (numero_mpos) REFERENCES coach_mobile(numero_mpos) ON DELETE CASCADE
);

-- Table synthèse GSM avec ajout de la colonne date_jour
CREATE TABLE synthese_gsm (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_mpos VARCHAR(50),
    date_jour DATE NOT NULL,  -- Ajout de la colonne date_jour
    total_all_sim INT DEFAULT 0,
    total_accepted_sim INT DEFAULT 0,
    taux_accepted DECIMAL(10,2) DEFAULT 0.00,
    total_gross_add_sim INT DEFAULT 0,
    taux_gross_add DECIMAL(10,2) DEFAULT 0.00,
    jour_presence INT DEFAULT 0,
    taux_presence DECIMAL(5,2) DEFAULT 0,
    drip VARCHAR(20) NOT NULL DEFAULT 'Accidental',
    productivity DECIMAL(10,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (numero_mpos) REFERENCES coach_mobile(numero_mpos) ON DELETE CASCADE,
    UNIQUE (numero_mpos, date_jour)  -- Contrainte UNIQUE sur numero_mpos et date_jour
);

CREATE TABLE IF NOT EXISTS jours_feries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date_ferie DATE UNIQUE NOT NULL
);

DELIMITER //

CREATE TRIGGER after_insert_all_sim
AFTER INSERT ON all_sim
FOR EACH ROW
BEGIN
    DECLARE cumul_total_sim INT;

    -- Calcul du cumul de total_sim depuis le début du mois jusqu'à la date de la ligne insérée
    SELECT SUM(total_sim) INTO cumul_total_sim
    FROM all_sim
    WHERE numero_mpos = NEW.numero_mpos
      AND date_releve BETWEEN DATE_FORMAT(NEW.date_releve, '%Y-%m-01') AND NEW.date_releve;

    -- Insérer ou mettre à jour la synthèse pour la date du jour
    IF NOT EXISTS (
        SELECT 1 FROM synthese_gsm
        WHERE numero_mpos = NEW.numero_mpos AND date_jour = NEW.date_releve
    ) THEN
        INSERT INTO synthese_gsm (
            numero_mpos, date_jour, total_all_sim
        ) VALUES (
            NEW.numero_mpos, NEW.date_releve, cumul_total_sim
        );
    ELSE
        UPDATE synthese_gsm
        SET total_all_sim = cumul_total_sim
        WHERE numero_mpos = NEW.numero_mpos AND date_jour = NEW.date_releve;
    END IF;
END;
//

DELIMITER ;

DELIMITER //

CREATE TRIGGER after_insert_accepted_sim
AFTER INSERT ON accepted_sim
FOR EACH ROW
BEGIN
    DECLARE cumul_total_accepted INT;
    DECLARE cumul_total_all INT;

    -- Cumul accepted du début du mois jusqu’à la date insérée
    SELECT SUM(total_accepted) INTO cumul_total_accepted
    FROM accepted_sim
    WHERE numero_mpos = NEW.numero_mpos
      AND date_releve BETWEEN DATE_FORMAT(NEW.date_releve, '%Y-%m-01') AND NEW.date_releve;

    -- Cumul all_sim pour la même période (pour le taux)
    SELECT SUM(total_sim) INTO cumul_total_all
    FROM all_sim
    WHERE numero_mpos = NEW.numero_mpos
      AND date_releve BETWEEN DATE_FORMAT(NEW.date_releve, '%Y-%m-01') AND NEW.date_releve;

    -- Mettre à jour ou insérer la ligne synthèse
    IF NOT EXISTS (
        SELECT 1 FROM synthese_gsm
        WHERE numero_mpos = NEW.numero_mpos AND date_jour = NEW.date_releve
    ) THEN
        INSERT INTO synthese_gsm (
            numero_mpos, date_jour, total_accepted_sim, taux_accepted
        ) VALUES (
            NEW.numero_mpos, NEW.date_releve,
            IFNULL(cumul_total_accepted, 0),
            IF(cumul_total_all = 0, 0, cumul_total_accepted / cumul_total_all)
        );
    ELSE
        UPDATE synthese_gsm
        SET total_accepted_sim = IFNULL(cumul_total_accepted, 0),
            taux_accepted = IF(cumul_total_all = 0, 0, cumul_total_accepted / cumul_total_all)
        WHERE numero_mpos = NEW.numero_mpos AND date_jour = NEW.date_releve;
    END IF;
END;
//

DELIMITER ;

DELIMITER //

CREATE TRIGGER after_insert_gross_add_sim
AFTER INSERT ON gross_add_sim
FOR EACH ROW
BEGIN
    DECLARE cumul_total_gross INT;
    DECLARE cumul_total_accepted INT;

    -- Cumul gross_add du début du mois à cette date
    SELECT SUM(total_gross_add) INTO cumul_total_gross
    FROM gross_add_sim
    WHERE numero_mpos = NEW.numero_mpos
      AND date_releve BETWEEN DATE_FORMAT(NEW.date_releve, '%Y-%m-01') AND NEW.date_releve;

    -- Cumul accepted_sim pour le taux
    SELECT SUM(total_accepted) INTO cumul_total_accepted
    FROM accepted_sim
    WHERE numero_mpos = NEW.numero_mpos
      AND date_releve BETWEEN DATE_FORMAT(NEW.date_releve, '%Y-%m-01') AND NEW.date_releve;

    -- Mettre à jour ou insérer dans synthèse
    IF NOT EXISTS (
        SELECT 1 FROM synthese_gsm
        WHERE numero_mpos = NEW.numero_mpos AND date_jour = NEW.date_releve
    ) THEN
        INSERT INTO synthese_gsm (
            numero_mpos, date_jour, total_gross_add_sim, taux_gross_add
        ) VALUES (
            NEW.numero_mpos, NEW.date_releve,
            IFNULL(cumul_total_gross, 0),
            IF(cumul_total_accepted = 0, 0, cumul_total_gross / cumul_total_accepted)
        );
    ELSE
        UPDATE synthese_gsm
        SET total_gross_add_sim = IFNULL(cumul_total_gross, 0),
            taux_gross_add = IF(cumul_total_accepted = 0, 0, cumul_total_gross / cumul_total_accepted)
        WHERE numero_mpos = NEW.numero_mpos AND date_jour = NEW.date_releve;
    END IF;
END;
//

DELIMITER ;

DELIMITER //

CREATE TRIGGER after_insert_jour_presence
AFTER INSERT ON all_sim
FOR EACH ROW
BEGIN
    DECLARE jours_travail INT;
    DECLARE jours_presence INT;

    -- Jours ouvrés du mois (hors dimanches et jours fériés)
    SELECT COUNT(*) INTO jours_travail
    FROM (
        SELECT DISTINCT ADDDATE(DATE_FORMAT(NEW.date_releve, '%Y-%m-01'), INTERVAL seq DAY) AS jour
        FROM (
            SELECT t0.n + t1.n * 10 AS seq
            FROM 
                (SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
                 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t0,
                (SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
                 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t1
        ) numbers
        WHERE ADDDATE(DATE_FORMAT(NEW.date_releve, '%Y-%m-01'), INTERVAL seq DAY) <= NEW.date_releve
    ) jours
    WHERE DAYOFWEEK(jours.jour) != 1
      AND jours.jour NOT IN (SELECT date_ferie FROM jours_feries);

    -- Jours de présence (au moins un total_sim > 0)
    SELECT COUNT(DISTINCT date_releve) INTO jours_presence
    FROM all_sim
    WHERE numero_mpos = NEW.numero_mpos
      AND date_releve BETWEEN DATE_FORMAT(NEW.date_releve, '%Y-%m-01') AND NEW.date_releve
      AND total_sim > 0;

    -- Insérer ou mettre à jour la ligne correspondante
    IF NOT EXISTS (
        SELECT 1 FROM synthese_gsm WHERE numero_mpos = NEW.numero_mpos AND date_jour = NEW.date_releve
    ) THEN
        INSERT INTO synthese_gsm (
            numero_mpos, date_jour, jour_presence, taux_presence
        ) VALUES (
            NEW.numero_mpos, NEW.date_releve,
            jours_presence,
            IF(jours_travail = 0, 0, jours_presence / jours_travail)
        );
    ELSE
        UPDATE synthese_gsm
        SET jour_presence = jours_presence,
            taux_presence = IF(jours_travail = 0, 0, jours_presence / jours_travail)
        WHERE numero_mpos = NEW.numero_mpos AND date_jour = NEW.date_releve;
    END IF;
END;
//

DELIMITER ;

DELIMITER //

-- INSERT
CREATE TRIGGER update_drip_productivity_insert
BEFORE INSERT ON synthese_gsm
FOR EACH ROW
BEGIN
    SET NEW.drip = CASE 
        WHEN (NEW.taux_presence * 100) >= 90 THEN 'Daily'
        WHEN (NEW.taux_presence * 100) >= 70 THEN 'Regular'
        WHEN (NEW.taux_presence * 100) >= 50 THEN 'Irregular'
        WHEN (NEW.taux_presence * 100) >= 20 THEN 'Poor'
        ELSE 'Accidental'
    END;

    IF NEW.jour_presence > 0 THEN
        SET NEW.productivity = NEW.total_gross_add_sim / NEW.jour_presence;
    ELSE
        SET NEW.productivity = 0;
    END IF;
END;
//

-- UPDATE
CREATE TRIGGER update_drip_productivity_update
BEFORE UPDATE ON synthese_gsm
FOR EACH ROW
BEGIN
    SET NEW.drip = CASE 
        WHEN (NEW.taux_presence * 100) >= 90 THEN 'Daily'
        WHEN (NEW.taux_presence * 100) >= 70 THEN 'Regular'
        WHEN (NEW.taux_presence * 100) >= 50 THEN 'Irregular'
        WHEN (NEW.taux_presence * 100) >= 20 THEN 'Poor'
        ELSE 'Accidental'
    END;

    IF NEW.jour_presence > 0 THEN
        SET NEW.productivity = NEW.total_gross_add_sim / NEW.jour_presence;
    ELSE
        SET NEW.productivity = 0;
    END IF;
END;
//

DELIMITER ;

-- Table pour les objectifs superviseurs
CREATE TABLE objectif_gsm (
    id INT AUTO_INCREMENT PRIMARY KEY,
    superviseur_id INT UNIQUE,
    mois DATE UNIQUE,
    objectif INT,
    FOREIGN KEY (superviseur_id) REFERENCES superviseur(id)
) ENGINE=InnoDB;
