import os
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import database

def create_app(config=None):
    app = Flask(__name__)
    app.config["DATABASE"] = os.environ.get("TASKFLOW_DB", "data/tasks.db")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
    if config:
        app.config.update(config)
    
    database.init_db(app.config["DATABASE"])

    def validate_task(form, is_edit=False):
        clean_data = {}
        errors = {}

        title = form.get("title", "").strip()
        if not title:
            errors["title"] = "Title is required"
        elif len(title) > 100:
            errors["title"] = "Title must be 100 characters or less"
        else:
            clean_data["title"] = title

        description = form.get("description", "").strip()
        if len(description) > 500:
            errors["description"] = "Description must be 500 characters or less"
        else:
            clean_data["description"] = description

        priority = form.get("priority", "")
        if priority not in ["Low", "Medium", "High"]:
            errors["priority"] = "Priority must be Low, Medium, or High"
        else:
            clean_data["priority"] = priority

        due_date = form.get("due_date", "")
        if not due_date:
            errors["due_date"] = "Due date is required"
        else:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
                clean_data["due_date"] = due_date
            except ValueError:
                errors["due_date"] = "Due date must be in YYYY-MM-DD format"

        if is_edit:
            status = form.get("status", "")
            if status not in ["Pending", "Completed"]:
                errors["status"] = "Status must be Pending or Completed"
            else:
                clean_data["status"] = status

        return clean_data, errors

    @app.route("/")
    def dashboard():
        tasks = database.get_all_tasks(app.config["DATABASE"])
        return render_template("index.html", tasks=tasks)

    @app.route("/add", methods=["GET", "POST"])
    def add_task():
        if request.method == "POST":
            clean_data, errors = validate_task(request.form)
            if errors:
                return render_template("add_task.html", errors=errors, form=request.form), 400
            
            database.create_task(
                app.config["DATABASE"],
                clean_data["title"],
                clean_data["description"],
                clean_data["priority"],
                clean_data["due_date"]
            )
            flash("Task added successfully!", "success")
            return redirect(url_for("dashboard"))
        
        return render_template("add_task.html", errors={}, form={})

    @app.route("/edit/<int:task_id>", methods=["GET", "POST"])
    def edit_task(task_id):
        task = database.get_task(app.config["DATABASE"], task_id)
        if not task:
            return "Task not found", 404
        
        if request.method == "POST":
            clean_data, errors = validate_task(request.form, is_edit=True)
            if errors:
                return render_template("edit_task.html", task=task, errors=errors, form=request.form), 400
            
            database.update_task(
                app.config["DATABASE"],
                task_id,
                clean_data["title"],
                clean_data["description"],
                clean_data["priority"],
                clean_data["due_date"],
                clean_data["status"]
            )
            flash("Task updated successfully!", "success")
            return redirect(url_for("dashboard"))
        
        return render_template("edit_task.html", task=task, errors={}, form=task)

    @app.route("/complete/<int:task_id>", methods=["POST"])
    def complete_task(task_id):
        task = database.get_task(app.config["DATABASE"], task_id)
        if not task:
            return "Task not found", 404
        
        database.complete_task(app.config["DATABASE"], task_id)
        flash("Task marked as completed!", "success")
        return redirect(url_for("dashboard"))

    @app.route("/delete/<int:task_id>", methods=["POST"])
    def delete_task(task_id):
        task = database.get_task(app.config["DATABASE"], task_id)
        if not task:
            return "Task not found", 404
        
        database.delete_task(app.config["DATABASE"], task_id)
        flash("Task deleted successfully!", "success")
        return redirect(url_for("dashboard"))

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
