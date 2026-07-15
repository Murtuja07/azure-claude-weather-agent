import os
from functools import lru_cache

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def read_key_vault_secret(
    vault_url: str,
    secret_name: str,
) -> str:
    credential = DefaultAzureCredential()

    client = SecretClient(
        vault_url=vault_url,
        credential=credential,
    )

    secret = client.get_secret(secret_name)

    if secret.value is None:
        raise ValueError(
            f"Key Vault secret has no value: {secret_name}"
        )

    return secret.value


class Settings(BaseSettings):
    anthropic_api_key: str | None = Field(
        default=None,
        alias="ANTHROPIC_API_KEY",
    )

    anthropic_model: str = Field(
        default="claude-sonnet-5",
        alias="ANTHROPIC_MODEL",
    )

    azure_maps_subscription_key: str | None = Field(
        default=None,
        alias="AZURE_MAPS_SUBSCRIPTION_KEY",
    )

    key_vault_url: str | None = Field(
        default=None,
        alias="KEY_VAULT_URL",
    )

    app_env: str = Field(
        default="local",
        alias="APP_ENV",
    )

    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def model_post_init(self, __context: object) -> None:
        if not self.key_vault_url:
            return

        if not self.anthropic_api_key:
            self.anthropic_api_key = read_key_vault_secret(
                self.key_vault_url,
                "anthropic-api-key",
            )

        if not self.azure_maps_subscription_key:
            self.azure_maps_subscription_key = (
                read_key_vault_secret(
                    self.key_vault_url,
                    "azure-maps-subscription-key",
                )
            )

        if not self.anthropic_api_key:
            raise ValueError(
                "Anthropic API key is not configured."
            )

        if not self.azure_maps_subscription_key:
            raise ValueError(
                "Azure Maps key is not configured."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()

# from functools import lru_cache

# from pydantic import Field
# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     anthropic_api_key: str = Field(alias="ANTHROPIC_API_KEY")
#     anthropic_model: str = Field(
#         default="claude-sonnet-5",
#         alias="ANTHROPIC_MODEL",
#     )

#     azure_maps_subscription_key: str = Field(
#         alias="AZURE_MAPS_SUBSCRIPTION_KEY"
#     )

#     app_env: str = Field(default="local", alias="APP_ENV")
#     log_level: str = Field(default="INFO", alias="LOG_LEVEL")

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         case_sensitive=False,
#         extra="ignore",
#     )


# @lru_cache
# def get_settings() -> Settings:
#     return Settings()