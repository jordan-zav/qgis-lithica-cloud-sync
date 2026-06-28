# Lithica Drive Sync para QGIS

Plugin experimental de solo lectura que descarga proyectos de Lithica Explorer desde Google Drive y abre observations.gpkg en QGIS.


## Requisitos

- QGIS 3.34 o posterior.
- Una cuenta de Google autorizada como usuario de prueba.
- Google Drive API habilitada en el mismo proyecto de Google Cloud usado por Lithica Explorer.
- Cliente OAuth tipo Aplicación de escritorio.

## Configuración OAuth privada

1. Abre Google Cloud Console y selecciona el proyecto de desarrollo de Lithica.
2. Confirma que Google Drive API esté habilitada.
3. Mantén la aplicación OAuth en modo Testing.
4. Añade tu cuenta de Google como usuario de prueba.
5. Crea un cliente OAuth de tipo Aplicación de escritorio.
6. Descarga el JSON.
7. Renómbralo como oauth_client.json.
8. Colócalo dentro de la carpeta lithica_drive_sync instalada en QGIS.

El plugin solicita únicamente el permiso drive.file. No solicita acceso completo al Drive.

## Instalación

1. Ejecuta qgis_plugin/package_plugin.ps1.
2. En QGIS abre Complementos, Administrar e instalar complementos.
3. Elige Instalar a partir de ZIP.
4. Selecciona artifacts/lithica_drive_sync-0.1.0.zip.
5. Después de instalar, añade oauth_client.json a la carpeta instalada del plugin.
6. Abre Lithica Drive Sync desde el menú Vector.

## Seguridad

- El ZIP público no incluye oauth_client.json.
- El flujo usa OAuth de escritorio con PKCE y navegador del sistema.
- El refresh token se guarda en el administrador de autenticación de QGIS solamente cuando existe una contraseña maestra.
- Sin almacén seguro, la autorización se conserva únicamente en memoria y debe repetirse al reiniciar.
- Nunca se escriben tokens en logs.
- Las descargas se validan antes de reemplazar la copia local.
- La primera versión no modifica ni elimina archivos de Google Drive.

## Limitaciones de desarrollo

En modo Testing, Google limita los usuarios autorizados y puede hacer vencer el refresh token después de siete días. Esto no genera cobros; obliga a reconectar la cuenta.

## Publicación futura

La versión pública necesitará un proyecto de producción separado, dominio verificado, página principal, política de privacidad y revisión OAuth. Lithica y el plugin deberán usar clientes del mismo proyecto de producción para mantener el acceso limitado mediante drive.file.
