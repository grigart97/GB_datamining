from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models


class Database:
    def __init__(self, bd_url):
        engine = create_engine(bd_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(engine)

    def get_or_create_data(self, session, model, unique_field, unique_value, **data):
        db_data = session.query(model).filter(unique_field == unique_value).first()
        if not db_data:
            db_data = model(**data)
        return db_data

    def get_or_create_comment(self, session, data: list) -> list:
        result = []
        for comment in data:
            comment_user = self.get_or_create_data(session,
                                                   models.User,
                                                   models.User.id,
                                                   comment['comment']['user']['id'],
                                                   id=comment['comment']['user']['id'],
                                                   name=comment['comment']['user']['full_name']
                                                   )
            comment_data = self.get_or_create_data(session,
                                                   models.Comment,
                                                   models.Comment.id,
                                                   comment['comment']['id'],
                                                   **comment['comment'],
                                                   author=comment_user
                                                   )
            result.append(comment_data)
            result.extend(self.get_or_create_comment(session, comment['comment']['children']))
        return result

    def create_post(self, data):
        session = self.maker()
        comments = self.get_or_create_comment(session, data['comments'])
        user = self.get_or_create_data(session,
                                       models.User,
                                       models.User.id,
                                       data['author_data']['id'],
                                       **data['author_data']
                                       )
        tags = map(lambda tag_data: self.get_or_create_data(
            session, models.Tag, models.Tag.url, tag_data['url'], **tag_data),
                   data['tags'])
        post = self.get_or_create_data(session,
                                       models.Post,
                                       models.Post.id,
                                       data['post_data']['id'],
                                       **data['post_data'],
                                       author=user
                                       )
        post.tags.extend(tags)
        post.comments.extend(comments)
        session.add(post)
        try:
            session.commit()
        except Exception as exc:
            print(exc)
            session.rollback()
        finally:
            session.close()
