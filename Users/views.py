import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate

from Users.auth_utils import create_token, get_user_from_request


def _user_payload(user):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name or "",
        "role": user.role,
        "organization_id": user.organization_id,
        "is_superadmin": getattr(user, "is_superuser", False),
    }


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(View):
    """POST /api/auth/login/  Body: { email, password }"""

    def post(self, request):
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        email = (body.get("email") or "").strip()
        password = body.get("password")

        if not email or not password:
            return JsonResponse({"error": "email and password required"}, status=400)

        user = authenticate(request, username=email, password=password)
        if user is None:
            return JsonResponse({"error": "Invalid email or password"}, status=401)
        if not user.is_active:
            return JsonResponse({"error": "Account is inactive"}, status=401)

        token = create_token(user)
        return JsonResponse(
            {"token": token, "user": _user_payload(user)},
            status=200,
        )


@method_decorator(csrf_exempt, name="dispatch")
class MeView(View):
    """GET /api/auth/me/  Requires Authorization: Bearer <token>"""

    def get(self, request):
        user = get_user_from_request(request)
        if user is None:
            return JsonResponse({"error": "Invalid or expired token"}, status=401)
        return JsonResponse({"user": _user_payload(user)}, status=200)
