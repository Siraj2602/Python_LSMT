import os
import shutil
import csv
class CompactionManager:
    def __init__(self, parent_folder, subfolders, threshold):
        self.parent_folder = parent_folder
        self.subfolders = subfolders
        self.threshold = threshold
        self.folder_paths = {}

    def create_folders(self):
        if not os.path.exists(self.parent_folder):
            os.makedirs(self.parent_folder)
        for folder in self.subfolders:
            folder_path = os.path.join(self.parent_folder, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            self.folder_paths[folder] = folder_path
    
    def check_threshold_and_compact(self, folder_name):
        folder_path = self.folder_paths.get(folder_name)
        if folder_path:
            file_count = len([name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))])
            if file_count >= self.threshold:
                self.compact_and_move(folder_name)

    def compact_and_move(self, folder_name):
        folder_path = self.folder_paths.get(folder_name)
        next_folder_index = self.subfolders.index(folder_name) + 1
        if next_folder_index < len(self.subfolders):
            next_folder_name = self.subfolders[next_folder_index]
            next_folder_path = self.folder_paths.get(next_folder_name)

        # List to store contents of all CSV files
        all_csv_contents = []

        # Iterate through CSV files in the current folder
        for filename in os.listdir(folder_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        all_csv_contents.append(row)

                # Remove the old CSV file after processing
                os.remove(file_path)

        all_csv_contents.sort(key=lambda x: int(x['key']))
        
        # Write the merged contents to a new CSV file in the next folder
        merged_csv_path = os.path.join(next_folder_path, 'merged.csv')
        with open(merged_csv_path, 'w', newline='') as csvfile:
            fieldnames = ['key', 'value']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in all_csv_contents:
                writer.writerow(row)

        print(f"CSV files merged and moved from {folder_name} to {next_folder_name}.")

     
    def create_csv_files(self, folder_path=None):
        if folder_path is None:
            folder_path = self.folder_paths["folder1"]  # Default to folder1 if no folder_path is provided
        for i in range(4):  # Creating 4 files in the specified folder
            file_path = os.path.join(folder_path, f"file{i}.csv")
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['key', 'value']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for j in range(1, 11):  # 10 key-value pairs
                    writer.writerow({'key': j, 'value': f"value_{j}"})

# Example usage 
# Functions are working as expected
# Working on linking them with each other so that compaction is achieved.

'''if __name__ == "__main__":
    parent_folder = "disk"
    subfolders = [f"folder{i}" for i in range(1, 6)]
    threshold = 3

    compaction_manager = CompactionManager(parent_folder, subfolders, threshold)
    compaction_manager.create_folders()

    # Simulate adding CSV files with key-value pairs to folders
    for folder_name in subfolders:
        folder_path = compaction_manager.folder_paths[folder_name]
        compaction_manager.create_csv_files(folder_path)

    # Check threshold and compact if necessary
    for folder_name in subfolders:
        compaction_manager.check_threshold_and_compact(folder_name)'''