INSERT INTO SUPERVISEUR (prenom, nom, adresse_mail, numero_telephone) VALUES
('AYMARD', 'BANTSIMBA', 'bantsimba.aymard@gmail.com', CONCAT('24206', FLOOR(RAND() * 10000000))),
('JUDEL', 'BATOUMOUENI', 'batoumoueni.judel@gmail.com', CONCAT('24206', FLOOR(RAND() * 10000000))),
('SERGES', 'BAZONZAMIO', 'bazonzamio.serges@gmail.com', CONCAT('24206', FLOOR(RAND() * 10000000))),
('HERMAN', 'ETOU', 'etou.herman@gmail.com', CONCAT('24206', FLOOR(RAND() * 10000000))),
('RY', 'KOMBO MBOUAKA', 'kombo.mbouaka.ry@gmail.com', CONCAT('24206', FLOOR(RAND() * 10000000))),
('JORDEIL', 'MAHOUMA', 'mahouma.jordeil@gmail.com', CONCAT('24206', FLOOR(RAND() * 10000000))),
('JOSLAIN', 'MALONGA', 'malonga.joslain@gmail.com', CONCAT('24206', FLOOR(RAND() * 10000000))),
('CHRIST', 'MBOUNGOU', 'mboungou.christ@gmail.com', CONCAT('24206', FLOOR(RAND() * 10000000))),
('ABEL', 'MOUKENGUE', 'moukengue.abel@gmail.com', CONCAT('24206', FLOOR(RAND() * 10000000))),
('JOB', 'TOUMBA', 'toumba.job@gmail.com', CONCAT('24206', FLOOR(RAND() * 10000000)));

-- Insertion des données dans la table all_sim
INSERT INTO all_sim (numero_mpos, date_releve, total_sim)
VALUES
('242067630401', '2025-03-01', 5),
('242067630401', '2025-03-02', 0),
('242067630401', '2025-03-03', 9),
('242067630420', '2025-03-01', 0),
('242067630420', '2025-03-02', 0),
('242067630420', '2025-03-03', 9),
('242067630351', '2025-03-01', 0),
('242067630351', '2025-03-02', 4),
('242067630351', '2025-03-03', 1),
('242067630401', '2025-03-04', 5),
('242067630401', '2025-03-05', 5),
('242067630401', '2025-03-06', 6),
('242067630420', '2025-03-04', 9),
('242067630420', '2025-03-05', 9),
('242067630420', '2025-03-06', 10),
('242067630351', '2025-03-04', 5),
('242067630351', '2025-03-05', 3),
('242067630351', '2025-03-06', 7);

-- Insertion des données dans la table accepted_sim
INSERT INTO accepted_sim (numero_mpos, date_releve, total_accepted)
VALUES
('242067630401', '2025-03-01', 4),
('242067630401', '2025-03-02', 0),
('242067630401', '2025-03-03', 8),
('242067630420', '2025-03-01', 0),
('242067630420', '2025-03-02', 0),
('242067630420', '2025-03-03', 9),
('242067630351', '2025-03-01', 0),
('242067630351', '2025-03-02', 4),
('242067630351', '2025-03-03', 1),
('242067630401', '2025-03-04', 5),
('242067630401', '2025-03-05', 4),
('242067630401', '2025-03-06', 6),
('242067630420', '2025-03-04', 9),
('242067630420', '2025-03-05', 9),
('242067630420', '2025-03-06', 10),
('242067630351', '2025-03-04', 5),
('242067630351', '2025-03-05', 3),
('242067630351', '2025-03-06', 7);

-- Insertion des données dans la table gross_add_sim
INSERT INTO gross_add_sim (numero_mpos, date_releve, total_gross_add)
VALUES
('242067630401', '2025-03-01', 4),
('242067630401', '2025-03-02', 0),
('242067630401', '2025-03-03', 7),
('242067630420', '2025-03-01', 0),
('242067630420', '2025-03-02', 0),
('242067630420', '2025-03-03', 9),
('242067630351', '2025-03-01', 0),
('242067630351', '2025-03-02', 4),
('242067630351', '2025-03-03', 1),
('242067630401', '2025-03-04', 5),
('242067630401', '2025-03-05', 4),
('242067630401', '2025-03-06', 6),
('242067630420', '2025-03-04', 7),
('242067630420', '2025-03-05', 7),
('242067630420', '2025-03-06', 8),
('242067630351', '2025-03-04', 5),
('242067630351', '2025-03-05', 3),
('242067630351', '2025-03-06', 7);

-- Insertion des données dans la table jours fériés
INSERT INTO jours_feries (date_ferie) VALUES
('2025-01-01'),  -- Nouvel An
('2025-03-18'),  -- Journée de la République
('2025-05-01'),  -- Fête du Travail
('2025-06-10'),  -- Journée de la Réconciliation
('2025-08-15'),  -- Assomption
('2025-11-28'),  -- Fête de la République
('2025-12-25');  -- Noël