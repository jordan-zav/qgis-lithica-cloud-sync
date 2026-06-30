# Lithica Drive Sync para QGIS

Lithica Cloud Sync es un plugin para QGIS que te permite conectar tu cuenta de Google Drive para descargar y sincronizar automáticamente tus proyectos creados en **Lithica Explorer**.

Con un par de clics, podrás importar los datos espaciales (`observations.gpkg`) de tus proyectos directamente a QGIS para su análisis y visualización avanzada.

## Requisitos

- QGIS 3.34 o posterior.
- Una cuenta de Google con acceso a Google Drive.
- Proyectos de Lithica Explorer previamente sincronizados en la nube.

## Instalación

1. Descarga la última versión en formato `.zip` desde la sección de **Releases** de este repositorio.
2. Abre QGIS y dirígete al menú **Complementos** > **Administrar e instalar complementos**.
3. Selecciona la pestaña **Instalar a partir de ZIP**.
4. Busca el archivo descargado (`Lithica Cloud Sync-1.0.0.zip`) y haz clic en instalar.
5. El panel de Lithica Cloud Sync aparecerá disponible para conectarte a tu cuenta.

## Uso

1. Haz clic en **Conectar** para enlazar tu cuenta de Google Drive.
2. Se abrirá una pestaña en tu navegador para que inicies sesión de forma segura y des permiso (sólo acceso a archivos de la aplicación).
3. Una vez conectado, haz clic en **Actualizar lista** para ver tus proyectos disponibles.
4. Selecciona un proyecto y presiona **Descargar y abrir**. El plugin descargará los datos y los añadirá automáticamente como capas en tu proyecto de QGIS.

## Soporte

Desarrollado por [GisGeo Dev](https://gisgeo.dev).
Para cualquier consulta o reporte de errores, por favor abre un *Issue* en este repositorio.
