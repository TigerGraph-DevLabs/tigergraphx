import httpx
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseAPI(ABC):
    def __init__(self, base_url: str, api_token: Optional[str] = None):
        """
        Initialize the BaseAPI class, which will be extended by specific API classes.

        Args:
            base_url (str): The base URL for the API (e.g., http://localhost:14240).
            api_token (Optional[str], optional): The API token for authentication. Defaults to None.
        """
        self.base_url = base_url
        self.api_token = api_token
        self.session = None

    @abstractmethod
    def _get(self, url: str, **params: Any) -> Dict[str, Any]:
        """
        Abstract method for making a GET request (either sync or async).
        Needs to be implemented by subclass (synchronous and asynchronous).
        """
        pass

    @abstractmethod
    def _post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Abstract method for making a POST request (either sync or async).
        Needs to be implemented by subclass (synchronous and asynchronous).
        """
        pass

    @abstractmethod
    def _delete(self, url: str, **params: Any) -> Dict[str, Any]:
        """
        Abstract method for making DELETE request (either sync or async).
        Needs to be implemented by subclass (synchronous and asynchronous).
        """
        pass

    async def _init_session(self):
        """
        Initialize the asynchronous session for async requests.
        """
        self.session = httpx.AsyncClient()

    async def close(self):
        """
        Close the session when done with asynchronous requests.
        """
        if self.session:
            await self.session.aclose()

    def get(self, endpoint: str, **params: Any) -> Dict[str, Any]:
        """
        Synchronous GET request.

        Args:
            endpoint (str): The endpoint (e.g., /restpp/echo).
            **params: Additional parameters to be substituted in the endpoint URL.

        Returns:
            dict: The JSON response from the GET request.
        """
        url = self.base_url + endpoint
        return self._get(url, **params)

    async def get_async(self, endpoint: str, **params: Any) -> Dict[str, Any]:
        """
        Asynchronous GET request.

        Args:
            endpoint (str): The endpoint (e.g., /restpp/echo).
            **params: Additional parameters to be substituted in the endpoint URL.

        Returns:
            dict: The JSON response from the GET request.
        """
        url = self.base_url + endpoint
        return await self._get(url, **params)

    def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synchronous POST request.

        Args:
            endpoint (str): The endpoint (e.g., /restpp/graph/{graph_name}/jobs/{job_name}).
            data (Optional[Dict[str, Any]], optional): The payload to be sent in the POST request. Defaults to None.

        Returns:
            dict: The JSON response from the POST request.
        """
        url = self.base_url + endpoint
        return self._post(url, data)

    async def post_async(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Asynchronous POST request.

        Args:
            endpoint (str): The endpoint (e.g., /restpp/graph/{graph_name}/jobs/{job_name}).
            data (Optional[Dict[str, Any]], optional): The payload to be sent in the POST request. Defaults to None.

        Returns:
            dict: The JSON response from the POST request.
        """
        url = self.base_url + endpoint
        return await self._post(url, data)

    def delete(self, endpoint: str, **params: Any) -> Dict[str, Any]:
        """
        Synchronous DELETE request.

        Args:
            endpoint (str): The endpoint (e.g., /restpp/graph/{graph_name}/delete).
            **params: Additional parameters for DELETE request.

        Returns:
            dict: The JSON response from the DELETE request.
        """
        url = self.base_url + endpoint
        return self._delete(url, **params)

    async def delete_async(self, endpoint: str, **params: Any) -> Dict[str, Any]:
        """
        Asynchronous DELETE request.

        Args:
            endpoint (str): The endpoint (e.g., /restpp/graph/{graph_name}/delete).
            **params: Additional parameters for DELETE request.

        Returns:
            dict: The JSON response from the DELETE request.
        """
        url = self.base_url + endpoint
        return await self._delete(url, **params)


# Concrete implementation for synchronous operations


class SyncAPI(BaseAPI):
    def __init__(self, base_url: str, api_token: Optional[str] = None):
        super().__init__(base_url, api_token)

    def _get(self, url: str, **params: Any) -> Dict[str, Any]:
        """Synchronous GET request"""
        with httpx.Client() as client:
            headers = (
                {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
            )
            response = client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

    def _post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synchronous POST request"""
        with httpx.Client() as client:
            headers = (
                {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
            )
            response = client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()

    def _delete(self, url: str, **params: Any) -> Dict[str, Any]:
        """Synchronous DELETE request"""
        with httpx.Client() as client:
            headers = (
                {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
            )
            response = client.delete(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()


# Concrete implementation for asynchronous operations


class AsyncAPI(BaseAPI):
    def __init__(self, base_url: str, api_token: Optional[str] = None):
        super().__init__(base_url, api_token)

    async def _get(self, url: str, **params: Any) -> Dict[str, Any]:
        """Asynchronous GET request"""
        if not self.session:
            await self._init_session()
        headers = (
            {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        )
        response = await self.session.get(url, headers=headers, params=params)
        response.raise_for_status()
        return await response.json()

    async def _post(
        self, url: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Asynchronous POST request"""
        if not self.session:
            await self._init_session()
        headers = (
            {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        )
        response = await self.session.post(url, headers=headers, json=data)
        response.raise_for_status()
        return await response.json()

    async def _delete(self, url: str, **params: Any) -> Dict[str, Any]:
        """Asynchronous DELETE request"""
        if not self.session:
            await self._init_session()
        headers = (
            {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        )
        response = await self.session.delete(url, headers=headers, params=params)
        response.raise_for_status()
        return await response.json()
