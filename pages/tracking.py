from src.storage.tables import User, UserInteraction
from pages.db import get_db_session
from datetime import datetime
import uuid

def log_interaction(user_id, page, component_id, value):
    """Registra la interacción del usuario en la base de datos."""
    session = get_db_session()
    interaction = UserInteraction(
        id=uuid.uuid4(),
        user_id=user_id,
        page=page,
        component_id=component_id,
        value=str(value),
        timestamp=datetime.utcnow()
    )
    session.add(interaction)
    session.commit()
    session.close()

def log_interaction_by_username(username, page, component_id, value):
    session = get_db_session()
    user = session.query(User).filter_by(username=username).first()
    if not user:
        print(f"Usuario no encontrado: {username}")
    else:
        log_interaction(user.id, page, component_id, value)

    session.close()
    
def save_view_by_username(username, page, view_name, estado_dict):
    session = get_db_session()
    user = session.query(User).filter_by(username=username).first()
    if not user:
        print(f" Usuario no encontrado: {username}")
        session.close()
        return False, "Usuario no encontrado."

    if not view_name:
        return False, "Debes introducir un nombre para la vista."

    vista = SavedView(
        id=uuid.uuid4(),
        user_id=user.id,
        page=page,
        name=view_name,
        params=json.dumps(estado_dict),
        timestamp=datetime.utcnow()
    )
    session.add(vista)
    session.commit()
    session.close()
    return True, f"✅ Vista '{view_name}' guardada correctamente."