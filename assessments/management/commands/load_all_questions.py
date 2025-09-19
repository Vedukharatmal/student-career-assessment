import os
from django.core.management.base import BaseCommand, CommandError
from assessments.models import Question, Option, Field

# Mapping filenames → field enum values
FIELD_MAP = {
    "arts": Field.ARTS,
    "science": Field.SCIENCE,
    "commerce": Field.COMMERCE,
    "civil_engg": Field.CIVIL,
    "electrical_engg": Field.ELECTRICAL,
    "computer_engg": Field.COMPUTER,
    "mechanical_engg": Field.MECHANICAL,
    "electronics_engg": Field.ELECTRONICS,
}

class Command(BaseCommand):
    help = "Load all questions from a folder of .txt files into the database"

    def add_arguments(self, parser):
        parser.add_argument("folder_path", type=str, help="Path to the folder with .txt question files")

    def handle(self, *args, **kwargs):
        folder_path = kwargs["folder_path"]

        if not os.path.isdir(folder_path):
            raise CommandError(f"{folder_path} is not a valid folder")

        for filename in os.listdir(folder_path):
            if not filename.endswith(".txt"):
                continue

            field_key = filename.replace(".txt", "").lower()
            if field_key not in FIELD_MAP:
                self.stdout.write(self.style.WARNING(f"Skipping {filename} (no matching field in FIELD_MAP)"))
                continue

            field = FIELD_MAP[field_key]
            file_path = os.path.join(folder_path, filename)
            self.load_file(file_path, field)

    def load_file(self, file_path, field):
        self.stdout.write(self.style.NOTICE(f"Loading {file_path} for field {field}..."))

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("#")
                if len(parts) < 3:
                    self.stdout.write(self.style.WARNING(f"Skipping malformed line: {line}"))
                    continue

                qid = parts[0].strip()
                question_text = parts[1].strip()

                # Create question
                question = Question.objects.create(text=question_text, field=field)

                # Create options
                for opt in parts[2:]:
                    try:
                        text, points = opt.split("@")
                        Option.objects.create(
                            question=question,
                            text=text.strip(),
                            points=int(points.strip())
                        )
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"Skipping malformed option: {opt}"))

                self.stdout.write(self.style.SUCCESS(f"Added Question: {question_text}"))
