from app import db
from typing import List
from .model import User
from pydantic import ValidationError


class UserService:
    # @staticmethod
    # def get_all() -> List[Fizzbar]:
    #     return Fizzbar.query.all()

    # @staticmethod
    # def get_by_id(fizzbar_id: int) -> Fizzbar:
    #     return Fizzbar.query.get(fizzbar_id)

    # @staticmethod
    # def update(fizzbar: Fizzbar, Fizzbar_change_updates: FizzbarInterface) -> Fizzbar:
    #     fizzbar.update(Fizzbar_change_updates)
    #     db.session.commit()
    #     return fizzbar

    # @staticmethod
    # def delete_by_id(fizzbar_id: int) -> List[int]:
    #     fizzbar = Fizzbar.query.filter(Fizzbar.fizzbar_id == fizzbar_id).first()
    #     if not fizzbar:
    #         return []
    #     db.session.delete(fizzbar)
    #     db.session.commit()
    #     return [fizzbar_id]

    @staticmethod
    def create(name:str, email:str):
      try:
        print(new_attrs)
        new_user = User(new_attrs)
        new_user.save()
        return new_user.pk

      except ValidationError as e:
          print(e)
          return "Bad request.", 400
