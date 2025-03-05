import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Технологии</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Технологии, которые применены в этом проекте:</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python"></img>
              </li>
              <li className={styles.textItem}>
                <img src="https://img.shields.io/badge/django-%230c4b34?style=for-the-badge&logo=django&logoColor=white" alt="Django"></img>
              </li>
              <li className={styles.textItem}>
                <img src="https://img.shields.io/badge/framework-%23a30000?style=for-the-badge&logo=django&logoColor=white&label=rest&labelColor=%232c2c2c" alt="Django REST Framework"></img>
              </li>
              <li className={styles.textItem}>
                <img src="https://img.shields.io/badge/Djoser-092E20?style=for-the-badge&amp;logo=django&amp;logoColor=whiteDjoser" alt="Djoser"></img>
              </li>
              <li className={styles.textItem}>
                <img src="https://img.shields.io/badge/PostgreSQL-336690?style=for-the-badge&logo=postgresql&logoColor=white&logoSize=auto" alt="Postgres"></img>
              </li>
              <li className={styles.textItem}>
                <img src="https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white" alt="Nginx"></img>
              </li>
              <li className={styles.textItem}>
                <img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"></img>
              </li>
              <li className={styles.textItem}>
                <img src="https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white" alt="GitHub Actions"></img>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
    </Container>
  </Main>
}

export default Technologies

