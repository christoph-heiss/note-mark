from functools import wraps
from typing import Any, Callable
from uuid import UUID

from quart import Blueprint, make_response, render_template
from quart_auth import current_user
from tortoise.exceptions import DoesNotExist

from ..database import crud
from ..helpers import read_note_file_html, read_note_file_md

blueprint = Blueprint("api", __name__)


def api_login_required(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not await current_user.is_authenticated:
            return "you must pass a valid login cookie", 401
        else:
            return await func(*args, **kwargs)
    return wrapper


@blueprint.route("/notebook/personal.html")
@api_login_required
async def rendered_notebook_personal_list():
    owner_id = UUID(current_user.auth_id)
    owned_notebooks = await crud.get_all_personal_notebooks(owner_id)
    return await render_template(
        "/shared/includes/notebook_personal.jinja2",
        owned_notebooks=owned_notebooks)


@blueprint.route("/notebook/shared.html")
@api_login_required
async def rendered_notebook_shared_list():
    owner_id = UUID(current_user.auth_id)
    shared_notebooks = crud.get_shared_notebooks(owner_id)
    return await render_template(
        "/shared/includes/notebook_shared.jinja2",
        shared_notebooks=shared_notebooks)


@blueprint.route("/notebook/<notebook_uuid>/notes.html")
@api_login_required
async def rendered_notes_list(notebook_uuid):
    try:
        notebook_uuid = UUID(notebook_uuid)
        owner_id = UUID(current_user.auth_id)
        notebook = await crud.get_personal_notebook(notebook_uuid)
        await crud.check_user_notebook_access(
            owner_id,
            notebook_uuid,
            ("read", "write", "owner"))
        notes = await crud.get_notes(notebook_uuid)
        return await render_template(
            "/shared/includes/notes.jinja2",
            notebook=notebook,
            notes=notes)
    except DoesNotExist:
        return "notebook does not exist, or you don't have access to it", 404
    except ValueError:
        return "invalid notebook uuid", 404


@blueprint.route("/notebook/<notebook_uuid>/notes/<note_uuid>.md")
@api_login_required
async def raw_note(notebook_uuid, note_uuid):
    try:
        notebook_uuid = UUID(notebook_uuid)
        note_uuid = UUID(note_uuid)
        owner_id = UUID(current_user.auth_id)
        await crud.check_user_notebook_access(
            owner_id,
            notebook_uuid,
            ("read", "write", "owner"))
        await crud.get_note(note_uuid)
        md_str = await read_note_file_md(notebook_uuid, note_uuid)
        file_resp = await make_response(md_str)
        file_resp.mimetype = "text/md"
        return file_resp
    except DoesNotExist:
        return "notebook does not exist, or you don't have access to it", 404
    except ValueError:
        return "invalid notebook/user/note", 404


@blueprint.route("/notebook/<notebook_uuid>/notes/<note_uuid>.html")
@api_login_required
async def rendered_note(notebook_uuid, note_uuid):
    try:
        notebook_uuid = UUID(notebook_uuid)
        note_uuid = UUID(note_uuid)
        owner_id = UUID(current_user.auth_id)
        await crud.check_user_notebook_access(
            owner_id,
            notebook_uuid,
            ("read", "write", "owner"))
        await crud.get_note(note_uuid)
        return await read_note_file_html(notebook_uuid, note_uuid)
    except DoesNotExist:
        return "notebook does not exist, or you don't have access to it", 404
    except ValueError:
        return "invalid notebook/user/note", 404
