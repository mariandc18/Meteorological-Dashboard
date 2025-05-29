from tables import UserInteraction
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