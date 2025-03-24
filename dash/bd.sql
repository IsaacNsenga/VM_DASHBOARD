-- Création de la base de données dashboard
CREATE DATABASE dashboard
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_general_ci;

-- Création de la table des Superviseurs
CREATE TABLE SUPERVISEUR (
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

-- Table synthèse GSM
CREATE TABLE synthese_gsm (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_mpos VARCHAR(50),
    total_all_sim INT DEFAULT 0,
    total_accepted_sim INT DEFAULT 0,
    taux_accepted DECIMAL(10,2) DEFAULT 0.00,
    total_gross_add_sim INT DEFAULT 0,
    taux_gross_add DECIMAL(10,2) DEFAULT 0.00,
    jour_presence INT DEFAULT 0,
    taux_presence DECIMAL(5,2) DEFAULT 0,
    drip VARCHAR(20) NOT NULL DEFAULT 'Accidental',
    productivity DECIMAL(10,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (numero_mpos) REFERENCES coach_mobile(numero_mpos) ON DELETE CASCADE
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
    -- Vérifier si le CM existe déjà dans la table synthèse
    IF NOT EXISTS (SELECT 1 FROM synthese_gsm WHERE numero_mpos = NEW.numero_mpos) THEN
        -- Insérer une nouvelle ligne avec la valeur initiale de total_sim
        INSERT INTO synthese_gsm (numero_mpos, total_all_sim, total_accepted_sim, taux_accepted, total_gross_add_sim, taux_gross_add)
        VALUES (NEW.numero_mpos, NEW.total_sim, 0, 0, 0, 0);
    ELSE
        -- Mettre à jour la somme de total_all_sim correctement
        UPDATE synthese_gsm
        SET total_all_sim = (SELECT SUM(total_sim) FROM all_sim WHERE numero_mpos = NEW.numero_mpos)
        WHERE numero_mpos = NEW.numero_mpos;
    END IF;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER after_insert_accepted_sim
AFTER INSERT ON accepted_sim
FOR EACH ROW
BEGIN
    -- Vérifier si le CM existe déjà dans la table synthèse
    IF NOT EXISTS (SELECT 1 FROM synthese_gsm WHERE numero_mpos = NEW.numero_mpos) THEN
        INSERT INTO synthese_gsm (numero_mpos, total_all_sim, total_accepted_sim, taux_accepted, total_gross_add_sim, taux_gross_add)
        VALUES (NEW.numero_mpos, 0, NEW.total_accepted, 0, 0, 0);
    ELSE
        -- Mettre à jour la somme des SIM acceptées et recalculer le taux
        UPDATE synthese_gsm
        SET total_accepted_sim = (SELECT SUM(total_accepted) FROM accepted_sim WHERE numero_mpos = NEW.numero_mpos),
            taux_accepted = IF(total_all_sim = 0, 0, total_accepted_sim / total_all_sim)  -- Correction ici
        WHERE numero_mpos = NEW.numero_mpos;
    END IF;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER after_insert_gross_add_sim
AFTER INSERT ON gross_add_sim
FOR EACH ROW
BEGIN
    -- Vérifier si le CM existe déjà dans la table synthèse
    IF NOT EXISTS (SELECT 1 FROM synthese_gsm WHERE numero_mpos = NEW.numero_mpos) THEN
        INSERT INTO synthese_gsm (numero_mpos, total_all_sim, total_accepted_sim, taux_accepted, total_gross_add_sim, taux_gross_add)
        VALUES (NEW.numero_mpos, 0, 0, 0, NEW.total_gross_add, 0);
    ELSE
        -- Mettre à jour la somme des Gross Add et recalculer le taux
        UPDATE synthese_gsm
        SET total_gross_add_sim = (SELECT SUM(total_gross_add) FROM gross_add_sim WHERE numero_mpos = NEW.numero_mpos),
            taux_gross_add = IF(total_accepted_sim = 0, 0, total_gross_add_sim / total_accepted_sim)  -- Correction ici
        WHERE numero_mpos = NEW.numero_mpos;
    END IF;
END //

DELIMITER ;


DELIMITER //

CREATE TRIGGER update_jour_presence
AFTER INSERT ON all_sim
FOR EACH ROW
BEGIN
    DECLARE jours_travail INT;
    DECLARE jours_presence INT;

    -- Calcul du nombre de jours travaillés dans le mois en excluant dimanches et jours fériés
    SELECT COUNT(*)
    INTO jours_travail
    FROM (
        SELECT DISTINCT DATE(ADDDATE(NEW.date_releve, INTERVAL -n DAY)) AS jour
        FROM (
            SELECT t0.n + t1.n * 10 AS n FROM 
            (SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
             UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t0,
            (SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
             UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t1
        ) numbers
        WHERE ADDDATE(NEW.date_releve, INTERVAL -n DAY) >= DATE_FORMAT(NEW.date_releve, '%Y-%m-01')
    ) jours
    WHERE DAYOFWEEK(jours.jour) != 1  -- Exclut les dimanches
    AND jours.jour NOT IN (SELECT date_ferie FROM jours_feries);  -- Exclut les jours fériés

    -- Calcul du nombre de jours de présence (où le CM a fait au moins une réalisation)
    SELECT COUNT(DISTINCT date_releve) INTO jours_presence
    FROM all_sim 
    WHERE numero_mpos = NEW.numero_mpos 
    AND date_releve >= DATE_FORMAT(NEW.date_releve, '%Y-%m-01')
    AND total_sim > 0;

    -- Insérer ou mettre à jour la synthèse
    IF NOT EXISTS (SELECT 1 FROM synthese_gsm WHERE numero_mpos = NEW.numero_mpos) THEN
        INSERT INTO synthese_gsm (numero_mpos, total_all_sim, total_accepted_sim, taux_accepted, 
            total_gross_add_sim, taux_gross_add, jour_presence, taux_presence)
        VALUES (NEW.numero_mpos, NEW.total_sim, 0, 0, 0, 0, jours_presence, IF(jours_travail = 0, 0, jours_presence / jours_travail));
    ELSE
        UPDATE synthese_gsm
        SET total_all_sim = total_all_sim + NEW.total_sim,
            jour_presence = jours_presence,
            taux_presence = IF(jours_travail = 0, 0, jours_presence / jours_travail)
        WHERE numero_mpos = NEW.numero_mpos;
    END IF;
END //

DELIMITER ;

DELIMITER //

-- Trigger pour INSERT
CREATE TRIGGER update_drip_productivity_insert
BEFORE INSERT ON synthese_gsm
FOR EACH ROW
BEGIN
    -- Calcul de DRIP en convertissant taux_presence en pourcentage
    SET NEW.drip = CASE 
        WHEN (NEW.taux_presence * 100) >= 90 THEN 'Daily'
        WHEN (NEW.taux_presence * 100) >= 70 THEN 'Regular'
        WHEN (NEW.taux_presence * 100) >= 50 THEN 'Irregular'
        WHEN (NEW.taux_presence * 100) >= 20 THEN 'Poor'
        ELSE 'Accidental'
    END;

    -- Calcul de la productivité
    IF NEW.jour_presence > 0 THEN
        SET NEW.productivity = NEW.total_gross_add_sim / NEW.jour_presence;
    ELSE
        SET NEW.productivity = 0;
    END IF;
END;
//

-- Trigger pour UPDATE
CREATE TRIGGER update_drip_productivity_update
BEFORE UPDATE ON synthese_gsm
FOR EACH ROW
BEGIN
    -- Calcul de DRIP en convertissant taux_presence en pourcentage
    SET NEW.drip = CASE 
        WHEN (NEW.taux_presence * 100) >= 90 THEN 'Daily'
        WHEN (NEW.taux_presence * 100) >= 70 THEN 'Regular'
        WHEN (NEW.taux_presence * 100) >= 50 THEN 'Irregular'
        WHEN (NEW.taux_presence * 100) >= 20 THEN 'Poor'
        ELSE 'Accidental'
    END;

    -- Calcul de la productivité
    IF NEW.jour_presence > 0 THEN
        SET NEW.productivity = NEW.total_gross_add_sim / NEW.jour_presence;
    ELSE
        SET NEW.productivity = 0;
    END IF;
END;
//

DELIMITER ;

