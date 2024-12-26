import httpx


class APIWrapper:
    def __init__(self, base_url: str, api_token: str | None = None):
        self.base_url = base_url
        self.api_token = api_token
        self.session = None  # Will be initialized later

    # Synchronous request
    def get_sync(self, endpoint: str):
        with httpx.Client() as client:
            headers = (
                {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
            )
            url = f"{self.base_url}/{endpoint}"
            response = client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    # Asynchronous request
    async def get_async(self, endpoint: str):
        if not self.session:
            await self._init_session()
        headers = (
            {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        )
        url = f"{self.base_url}/{endpoint}"
        response = await self.session.get(url, headers=headers)
        response.raise_for_status()
        return await response.json()

    async def _init_session(self):
        """Initialize session asynchronously for async requests."""
        self.session = httpx.AsyncClient()

    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.aclose()
