-- Généré par Oracle SQL Developer Data Modeler 19.4.0.350.1424
--   à :        2020-01-08 16:10:17 EST
--   site :      Oracle Database 11g
--   type :      Oracle Database 11g

--suppression de toutes les tablesn sequences et triggers

--BEGIN
--
--FOR c IN (SELECT table_name FROM user_tables) LOOP
--EXECUTE IMMEDIATE ('DROP TABLE "' || c.table_name || '" CASCADE CONSTRAINTS');
--END LOOP;
--
--FOR s IN (SELECT sequence_name FROM user_sequences) LOOP
--EXECUTE IMMEDIATE ('DROP SEQUENCE ' || s.sequence_name);
--END LOOP;
--
----select 'drop trigger ' || trigger_name || ';' stmt from user_triggers;
--
--END;
--/

CREATE TABLE calendrier (
    idcalendrier      VARCHAR2(50) NOT NULL,
    nomcalendrier     VARCHAR2(50) NOT NULL,
    idadministrateur  VARCHAR2(50) NOT NULL,
    description       VARCHAR2(50),
    couleurTheme      varchar2(50) Not null
);

ALTER TABLE calendrier ADD CONSTRAINT calendrier_pk PRIMARY KEY ( idcalendrier );

CREATE TABLE calendrierevenement (
    idcalendrierevenement  INTEGER NOT NULL,
    idcalendrier           VARCHAR2(50) NOT NULL,
    idevenement            VARCHAR2(50) NOT NULL
);

ALTER TABLE calendrierevenement ADD CONSTRAINT calendrierevenement_pk PRIMARY KEY ( idcalendrierevenement );

CREATE TABLE evenement (
    idevenement   VARCHAR2(50) NOT NULL,
    datedebut     DATE,
    nomevenement  VARCHAR2(50),
    description   CLOB,
    location      VARCHAR2(150),
    datefin       DATE
);

ALTER TABLE evenement ADD CONSTRAINT evenement_pk PRIMARY KEY ( idevenement );

CREATE TABLE historiquesuivievenement (
    idhistoriquesuivi  INTEGER NOT NULL,
    idsuivi            INTEGER NOT NULL,
    datedebut          DATE,
    nomevenement       VARCHAR2(50),
    desctiption        VARCHAR2(50),
    localisation       VARCHAR2(50),
    datefin            DATE
);

ALTER TABLE historiquesuivievenement ADD CONSTRAINT historiquesuivievenement_pk PRIMARY KEY ( idhistoriquesuivi );

CREATE TABLE message (
    datemessage   DATE,
    contenu       BLOB,
    idmessage     INTEGER NOT NULL,
    idcalendrier  VARCHAR2(50) NOT NULL,
    idProprietaire varchar2(50) NOT NULL
);


ALTER TABLE message ADD CONSTRAINT message_pk PRIMARY KEY ( idmessage );

CREATE TABLE participantstransactionevt (
    idparticipant             VARCHAR2(50) NOT NULL,
    idtransaction             VARCHAR2(50) NOT NULL,
    montant                   FLOAT,
    idtransactionparticipant  INTEGER NOT NULL,
);

COMMENT ON COLUMN participantstransactionevt.etat IS
    '"Paye"
"En cours"
"A Payer"';

ALTER TABLE participantstransactionevt ADD CONSTRAINT participantstransactionevt_pk PRIMARY KEY ( idtransactionparticipant );

CREATE TABLE suivicalendrierevenement (
    idsuivi        INTEGER NOT NULL,
    idcalendrier   VARCHAR2(50),
    datesuivi      DATE,
    etat           CHAR(5),
    idutilisateur  VARCHAR2(50),
    idevenement    VARCHAR2(50)
);

ALTER TABLE suivicalendrierevenement ADD CONSTRAINT suivicalendrierevenement_pk PRIMARY KEY ( idsuivi );


CREATE TABLE suivitransaction (
    idsuivi        INTEGER NOT NULL,
    idtransaction  VARCHAR2(50),
    etat           CHAR(10),
    montant        FLOAT,
    datesuivi      DATE,
    idutilisateur  VARCHAR2(50)
);

COMMENT ON COLUMN suivitransaction.etat IS
    'ça peut être "modif" du montant total de la transaction (modificaton du montant dans la table transaction

ça peut être "remb" du montant c''est à dire que l''utilisateur en question paie une partie du montant de la transacrion ou la totalitée';

ALTER TABLE suivitransaction ADD CONSTRAINT suivitransaction_pk PRIMARY KEY ( idsuivi );

CREATE TABLE suiviutilisateurcalendrier (
    idsuivi        INTEGER NOT NULL,
    idutilisateur  VARCHAR2(50),
    etat           CHAR(10),
    idcalendrier   VARCHAR2(50),
    datesuivi      DATE
);

COMMENT ON COLUMN suiviutilisateurcalendrier.idsuivi IS
    'Faire un trigger pour verifier les etats des utilisateus dans un calendrier (ajout suppression)';

ALTER TABLE suiviutilisateurcalendrier ADD CONSTRAINT suiviutilisateurcalendrier_pk PRIMARY KEY ( idsuivi );

CREATE TABLE transaction (
    idtransaction          VARCHAR2(50) NOT NULL,
    idutilisateur          VARCHAR2(50) NOT NULL,
    montant                FLOAT,
    idcalendrierevenement  INTEGER NOT NULL,
    dateTransaction        DATE
);

ALTER TABLE transaction ADD CONSTRAINT transaction_pk PRIMARY KEY ( idtransaction );

CREATE TABLE utilisateur (
    uniqueid         VARCHAR2(50) NOT NULL,
    login            VARCHAR2(50),
    password         VARCHAR2(50),
    email            VARCHAR2(50),
    phone            VARCHAR2(50),
    photo            BLOB,
    dateinscription  DATE,
    prenom           VARCHAR2(50),
    nom              VARCHAR2(50)
);

ALTER TABLE utilisateur ADD CONSTRAINT utilisateur_pk PRIMARY KEY ( uniqueid );

CREATE TABLE utilisateurcalendrier (
    idcalendrier             VARCHAR2(50) NOT NULL,
    idutilisateur            VARCHAR2(50) NOT NULL,
    idutilisateurcalendrier  INTEGER NOT NULL,
    dateajoutinvite          DATE,
    droits                   char(1) not null,
    derniermessagelu         integer
);

ALTER TABLE utilisateurcalendrier ADD CONSTRAINT utilisateurcalendrier_pk PRIMARY KEY ( idutilisateurcalendrier );

ALTER TABLE calendrier
    ADD CONSTRAINT calendrier_utilisateur_fk FOREIGN KEY ( idadministrateur )
        REFERENCES utilisateur ( uniqueid );

--  ERROR: FK name length exceeds maximum allowed length(30) 
ALTER TABLE calendrierevenement
    ADD CONSTRAINT calendrierevent_cal_fk FOREIGN KEY ( idcalendrier )
        REFERENCES calendrier ( idcalendrier )
            ON DELETE CASCADE;

--  ERROR: FK name length exceeds maximum allowed length(30) 
ALTER TABLE calendrierevenement
    ADD CONSTRAINT calendrierevt_evt_fk FOREIGN KEY ( idevenement )
        REFERENCES evenement ( idevenement )
            ON DELETE CASCADE;

ALTER TABLE message
    ADD CONSTRAINT message_calendrier_fk FOREIGN KEY ( idcalendrier )
        REFERENCES calendrier ( idcalendrier );

ALTER TABLE message
    ADD CONSTRAINT message_proprietaire_fk FOREIGN KEY ( idproprietaire )
        REFERENCES utilisateur ( uniqueid );
        
--  ERROR: FK name length exceeds maximum allowed length(30) 
ALTER TABLE participantstransactionevt
    ADD CONSTRAINT participantstransevt_trans_fk FOREIGN KEY ( idtransaction )
        REFERENCES transaction ( idtransaction );

--  ERROR: FK name length exceeds maximum allowed length(30) 
ALTER TABLE participantstransactionevt
    ADD CONSTRAINT PTE_utilisateur_fk FOREIGN KEY ( idparticipant )
        REFERENCES utilisateur ( uniqueid );


--  ERROR: FK name length exceeds maximum allowed length(30) 
ALTER TABLE historiquesuivievenement
    ADD CONSTRAINT histosuivi_suivicalevt_fk FOREIGN KEY ( idsuivi )
        REFERENCES suivicalendrierevenement ( idsuivi );

ALTER TABLE utilisateurcalendrier
    ADD CONSTRAINT table_4_calendrier_fk FOREIGN KEY ( idcalendrier )
        REFERENCES calendrier ( idcalendrier );

ALTER TABLE utilisateurcalendrier
    ADD CONSTRAINT table_4_utilisateur_fk FOREIGN KEY ( idutilisateur )
        REFERENCES utilisateur ( uniqueid );

ALTER TABLE utilisateurcalendrier
    ADD CONSTRAINT suivimessage_message_fk FOREIGN KEY ( derniermessagelu )
        REFERENCES message ( idmessage );

--  ERROR: FK name length exceeds maximum allowed length(30) 
ALTER TABLE transaction
    ADD CONSTRAINT trans_calevt_fk FOREIGN KEY ( idcalendrierevenement )
        REFERENCES calendrierevenement ( idcalendrierevenement );

ALTER TABLE transaction
    ADD CONSTRAINT transaction_utilisateur_fk FOREIGN KEY ( idutilisateur )
        REFERENCES utilisateur ( uniqueid );

CREATE SEQUENCE calendrierevenement_idcalendri START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER calendrierevenement_idcalendri BEFORE
    INSERT ON calendrierevenement
    FOR EACH ROW
    WHEN ( new.idcalendrierevenement IS NULL )
BEGIN
    :new.idcalendrierevenement := calendrierevenement_idcalendri.nextval;
END;
/

CREATE SEQUENCE historiquesuivievenement_idhis START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER historiquesuivievenement_idhis BEFORE
    INSERT ON historiquesuivievenement
    FOR EACH ROW
    WHEN ( new.idhistoriquesuivi IS NULL )
BEGIN
    :new.idhistoriquesuivi := historiquesuivievenement_idhis.nextval;
END;
/

CREATE SEQUENCE message_idmessage_seq START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER message_idmessage_trg BEFORE
    INSERT ON message
    FOR EACH ROW
    WHEN ( new.idmessage IS NULL )
BEGIN
    :new.idmessage := message_idmessage_seq.nextval;
END;
/

CREATE SEQUENCE pute_idtransactionparticipant START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER pute_idtransactionparticipant BEFORE
    INSERT ON participantstransactionevt
    FOR EACH ROW
    WHEN ( new.idtransactionparticipant IS NULL )
BEGIN
    :new.idtransactionparticipant := pute_idtransactionparticipant.nextval;
END;
/

CREATE SEQUENCE suivicalendrierevenement_idsui START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER suivicalendrierevenement_idsui BEFORE
    INSERT ON suivicalendrierevenement
    FOR EACH ROW
    WHEN ( new.idsuivi IS NULL )
BEGIN
    :new.idsuivi := suivicalendrierevenement_idsui.nextval;
END;
/


CREATE SEQUENCE suivitransaction_idsuivi_seq START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER suivitransaction_idsuivi_trg BEFORE
    INSERT ON suivitransaction
    FOR EACH ROW
    WHEN ( new.idsuivi IS NULL )
BEGIN
    :new.idsuivi := suivitransaction_idsuivi_seq.nextval;
END;
/

CREATE SEQUENCE suiviutilisateurcalendrier_ids START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER suiviutilisateurcalendrier_ids BEFORE
    INSERT ON suiviutilisateurcalendrier
    FOR EACH ROW
    WHEN ( new.idsuivi IS NULL )
BEGIN
    :new.idsuivi := suiviutilisateurcalendrier_ids.nextval;
END;
/

CREATE SEQUENCE ug_idutilisateurcalendrier_seq START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER ug_idutilisateurcalendrier_trg BEFORE
    INSERT ON utilisateurcalendrier
    FOR EACH ROW
    WHEN ( new.idutilisateurcalendrier IS NULL )
BEGIN
    :new.idutilisateurcalendrier := ug_idutilisateurcalendrier_seq.nextval;
END;
/


--creation des current_timestamp pour les suivis
ALTER TABLE suiviUTILISATEURCALENDRIER
MODIFY dateSuivi DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE suiviCALENDRIEREVENEMENT
MODIFY dateSuivi DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE suiviTRANSACTION
MODIFY dateSuivi DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE MESSAGE
MODIFY dateMESSAGE DEFAULT CURRENT_TIMESTAMP;

-- Rapport récapitulatif d'Oracle SQL Developer Data Modeler : 
-- 
-- CREATE TABLE                            13
-- CREATE INDEX                             0
-- ALTER TABLE                             26
-- CREATE VIEW                              0
-- ALTER VIEW                               0
-- CREATE PACKAGE                           0
-- CREATE PACKAGE BODY                      0
-- CREATE PROCEDURE                         0
-- CREATE FUNCTION                          0
-- CREATE TRIGGER                           9
-- ALTER TRIGGER                            0
-- CREATE COLLECTION TYPE                   0
-- CREATE STRUCTURED TYPE                   0
-- CREATE STRUCTURED TYPE BODY              0
-- CREATE CLUSTER                           0
-- CREATE CONTEXT                           0
-- CREATE DATABASE                          0
-- CREATE DIMENSION                         0
-- CREATE DIRECTORY                         0
-- CREATE DISK GROUP                        0
-- CREATE ROLE                              0
-- CREATE ROLLBACK SEGMENT                  0
-- CREATE SEQUENCE                          9
-- CREATE MATERIALIZED VIEW                 0
-- CREATE MATERIALIZED VIEW LOG             0
-- CREATE SYNONYM                           0
-- CREATE TABLESPACE                        0
-- CREATE USER                              0
-- 
-- DROP TABLESPACE                          0
-- DROP DATABASE                            0
-- 
-- REDACTION POLICY                         0
-- 
-- ORDS DROP SCHEMA                         0
-- ORDS ENABLE SCHEMA                       0
-- ORDS ENABLE OBJECT                       0
-- 
-- ERRORS                                   7
-- WARNINGS                                 0
