# Despliegue Megadominio

## Nginx: bloquear Host inválidos (0.0.0.0, bots)

El archivo `nginx-megadominio.example.conf` incluye:

1. **Servidor principal** para `megadominio.co` y `www.megadominio.co` con `proxy_set_header Host $host` para que Gunicorn reciba el host correcto.
2. **Bloque `default_server`** que responde `444` (conexión cerrada sin respuesta) a cualquier petición con otro `Host` (por ejemplo `0.0.0.0`, IPs, o dominios que no son los tuyos). Así los probes de bots no llegan a Django.

### Cómo aplicarlo

- Si ya tienes un `server` para Megadominio, añade solo el segundo bloque `server` (el de `default_server`) en tu config y recarga Nginx.
- Si partes de cero, copia el ejemplo, ajusta rutas SSL y paths, y habilita el sitio:

```bash
sudo cp nginx-megadominio.example.conf /etc/nginx/sites-available/megadominio
sudo ln -s /etc/nginx/sites-available/megadominio /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

**Importante:** Solo puede haber un `default_server` por puerto. Si otro sitio ya usa `default_server` en 443, quita esa directiva del otro o ajusta según tu configuración.
