# tpsqa
tp sqa de Ingenieria y calidad de sofware

## Cómo ejecutar desde cero

### Requisitos previos

#### Python
- [Python 3.9+](https://www.python.org/downloads/)

Verificar la versión instalada:
```bash
python3 --version
```

#### Componentes adicionales
- [pip](https://pip.pypa.io/en/installation/) (gestor de paquetes de Python)
- [Docker](https://docs.docker.com/get-docker/) (para levantar SonarQube server)
- [SonarQube Scanner](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/) (para análisis estático remoto, en local)

### Instalación y configuración

#### 1. Instalar dependencias del proyecto
```bash
pip install -r requirements.txt
```

Se instalarán automáticamente:
- [pytest](https://docs.pytest.org/) - framework de testing
- [pytest-cov](https://pytest-cov.readthedocs.io/) - cobertura de código
- [pylint](https://www.pylintrc.com/) - análisis estático de código
- [bandit](https://bandit.readthedocs.io/) - análisis de seguridad

#### 2. Ejecutar pruebas locales
```bash
pytest test/
```

#### 3. Configurar y ejecutar SonarQube

**Iniciar el servidor SonarQube (primera vez):**
```bash
docker run --name sonarqube-custom -p 9000:9000 sonarqube:community
```

> Nota: El servidor estará disponible en `http://localhost:9000` (usuario por defecto: admin/admin)

**Iniciar el servidor en ejecuciones posteriores:**
```bash
docker start sonarqube-custom
```

#### 4. Generar token en SonarQube
1. Ingresar a http://localhost:9000
2. Ir a **Administración → Seguridad → Tokens**
3. Generar un nuevo token y copiar su valor

#### 5. Configurar variables de ambiente
```bash
export SONAR_HOST_URL=http://localhost:9000
export SONAR_LOGIN=<token_generado>
```

#### 6. Ejecutar análisis completo
```bash
bash run-analysis.sh
```

Este script ejecutará automáticamente:
- Análisis de código estático con pylint
- Cobertura de pruebas con pytest-cov
- Análisis de seguridad con bandit
- Análisis remoto con SonarQube (si sonar-scanner está disponible)

### Documentación oficial
- [Documentación de Python](https://docs.python.org/3/)
- [Documentación de pytest](https://docs.pytest.org/en/stable/contents.html)
- [Documentación de pylint](https://pylint.pycqa.org/)
- [Documentación de SonarQube](https://docs.sonarqube.org/)
- [Documentación de Docker](https://docs.docker.com/)
- [Documentación de SonarQube Scanner](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/)
- [Documentación de bandit](https://bandit.readthedocs.io/)
