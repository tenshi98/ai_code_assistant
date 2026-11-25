"""Paquete interno del servicio AI Code Generator & Debugger.

Agrupa la configuración, la capa HTTP (rutas), los esquemas de respuesta y
los clientes de servicios externos. Mantener este paquete separado de
``app.py`` permite importar y probar la aplicación sin arrancar Uvicorn.
"""
