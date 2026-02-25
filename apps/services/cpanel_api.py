import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


class CpanelAPIError(Exception):
    """Error de integración con cPanel API."""


class CpanelAPI:
    """Cliente mínimo para cPanel UAPI (Email)."""

    def __init__(
        self,
        host,
        username,
        api_token,
        use_https=True,
        port=2083,
        timeout=20,
    ):
        self.host = host
        self.username = username
        self.api_token = api_token
        self.use_https = use_https
        self.port = port
        self.timeout = timeout

    @property
    def base_url(self):
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.host}:{self.port}/execute"

    def _request(self, module, function, **params):
        query = urlencode(params)
        url = f"{self.base_url}/{module}/{function}"
        if query:
            url = f"{url}?{query}"

        req = Request(url=url, method="GET")
        req.add_header(
            "Authorization",
            f"cpanel {self.username}:{self.api_token}",
        )
        req.add_header("Accept", "application/json")

        try:
            with urlopen(req, timeout=self.timeout) as response:
                payload = response.read().decode("utf-8")
                data = json.loads(payload)
        except HTTPError as exc:
            raise CpanelAPIError(
                f"HTTP {exc.code} al conectar con cPanel: {exc.reason}"
            ) from exc
        except URLError as exc:
            raise CpanelAPIError(
                f"No se pudo conectar con cPanel: {exc.reason}"
            ) from exc
        except Exception as exc:
            raise CpanelAPIError(
                f"Error inesperado en cPanel API: {str(exc)}"
            ) from exc

        status = data.get("status")
        errors = data.get("errors") or []
        if status != 1:
            msg = errors[0] if errors else "Operación no exitosa en cPanel."
            raise CpanelAPIError(msg)
        return data

    @staticmethod
    def split_email(email):
        if "@" not in email:
            raise CpanelAPIError(
                "El correo no es válido. Debe tener formato usuario@dominio."
            )
        local_part, domain = email.split("@", 1)
        return local_part.strip(), domain.strip().lower()

    def create_mailbox(self, email, password, quota_mb=2048):
        local_part, domain = self.split_email(email)
        return self._request(
            "Email",
            "add_pop",
            email=local_part,
            domain=domain,
            password=password,
            quota=int(quota_mb),
        )

    def delete_mailbox(self, email):
        local_part, domain = self.split_email(email)
        return self._request(
            "Email",
            "delete_pop",
            email=local_part,
            domain=domain,
        )

    def update_mailbox_password(self, email, new_password):
        local_part, domain = self.split_email(email)
        return self._request(
            "Email",
            "passwd_pop",
            email=local_part,
            domain=domain,
            password=new_password,
        )

    def suspend_mailbox(self, email):
        local_part, domain = self.split_email(email)
        return self._request(
            "Email",
            "suspend_login",
            email=local_part,
            domain=domain,
        )

    def unsuspend_mailbox(self, email):
        local_part, domain = self.split_email(email)
        return self._request(
            "Email",
            "unsuspend_login",
            email=local_part,
            domain=domain,
        )
