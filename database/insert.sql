INSERT INTO superviseur (prenom, nom, adresse_mail, numero_telephone) VALUES
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

-- Insertion des données dans la table jours fériés
INSERT INTO jours_feries (date_ferie) VALUES
('2025-01-01'),
('2025-03-18'),
('2025-05-01'),
('2025-06-10'),
('2025-08-15'),
('2025-11-28'), 
('2025-12-25'); 

SELECT 
    CONCAT(s.prenom, ' ', s.nom) AS superviseur,
    o.objectif,
    COALESCE(SUM(sg.total_gross_add_sim), 0) AS total_realisations,
    ROUND(COALESCE(SUM(sg.total_gross_add_sim) / o.objectif * 100, 0), 2) AS taux_realisation
FROM superviseur s
JOIN objectif_gsm o ON o.superviseur_id = s.id 
    AND DATE_FORMAT(o.mois, '%Y-%m') = '2025-03'  -- Objectif de mars 2025
LEFT JOIN coach_mobile cm ON cm.id_superviseur = s.id
LEFT JOIN synthese_gsm sg ON sg.numero_mpos = cm.numero_mpos
    AND sg.date_jour = '2025-03-30'  -- Limite à la date exacte du 30 mars 2025
GROUP BY s.id, o.objectif
ORDER BY total_realisations DESC;
