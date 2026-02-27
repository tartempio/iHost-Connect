[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

*Lire dans d'autres langues : [English](README.md), [Français](README.fr.md).*

[releases-shield]: https://img.shields.io/github/release/tartempio/iHost-Connect.svg?style=for-the-badge
[releases]: https://github.com/tartempio/iHost-Connect/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/tartempio/iHost-Connect.svg?style=for-the-badge
[commits]: https://github.com/tartempio/iHost-Connect/commits/main
[license-shield]: https://img.shields.io/github/license/tartempio/iHost-Connect.svg?style=for-the-badge
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[hacs]: https://github.com/custom-components/hacs

# iHost Connect

Une intégration personnalisée **Home Assistant** pour la passerelle domotique **SONOFF iHost** (eWeLink CUBE).

Surveillez votre passerelle iHost directement depuis Home Assistant : température du processeur (CPU), utilisation de la RAM, utilisation de la carte SD, nombre d'appareils connectés, mode de sécurité, etc. L'intégration communique **localement** avec votre iHost — aucun cloud n'est requis.

_N'hésitez pas à ⭐ ce dépôt s'il vous est utile !_

---

## Fonctionnalités

- **Interrogation locale** — toute la communication se fait directement sur votre réseau local
- **Découverte automatique** — le iHost est automatiquement détecté via Zeroconf (mDNS)
- **Capteurs** — surveillance approfondie du fonctionnement de votre passerelle
- **Capteur binaire** — détection automatique des mises à jour du firmware (vérifie les [releases GitHub de CUBE-OS](https://github.com/eWeLinkCUBE/CUBE-OS/releases))
- **Bouton** — redémarrez votre passerelle iHost depuis Home Assistant

### Ce que cette intégration ne fait PAS

> **Remarque :** Cette intégration est conçue exclusivement pour **surveiller l'état de la passerelle iHost elle-même**. Elle **N'EXPOSE PAS** les différents appareils domotiques connectés à votre iHost (comme les capteurs Zigbee, les interrupteurs, etc.), et ne permet pas de les contrôler. Pour intégrer et contrôler vos appareils iHost individuels dans Home Assistant, nous vous invitons à utiliser la fonctionnalité **Matter Bridge** intégrée au iHost.

### Entités fournies

#### Capteurs

| Entité | Type | Description |
|---|---|---|
| Nombre d'appareils | Sensor | Nombre d'appareils connectés au iHost |
| Mode de sécurité | Sensor | Mode de sécurité actif (ex. À la maison, À l'extérieur, Désarmé) |

#### Diagnostic

| Entité | Type | Description |
|---|---|---|
| Dernier démarrage | Sensor | Horodatage du dernier démarrage de la passerelle |
| Température CPU | Sensor | Température du processeur (°C) |
| Utilisation CPU | Sensor | Utilisation du processeur (%) |
| Utilisation RAM | Sensor | Utilisation de la RAM (%) |
| Utilisation Carte SD | Sensor | Utilisation de la carte SD (%) |
| Adresse IP | Sensor | Adresse IP actuelle du iHost |
| Mise à jour du firmware | Binary Sensor | `On` lorsqu'un nouveau firmware CUBE-OS est disponible |

#### Configuration

| Entité | Type | Description |
|---|---|---|
| Redémarrer | Button | Envoyer une commande de redémarrage au iHost |

---

## Prérequis

- Une passerelle [SONOFF iHost](https://itead.cc/product/sonoff-ihost-smart-home-hub/) fonctionnant sous **CUBE-OS**
- Le iHost doit être **sur le même réseau local** que votre instance Home Assistant
- [HACS](https://hacs.xyz/) doit être installé dans Home Assistant

---

## Installation

### Via HACS (recommandé)

[![Ouvrez votre instance Home Assistant et ouvrez un dépôt dans le Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tartempio&repository=iHost-Connect&category=Integration)

Ou manuellement :

1. Ouvrez **HACS** dans Home Assistant
2. Allez dans **Intégrations**
3. Cliquez sur le menu **⋮** (en haut à droite) → **Dépôts personnalisés**
4. Ajoutez `https://github.com/tartempio/iHost-Connect` avec la catégorie **Integration**
5. Recherchez **iHost** et cliquez sur **Télécharger**
6. **Redémarrez Home Assistant**

### Installation manuelle

<details>
<summary>Développer pour plus de détails</summary>

1. Téléchargez la dernière version depuis la [page des Releases](https://github.com/tartempio/iHost-Connect/releases)
2. Copiez le dossier `custom_components/ihost` dans le répertoire `config/custom_components/` de votre Home Assistant
3. **Redémarrez Home Assistant**

</details>

---

## Configuration

### Découverte automatique (recommandé)

Si votre iHost est sur le même réseau que Home Assistant, il sera **découvert automatiquement** via Zeroconf (mDNS). Une notification apparaîtra dans l'interface de Home Assistant vous demandant de confirmer la configuration.

1. Allez dans **Paramètres → Appareils et services** (Intégrations)
2. Une entrée **iHost** découverte apparaîtra — cliquez sur **Configurer**
3. Suivez les étapes ci-dessous pour autoriser la connexion

### Configuration manuelle

1. Allez dans **Paramètres → Appareils et services** (Intégrations)
2. Cliquez sur **+ Ajouter une intégration** et recherchez **iHost**
3. Saisissez l'**adresse IP** de votre passerelle iHost

### Autoriser la connexion

Après avoir saisi l'adresse IP (ou confirmé la découverte automatique), l'intégration vous demandera d'**approuver la connexion sur l'interface web du iHost** :

1. Ouvrez l'interface web de votre iHost à l'adresse `http://<ip-du-ihost>` dans un navigateur
2. Lancez la demande de jeton (token) depuis l'intégration iHost de Home Assistant
3. **Approuvez** la demande de connexion — un bouton apparaîtra pour autoriser l'application `HomeAssistant`
4. Retournez dans Home Assistant et cliquez sur **Valider** — le jeton sera récupéré automatiquement

> **Remarque :** Vous disposez d'environ 60 secondes pour approuver la demande côté iHost avant que la connexion n'expire.

---

## Actualisation des données

Les données des capteurs sont interrogées **toutes les 60 secondes**. La disponibilité des mises à jour du firmware est vérifiée **toutes les 6 heures** par rapport aux [versions GitHub de CUBE-OS](https://github.com/eWeLinkCUBE/CUBE-OS/releases).

---

## Dépannage

| Problème | Solution |
|---|---|
| L'intégration n'est pas découverte | Assurez-vous que votre iHost est sur le même sous-réseau que Home Assistant et que le trafic mDNS est autorisé |
| Impossible de se connecter | Vérifiez que l'adresse IP est correcte et que votre iHost est accessible |
| Jeton non obtenu | Assurez-vous d'avoir approuvé la connexion dans l'interface web de l'iHost dans le délai imparti |
| Les capteurs affichent `indisponible` | Vérifiez vos journaux Home Assistant pour d'éventuelles erreurs de connexion ; redémarrez l'intégration |

---

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une *issue* ou à soumettre une *pull request*.

Cette intégration utilise l'[API ouverte eWeLink CUBE](https://ewelink.cc/ewelink-cube/introduce-open-api/document).

---

## Licence

Ce projet est sous licence [MIT License](LICENSE).

AVERTISSEMENT : Ce projet est une intégration Home Assistant indépendante, 
développée par la communauté. L'auteur n'est pas affilié, soutenu par, ou 
associé de quelque manière que ce soit à eWeLink, eWeLink Cube, iHost ou 
Sonoff (ITEAD Intelligent Systems Co., Ltd.). Tous les noms de produits, 
marques commerciales et marques déposées sont la propriété de leurs 
propriétaires respectifs.
