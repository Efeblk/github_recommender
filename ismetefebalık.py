import math
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk


class User:
    def __init__(self, user_id, name, github):
        self.id = user_id
        self.name = name
        self.github = github


class Star:
    def __init__(self, user_id, repo_ids):
        self.user_id = user_id
        self.repo_ids = repo_ids


class Repo:
    def __init__(self, repo_id, name, url, language):
        self.id = repo_id
        self.name = name
        self.url = url
        self.language = language


class DataUploader:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Github Project Recommender")
        self.window.geometry("1500x600")

        self.title_label = tk.Label(
            self.window,
            text="Github Project Recommender",
            bg="yellow",
            fg="black",
            font=("Arial", 14, "bold")
        )
        self.title_label.pack(fill=tk.X, padx=10, pady=10)

        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack(pady=10)

        self.user_data_button = tk.Button(
            self.button_frame,
            text="Select User Data",
            command=self.load_user_data
        )
        self.user_data_button.pack(side=tk.LEFT, padx=10)

        self.repository_data_button = tk.Button(
            self.button_frame,
            text="Select Repository Data",
            command=self.load_repository_data
        )
        self.repository_data_button.pack(side=tk.LEFT, padx=10)

        self.star_data_button = tk.Button(
            self.button_frame,
            text="Select Star Data",
            command=self.load_star_data
        )
        self.star_data_button.pack(side=tk.LEFT, padx=10)

        self.user_data = None
        self.repository_data = None
        self.star_data = None

        self.user_table_frame = tk.Frame(self.window)
        self.user_table_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.user_table = ttk.Treeview(
            self.user_table_frame,
            columns=("Username", "ID"),
            show="headings"
        )
        self.user_table.heading("Username", text="Username")
        self.user_table.heading("ID", text="ID")
        self.user_table.pack(side=tk.TOP, padx=10, pady=10)

        self.language_combo = ttk.Combobox(self.user_table_frame, state="readonly")
        self.language_combo.pack(side=tk.LEFT, padx=5)

        self.similarity_frame = tk.Frame(self.user_table_frame)
        self.similarity_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.pearson_var = tk.BooleanVar(value=False)
        self.euclidean_var = tk.BooleanVar(value=False)

        self.pearson_checkbox = tk.Checkbutton(
            self.similarity_frame,
            text="Pearson",
            variable=self.pearson_var,
            command=self.update_pearson_checkbox_state
        )
        self.pearson_checkbox.pack(side=tk.LEFT, padx=10, pady=10)

        self.euclidean_checkbox = tk.Checkbutton(
            self.similarity_frame,
            text="Euclidean",
            variable=self.euclidean_var,
            command=self.update_euclidean_checkbox_state
        )
        self.euclidean_checkbox.pack(side=tk.LEFT, padx=10, pady=10)

        self.num_recs_label = tk.Label(self.similarity_frame, text="Number of Recommendations:")
        self.num_recs_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.num_recs_entry = tk.Entry(self.similarity_frame, width=5)
        self.num_recs_entry.pack(side=tk.LEFT, padx=10, pady=10)

        self.recommendation_table_frame = tk.Frame(self.window)
        self.recommendation_table_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.recommendation_table = ttk.Treeview(
            self.recommendation_table_frame,
            columns=("Name", "Url", "Score"),
            show="headings"
        )
        self.recommendation_table.heading("Name", text="Name")
        self.recommendation_table.heading("Url", text="Url")
        self.recommendation_table.heading("Score", text="Score")
        self.recommendation_table.pack(padx=10, pady=10)

        self.calculate_repo_button = tk.Button(
            self.window,
            text="Recommend Repository",
            command=self.calculate_repository_similarity
        )
        self.calculate_repo_button.pack(pady=10)

        self.calculate_user_button = tk.Button(
            self.window,
            text="Recommend Github User",
            command=self.calculate_user_similarity
        )
        self.calculate_user_button.pack(pady=10)

    def load_user_data(self):
        file_path = filedialog.askopenfilename(
            title="Select User Data File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if file_path:
            self.user_data = self.load_data(file_path)
            self.user_objects = []

            for row in self.user_data:
                user_id, name, github = row.split(",")
                user = User(user_id, name, github)
                self.user_objects.append(user)

            print("User Data Loaded:")
            for user in self.user_objects:
                print("ID:", user.id, "Name:", user.name, "GitHub:", user.github)

            self.display_user_data()

    def load_repository_data(self):
        file_path = filedialog.askopenfilename(
            title="Select Repository Data File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if file_path:
            self.repository_data = self.load_data(file_path)
            self.repository_objects = []
            self.languages = set()

            for row in self.repository_data:
                repo_id, name, url, language = row.split(",")
                repo = Repo(repo_id, name, url, language)
                self.repository_objects.append(repo)
                self.languages.add(language)

            print("Repository Data Loaded:")
            for repo in self.repository_objects:
                print("ID:", repo.id, "Name:", repo.name, "URL:", repo.url, "Language:", repo.language)

            self.populate_language_combo()
            self.language_combo.set("None")

    def populate_language_combo(self):
        self.language_combo["values"] = list(self.languages)

    def load_star_data(self):
        file_path = filedialog.askopenfilename(
            title="Select Star Data File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if file_path:
            self.star_data = self.load_data(file_path)
            self.star_objects = []

            for row in self.star_data:
                user_id, repo_ids = row.split("\t")
                repo_ids = repo_ids.split(",")
                star = Star(user_id, repo_ids)
                self.star_objects.append(star)

            print("Star Data Loaded:")
            for star in self.star_objects:
                print("User ID:", star.user_id, "Starred Repos:", star.repo_ids)

    def load_data(self, file_path):
        data = []
        with open(file_path, "r") as file:
            for line in file:
                data.append(line.strip())
        return data

    def display_user_data(self):
        self.user_table.delete(*self.user_table.get_children())
        for user in self.user_objects:
            self.user_table.insert("", tk.END, values=(user.name, user.id))

    def update_pearson_checkbox_state(self):
        if self.pearson_var.get():
            self.euclidean_checkbox.config(state=tk.DISABLED)
        else:
            self.euclidean_checkbox.config(state=tk.NORMAL)

    def update_euclidean_checkbox_state(self):
        if self.euclidean_var.get():
            self.pearson_checkbox.config(state=tk.DISABLED)
        else:
            self.pearson_checkbox.config(state=tk.NORMAL)

    def calculate_repository_similarity(self):
        user_index = self.user_table.selection()  # Get the selected user from the Treeview
        selected_user = None
        if user_index:
            selected_user_id = int(self.user_table.item(user_index)['values'][1])  # Convert to integer
            selected_user = next((user for user in self.user_objects if int(user.id) == selected_user_id), None)

        language = self.language_combo.get()
        num_recs = int(self.num_recs_entry.get())

        if not selected_user or language == "None":
            return

        selected_user_stars = self.get_user_stars(selected_user)

        recommendations = []
        for repo in self.repository_objects:
            if repo.language == language and repo.id not in selected_user_stars:
                score = 0
                if self.pearson_var.get():
                    score = self.calculate_pearson_score(selected_user, selected_user_stars, repo.id)
                elif self.euclidean_var.get():
                    score = self.calculate_euclidean_score(selected_user, selected_user_stars, repo.id)
                recommendations.append((repo, score))

        recommendations.sort(key=lambda x: x[1], reverse=True)
        recommendations = recommendations[:num_recs]

        self.display_recommendations(recommendations)


    def calculate_user_similarity(self):
        user_index = self.language_combo.current()
        language = self.language_combo.get()
        num_recs = int(self.num_recs_entry.get())  # Get the number of recommendations

        if user_index < 0 or language == "None":
            return

        selected_user = self.user_objects[user_index]

        recommendations = []
        for user in self.user_objects:
            if user.id != selected_user.id:
                score = 0
                if self.pearson_var.get():
                    score = self.calculate_pearson_user_score(selected_user, user)
                elif self.euclidean_var.get():
                    score = self.calculate_euclidean_user_score(selected_user, user)
                recommendations.append((user, score))

        recommendations.sort(key=lambda x: x[1], reverse=True)
        recommendations = recommendations[:num_recs]  # Consider only the specified number of recommendations

        self.display_user_recommendations(recommendations)

    def calculate_pearson_score(self, selected_user, user_stars, repo_id):
        score = 0
        selected_user_stars_set = set(user_stars)
        for star in self.star_objects:
            if repo_id in star.repo_ids:
                other_user_stars_set = set(self.get_user_stars(selected_user))
                common_stars = selected_user_stars_set.intersection(other_user_stars_set)
                num_common_stars = len(common_stars)
                if star.user_id != selected_user.id:
                    score += num_common_stars
                else:
                    score -= num_common_stars
        return score

    def calculate_euclidean_score(self, selected_user, user_stars, repo_id):
        score = 0
        selected_user_stars_set = set(user_stars)
        for star in self.star_objects:
            if repo_id in star.repo_ids:
                other_user_stars_set = set(self.get_user_stars(selected_user))
                common_stars = selected_user_stars_set.intersection(other_user_stars_set)
                num_common_stars = len(common_stars)
                if star.user_id != selected_user.id:
                    score += math.sqrt(num_common_stars)
                else:
                    score -= math.sqrt(num_common_stars)
        return score

    def calculate_pearson_user_score(self, selected_user, other_user):
        selected_user_stars_set = set(self.get_user_stars(selected_user.id))  # Pass the user ID
        other_user_stars_set = set(self.get_user_stars(other_user.id))  # Pass the user ID
        common_stars = selected_user_stars_set.intersection(other_user_stars_set)
        num_common_stars = len(common_stars)
        num_selected_user_stars = len(selected_user_stars_set)
        num_other_user_stars = len(other_user_stars_set)
        score = num_common_stars / math.sqrt((num_selected_user_stars * num_other_user_stars))
        return score

    def calculate_euclidean_user_score(self, selected_user, other_user):
        selected_user_stars_set = set(self.get_user_stars(selected_user.id))
        other_user_stars_set = set(self.get_user_stars(other_user.id))
        common_stars = selected_user_stars_set.intersection(other_user_stars_set)
        num_common_stars = len(common_stars)
        score = math.sqrt(num_common_stars)
        return score

    def get_user_stars(self, user):
        user_stars = []
        for star in self.star_objects:
            if star.user_id == user.id:
                user_stars.extend(star.repo_ids)
        return user_stars


    def display_recommendations(self, recommendations):
        self.recommendation_table.delete(*self.recommendation_table.get_children())
        for repo, score in recommendations:
            self.recommendation_table.insert("", tk.END, values=(repo.name, repo.url, score))
        self.recommendation_table.update_idletasks()

    def display_user_recommendations(self, recommendations):
        self.recommendation_table.delete(*self.recommendation_table.get_children())
        for user, score in recommendations:
            self.recommendation_table.insert("", tk.END, values=(user.name, user.github, score))
        self.recommendation_table.update_idletasks()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    uploader = DataUploader()
    uploader.run()
