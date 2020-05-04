Configuration de la base de données, structure
============

Ce document explique comment marche la bd, comment l'initialiser dans un serveur et comment l'utiliser (explications TRG, reinitialiser des données, etc)

# Initialiser la BD

Pour initialiser la bd, il suffit d'executer le script "initialisation_projet.sql" qui va :
  1. supprimer toutes les tables de l'utilisateur (attention à avoir que les tables du projet sur la bd et pas d'autres, sinon il faut modifier le script de suppression de données et tables)
  2. Creer les tables, les contraintes (fk,pk), les sequences, et les triggers


# INFORMATIONS RELATIVES À LA BD

### Liste des triggers ###

***

CREATION_CAL_PERSO_TRG [`AFTER INSERT ON UTILISATEUR`]
  : Déclencheur appelé lors de la création d'un utilisateur. ajoute un calendrier personnel lié à l'utilisateur

PARTICIPANTS_EVT_TRG [`before INSERT or DELETE ON Transaction`]
  : Déclencheur appelé après la création d'une transaction, par défaut elle ajoute tous les utilisateurs d'un calendrier dans la transaction

SUIVI_UTILISATEUR_CAL_TRG [`before INSERT OR DELETE ON UTILISATEURCALENDRIER`]
  : Déclencheur appelé après la création d'une transaction, par défaut elle ajoute tous les utilisateurs d'un calendrier dans la transaction

***

### *Liste des id spéciaux* ###
1. **idUtilisateur** :
 `Login-JJMMYYYYHHMIN-MILLISEC`
2. **idCalendrier** :
 `nomCal-3premièreslettresdulogin-MMDDYYYY_id_calendrier_seq`
3. **idEvenement** :
`nomEvt-DateDebutEVT_id_evenement_seq`

4. **idTransaction** :
`idUtilisateur-Montant-idCalendrierEVT_id_transaction_seq`

***

### Liste des séquences du projet ###

~~~
Sequences pour les tables avec un id qui autoincrement:
CALENDRIEREVENEMENT_IDCALENDRIEREVENEMENT
HISTORIQUESUIVIEVENEMENT_IDHISTORIQUE
MESSAGE_IDMESSAGE
PTE_IDTRANSACTIONPARTICIPANTEVENEMENT
SUIVICALENDRIEREVENEMENT_IDSUIVI
SUIVIMESSAGELU_IDSUIVIMESSAGE
SUIVITRANSACTION_IDSUIVI
SUIVIUTILISATEURCALENDRIER_IDSUIVI
UG_IDUTILISATEURCALENDRIER_SEQ

Sequences pour créer des id avec des varchar2:
ID_CALENDRIER_SEQ
ID_TRANSACTION_SEQ
ID_EVENEMENT_SEQ
~~~

> Certains id sont créés pour faire des identifiants spécifiques (ex : uniqueID pour l'utilisateur).


~~~SQL
 CREATE SEQUENCE id_transaction_seq
 START WITH     1
 INCREMENT BY   1
 NOCACHE
 NOCYCLE;
~~~

LIENS GIT DES PROJETS
---

Lien du projet serveur [ici](https://github.com/victordu45/projetCalendrierInterface.git)
Lien du projet interface [ici](https://github.com/victordu45/projetCalendrierServeur.git)

# Livrables

1er livrable
  : SGBD, quelques fonctionnalités