from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from flask import Blueprint, jsonify, request, current_app

from payment.party.application.command.party_command_service import PartyCommandService
from payment.party.application.queries.party_query_service import PartyQueryService
from payment.party.domain.entities.party import PartyAppName, PartySubjectType


# --------------------------
# Helpers (parse / utils)
# --------------------------
def _get_services() -> Tuple[PartyCommandService, PartyQueryService]:
    services = current_app.config.get("services") or {}
    cmd: PartyCommandService = services["party_command_service"]
    qry: PartyQueryService = services["party_query_service"]
    return cmd, qry


def _as_enum(value: Any, enum_cls):
    if value is None:
        raise ValueError(f"valor requerido para {enum_cls.__name__}")
    if isinstance(value, enum_cls):
        return value
    # tolerar mayúsc/minúsculas
    s = str(value)
    try:
        return enum_cls(s)
    except Exception:
        for e in enum_cls:
            if e.value.lower() == s.lower():
                return e
        raise ValueError(f"valor inválido para {enum_cls.__name__}: {value}")


def _require(body: Dict[str, Any], field: str):
    if field not in body:
        raise ValueError(f"'{field}' es requerido")
    return body[field]


def _optional(body: Dict[str, Any], field: str, default=None):
    return body[field] if field in body else default


def _entity_to_dict(e) -> Dict[str, Any]:
    if hasattr(e, "to_dict") and callable(getattr(e, "to_dict")):
        return e.to_dict()
    # fallback (por si tu entidad no tiene to_dict)
    return {
        "id": getattr(e, "id", None),
        "app_name": getattr(e, "app_name", None).value
        if isinstance(getattr(e, "app_name", None), PartyAppName)
        else getattr(e, "app_name", None),
        "subject_type": getattr(e, "subject_type", None).value
        if isinstance(getattr(e, "subject_type", None), PartySubjectType)
        else getattr(e, "subject_type", None),
        "subject_id": getattr(e, "subject_id", None),
        "display_name": getattr(e, "display_name", None),
        "created_at": getattr(e, "created_at", None).isoformat()
        if getattr(e, "created_at", None)
        else None,
        "updated_at": getattr(e, "updated_at", None).isoformat()
        if getattr(e, "updated_at", None)
        else None,
    }


# --------------------------
# Blueprint factory
# --------------------------
def create_party_blueprint(url_prefix: str = "/parties") -> Blueprint:
    """
    Controller (capa de interfaz) para Party.
    Requiere services inyectados en current_app.config['services']:
      - party_command_service
      - party_query_service
    """
    bp = Blueprint("parties", __name__)

    @bp.route("/ping", methods=["GET"])
    def ping():
        return jsonify(ok=True), 200

    # --------------------------
    # Commands
    # --------------------------

    # POST /parties
    # body: {app_name, subject_type, subject_id, display_name?}
    @bp.route("", methods=["POST"])
    def create_party():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            app_name = _as_enum(_require(body, "app_name"), PartyAppName)
            subject_type = _as_enum(_require(body, "subject_type"), PartySubjectType)
            subject_id = int(_require(body, "subject_id"))
            display_name = _optional(body, "display_name")
            if display_name is not None:
                display_name = display_name.strip() or None
        except ValueError as ve:
            return jsonify(ok=False, error=str(ve)), 400

        entity = cmd.create(
            app_name=app_name,
            subject_type=subject_type,
            subject_id=subject_id,
            display_name=display_name,
        )
        return jsonify(ok=True, data=_entity_to_dict(entity)), 201

    # PUT /parties/upsert-by-subject
    # body: {app_name, subject_type, subject_id, display_name?}
    @bp.route("/upsert-by-subject", methods=["PUT"])
    def upsert_by_subject():
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        try:
            app_name = _as_enum(_require(body, "app_name"), PartyAppName)
            subject_type = _as_enum(_require(body, "subject_type"), PartySubjectType)
            subject_id = int(_require(body, "subject_id"))
            display_name = _optional(body, "display_name")
            if display_name is not None:
                display_name = display_name.strip() or None
        except ValueError as ve:
            return jsonify(ok=False, error=str(ve)), 400

        entity = cmd.upsert_by_subject(
            app_name=app_name,
            subject_type=subject_type,
            subject_id=subject_id,
            display_name=display_name,
        )
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # PATCH /parties/<id>/display-name
    # body: {display_name?}
    @bp.route("/<int:party_id>/display-name", methods=["PATCH"])
    def update_display_name(party_id: int):
        cmd, _ = _get_services()
        body = request.get_json(silent=True) or {}
        display_name = _optional(body, "display_name")
        if display_name is not None:
            display_name = display_name.strip() or None

        entity = cmd.update_display_name(party_id, display_name)
        if not entity:
            return jsonify(ok=False, error="party no encontrada"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # DELETE /parties/id/<id>
    @bp.route("/id/<int:party_id>", methods=["DELETE"])
    def delete_party(party_id: int):
        cmd, _ = _get_services()
        ok = cmd.delete(party_id)
        if not ok:
            return jsonify(ok=False, error="party no encontrada"), 404
        return jsonify(ok=True), 200

    # --------------------------
    # Queries
    # --------------------------

    # GET /parties/id/<id>
    @bp.route("/id/<int:party_id>", methods=["GET"])
    def get_by_id(party_id: int):
        _, qry = _get_services()
        entity = qry.get_by_id(party_id)
        if not entity:
            return jsonify(ok=False, error="party no encontrada"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # GET /parties/by-subject?app_name=emprende&subject_type=user&subject_id=123
    @bp.route("/by-subject", methods=["GET"])
    def get_by_subject():
        _, qry = _get_services()
        try:
            app_name = _as_enum(request.args.get("app_name"), PartyAppName)
            subject_type = _as_enum(request.args.get("subject_type"), PartySubjectType)
            subject_id = int(request.args.get("subject_id"))
        except Exception as e:
            return jsonify(ok=False, error=str(e)), 400

        entity = qry.get_by_subject(app_name, subject_type, subject_id)
        if not entity:
            return jsonify(ok=False, error="party no encontrada"), 404
        return jsonify(ok=True, data=_entity_to_dict(entity)), 200

    # GET /parties (lista todas)
    @bp.route("", methods=["GET"])
    def list_all():
        _, qry = _get_services()
        items = qry.list_all()
        return jsonify(ok=True, data=[_entity_to_dict(i) for i in items]), 200

    # GET /parties/search?text=juan&limit=50
    @bp.route("/search", methods=["GET"])
    def search_by_name():
        _, qry = _get_services()
        text = request.args.get("text", "").strip()
        if not text:
            return jsonify(ok=False, error="'text' es requerido"), 400
        limit = int(request.args.get("limit", 50))
        items = qry.search_by_name(text, limit=limit)
        return jsonify(ok=True, data=[_entity_to_dict(i) for i in items]), 200

    # POST /parties/by-app-subjects
    # body: {"triples":[{"app_name":"emprende","subject_type":"user","subject_id":1}, ...]}
    @bp.route("/by-app-subjects", methods=["POST"])
    def list_by_app_subjects():
        _, qry = _get_services()
        body = request.get_json(silent=True) or {}
        triples_json = body.get("triples") or []
        triples: List[tuple[str, str, int]] = []
        try:
            for t in triples_json:
                app_name = _as_enum(t["app_name"], PartyAppName).value
                subject_type = _as_enum(t["subject_type"], PartySubjectType).value
                subject_id = int(t["subject_id"])
                triples.append((app_name, subject_type, subject_id))
        except Exception as e:
            return jsonify(ok=False, error=f"triples inválidos: {e}"), 400

        items = qry.list_by_app_subjects(triples)
        return jsonify(ok=True, data=[_entity_to_dict(i) for i in items]), 200

    bp.url_prefix = url_prefix
    return bp
