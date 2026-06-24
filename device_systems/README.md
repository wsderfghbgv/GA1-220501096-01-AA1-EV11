# device_systems API

## Descripción

**device_systems** es una API REST segura construida con **FastAPI** para la gestión de usuarios, dispositivos tecnológicos y préstamos. Esta versión (v3.0.0) incorpora mecanismos de seguridad profesional incluyendo autenticación OAuth2 con JWT, autorización basada en roles, middleware personalizado, CORS, rate limiting y validaciones avanzadas con Pydantic v2.

## Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|---|---|---|
| FastAPI | Latest | Framework web principal |
| SQLAlchemy | Latest | ORM para base de datos |
| Alembic | Latest | Migraciones de base de datos |
| Pydantic v2 | Latest | Validación de datos |
| Passlib (bcrypt) | Latest | Hash seguro de contraseñas |
| Python-Jose | Latest | Generación/validación de JWT |
| SlowAPI | Latest | Rate limiting |
| Uvicorn | Latest | Servidor ASGI |
| SQLite | 3.x | Base de datos (desarrollo) |

## Estructura del Proyecto

```
device_systems/
│── app/
│   │── main.py
│   │
│   │── auth/
│   │   │── auth_routes.py
│   │   │── auth_service.py
│   │   │── security.py
│   │
│   │── database/
│   │   │── connection.py
│   │
│   │── models/
│   │   │── user_model.py
│   │   │── device_model.py
│   │   │── loan_model.py
│   │
│   │── schemas/
│   │   │── user_schema.py
│   │   │── device_schema.py
│   │   │── loan_schema.py
│   │   │── auth_schema.py
│   │
│   │── routes/
│   │   │── user_routes.py
│   │   │── device_routes.py
│   │   │── loan_routes.py
│   │
│   │── services/
│   │   │── user_service.py
│   │   │── device_service.py
│   │   │── loan_service.py
│   │
│   │── dependencies/
│   │   │── database_dependency.py
│   │   │── auth_dependency.py
│   │
│   │── middlewares/
│   │   │── request_middleware.py
│
│── alembic/
│   │── versions/
│
│── .env
│── .env.example
│── alembic.ini
│── requirements.txt
│── README.md
```

## Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd device_systems
```

### 2. Crear entorno virtual

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo de ejemplo y ajustar los valores:

```bash
cp .env.example .env
```

Variables disponibles:

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `DATABASE_URL` | URL de conexión a la base de datos | `sqlite:///./device_systems.db` |
| `SECRET_KEY` | Clave secreta para firmar tokens JWT | (cambiar en producción) |
| `ALGORITHM` | Algoritmo de encriptación JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tiempo de expiración del token en minutos | `30` |

### 5. Ejecutar migraciones con Alembic

```bash
alembic upgrade head
```

### 6. Iniciar el servidor

```bash
uvicorn app.main:app --reload
```

La API estará disponible en: `http://localhost:8000`

Documentación Swagger: `http://localhost:8000/docs`

Documentación ReDoc: `http://localhost:8000/redoc`

## Endpoints de la API

### Auth (`/auth`)

| Método | Ruta | Descripción | Protección | Rate Limit |
|---|---|---|---|---|
| POST | `/auth/register` | Registrar nuevo usuario | Público | 3/min |
| POST | `/auth/login` | Autenticar y obtener token JWT | Público | 5/min |
| GET | `/auth/me` | Obtener perfil del usuario autenticado | Token JWT | - |

### Users (`/users`)

| Método | Ruta | Descripción | Protección | Rate Limit |
|---|---|---|---|---|
| GET | `/users/` | Listar todos los usuarios | Token JWT | 30/min |
| GET | `/users/{user_id}` | Obtener usuario por ID | Token JWT | - |

### Devices (`/devices`)

| Método | Ruta | Descripción | Protección |
|---|---|---|---|
| GET | `/devices/` | Listar todos los dispositivos | Token JWT |
| GET | `/devices/{device_id}` | Obtener dispositivo por ID | Token JWT |
| POST | `/devices/` | Crear nuevo dispositivo | Admin o Support |
| PUT | `/devices/{device_id}` | Actualizar dispositivo | Admin o Support |
| DELETE | `/devices/{device_id}` | Eliminar dispositivo | Solo Admin |

### Loans (`/loans`)

| Método | Ruta | Descripción | Protección | Rate Limit |
|---|---|---|---|---|
| GET | `/loans/` | Listar todos los préstamos | Token JWT | - |
| GET | `/loans/details` | Detalles de préstamos (con joins) | Admin o Support | - |
| POST | `/loans/` | Crear nuevo préstamo | Token JWT | 10/min |
| PATCH | `/loans/{loan_id}/return` | Devolver dispositivo | Admin o Support | - |

## Autenticación y Autorización

### Flujo de Autenticación OAuth2

1. **Registro**: El usuario se registra con nombre, email, contraseña segura y rol.
2. **Login**: El usuario se autentica con email y contraseña, recibiendo un token JWT.
3. **Acceso**: El token se envía en el header `Authorization: Bearer <token>` para acceder a rutas protegidas.

### Roles del Sistema

| Rol | Permisos |
|---|---|
| `admin` | Acceso completo: CRUD de dispositivos, gestión de préstamos, eliminación |
| `support` | Crear/actualizar dispositivos, gestionar devoluciones, ver detalles de préstamos |
| `user` | Consultar usuarios, dispositivos y préstamos. Crear préstamos |

### Validación de Contraseña

Las contraseñas deben cumplir:
- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula
- Al menos un dígito numérico
- No se permiten espacios en blanco

### Hash de Contraseñas

Las contraseñas se almacenan usando **bcrypt** a través de `passlib`. Nunca se guarda ni se retorna la contraseña en texto plano. El campo `hashed_password` está excluido de todos los schemas de respuesta.

## Middleware Personalizado

El middleware personalizado agrega las siguientes cabeceras a cada respuesta:

| Cabecera | Descripción | Ejemplo |
|---|---|---|
| `X-Process-Time` | Tiempo de procesamiento en segundos | `0.0042` |
| `X-App-Name` | Nombre de la aplicación | `device_systems` |
| `X-Request-ID` | Identificador único de la petición | `8f42e9c1` |

Además registra en logs: método HTTP, ruta, código de estado y tiempo de respuesta.

## Configuración CORS

### Configuración actual (desarrollo)

```python
allow_origins=["http://localhost:5173", "http://localhost:3000"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

### ¿Por qué no usar `"*"` en producción con credenciales?

**No se recomienda usar `allow_origins=["*"]` en producción cuando `allow_credentials=True`** por las siguientes razones:

1. **Vulnerabilidad CSRF**: Al permitir cualquier origen con credenciales, cualquier sitio web malicioso podría realizar peticiones autenticadas a nuestra API en nombre del usuario, robando datos o ejecutando acciones no autorizadas.

2. **Especificación CORS**: El estándar HTTP prohíbe explícitamente combinar `Access-Control-Allow-Origin: *` con `Access-Control-Allow-Credentials: true`. Los navegadores modernos bloquearán estas respuestas.

3. **Principio de mínimo privilegio**: En producción, se deben listar únicamente los dominios de confianza que necesitan acceder a la API (ej: el dominio del frontend desplegado).

4. **Trazabilidad**: Restringir orígenes permite identificar y auditar qué clientes acceden a la API.

**Configuración recomendada para producción:**
```python
allow_origins=["https://mi-frontend.com"]
```

## Rate Limiting

Se utiliza **SlowAPI** para limitar el número de peticiones por cliente (por IP):

| Endpoint | Límite |
|---|---|
| `POST /auth/login` | 5 solicitudes por minuto |
| `POST /auth/register` | 3 solicitudes por minuto |
| `GET /users/` | 30 solicitudes por minuto |
| `POST /loans/` | 10 solicitudes por minuto |

Al superar el límite, la API responde con:
```
HTTP 429 Too Many Requests
```

## Validaciones con Pydantic v2

La API utiliza características avanzadas de Pydantic v2:

- **`ConfigDict(from_attributes=True)`**: Permite serializar modelos ORM de SQLAlchemy directamente.
- **`Field()`**: Define metadata, restricciones (min_length, max_length, gt), descripciones y ejemplos.
- **`field_validator`**: Validaciones personalizadas como fortaleza de contraseña y estados válidos.
- **`model_validator`**: Validaciones entre campos (nombre ≠ email, IDs positivos).
- **Schemas de respuesta**: Nunca exponen `hashed_password`.

## Pruebas Funcionales

### Lista de pruebas requeridas

| # | Prueba | Resultado esperado |
|---|---|---|
| 1 | Registro de usuario | 201 Created |
| 2 | Registro con contraseña débil | 422 Validation Error |
| 3 | Registro con email duplicado | 400 Bad Request |
| 4 | Login correcto | 200 + Token JWT |
| 5 | Login con contraseña incorrecta | 401 Unauthorized |
| 6 | Consulta /auth/me | 200 + datos del usuario |
| 7 | Acceso a ruta protegida sin token | 401 Unauthorized |
| 8 | Acceso con token inválido | 401 Unauthorized |
| 9 | Acceso con rol no permitido | 403 Forbidden |
| 10 | Crear dispositivo con rol permitido | 201 Created |
| 11 | Eliminar dispositivo con rol no admin | 403 Forbidden |
| 12 | CORS headers presentes | Headers de CORS en respuesta |
| 13 | Cabeceras de middleware | X-Process-Time, X-App-Name, X-Request-ID |
| 14 | Rate limiting activado | 429 Too Many Requests |
| 15 | Swagger/OpenAPI funcional | Documentación con OAuth2 |

## Reflexión sobre Seguridad en APIs REST

La seguridad en APIs REST es fundamental porque las APIs son puntos de acceso directos a los datos y la lógica de negocio de una aplicación. Sin mecanismos adecuados de protección:

- Las contraseñas podrían quedar expuestas en texto plano
- Cualquier usuario podría acceder a datos sensibles
- Un atacante podría realizar miles de peticiones por segundo (DDoS)
- Sitios web maliciosos podrían hacer peticiones en nombre de usuarios legítimos

Las capas de seguridad implementadas en este proyecto (hash de contraseñas, JWT, roles, CORS, rate limiting, middleware de trazabilidad) trabajan en conjunto para crear una API robusta y preparada para producción.

## Autor

Desarrollado como parte de la actividad GA1-220501096-01-AA1-EV11 del programa de formación ADSO - SENA.
