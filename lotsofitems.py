from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, Category, User
from database_setup import parseCFG
res = parseCFG()
eng_str = 'postgresql://{}:{}@localhost/{}'.format(res[0], res[1], res[2])

engine = create_engine(eng_str)
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()

session = DBSession()


# Create dummy user

User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

category1 = Category(user_id=1, name="Acrobatics")

session.add(category1)
session.commit()

description = """An acrobatic flip is a sequence
of body movements in which a person leaps into the air and then rotates one
or more times while airborne. Acrobatic flips are performed in acro dance,
free running, gymnastics, cheerleading and various other activities. During
the baclflip body rotates backwards along the transverse axis of the body.
"""

item1 = Item(user_id=1, name="Backflip", description=description,
             category_id=1)

session.add(item1)
session.commit()

description = """It's also a flip, but during the frontflip body rotates forwards along the
transverse axis of the body. It is more complex movement then backflip, but it can be more
scaring to do backflip.
"""

item2 = Item(user_id=1, name="Frontflip", description=description,
             category_id=1)

session.add(item2)
session.commit()

category2 = Category(user_id=1, name="Grappling")

session.add(category2)
session.commit()

description = """In martial arts and combat sports, a takedown is a technique that involves
 off-balancing an opponent and bringing him or her to the ground, typically with the attacker
 landing on top. The process of quickly advancing on an opponent and attempting a takedown
 is known as shooting for a takedown. Takedowns are usually distinguished
 from throws by the forward motion and target of advancement (typically the legs);
 the terms are used interchangeably for techniques. Takedowns are featured in all forms
  of wrestling and stand-up grappling.
"""

item3 = Item(user_id=1, name="Takedowns", description=description,
             category_id=2)

session.add(item3)
session.commit()

description = """A chokehold, choke, stranglehold or, in Judo, shime-waza
 is a general term for a grappling hold that critically reduces or prevents either air (choking)[2] or blood (strangling)
 from passing through the neck of an opponent. The restriction may be of one or both and depends
 on the hold used and the reaction of the victim. The lack of blood or air may lead to unconsciousness
 or even death if the hold is maintained. Chokeholds are used in martial arts, combat sports, self-defense,
 law enforcement and in military hand to hand combat applications.
"""

item4 = Item(user_id=1, name="Chokehold", description=description,
             category_id=2)

session.add(item4)
session.commit()

description = """A joint lock is a grappling technique involving manipulation
 of an opponent's joints in such a way that the joints reach their maximal degree of motion.
"""

item5 = Item(user_id=1, name="Joint lock", description=description,
             category_id=2)

session.add(item5)
session.commit()


print "added menu items!"