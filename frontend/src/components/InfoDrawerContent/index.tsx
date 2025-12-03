import styles from './style.module.css';


export default function InfoDrawerContent() {

  return (
    <div
      className={styles.container}
    >
      <p>Application de visualisation d'indicateurs climatiques relatifs aux impacts du changement climatique sur la demande et ressource en énergie</p>

      <h2>Indicateurs climatiques</h2>
      <ul>
      <li><strong>DJU - Degrée Jours Unifiés :</strong>Indicateur de consommation de chauffage. Somme de l'écart entre la température moyenne journalière et 18°C sur la saison de chauffage entre octobre et avril</li>
      <li><strong>Rayonnement solaire :</strong>Indicateur de production solaire. Moyenne du rayonnement solaire mensuel</li>
      <li><strong>Vitesse du vent :</strong>Indicateur de production éolien. Moyenne de la vitesse </li>
      </ul>
    </div>
  )
}