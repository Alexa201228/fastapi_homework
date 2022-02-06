from sqlalchemy.orm import Session

import models, schemas


async def get_user_by_email(db_session: Session, user_email: str):
    user = db_session.query(models.User).filter(models.User.email == user_email).first()
    if user:
        return user
    raise KeyError('User with this email does not exist')


async def create_user(db_session: Session, new_user: schemas.UserIn):
    try:
        exist_user = await get_user_by_email(db_session, new_user.email)
        if not exist_user:
            user_role = models.Role(role_id=new_user.role.role_id,
                                    role_description=new_user.role.role_description)
            db_session.add(user_role)
            user = models.User(email=new_user.email,
                               password=new_user.password, role=user_role)
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
            db_session.refresh(user_role)
            return user
        raise ValueError("User already exists!")
    except Exception as e:
        db_session.rollback()
        raise e
