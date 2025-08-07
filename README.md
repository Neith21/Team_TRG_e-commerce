# Team_TRG_e-commerce
Repositorio destinado a los avances del proyecto. Ciclo-02-2025, Transacciones Comerciales por Medios Electrónicos

---

# PASOS PARA EJECUTAR EL BACKEND DE MANERA LOCAL:

**Necesario tener:**

- Python versión >= 3...
- Pip
- Postman (opcional pero recomendado para evaluar las rutas)
- Workbench

---

## PASO 1:

- Descargar el proyecto:
  - En .rar o zip.
  - O Clonación: `https://github.com/Neith21/Team_TRG_e-commerce.git`

---

## PASO 2:

- Posicionarse en el repositorio y crear un entorno virtual:
  1. Abrir terminal y `cd` hasta el repositorio.
  2. Ejecutar el comando: `python -m venv env` (se creará una carpeta env en el mismo nivel de la carpeta backend)
  3. Para activar el entorno virtual el comando es: `env\Scripts\activate` (debemos estar en el mismo nivel de la carpeta env)

---

## PASO 3:

- Ejecutar librerías comandos:
  1. `cd backend`
  2. `pip install -r requirements.txt`

---

## PASO 4:

Configuraciones generales del proyecto:

- Crear una base de datos en MySQL (archivo `team_trg_ecommerce.sql`):
  - `CREATE DATABASE team_trg_ecommerce;`
  - `USE team_trg_ecommerce;` (¡¡¡ IMPORTANTE QUEDARSE HASTA AQUÍ !!!, no hacer los insert porque aún no se han hecho las migraciones)
- Crear un archivo `.env` dentro de backend al mismo nivel de `.env.example` y ponerle las credenciales (seguir el ejemplo de `.env.example`)

---

## PASO 5:

- Hacer migraciones comandos (estar en el mismo nivel de backend):
  1. `python manage.py migrate`
  2. `python manage.py makemigrations`
  3. `python manage.py migrate`
- Crear un super usuario:
  1. `python manage.py createsuperuser`
  2. Ponerle nombre de usuario, correo y contraseñas genéricos (`admin`, `me@admin.com`, `123`)
  3. Dirá que la contraseña es débil pero dejenlo pasar (Y)

---

## PASO 6:

- Ejecutar la información de la base de datos:
  - archivo `team_trg_ecommerce.sql` y ejecutar todo lo que está después de `USE team_trg_ecommerce;`

---

## PASO 7:

- Correr el servidor comando (estar en el mismo nivel de backend):
  - `python manage.py runserver 192.168.1.6:8000` (antes es necesario conocer nuestra ip)

---

A partir de aquí tenemos la libertad de hacer lo que sea.
Para volver a usar el backend es necesario activar el entorno virtual y correr el servidor.

---
