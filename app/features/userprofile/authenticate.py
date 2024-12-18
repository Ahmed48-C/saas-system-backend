import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions
from django.urls import resolve

logger = logging.getLogger(__name__)

def enforce_csrf(request):
    """
    Enforce CSRF validation using Django's CSRFCheck.
    """
    check = CSRFCheck()
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        logger.warning(f"CSRF validation failed: {reason}")
        raise exceptions.PermissionDenied(f'CSRF Failed: {reason}')

class CustomAuthentication(JWTAuthentication):
    """
    Custom authentication class that retrieves JWT from cookies
    and enforces CSRF protection.
    """
    def authenticate(self, request):
        # Determine the current endpoint
        current_url = resolve(request.path_info).url_name
        logger.debug(f"Authenticating request for URL name: {current_url}")

        if current_url in ['token_refresh', 'token_obtain_pair', 'token_verify']:
            logger.debug("Skipping authentication for token-related endpoint.")
            return None  # Skip authentication for token endpoints

        # Attempt to retrieve the Authorization header
        header = self.get_header(request)
        logger.debug(f"Authorization header: {header}")

        if header is None:
            # If no header, attempt to get the token from the cookie
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE']) or None
            logger.debug(f"Raw token from cookies: {raw_token}")
        else:
            # If header is present, extract the raw token
            raw_token = self.get_raw_token(header)
            logger.debug(f"Raw token from header: {raw_token}")

        if raw_token is None:
            logger.warning("No JWT token found in request.")
            return None

        try:
            # Validate the token
            validated_token = self.get_validated_token(raw_token)
            logger.debug("JWT token validated successfully.")

            # Enforce CSRF validation
            enforce_csrf(request)
            logger.debug("CSRF validation passed.")

            # Retrieve the user associated with the token
            user = self.get_user(validated_token)
            logger.debug(f"Authenticated user: {user.username}")

            return (user, validated_token)
        except TokenError as e:
            logger.error(f"Invalid token: {e}")
            raise InvalidToken(e.args[0])
        except exceptions.PermissionDenied as e:
            logger.error(f"Permission denied: {e}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error during authentication: {e}")
            raise exceptions.AuthenticationFailed('Authentication failed due to an unexpected error.')