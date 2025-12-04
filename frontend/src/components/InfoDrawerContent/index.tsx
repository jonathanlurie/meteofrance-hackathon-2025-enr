import styles from './style.module.css';


export default function InfoDrawerContent() {

  return (
    <div
      className={styles.container}
    >

      <p>
        Planification énergétique saisonnière et à l'échelle d'un territoire et visualisation d'indicateurs climatiques relatifs à la TRACC sur la demande et ressource en énergie
      </p>

      

      <h2>Indicateurs climatiques</h2>
      <ul>
        <li><strong>DJU - Degrée Jours Unifiés :</strong> Indicateur de consommation de chauffage. Somme de l'écart entre la température moyenne journalière et 18°C sur la saison de chauffage entre octobre et avril</li>

        <li><strong>Température moyenne :</strong> Moyenne mensuelle de la température</li>

        <li><strong>Nombre de jour(s) inf. à 0°C :</strong> Nombre de jour(s) par mois avec des températures minimales inférieures à 0°C</li>

        <li><strong>Nombre de jour(s) sup. à 30°C :</strong> Nombre de jour(s) par mois avec des températures maximales supérieures à 30°C</li>
        
        <li><strong>Rayonnement solaire :</strong> Indicateur de production solaire. Moyenne mensuelle du rayonnement solaire mensuel</li>
        
        <li><strong>Vitesse du vent :</strong> Indicateur de production éolien. Moyenne mensuelle de la vitesse des vents</li>
      </ul>

      <h2>Modèles</h2>
      <p>
        Les données utilisées par cette application proviennent du modèle CNRM-ALADIN forcé par CMCC-CM. Nous prévoyons aussi d'intégrer les données du modèle HCLIM43-ALADIN forcé par IPSL-CM.
      </p>


      <h2>L'équipe</h2>
      <ul>
        <li>Mareva July-Wormit</li>

        <li>Marie Jamet</li>
        
        <li>Florent Cornet</li>
        
        <li>Jonathan Lurie</li>
      </ul>
      <p>
        Ce projet a été réalisé dans le cadre du hackathon organisé par Météo France, avec pour thème <a href="https://guides.data.gouv.fr/guide-du-participant-au-hackathon-le-climat-en-donnees">le climat en données</a>
      </p>

      <p>
        Retrouvez le code source complet du projet <a href='https://github.com/Florent-Co/mf-hackathon-enr'>sur GitHub</a>.
      </p>

      <img src="/hackathon.avif"></img>

    </div>
  )
}