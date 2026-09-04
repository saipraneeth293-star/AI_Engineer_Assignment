from typing import Optional

from pydantic import BaseModel


class ProductSource(BaseModel):

    name: str

    url: str


class ProductContent(BaseModel):

    productName: str

    productUrl: Optional[str] = None

    description: Optional[str] = None

    category: Optional[str] = None

    price: Optional[float] = None

    currency: Optional[str] = None


class Product(BaseModel):

    schemaVersion: str = "1.0"

    recordType: str = "PRODUCT"

    source: ProductSource

    content: ProductContent

    collectedAt: str