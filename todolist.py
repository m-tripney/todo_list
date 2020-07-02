from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def initialise():
    engine = create_engine("sqlite:///todo.db?check_same_thread=False")
    todo_list = TodoList(engine, sessionmaker(bind=engine)())
    todo_list.create_table()
    todo_list.interface()


class Table(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True)
    task = Column(String, default="Unnamed task")
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        """Return a string representation of the class object."""
        return self.task


class TodoList:
    def __init__(self, engine, session):
        """Create database and session."""
        self.engine = engine
        self.session = session

    def create_table(self):
        """Create table in database."""
        Base.metadata.create_all(self.engine)

    @staticmethod
    def format_date(date):
        """Convert task date to datetime (or default to today's date)"""
        if date:
            task_date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            task_date = datetime.today().date()
        return task_date

    @staticmethod
    def format_tasks(rows, message):
        if rows:
            for index, row in enumerate(rows, 1):
                date = row.deadline.strftime("%-d")
                month = row.deadline.strftime("%b")
                print(f"{index}. {row.task} ({date} {month})")
        else:
            print(message)

    def view_today(self):
        """View todos (rows) with today's date."""
        today = datetime.today().date()
        print(f"\nToday ({today.strftime('%-d %b')}):")
        rows = self.session.query(Table).filter(Table.deadline == today).all()
        if rows:
            for row in rows:
                print(f"{row.id}. {row.task}")
        else:
            print("Nothing to do!")

    def view_week(self):
        """View todos (rows) spanning next seven days, including today."""
        today = datetime.today().date()
        week_hence = today + timedelta(days=7)
        while today < week_hence:
            print(f"\n{today.strftime('%A %-d %b')}:")
            daily_tasks = (
                self.session.query(Table).filter(Table.deadline == today).all()
            )
            if daily_tasks:
                for index, row in enumerate(daily_tasks, 1):
                    print(f"{index}. {row.task}")
            else:
                print("Nothing to do!")
            today += timedelta(days=1)

    def view_all(self):
        """View all todos (rows), in date order."""
        rows = self.session.query(Table).order_by(Table.deadline).all()
        self.format_tasks(rows, "Nothing to do!")

    def view_missed(self):
        """Show tasks with a deadline before today's date."""
        print("\nMissed tasks:")
        today = datetime.today().date()
        rows = (
            self.session.query(Table)
            .filter(Table.deadline < today)
            .order_by(Table.deadline)
            .all()
        )
        self.format_tasks(rows, "Nothing is missed!")

    def add_task(self):
        """Add new row (i.e. new todo) to database, and commit."""
        new_task = input("\nEnter task:\n> ")
        date_string = input("Enter deadline (YYYY-MM-DD):\n> ")
        task_date = self.format_date(date_string)
        new_row = Table(task=new_task, deadline=task_date)
        self.session.add(new_row)
        self.session.commit()
        print("The task has been added!")

    def delete_task(self):
        rows = self.session.query(Table).order_by(Table.deadline).all()
        if rows:
            print("\nChoose the number of the task you want to delete:")
            self.view_all()
            to_delete = int(input("> "))
            self.session.delete(rows[to_delete - 1])
            self.session.commit()
            print("The task has been deleted!")
        else:
            print("\nNothing to delete!")

    def interface(self):
        """User interaction with menu (and database)."""
        while True:
            print(
                "\n1) Today's tasks",
                "2) Week's tasks",
                "3) All tasks",
                "4) Missed tasks",
                "5) Add task",
                "6) Delete task",
                "0) Exit",
                sep="\n",
            )
            user_input = input("> ")
            if user_input == "1":
                self.view_today()
            elif user_input == "2":
                self.view_week()
            elif user_input == "3":
                print("\nAll tasks:")
                self.view_all()
            elif user_input == "4":
                self.view_missed()
            elif user_input == "5":
                self.add_task()
            elif user_input == "6":
                self.delete_task()
            elif user_input == "0":
                print("Bye!")
                break


if __name__ == "__main__":
    initialise()
