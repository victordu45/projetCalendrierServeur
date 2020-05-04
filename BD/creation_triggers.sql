
--trg pour ajouter un suivis des utilisateurs : S'IL EST AJOUTÉ OU SUPPRIMÉ
Create or replace TRIGGER SUIVI_UTILISATEUR_CAL_TRG 
before INSERT OR DELETE 
ON UTILISATEURCALENDRIER 
for each row
DECLARE
    etatUtilisateur varchar2(50);
BEGIN
    IF INSERTING THEN
        etatUtilisateur := 'ADD';
    ELSE
          etatUtilisateur := 'DEL';
    END IF;
    INSERT INTO SUIVIUTILISATEURCALENDRIER(idUtilisateur,idCalendrier,etat) values (:new.idUtilisateur, :new.idCalendrier,etatUtilisateur);
    
END;
/

Create or replace TRIGGER PARTICIPANTS_EVT_TRG 
before INSERT or DELETE
ON Transaction 
for each row
DECLARE
    montant_initial             float;
    nombre_personne_calendrier  number;
BEGIN
    --si on insert : on ajoute toutes les personnes du calendrier en tant que participants
    IF INSERTING THEN
    
    --recuperation du nombre de personnes dans un groupe.
    Select count(idutilisateur) into nombre_personne_calendrier 
    from utilisateurCalendrier 
    where idCalendrier in (select idCalendrier
                            from calendrierEvenement
                            where idCalendrierEvenement = :new.idCalendrierEvenement);
    
    montant_initial := :new.montant/nombre_personne_calendrier;
    
    insert into ParticipantsTransactionEvt(idparticipant,idtransaction,montant,etat) 
    select idutilisateur, :new.idTransaction,1,'a payer'
                            from utilisateurcalendrier 
                            where idcalendrier in (select idcalendrier 
                                                   from calendrierEvenement
                                                   where idCalendrierEvenement = :new.idCalendrierEvenement);
    
    END IF;
    --si on delete un evenement, tous les participants sont supprimés
END;
/



create or replace TRIGGER CREATION_CAL_PERSO_TRG
AFTER INSERT
ON UTILISATEUR
for each row
declare
    idCalendrierValue   varchar2(50);
begin
    idCalendrierValue := 'PERSO' || '-' || SUBSTR(:new.login,1,3) || '-' || TO_CHAR(sysdate, 'MMDDYYYY') ||'_'|| ID_CALENDRIER_SEQ.NEXTVAL;
    
    Insert into calendrier (idCalendrier, nomCalendrier,idAdministrateur,description) values
    (idCalendrierValue,'PERSO', :new.uniqueID, 'Agenda Personnel');
    
    
    
    insert into utilisateurcalendrier(idCalendrier,idUtilisateur,idUtilisateurCalendrier,dateajoutinvite)
    values (idCalendrierValue,:new.uniqueID,ug_idutilisateurcalendrier_seq.nextval,sysdate);
    
    
end;
/


DROP TRIGGER CREATION_CAL_PERSO_TRG;








Drop trigger Id_CAL_TRG;
CREATE OR REPLACE TRIGGER ID_CAL_TRG
before insert
on calendrier
for each row
Declare
    nom varchar2(50);
BEGIN
    Select LOGIN
    INTO NOM
    FROM UTILISATEUR
    WHERE UNIQUEID = :new.idadministrateur;
   
    IF :NEW.IDCALENDRIER IS NULL THEN
    
    SELECT :new.NOMCalendrier|| '-' || SUBSTR(NOM, 1, 6) ||  '-' || TO_CHAR(sysdate, 'MMDDYYYY') || '_' || ID_CALENDRIER_SEQ.NEXTVAL
    INTO :new.idcalendrier
    FROM dual;
    
    END IF; 
   
END;



