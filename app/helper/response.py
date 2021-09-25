from flask import jsonify


def build_response(status=200, error=False, error_reason=None, payload=None):
    return jsonify({
        "status_code": status,
        "error": error,
        "error_reason": error_reason,
        "payload": payload,
    })


def return_success(**kwargs):
    return build_response(**kwargs)


def return_failed(reason):
    return build_response(error=True, error_reason=reason)
